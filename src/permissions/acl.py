# src/permissions/acl.py

from .permission import Permission
from .user import User

class ACL:
    """
    Access Control List for filesystem nodes.
    
    Implements Unix-like permissions with owner, group, and others access levels.
    Each level (owner, group, others) can have different read/write/execute
    permissions.
    
    Example:
        A file might have these permissions:
        - Owner can read and write: rw-
        - Group (developers) can read only: r--
        - Others can't do anything: ---
    """
    
    def __init__(self, owner: str, group: str):
        """
        Initialize a new ACL.
        
        Args:
            owner: Username of the owner
            group: Group name for group permissions
            
        By default:
        - Owner gets read and write permissions
        - Group gets read permission
        - Others get read permission
        """
        self.owner = owner
        self.group = group
        
        # Set default permissions
        self.owner_perms = Permission.READ | Permission.WRITE
        self.group_perms = Permission.READ
        self.other_perms = Permission.READ

    def check_permission(self, user: User, required_perm: Permission) -> bool:
        """
        Check if a user has the required permission.
        """
        # Root can do anything
        if 'root' in user.groups:
            return True
            
        # Check if user is the owner
        if user.username == self.owner:
            return bool(self.owner_perms & required_perm)
            
        # Check if user is in the group
        if user.is_in_group(self.group):
            return bool(self.group_perms & required_perm)
            
        # Otherwise, use other permissions
        return bool(self.other_perms & required_perm)
    
    def __str__(self) -> str:
        """
        Return string representation of permissions (like Unix 'ls -l').
        """
        return f"{str(self.owner_perms)}{str(self.group_perms)}{str(self.other_perms)} {self.owner}:{self.group}"