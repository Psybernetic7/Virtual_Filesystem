# src/core/file.py

from typing import Optional
from .filesystem_node import FileSystemNode
from ..permissions.user import User

class File(FileSystemNode):
    """
    Represents a file in the virtual filesystem.
    """
    
    def __init__(self, name: str, owner: str, group: str, parent: Optional[FileSystemNode] = None, content: str = ''):
        """
        Initialize a new file.
        
        Args:
            name: The name of the file
            owner: Username of the file owner
            group: Group name for the file
            parent: Reference to the parent directory (None for root)
            content: Initial content of the file (empty by default)
        """
        super().__init__(name, owner, group, parent)
        self._content = content
    
    def get_content(self, user: Optional[User] = None) -> str:
        """
        Retrieve the file's content.
        """
        self.update_accessed_time()
        return self._content
    
    def set_content(self, content: str, user: Optional[User] = None) -> bool:
        """
        Update the file's content.
        """
        self._content = content
        self.update_modified_time()
        return True
    
    def get_size(self) -> int:
        """
        Calculate the size of the file in bytes.
        """
        return len(self._content.encode('utf-8'))