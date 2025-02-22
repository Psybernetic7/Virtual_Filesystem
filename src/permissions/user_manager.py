# src/permissions/user_manager.py

from typing import Dict, Set, Optional
from .user import User

class UserManager:
    """
    Manages users and groups in the virtual filesystem.
    
    This class is responsible for:
    - Creating and removing users
    - Managing user groups
    - Ensuring unique usernames and user IDs
    - Tracking all users and groups in the system
    
    It maintains the system's user and group database, similar to how Unix-like
    systems manage /etc/passwd and /etc/group files.
    """
    
    def __init__(self):
        """
        Initialize the user management system.
        
        Sets up initial state with:
        - Empty user database
        - Basic groups (root and users)
        - Root user
        Sets root as the current user.
        """
        # Initialize user and group storage
        self.users: Dict[str, User] = {} 
        self.groups: Dict[str, Set[str]] = {
            'root': set(),   # Special admin group
            'users': set()   # Default group for all users
        }
        
        # Create root user
        self.add_user('root', 0, {'root'})
        
        # Set current user to root initially
        self.current_user = self.users['root']
    
    def add_user(self, username: str, user_id: int, groups: Set[str] = None) -> User:
        """
        Create a new user in the system.
        
        Args:
            username: Unique username for the new user
            user_id: Unique user ID number
            groups: Set of groups the user should belong to (defaults to ['users'])
            
        Returns:
            The newly created User object
            
        Raises:
            ValueError: If username or user_id is already taken
        """
        # Check for duplicate username
        if username in self.users:
            raise ValueError(f"Username '{username}' already exists")
        
        # Check for duplicate user ID
        if any(user.user_id == user_id for user in self.users.values()):
            raise ValueError(f"User ID {user_id} already exists")
        
        # If no groups specified, add to 'users' group
        if groups is None:
            groups = {'users'}
        
        # Create new user
        user = User(username, user_id, groups)
        self.users[username] = user
        
        # Add user to their groups
        for group in user.groups:
            if group not in self.groups:
                self.groups[group] = set()
            self.groups[group].add(username)
        
        return user
    
    def remove_user(self, username: str) -> bool:
        """
        Remove a user from the system.
        
        The root user cannot be removed. When a user is removed,
        they are also removed from all their groups.
        
        Args:
            username: The username of the user to remove
            
        Returns:
            True if user was removed, False if user didn't exist or was root
        """
        if username == 'root' or username not in self.users:
            return False
        
        user = self.users[username]
        
        # Remove user from all their groups
        for group in user.groups:
            if group in self.groups and username in self.groups[group]:
                self.groups[group].remove(username)
        
        # Remove user from users dictionary
        del self.users[username]
        return True
    
    def switch_user(self, username: str) -> bool:
        """
        Change the current user.
        
        Args:
            username: The username to switch to
            
        Returns:
            True if successful, False if user doesn't exist
        """
        if username not in self.users:
            return False
        
        # Only root can switch to any user
        # Other users can't switch to different users
        if (self.current_user.username != 'root' and 
            self.current_user.username != username):
            return False
        
        self.current_user = self.users[username]
        return True
    
    def get_current_user(self) -> User:
        """
        Get the currently active user.
        
        Returns:
            The current User object
        """
        return self.current_user
    
    def get_user(self, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            username: The username to look up
            
        Returns:
            The User object if found, None otherwise
        """
        return self.users.get(username) 