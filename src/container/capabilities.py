from .syscall_wrappers import prctl, PR_SET_NO_NEW_PRIVS, PR_CAPBSET_DROP, PR_CAP_AMBIENT, PR_CAP_AMBIENT_CLEAR_ALL

CAP_CHOWN = 0
CAP_DAC_OVERRIDE = 1
CAP_FOWNER = 3
CAP_FSETID = 4
CAP_KILL = 5
CAP_SETGID = 6
CAP_SETUID = 7
CAP_SETPCAP = 8
CAP_NET_BIND_SERVICE = 10
CAP_NET_RAW = 13
CAP_SYS_CHROOT = 18
CAP_MKNOD = 27
CAP_AUDIT_WRITE = 29
CAP_SETFCAP = 31

DEFAULT_CONTAINER_CAPS = [
    CAP_CHOWN, CAP_DAC_OVERRIDE, CAP_FOWNER, CAP_FSETID,
    CAP_KILL, CAP_SETGID, CAP_SETUID, CAP_SETPCAP,
    CAP_NET_BIND_SERVICE, CAP_NET_RAW, CAP_SYS_CHROOT,
    CAP_MKNOD, CAP_AUDIT_WRITE, CAP_SETFCAP,
]


class CapabilityManager:

    def __init__(self, keep_caps: list[int] | None = None):
        self.keep_caps = set(keep_caps if keep_caps is not None else DEFAULT_CONTAINER_CAPS)

    def get_last_cap(self) -> int:
        with open('/proc/sys/kernel/cap_last_cap') as f:
            return int(f.read().strip())

    def drop_bounding_set(self):
        last_cap = self.get_last_cap()
        for cap in range(last_cap + 1):
            if cap not in self.keep_caps:
                try:
                    prctl(PR_CAPBSET_DROP, cap)
                except OSError:
                    pass

    def set_no_new_privs(self):
        prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)

    def clear_ambient(self):
        try:
            prctl(PR_CAP_AMBIENT, PR_CAP_AMBIENT_CLEAR_ALL, 0, 0, 0)
        except OSError:
            pass

    def apply(self):
        self.set_no_new_privs()
        self.drop_bounding_set()
        self.clear_ambient()
