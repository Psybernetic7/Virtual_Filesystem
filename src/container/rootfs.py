import os
import tempfile

from .syscall_wrappers import mount, umount2, pivot_root
from .syscall_wrappers import MS_BIND, MS_REC, MS_PRIVATE, MS_NOSUID, MS_NODEV, MS_NOEXEC, MNT_DETACH


class RootfsManager:

    def __init__(self, rootfs_path: str):
        self.rootfs_path = os.path.realpath(rootfs_path)
        self._mount_point = None

    def validate_rootfs(self) -> bool:
        if not os.path.isdir(self.rootfs_path):
            return False
        for d in ('bin', 'lib', 'usr'):
            if os.path.isdir(os.path.join(self.rootfs_path, d)):
                return True
        return False

    def setup_mount_namespace(self):
        mount("", "/", "", MS_REC | MS_PRIVATE, "")

    def bind_mount_rootfs(self):
        self._mount_point = tempfile.mkdtemp(prefix='vfs_root_')
        mount(self.rootfs_path, self._mount_point, "", MS_BIND | MS_REC, "")

    def do_pivot_root(self):
        put_old = os.path.join(self._mount_point, '.pivot_old')
        os.makedirs(put_old, exist_ok=True)

        pivot_root(self._mount_point, put_old)
        os.chdir('/')

        umount2('/.pivot_old', MNT_DETACH)
        try:
            os.rmdir('/.pivot_old')
        except OSError:
            pass

    def mount_proc(self):
        os.makedirs('/proc', exist_ok=True)
        mount("proc", "/proc", "proc", MS_NOSUID | MS_NODEV | MS_NOEXEC, "")

    def mount_dev(self):
        import stat
        os.makedirs('/dev', exist_ok=True)
        mount("tmpfs", "/dev", "tmpfs", MS_NOSUID, "mode=755")
        devices = {
            'null':    (1, 3),
            'zero':    (1, 5),
            'random':  (1, 8),
            'urandom': (1, 9),
            'tty':     (5, 0),
        }
        for name, (major, minor) in devices.items():
            path = f'/dev/{name}'
            try:
                os.mknod(path, 0o666 | stat.S_IFCHR, os.makedev(major, minor))
            except OSError:
                pass

    def mount_sys(self):
        os.makedirs('/sys', exist_ok=True)
        try:
            mount("sysfs", "/sys", "sysfs", MS_NOSUID | MS_NODEV | MS_NOEXEC, "")
        except OSError:
            pass

    @staticmethod
    def export_vfs_to_rootfs(filesystem, target_dir: str):
        from ..core.directory import Directory
        from ..core.file import File
        from ..core.symlink import SymbolicLink

        os.makedirs(target_dir, exist_ok=True)

        def _export_node(node, current_path: str):
            if isinstance(node, Directory):
                os.makedirs(current_path, exist_ok=True)
                for name, child in node.children.items():
                    child_path = os.path.join(current_path, name)
                    _export_node(child, child_path)
            elif isinstance(node, File):
                with open(current_path, 'w') as f:
                    f.write(node._content)
            elif isinstance(node, SymbolicLink):
                target = node.target_path
                if os.path.exists(current_path) or os.path.islink(current_path):
                    os.unlink(current_path)
                os.symlink(target, current_path)

        _export_node(filesystem.root, target_dir)
