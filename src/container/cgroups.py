import os
import shutil

CGROUP_BASE = '/sys/fs/cgroup'


class CgroupManager:

    def __init__(self, name: str):
        self.name = name
        self.cgroup_path = os.path.join(CGROUP_BASE, f'vfs_container_{name}')

    def create(self):
        self.enable_controllers()
        os.makedirs(self.cgroup_path, exist_ok=True)

    def enable_controllers(self):
        subtree_control = os.path.join(CGROUP_BASE, 'cgroup.subtree_control')
        try:
            with open(subtree_control, 'w') as f:
                f.write('+memory +cpu +pids')
        except PermissionError:
            pass

    def set_memory_limit(self, limit_bytes: int):
        with open(os.path.join(self.cgroup_path, 'memory.max'), 'w') as f:
            f.write(str(limit_bytes))

    def set_cpu_limit(self, quota_us: int, period_us: int = 100000):
        with open(os.path.join(self.cgroup_path, 'cpu.max'), 'w') as f:
            f.write(f'{quota_us} {period_us}')

    def set_pid_limit(self, max_pids: int):
        with open(os.path.join(self.cgroup_path, 'pids.max'), 'w') as f:
            f.write(str(max_pids))

    def add_process(self, pid: int):
        with open(os.path.join(self.cgroup_path, 'cgroup.procs'), 'w') as f:
            f.write(str(pid))

    def get_stats(self) -> dict:
        stats = {}
        for name in ('memory.current', 'pids.current'):
            path = os.path.join(self.cgroup_path, name)
            if os.path.exists(path):
                with open(path) as f:
                    stats[name] = f.read().strip()
        cpu_stat = os.path.join(self.cgroup_path, 'cpu.stat')
        if os.path.exists(cpu_stat):
            with open(cpu_stat) as f:
                stats['cpu.stat'] = f.read().strip()
        return stats

    def cleanup(self):
        try:
            if os.path.exists(self.cgroup_path):
                os.rmdir(self.cgroup_path)
        except OSError:
            pass
