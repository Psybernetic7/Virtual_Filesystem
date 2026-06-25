# Virtual Filesystem Usage Examples

## Basic File Operations Example
```bash
# Create and navigate directories
mkdir documents
cd documents
pwd                     # Output: /documents

# Create and write to files
write hello.txt "Hello, World!"
write notes.txt "Important notes"
ls                      # Shows: hello.txt, notes.txt
cat hello.txt          # Output: Hello, World!

# Delete files
rm notes.txt
ls                      # Shows: hello.txt
```

## User Management Example
```bash
# Initially logged in as root
whoami                  # Output: root

# Create new user
useradd alice
su alice                # Switch to alice
whoami                  # Output: alice

# Try to create file as alice
write secret.txt "Alice's secret"
cat secret.txt         # Output: Alice's secret

# Switch back to root
su root
```

## Symbolic Links Example
```bash
# Create a directory structure
mkdir /home
cd /home
write original.txt "Original content"
ln -s original.txt link_to_original
cat link_to_original   # Output: Original content
```

## Search Functionality Example
```bash
# Create some files to search
write doc1.txt "Hello world"
write doc2.txt "Another document"
write note.txt "Hello there"

# Search by name
find *.txt             # Shows all .txt files

# Search by content
grep "Hello"           # Shows doc1.txt and note.txt
```

## State Persistence Example
```bash
# Create some data
mkdir /data
cd /data
write important.txt "Critical information"

# Save the state
save backup1

# Make changes
rm important.txt

# Restore the state
load backup1           # important.txt is restored
```

## Container Operations Example

### Check System Capabilities
```bash
# See what container features your system supports
contain info
# Output:
#   Container capabilities:
#     Root: no (container run requires root)
#     os.unshare: available
#       uts namespace: available
#       pid namespace: available
#     mount namespace: available
#       net namespace: available
#      user namespace: available
#       ipc namespace: available
#    cgroup namespace: available
#     Capabilities: 41 supported
#     cgroup v2: available
```

### Export VFS to Disk
```bash
# Build a filesystem in memory
mkdir /myroot
cd /myroot
mkdir bin
mkdir lib
mkdir usr
mkdir etc
write etc/hostname "my-container"
write etc/greeting "Welcome to the container!"

# Export it to a real directory on disk
contain export /tmp/my_rootfs

# The in-memory tree is now materialized at /tmp/my_rootfs
# with real directories and files matching what you built
```

### Run a Contained Process
```bash
# Requires root (run the VFS CLI with sudo)
# Launch /bin/sh inside a container with full isolation:
#   - UTS, PID, mount, net, IPC namespaces
#   - pivot_root into the rootfs
#   - /proc, /dev, /sys mounted
#   - Capabilities dropped
#   - Resource limits applied (256MB memory, 64 PIDs)
contain run /path/to/rootfs /bin/sh

# Inside the container:
#   hostname         -> "container"
#   cat /proc/1/status -> shows the shell as PID 1
#   ls /dev          -> null, zero, random, urandom, tty
# Container exited with code 0
```