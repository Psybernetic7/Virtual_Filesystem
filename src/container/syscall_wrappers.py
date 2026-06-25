import ctypes
import ctypes.util
import os

_libc = ctypes.CDLL(ctypes.util.find_library('c'), use_errno=True)

SYS_pivot_root = 155  # x86_64

MS_RDONLY = 1
MS_NOSUID = 2
MS_NODEV = 4
MS_NOEXEC = 8
MS_BIND = 4096
MS_REC = 16384
MS_PRIVATE = 1 << 18

MNT_DETACH = 2

PR_SET_NO_NEW_PRIVS = 38
PR_CAPBSET_DROP = 24
PR_CAP_AMBIENT = 47
PR_CAP_AMBIENT_CLEAR_ALL = 4


def _check_errno(ret, func_name):
    if ret == -1:
        errno = ctypes.get_errno()
        raise OSError(errno, f"{func_name}: {os.strerror(errno)}")
    return ret


def mount(source: str, target: str, fstype: str, flags: int, data: str) -> int:
    ret = _libc.mount(
        source.encode() if source else None,
        target.encode(),
        fstype.encode() if fstype else None,
        ctypes.c_ulong(flags),
        data.encode() if data else None,
    )
    return _check_errno(ret, "mount")


def umount2(target: str, flags: int) -> int:
    ret = _libc.umount2(target.encode(), ctypes.c_int(flags))
    return _check_errno(ret, "umount2")


def pivot_root(new_root: str, put_old: str) -> int:
    _libc.syscall.restype = ctypes.c_long
    _libc.syscall.argtypes = [ctypes.c_long, ctypes.c_char_p, ctypes.c_char_p]
    ret = _libc.syscall(SYS_pivot_root, new_root.encode(), put_old.encode())
    return _check_errno(ret, "pivot_root")


def prctl(option: int, arg2: int = 0, arg3: int = 0, arg4: int = 0, arg5: int = 0) -> int:
    ret = _libc.prctl(
        ctypes.c_int(option),
        ctypes.c_ulong(arg2),
        ctypes.c_ulong(arg3),
        ctypes.c_ulong(arg4),
        ctypes.c_ulong(arg5),
    )
    return _check_errno(ret, "prctl")


def sethostname(name: str) -> int:
    name_bytes = name.encode()
    ret = _libc.sethostname(name_bytes, len(name_bytes))
    return _check_errno(ret, "sethostname")
