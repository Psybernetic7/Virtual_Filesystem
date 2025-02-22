# src/permissions/permission.py

from enum import Flag, auto

class Permission(Flag):
    """
    Represents file system permissions using a flag enumeration.
    
    This class uses Python's Flag enum to represent Unix-like permissions where
    multiple permissions can be combined using bitwise operations. Each permission
    is a power of 2, allowing them to be combined without overlapping:
    
    READ    = 1  (001 in binary)
    WRITE   = 2  (010 in binary)
    EXECUTE = 4  (100 in binary)
    
    For example, if a file has READ and WRITE permissions:
    001 | 010 = 011 (binary) = 3 (decimal)
    
    This binary approach allows us to efficiently store and check permissions,
    similar to how real Unix-like systems handle file permissions.
    """
    
    # Define our basic permission flags
    NONE = 0        # No permissions (000)
    READ = auto()   # Read permission (001)
    WRITE = auto()  # Write permission (010)
    EXECUTE = auto()# Execute permission (100)
    
    @classmethod
    def from_string(cls, perm_str: str) -> 'Permission':
        """
        Convert a string representation of permissions to Permission flags.
        
        This method accepts a string using the familiar 'rwx' format:
        - 'r' indicates read permission
        - 'w' indicates write permission
        - 'x' indicates execute permission
        - '-' indicates no permission
        
        For example:
        - "rw-" means READ and WRITE permissions
        - "r-x" means READ and EXECUTE permissions
        - "---" means no permissions
        
        Args:
            perm_str: A string containing 'r', 'w', 'x', or '-' characters
        
        Returns:
            A Permission object with the corresponding flags set
        
        Example:
            >>> Permission.from_string("rw-")
            <Permission.READ|WRITE: 3>
        """
        result = Permission.NONE
        
        if 'r' in perm_str:
            result |= Permission.READ
        if 'w' in perm_str:
            result |= Permission.WRITE
        if 'x' in perm_str:
            result |= Permission.EXECUTE
            
        return result
    
    def __str__(self) -> str:
        """
        Convert permissions to a human-readable string format.
        
        This method creates a string using the familiar 'rwx' format where:
        - 'r' indicates read permission is present
        - 'w' indicates write permission is present
        - 'x' indicates execute permission is present
        - '-' indicates a permission is not present
        
        Returns:
            A three-character string representing the permissions
        
        Example:
            >>> str(Permission.READ | Permission.WRITE)
            'rw-'
        """
        return (
            ('r' if self & Permission.READ else '-') +
            ('w' if self & Permission.WRITE else '-') +
            ('x' if self & Permission.EXECUTE else '-')
        )