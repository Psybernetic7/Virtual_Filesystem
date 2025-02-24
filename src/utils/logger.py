# src/utils/logger.py

from datetime import datetime
from typing import Optional

class FileSystemLogger:
    """
    Logger for filesystem operations.
    Records all filesystem actions with timestamps and details.
    """
    
    def __init__(self):
        """
        Initialize the logger.
        Stores logs in memory for now.
        """
        self.logs = []
    
    def log_operation(self, operation: str, path: str, user: str, 
                     success: bool, details: Optional[str] = None):
        """
        Log a filesystem operation.
        
        Args:
            operation: Type of operation (create, read, write, delete, etc.)
            path: Path where operation was performed
            user: Username who performed the operation
            success: Whether operation succeeded
            details: Additional details about the operation
        """
        timestamp = datetime.now()
        status = "SUCCESS" if success else "FAILED"
        log_entry = f"[{timestamp}] {user} {operation} {path} - {status}"
        if details:
            log_entry += f" ({details})"
            
        self.logs.append(log_entry)
        # Also print to console for visibility
        print(log_entry)
    
    def get_logs(self) -> list[str]:
        """Get all logged operations."""
        return self.logs