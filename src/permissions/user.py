# src/permissions/user.py

from typing import Set

class User:
    """
    Represents a user in the virtual filesystem.
    
    A user is an entity that can own and access files and directories.
    Each user has:
    - A unique username
    - A unique user ID (UID)
    - Membership in one or more groups
    
    Users are similar to users in Unix-like systems, where each user can belong
    to multiple groups and this affects what files they can access.
    
    Attributes:
        username (str): Unique name identifying the user
        user_id (int): Unique numeric identifier for the user
        groups (Set[str]): Set of group names the user belongs to
    """
    
    def __init__(self, username: str, user_id: int, groups: Set[str] = None):
        """
        Initialize a new user.
        
        Args:
            username: The user's unique username
            user_id: Unique numeric identifier for the user
            groups: Set of group names the user belongs to. If None, defaults to
                   just the 'users' group.
                   
        Raises:
            ValueError: If username is empty or contains invalid characters
        """
        if not username or '/' in username or '\0' in username:
            raise ValueError("Username cannot be empty or contain '/' or null characters")
            
        self.username = username
        self.user_id = user_id
        # If no groups specified, add user to 'users' group by default
        self.groups = groups if groups is not None else {'users'}
    
    def is_in_group(self, group: str) -> bool:
        """
        Check if the user is a member of the specified group.
        
        Args:
            group: Name of the group to check membership in
            
        Returns:
            True if user is a member of the group, False otherwise
        """
        return group in self.groups
    
    def add_group(self, group: str) -> None:
        """
        Add the user to a new group.
        
        Args:
            group: Name of the group to add the user to
        """
        self.groups.add(group)
    
    def remove_group(self, group: str) -> bool:
        """
        Remove the user from a group.
        
        Users cannot be removed from their last group to ensure they
        always belong to at least one group.
        
        Args:
            group: Name of the group to remove the user from
            
        Returns:
            True if user was removed from the group, False if they
            weren't in the group or it was their last group
        """
        if len(self.groups) <= 1:
            return False  # Can't remove user from their last group
        
        if group in self.groups:
            self.groups.remove(group)
            return True
            
        return False
    
    def __str__(self) -> str:
        """
        Get a string representation of the user.
        
        Returns:
            A string in the format "username (uid: <id>, groups: <group1,group2,...>)"
        """
        groups_str = ','.join(sorted(self.groups))  # Sort groups for consistent output
        return f"{self.username} (uid: {self.user_id}, groups: {groups_str})"
    
    def __eq__(self, other: object) -> bool:
        """
        Check if two users are equal.
        
        Two users are considered equal if they have the same username and user_id.
        Group membership is not considered for equality.
        
        Args:
            other: Another user object to compare with
            
        Returns:
            True if the users are equal, False otherwise
        """
        if not isinstance(other, User):
            return False
        return self.username == other.username and self.user_id == other.user_id