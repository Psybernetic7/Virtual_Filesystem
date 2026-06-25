import os
from .syscall_wrappers import sethostname

NAMESPACE_FLAGS = {
    'uts': os.CLONE_NEWUTS,
    'pid': os.CLONE_NEWPID,
    'mount': os.CLONE_NEWNS,
    'net': os.CLONE_NEWNET,
    'user': os.CLONE_NEWUSER,
    'ipc': os.CLONE_NEWIPC,
    'cgroup': os.CLONE_NEWCGROUP,
}


class NamespaceManager:

    def __init__(self, namespaces: list[str]):
        for ns in namespaces:
            if ns not in NAMESPACE_FLAGS:
                raise ValueError(f"Unknown namespace: {ns}. Valid: {', '.join(NAMESPACE_FLAGS)}")
        self.namespaces = namespaces

    def combined_flags(self) -> int:
        flags = 0
        for ns in self.namespaces:
            flags |= NAMESPACE_FLAGS[ns]
        return flags

    def unshare(self):
        os.unshare(self.combined_flags())

    def setup_uts(self, hostname: str):
        sethostname(hostname)

    def setup_user_ns(self, pid: int, uid_map: str = '0 1000 1', gid_map: str = '0 1000 1'):
        proc = f'/proc/{pid}'
        with open(f'{proc}/setgroups', 'w') as f:
            f.write('deny')
        with open(f'{proc}/uid_map', 'w') as f:
            f.write(uid_map)
        with open(f'{proc}/gid_map', 'w') as f:
            f.write(gid_map)
