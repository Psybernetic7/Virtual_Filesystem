# Virtual Filesystem API Documentation

This document describes the programmatic API for the virtual filesystem.

## Core Classes

### FileSystem

Main class for filesystem operations.

```python
from src.core.filesystem import FileSystem
from src.permissions.user_manager import UserManager

# Initialize
user_manager = UserManager()
fs = FileSystem(user_manager)

# Examples of programmatic usage
fs.create_file("/home/test.txt", "Hello World")
fs.read_file("/home/test.txt")
fs.write_file("/home/test.txt", "New content")
fs.create_directory("/home/docs")
fs.list_directory("/home")