# src/core/symlink.py

from typing import Optional
from .filesystem_node import FileSystemNode
from ..permissions.user import User

class SymbolicLink(FileSystemNode):
    """
    Represents a symbolic link in the virtual filesystem.
    A symbolic link is a special file that points to another file or directory.
    """
    
    def __init__(self, name: str, owner: str, group: str, target_path: str, parent: Optional[FileSystemNode] = None):
        """
        Initialize a symbolic link.
        
        Args:
            name: Name of the symbolic link
            owner: Username of the owner
            group: Group name for permissions
            target_path: Path that this link points to
            parent: Parent directory of this link
        """
        super().__init__(name, owner, group, parent)
        self.target_path = target_path
    
    def get_size(self) -> int:
        """
        Get the size of the symbolic link.
        For symlinks, the size is the length of the target path in bytes.
        """
        return len(self.target_path.encode('utf-8'))
    
    def get_target_path(self, user: Optional[User] = None) -> str:
        """
        Get the path this symlink points to.
        """
        self.update_accessed_time()
        return self.target_path