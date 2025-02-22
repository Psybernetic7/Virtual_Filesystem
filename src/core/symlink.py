# src/core/symlink.py

from typing import Optional
from .filesystem_node import FileSystemNode

class SymbolicLink(FileSystemNode):
    """
    Represents a symbolic link in the virtual filesystem.
    
    A symbolic link is a special type of filesystem node that serves as a reference 
    or pointer to another file or directory. Unlike hard links, symbolic links can:
    - Point to files or directories that don't exist (called "dangling" links)
    - Point to directories (not just files)
    - Link to targets across different parts of the filesystem
    
    For example, if you have a file structure:
    /home/user/documents/report.txt
    You could create a symlink:
    /home/user/desktop/report-shortcut -> /home/user/documents/report.txt
    
    Attributes:
        Inherits all attributes from FileSystemNode, plus:
        target_path (str): The path that this symbolic link points to
    """
    
    def __init__(self, name: str, target_path: str, parent: Optional[FileSystemNode] = None):
        """
        Initialize a new symbolic link.
        
        Creates a symbolic link with a specified target path. The target path is
        stored exactly as provided - resolution of relative paths happens when
        the link is followed, not when it's created.
        
        Args:
            name: The name of the symbolic link
            target_path: The path this link points to
            parent: Reference to the parent directory (None for root)
        """
        super().__init__(name, parent)
        self.target_path = target_path
    
    def get_size(self) -> int:
        """
        Calculate the size of the symbolic link.
        
        In most real filesystems, the size of a symbolic link is the length
        of its target path in bytes. This matches that behavior.
        
        Returns:
            Size of the target path in bytes
        """
        return len(self.target_path.encode('utf-8'))
    
    def get_target_path(self) -> str:
        """
        Get the path that this symbolic link points to.
        
        This method updates the access time since reading the target path
        counts as accessing the link's "content".
        
        Returns:
            The target path of this symbolic link
        """
        self.update_accessed_time()
        return self.target_path
    
    def set_target_path(self, new_target: str) -> None:
        """
        Update where this symbolic link points to.
        
        This is equivalent to deleting and recreating the symlink with a new
        target. Updates both modification and access times.
        
        Args:
            new_target: The new path this link should point to
        """
        self.target_path = new_target
        self.update_modified_time()  # This also updates access time