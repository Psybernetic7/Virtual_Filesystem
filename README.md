# Virtual Filesystem Documentation

## Overview
This project implements an in-memory virtual filesystem that provides Unix-like file operations and directory management. The filesystem supports basic file operations, directory navigation, user permissions, symbolic links, and file search capabilities, all while maintaining data exclusively in memory.

## Build and Installation

### Prerequisites
- Python 3.8 or higher
- cryptography package for state encryption
- cmd2 package for enhanced CLI

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
cd ..                 # Move up one directory
cd /path/to/dir       # Absolute path navigation
ls                    # List contents
pwd                   # Show current path
```

### Search Operations:
```bash
find *.txt          # Search by filename (supports wildcards)
grep "text"          # Search by file contents
```

### Symbolic Links:
```bash
ln -s /path/to/target link_name     # Create symbolic link
```

### User Management:
```bash
whoami               # Show current user
useradd username     # Create new user (root only)
su username          # Switch user
```

### State Persistence
```bash
save filename        # Save encrypted filesystem state
load filename        # Load encrypted filesystem state
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

### State Persistence:
- Chose local encryption over remote storage
- Pro: Self-contained, secure. Con: Limited to local machine. Trade-off: Simplicity vs distributed capabilities

## Implementation Notes

### Path Resolution Process

- Split path into components
- Handle absolute vs relative paths
- Process special directories (., ..)
- Follow symbolic links when encountered
- Validate permissions at each step

### Symbolic Link Handling

- Links store target paths, not references
- Followed automatically during path resolution
- Can point to non-existent targets
- Circular references prevented

### Permission Checking

- Checked at each operation
- Root user bypasses permission checks
- Group permissions inherited from Unix model
- Owner/group/others access levels

## Known Limitations & Areas for Improvement

### Current Limitations:
- **No concurrent access support**: Single-user access at a time
- **User Management**: Basic user commands only (useradd, su, whoami)
- **Limited file types**: Currently only supports text-based files
- **Basic permission model** compared to real Unix systems

### Potential Improvements:
- Add support for binary files
- Enhanced User Management
- State Persistence by remote storage option
- Add more sophisticated permission management
- Implement proper concurrent access
- Add command history and tab completion in CLI
- Implement file type detection

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

