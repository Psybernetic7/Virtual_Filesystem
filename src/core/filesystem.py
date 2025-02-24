# src/core/filesystem.py

from typing import Dict, Optional
import os
from .file import File
from .directory import Directory
from .filesystem_node import FileSystemNode
from ..permissions.user import User
from ..permissions.user_manager import UserManager
from ..utils.logger import FileSystemLogger
from .symlink import SymbolicLink
from ..utils.state_persistence import StatePersistence


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
        self.logger = FileSystemLogger()
        self.state_manager = StatePersistence()

    def save_state(self, filepath: str) -> bool:
        """Save filesystem state to encrypted file."""
        return self.state_manager.save_state(self, filepath)
    
    def load_state(self, filepath: str) -> bool:
        """Load filesystem state from encrypted file."""
        return self.state_manager.load_state(self, filepath)

    
    def get_node_by_path(self, path: str, follow_links: bool = True) -> Optional[FileSystemNode]:
        """Resolve a path to its corresponding filesystem node."""
        user = self.user_manager.get_current_user()
        
        # Starting point for path resolution
        if path.startswith('/'):
            current = self.root
            path = path[1:]
        else:
            current = self.current_directory
        
        # Handle empty path or root
        if not path:
            return current
        
        # Path traversal with logging
        try:
            components = path.split('/')
            for component in components:
                if component == '' or component == '.':
                    continue
                if component == '..':
                    if current.parent is not None:
                        current = current.parent
                    continue
                
                if not isinstance(current, Directory):
                    self.logger.log_operation("PATH_RESOLVE", path, user.username, False, 
                                            "Not a directory during path traversal")
                    return None
                
                current = current.get_child(component, user)
                if current is None:
                    self.logger.log_operation("PATH_RESOLVE", path, user.username, False, 
                                            f"Component not found: {component}")
                    return None
                
                # Handle symbolic links
                if follow_links and isinstance(current, SymbolicLink):
                    target_path = current.get_target_path(user)
                    # Recursively resolve the target
                    resolved = self.get_node_by_path(target_path, follow_links)
                    if resolved is None:
                        self.logger.log_operation("PATH_RESOLVE", path, user.username, False, 
                                                f"Broken symbolic link to {target_path}")
                        return None
                    current = resolved
            
            self.logger.log_operation("PATH_RESOLVE", path, user.username, True)
            return current
            
        except Exception as e:
            self.logger.log_operation("PATH_RESOLVE", path, user.username, False, 
                                    f"Error: {str(e)}")
            return None

    def create_file(self, path: str, content: str = '') -> Optional[File]:
        user = self.user_manager.get_current_user()
        dirname, filename = os.path.split(path)
        
        if not filename:
            self.logger.log_operation("CREATE_FILE", path, user.username, False, 
                                    "Invalid filename")
            return None
        
        parent_dir = self.get_node_by_path(dirname)
        if parent_dir is None or not isinstance(parent_dir, Directory):
            self.logger.log_operation("CREATE_FILE", path, user.username, False, 
                                    "Invalid directory")
            return None
        
        if parent_dir.get_child(filename, user) is not None:
            self.logger.log_operation("CREATE_FILE", path, user.username, False, 
                                    "File already exists")
            return None
        
        new_file = File(filename, owner=user.username, 
                       group=next(iter(user.groups)), content=content)
        
        if not parent_dir.add_child(new_file, user):
            self.logger.log_operation("CREATE_FILE", path, user.username, False, 
                                    "Permission denied")
            return None
        
        self.logger.log_operation("CREATE_FILE", path, user.username, True)
        return new_file

    def read_file(self, path: str) -> Optional[str]:
        """Read the contents of a file."""
        user = self.user_manager.get_current_user()
        node = self.get_node_by_path(path)
        
        if node is None or not isinstance(node, File):
            self.logger.log_operation("READ_FILE", path, user.username, False, 
                                    "File not found or not a file")
            return None
        
        content = node.get_content(user)
        success = content is not None
        self.logger.log_operation("READ_FILE", path, user.username, success)
        return content

    def write_file(self, path: str, content: str) -> bool:
        user = self.user_manager.get_current_user()
        node = self.get_node_by_path(path)
        
        if node is None:
            # Try to create new file
            success = self.create_file(path, content) is not None
            if not success:
                self.logger.log_operation("WRITE_FILE", path, user.username, False, 
                                        "Failed to create new file")
            return success
        
        if not isinstance(node, File):
            self.logger.log_operation("WRITE_FILE", path, user.username, False, 
                                    "Not a file")
            return False
        
        success = node.set_content(content, user)
        self.logger.log_operation("WRITE_FILE", path, user.username, success)
        return success


    def create_directory(self, path: str) -> Optional[Directory]:
        """Create a new directory at the specified path."""
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
        """List contents of a directory."""
        user = self.user_manager.get_current_user()
        node = self.get_node_by_path(path)
        
        if node is None or not isinstance(node, Directory):
            self.logger.log_operation("LIST_DIR", path, user.username, False, 
                                    "Not a directory")
            return None
        
        contents = node.list_children(user)
        self.logger.log_operation("LIST_DIR", path, user.username, True, 
                                f"Found {len(contents)} items")
        return contents

    def change_directory(self, path: str) -> bool:
        """Change current working directory."""
        user = self.user_manager.get_current_user()
        node = self.get_node_by_path(path)
        
        if node is None or not isinstance(node, Directory):
            self.logger.log_operation("CHANGE_DIR", path, user.username, False, 
                                    "Invalid directory")
            return False
        
        self.current_directory = node
        self.logger.log_operation("CHANGE_DIR", path, user.username, True)
        return True

    def get_current_path(self) -> str:
        """
        Get the absolute path of current working directory.
        
        Returns:
            String representation of current path
        """
        return self.current_directory.get_full_path()
    
    def delete(self, path: str) -> bool:
        """
        Delete a file or directory.
        
        Args:
            path: Path to the file or directory to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        user = self.user_manager.get_current_user()
        
        # Can't delete root
        if path == '/':
            self.logger.log_operation("DELETE", path, user.username, False, 
                                    "Cannot delete root directory")
            return False
        
        # Get the parent directory and the node to delete
        dirname, basename = os.path.split(path)
        parent_dir = self.get_node_by_path(dirname)
        
        if parent_dir is None or not isinstance(parent_dir, Directory):
            self.logger.log_operation("DELETE", path, user.username, False, 
                                    "Parent directory not found")
            return False
        
        # Check if node exists
        node = parent_dir.get_child(basename, user)
        if node is None:
            self.logger.log_operation("DELETE", path, user.username, False, 
                                    "File/directory not found")
            return False
        
        # Delete the node
        success = parent_dir.remove_child(basename, user)
        self.logger.log_operation("DELETE", path, user.username, success)
        return success
    
    def search_by_name(self, pattern: str, current_path: str = '.') -> list[str]:
        """
        Search for files/directories whose names match a pattern.
        
        Args:
            pattern: The name pattern to search for (supports * and ? wildcards)
            current_path: Directory to start search from
            
        Returns:
            List of paths to matching files/directories
        """
        import fnmatch
        results = []
        user = self.user_manager.get_current_user()

        def _search_recursive(directory: Directory, current_path: str):
            contents = directory.list_children(user)
            for name, node in contents.items():
                full_path = os.path.join(current_path, name)
                
                # Check if name matches pattern
                if fnmatch.fnmatch(name, pattern):
                    results.append(full_path)
                
                # Recursively search directories
                if isinstance(node, Directory):
                    _search_recursive(node, full_path)

        # Get starting directory
        start_dir = self.get_node_by_path(current_path)
        if start_dir and isinstance(start_dir, Directory):
            _search_recursive(start_dir, current_path)
            
        self.logger.log_operation("SEARCH_NAME", pattern, user.username, True, 
                                f"Found {len(results)} matches")
        return results
    
    def search_by_content(self, text: str, current_path: str = '.') -> list[str]:
        """
        Search for files containing specific text.
        """
        results = []
        user = self.user_manager.get_current_user()
        
        search_text = text.strip()
        if search_text.startswith('"') and search_text.endswith('"'):
            search_text = search_text[1:-1]
        
        def _search_recursive(directory: Directory, current_path: str):
            contents = directory.list_children(user)
            for name, node in contents.items():
                full_path = name if current_path == '.' else f"{current_path}/{name}"
                
                if isinstance(node, File):
                    content = node.get_content(user)
                    if content and search_text in content:
                        results.append(full_path)
                elif isinstance(node, Directory):
                    _search_recursive(node, full_path)
        
        start_dir = self.get_node_by_path(current_path)
        if start_dir and isinstance(start_dir, Directory):
            _search_recursive(start_dir, current_path)
        
        return results
    
    def create_symlink(self, link_path: str, target_path: str) -> Optional[SymbolicLink]:
        """
        Create a symbolic link.
        
        Args:
            link_path: Path where the symlink should be created
            target_path: Path that the symlink should point to
            
        Returns:
            The created SymbolicLink object, or None if creation failed
        """
        user = self.user_manager.get_current_user()
        
        # Split the link path into directory and link name
        dirname, linkname = os.path.split(link_path)
        
        if not linkname:
            self.logger.log_operation("CREATE_SYMLINK", link_path, user.username, 
                                    False, "Invalid link name")
            return None
        
        # Get parent directory where link will be created
        parent_dir = self.get_node_by_path(dirname)
        if parent_dir is None or not isinstance(parent_dir, Directory):
            self.logger.log_operation("CREATE_SYMLINK", link_path, user.username, 
                                    False, "Parent directory not found")
            return None
        
        # Check if a file/directory already exists at link_path
        if parent_dir.get_child(linkname, user) is not None:
            self.logger.log_operation("CREATE_SYMLINK", link_path, user.username, 
                                    False, "Path already exists")
            return None
        
        # Create the symbolic link
        new_link = SymbolicLink(linkname, user.username, 
                            next(iter(user.groups)), target_path)
        
        if not parent_dir.add_child(new_link, user):
            self.logger.log_operation("CREATE_SYMLINK", link_path, user.username, 
                                    False, "Failed to add to parent directory")
            return None
        
        self.logger.log_operation("CREATE_SYMLINK", link_path, user.username, 
                                True, f"Target: {target_path}")
        return new_link