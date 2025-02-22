# src/core/filesystem_node.py

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

class FileSystemNode(ABC):
    """
    Abstract base class for all filesystem objects (files, directories, symbolic links).
    
    This class defines the common interface and behavior that all filesystem nodes
    must implement. It tracks basic metadata like creation and modification times,
    ownership, and handles path construction.
    
    Attributes:
        name (str): Name of the filesystem node
        parent (Optional[FileSystemNode]): Reference to the parent node (None for root)
        created_at (datetime): Timestamp of when the node was created
        modified_at (datetime): Timestamp of last modification
        accessed_at (datetime): Timestamp of last access
    """
    
    def __init__(self, name: str, owner: str, group: str, parent: Optional['FileSystemNode'] = None):
        """
        Initialize a new filesystem node.
        
        Args:
            name: The name of the node (file or directory name)
            parent: Reference to the parent node (None for root node)
        
        Raises:
            ValueError: If name contains invalid characters (/, \0)
        """
        # Validate node name
        if '/' in name or '\0' in name:
            raise ValueError("Node name cannot contain '/' or null characters")
            
        self.name = name
        self.owner = owner
        self.group = group
        self.parent = parent
        
        # Initialize timestamps
        current_time = datetime.now()
        self.created_at = current_time
        self.modified_at = current_time
        self.accessed_at = current_time
    
    def get_full_path(self) -> str:
        """
        Construct the full path to this node from the root.
        
        Returns:
            The absolute path to this node, starting with /
        """
        if self.parent is None:
            return '/' if self.name == '' else f'/{self.name}'
            
        if self.parent.get_full_path() == '/':
            return f'/{self.name}'
            
        return f'{self.parent.get_full_path()}/{self.name}'
    
    @abstractmethod
    def get_size(self) -> int:
        """
        Calculate the size of this node in bytes.
        
        This is an abstract method that must be implemented by subclasses.
        Files will return their content size, directories will return the sum
        of all children's sizes, and symbolic links will return the length
        of their target path.
        
        Returns:
            Size in bytes
        """
        pass
    
    def update_accessed_time(self) -> None:
        """
        Update the last accessed timestamp to the current time.
        Should be called whenever the node's data is read.
        """
        self.accessed_at = datetime.now()
    
    def update_modified_time(self) -> None:
        """
        Update the last modified timestamp to the current time.
        Should be called whenever the node's data is changed.
        Also updates the access time since modification implies access.
        """
        self.modified_at = datetime.now()
        self.update_accessed_time()