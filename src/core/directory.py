# src/core/directory.py

from typing import Dict, Optional
from .filesystem_node import FileSystemNode
from ..permissions.user import User

class Directory(FileSystemNode):
    """
    Represents a directory in the virtual filesystem.
    
    A directory is a container that can hold other filesystem nodes (files, directories,
    or symbolic links). It maintains a collection of its children and provides methods
    to manage them. Unlike files, directories don't have content of their own - their
    'content' is their collection of child nodes.
    
    Think of a directory like a folder in a real filing cabinet - it can contain
    documents (files) and other folders (subdirectories), but it doesn't contain
    direct content itself.
    
    Attributes:
        Inherits all attributes from FileSystemNode, plus:
        children (Dict[str, FileSystemNode]): Dictionary mapping child names to nodes
    """
    
    def __init__(self, name: str, owner: str, group: str, parent: Optional[FileSystemNode] = None):
        """
        Initialize a new directory.
        
        Creates an empty directory that can store child nodes. The children are stored
        in a dictionary where the keys are the names of the children and the values
        are the child nodes themselves. This allows for fast lookups by name.
        
        Args:
            name: The name of the directory
            parent: Reference to the parent directory (None for root)
        """
        super().__init__(name, owner, group, parent)
        self.children: Dict[str, FileSystemNode] = {}
    
    def add_child(self, node: FileSystemNode, user: Optional[User] = None) -> bool:
        """
        Add a new child node to this directory.
        
        Args:
            node: The filesystem node to add as a child
            user: The user performing the operation (for permission checking)
            
        Returns:
            True if successful, False if failed (e.g., no permission)
        """
        self.children[node.name] = node
        node.parent = self
        self.update_modified_time()
        return True
    
    def remove_child(self, name: str, user: Optional[User] = None) -> bool:
        """
        Remove a child node from this directory.
        
        Args:
            name: The name of the child to remove
            user: The user requesting the removal (for permission checking)
        
        Returns:
            True if child was removed, False if child didn't exist or permission denied
        """
        if name in self.children:
            del self.children[name]
            self.update_modified_time()
            return True
        return False
    
    def get_child(self, name: str, user: Optional[User] = None) -> Optional[FileSystemNode]:
        """
        Retrieve a child node by its name.
        
        Args:
            name: The name of the child to retrieve
            user: The user requesting access (for permission checking)
        
        Returns:
            The child node if found and accessible, None otherwise
        """
        self.update_accessed_time()
        return self.children.get(name)
    
    def list_children(self, user: Optional[User] = None) -> Dict[str, FileSystemNode]:
        """
        Get a dictionary of all children in this directory.
        
        Args:
            user: The user requesting the listing (for permission checking)
        """
        self.update_accessed_time()
        return self.children
    
    def get_size(self) -> int:
        """
        Calculate the total size of the directory.
        
        For a directory, the size is the sum of the sizes of all its children.
        This is similar to how the 'du' command works in Unix-like systems.
        
        Returns:
            Total size in bytes of all children recursively
        """
        return sum(child.get_size() for child in self.children.values())