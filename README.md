# Virtual Filesystem Documentation

## Overview
This project implements an in-memory virtual filesystem that provides Unix-like file operations and directory management. The filesystem supports basic file operations, directory navigation, user permissions, symbolic links, and file search capabilities, all while maintaining data exclusively in memory.

## Build and Installation

### Prerequisites
- Python 3.8 or higher

### Installation

Clone the repository:

```bash
git clone https://github.com/Psybernetic7/Virtual_Filesystem.git
cd Virtual_Filesystem
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the filesystem:

```bash
python main.py
```

## Usage
The filesystem provides a Unix-like command-line interface with familiar commands:

### File Operations:
```bash
touch file.txt          # Create empty file
write file.txt "text"   # Create/write to file
cat file.txt           # Display file contents
rm file.txt           # Delete file
```

### Directory Operations:
```bash
mkdir dirname          # Create directory
cd dirname            # Change directory
ls                    # List contents
pwd                   # Show current path
```

### Search Operations:
```bash
find *.txt          # Search by filename
grep "text"          # Search by file contents
```

### Symbolic Links:
```bash
ln -s path_to_target target_link     # Create symbolic link
```

### User Management:
```bash
whoami               # Show current user
su username          # Switch user
```

## API Design Decisions
The API design follows several key principles:

- **Separation of Concerns**: The system is divided into distinct components:
  - `FileSystemNode` as the base class for filesystem entities
  - Separate `File` and `Directory` classes for specific behaviors
  - `UserManager` for handling permissions and access control
  - `FileSystem` class as the main interface for operations

- **Consistent Error Handling**: Methods return `Optional` types or boolean values to indicate success/failure rather than raising exceptions, making error handling more predictable.

- **Path Resolution**: The system handles both absolute and relative paths uniformly through a single path resolution mechanism in `get_node_by_path()`.

- **Permission Management**: User permissions are checked at every operation level, ensuring security is maintained consistently throughout the system.

## Data Structure Choices

### Directory Structure:
- Hierarchical tree structure where directories contain references to their children
- Dictionary-based storage for O(1) child lookup
- Parent references for efficient upward traversal

### File Storage:
- Content stored as strings in memory
- Metadata (creation time, modification time, access time) stored with each node
- Permissions handled separately through the ACL system

### Path Management:
- Paths split into components for traversal
- Special handling for `.` and `..` references
- Support for both absolute and relative paths

## Known Limitations & Areas for Improvement

### Current Limitations:
- **No concurrent access support**: Single-user access at a time
- **Limited file types**: Currently only supports text-based files
- **Basic permission model** compared to real Unix systems

### Potential Improvements:
- Add support for binary files
- Add more sophisticated permission management
- Implement proper concurrent access
- Add command history and tab completion in CLI
- Implement file type detection
- Add support for file attributes and extended metadata

## Project Structure
```
virtual_filesystem/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
└── src/
    ├── core/              # Core filesystem components
    ├── permissions/       # User and permission management
    ├── cli/               # Command-line interface
    └── utils/             # Utility functions
```

