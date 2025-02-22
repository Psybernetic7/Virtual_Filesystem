# src/core/filesystem.py

from typing import Dict, Optional
import os
from .file import File
from .directory import Directory
from .filesystem_node import FileSystemNode
from ..permissions.user import User
from ..permissions.user_manager import UserManager

class FileSystem:
    """
    Main class that manages the virtual filesystem operations.
    
    This class serves as the primary interface for filesystem operations,
    handling path resolution, file/directory operations, and permission checks.
    """
    
    def __init__(self, user_manager: UserManager):
        """
        Initialize a new filesystem instance.
        
        Creates the root directory and sets it as the current working directory.
        The root directory is owned by root:root with standard permissions.
        
        Args:
            user_manager: UserManager instance to handle user operations
        """
        self.user_manager = user_manager
        self.root = Directory('', owner='root', group='root')
        self.current_directory = self.root
    
    def get_node_by_path(self, path: str) -> Optional[FileSystemNode]:
        """
        Resolve a path to its corresponding filesystem node.
        
        Handles both absolute paths (starting with /) and relative paths.
        Also manages special path components:
        - '.' (current directory)
        - '..' (parent directory)
        
        Args:
            path: The path to resolve
            
        Returns:
            The found FileSystemNode or None if path doesn't exist
        """
        # Handle absolute vs relative paths
        if path.startswith('/'):
            current = self.root
            path = path[1:]  # Remove leading '/'
        else:
            current = self.current_directory
        
        # Handle empty path or root
        if not path:
            return current
            
        # Split path into components and traverse
        components = path.split('/')
        for component in components:
            if component == '':
                continue
            if component == '.':
                continue
            if component == '..':
                if current.parent is not None:
                    current = current.parent
                continue
            
            if isinstance(current, Directory):
                current = current.get_child(component, self.user_manager.get_current_user())
                if current is None:
                    return None
            else:
                return None
        
        return current

    def create_file(self, path: str, content: str = '') -> Optional[File]:
        """
        Create a new file at the specified path.
        
        Args:
            path: Where to create the file
            content: Initial content of the file (empty by default)
        
        Returns:
            The newly created File object, or None if creation failed
        """
        dirname, filename = os.path.split(path)
        
        if not filename:
            return None
        
        user = self.user_manager.get_current_user()
        parent_dir = self.get_node_by_path(dirname)
        
        if parent_dir is None or not isinstance(parent_dir, Directory):
            return None
        
        if parent_dir.get_child(filename, user) is not None:
            return None  # File already exists
        
        new_file = File(filename, owner=user.username, 
                        group=next(iter(user.groups)), content=content)
        
        if not parent_dir.add_child(new_file, user):
            return None
        
        return new_file

    def read_file(self, path: str) -> Optional[str]:
        """
        Read the contents of a file.
        
        Args:
            path: Path to the file to read
        
        Returns:
            The file's contents, or None if file doesn't exist or permission denied
        """
        node = self.get_node_by_path(path)
        user = self.user_manager.get_current_user()
        
        if node is None or not isinstance(node, File):
            return None
        
        return node.get_content(user)

    def write_file(self, path: str, content: str) -> bool:
        """
        Write content to a file, creating it if it doesn't exist.
        
        Args:
            path: Path to the file
            content: New content for the file
        
        Returns:
            True if write successful, False otherwise
        """
        node = self.get_node_by_path(path)
        user = self.user_manager.get_current_user()
        
        if node is None:
            # Create new file if it doesn't exist
            return self.create_file(path, content) is not None
        
        if not isinstance(node, File):
            return False
        
        return node.set_content(content, user)


    def create_directory(self, path: str) -> Optional[Directory]:
        """
        Create a new directory at the specified path.
        
        Args:
            path: Where to create the directory
        
        Returns:
            The newly created Directory object, or None if creation failed
        """
        if path.endswith('/'):
            path = path[:-1]  # Remove trailing slash
        
        dirname, new_dirname = os.path.split(path)
        
        if not new_dirname:
            return None
        
        user = self.user_manager.get_current_user()
        parent_dir = self.get_node_by_path(dirname)
        
        if parent_dir is None or not isinstance(parent_dir, Directory):
            return None
        
        if parent_dir.get_child(new_dirname, user) is not None:
            return None  # Directory already exists
        
        new_directory = Directory(new_dirname, 
                                owner=user.username,
                                group=next(iter(user.groups)))
        
        if not parent_dir.add_child(new_directory, user):
            return None
            
        return new_directory

    def list_directory(self, path: str = '.') -> Optional[Dict[str, FileSystemNode]]:
        """
        List contents of a directory.
        
        Args:
            path: Path to directory to list (defaults to current directory)
        
        Returns:
            Dictionary of child names to nodes, or None if path invalid/permission denied
        """
        node = self.get_node_by_path(path)
        user = self.user_manager.get_current_user()
        
        if node is None or not isinstance(node, Directory):
            return None
        
        return node.list_children(user)

    def change_directory(self, path: str) -> bool:
        """
        Change current working directory.
        
        Args:
            path: Path to change to
        
        Returns:
            True if successful, False if path invalid or permission denied
        """
        node = self.get_node_by_path(path)
        user = self.user_manager.get_current_user()
        
        if node is None or not isinstance(node, Directory):
            return False
        
        self.current_directory = node
        return True

    def get_current_path(self) -> str:
        """
        Get the absolute path of current working directory.
        
        Returns:
            String representation of current path
        """
        return self.current_directory.get_full_path()