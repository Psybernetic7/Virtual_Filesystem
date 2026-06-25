import json
import os
import subprocess
import sys

from .namespaces import NamespaceManager
from .rootfs import RootfsManager
from .cgroups import CgroupManager
from .capabilities import CapabilityManager
from .rlimits import RlimitManager


class Container:

    def __init__(
        self,
        rootfs_path: str,
        command: list[str],
        hostname: str = 'container',
        namespaces: list[str] | None = None,
        memory_limit: int = 256 * 1024 * 1024,
        cpu_quota: int = 50000,
        pid_limit: int = 64,
        keep_caps: list[int] | None = None,
        rlimits: dict[str, tuple[int, int]] | None = None,
    ):
        self.rootfs_path = rootfs_path
        self.command = command
        self.hostname = hostname
        self.memory_limit = memory_limit
        self.cpu_quota = cpu_quota
        self.pid_limit = pid_limit

        if namespaces is None:
            namespaces = ['uts', 'pid', 'mount', 'ipc', 'net']
        self.ns_manager = NamespaceManager(namespaces)
        self.rootfs_manager = RootfsManager(rootfs_path)
        self.cgroup_manager = CgroupManager(hostname)
        self.cap_manager = CapabilityManager(keep_caps)
        self.rlimit_manager = RlimitManager(rlimits)

    def run(self) -> int:
        if os.geteuid() != 0:
            print("Error: Container operations require root. Run with sudo.")
            return 1

        if not self.rootfs_manager.validate_rootfs():
            print(f"Error: Invalid rootfs at '{self.rootfs_path}'. Needs bin/, lib/, or usr/.")
            return 1

        config = json.dumps({
            'rootfs_path': self.rootfs_path,
            'command': self.command,
            'hostname': self.hostname,
            'namespaces': self.ns_manager.namespaces,
            'memory_limit': self.memory_limit,
            'cpu_quota': self.cpu_quota,
            'pid_limit': self.pid_limit,
            'keep_caps': sorted(self.cap_manager.keep_caps),
            'rlimits': self.rlimit_manager.limits,
        })

        main_script = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'main.py',
        )

        env = os.environ.copy()
        env['_VFS_CONTAINER_CONFIG'] = config

        result = subprocess.run(
            [sys.executable, main_script, '--container-child'],
            env=env,
        )
        return result.returncode


def container_child_entry():
    config = json.loads(os.environ['_VFS_CONTAINER_CONFIG'])

    cgroup = CgroupManager(config['hostname'])
    try:
        cgroup.create()
        cgroup.set_memory_limit(config['memory_limit'])
        cgroup.set_cpu_limit(config['cpu_quota'])
        cgroup.set_pid_limit(config['pid_limit'])
        cgroup.add_process(os.getpid())
    except (OSError, PermissionError) as e:
        print(f"Warning: Could not configure cgroups: {e}", file=sys.stderr)

    ns_manager = NamespaceManager(config['namespaces'])
    rootfs_manager = RootfsManager(config['rootfs_path'])
    cap_manager = CapabilityManager(config.get('keep_caps'))
    rlimit_manager = RlimitManager(config.get('rlimits'))

    ns_manager.unshare()

    if 'uts' in config['namespaces']:
        ns_manager.setup_uts(config['hostname'])

    if 'pid' in config['namespaces']:
        pid = os.fork()
        if pid > 0:
            _, status = os.waitpid(pid, 0)
            cgroup.cleanup()
            code = os.WEXITSTATUS(status) if os.WIFEXITED(status) else 1
            os._exit(code)

    rootfs_manager.setup_mount_namespace()
    rootfs_manager.bind_mount_rootfs()
    rootfs_manager.do_pivot_root()
    rootfs_manager.mount_proc()
    rootfs_manager.mount_dev()
    rootfs_manager.mount_sys()

    rlimit_manager.apply()
    cap_manager.apply()

    os.execvp(config['command'][0], config['command'])
