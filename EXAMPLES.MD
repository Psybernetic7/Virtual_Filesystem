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