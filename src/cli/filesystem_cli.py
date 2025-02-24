# src/cli/filesystem_cli.py

import cmd
from typing import Optional, List
from ..core.directory import Directory
from ..core.filesystem import FileSystem
from ..permissions.user_manager import UserManager
from ..core.file import File

class FilesystemCLI(cmd.Cmd):
    """
    Command-line interface for the virtual filesystem.
    Provides Unix-like commands for file operations.
    """
    
    def __init__(self):
        """
        Initialize the CLI with a new filesystem and user manager.
        Set up the prompt and introduction message.
        """
        super().__init__()
        self.user_manager = UserManager()
        self.fs = FileSystem(self.user_manager)
        self.intro = 'Welcome to Virtual Filesystem. Type help or ? to list commands.'
        self.update_prompt()
    
    def update_prompt(self):
        """Update the prompt to show current user and directory."""
        username = self.user_manager.get_current_user().username
        path = self.fs.get_current_path()
        self.prompt = f'{username}:{path}$ '
    
    def do_pwd(self, arg):
        'Print current working directory'
        print(self.fs.get_current_path())

    def do_ls(self, arg):
        'List directory contents: ls [directory_name]'
        path = arg if arg else '.'
        contents = self.fs.list_directory(path)
        
        if contents is None:
            print(f"Error: Could not list directory '{path}'")
            return
            
        if not contents:
            return  # Empty directory
        
        # Format and display the listing
        for name, node in sorted(contents.items()):
            node_type = 'DIR' if isinstance(node, Directory) else 'FILE'
            print(f"{node_type:<6} {name}")

    def do_cd(self, arg):
        'Change directory: cd [directory_name]'
        if not arg:  # No argument means go to root
            arg = '/'
            
        if not self.fs.change_directory(arg):
            print(f"Error: Cannot change to directory '{arg}'")
        else:
            self.update_prompt()

    def do_mkdir(self, arg):
        'Create a new directory: mkdir directory_name'
        if not arg:
            print("Error: Missing directory name")
            return
            
        result = self.fs.create_directory(arg)
        if result is None:
            # Get the last log entry to see what went wrong
            last_log = self.fs.logger.logs[-1] if self.fs.logger.logs else "No log available"
            print(f"Error: Could not create directory '{arg}'")
            print(f"Debug info: {last_log}")

    def do_touch(self, arg):
        'Create an empty file: touch filename'
        if not arg:
            print("Error: Missing filename")
            return
            
        if self.fs.create_file(arg) is None:
            print(f"Error: Could not create file '{arg}'")

    def do_cat(self, arg):
        'Display file contents: cat filename'
        if not arg:
            print("Error: Missing filename")
            return
            
        content = self.fs.read_file(arg)
        if content is None:
            print(f"Error: Could not read file '{arg}'")
        else:
            print(content)

    def do_write(self, arg):
        'Write content to a file: write filename "content"'
        args = arg.split(maxsplit=1)
        if len(args) < 1:
            print("Error: Missing filename")
            return
            
        filename = args[0]
        content = args[1] if len(args) > 1 else ''
        
        # Remove quotes if present
        if content and content.startswith('"') and content.endswith('"'):
            content = content[1:-1]
            
        if not self.fs.write_file(filename, content):
            print(f"Error: Could not write to file '{filename}'")

    def do_exit(self, arg):
        'Exit the filesystem'
        print("Goodbye!")
        return True

    
    def do_logs(self, arg):
        'Show recent filesystem operations'
        for log_entry in self.fs.logger.get_logs():
            print(log_entry)

    def do_rm(self, arg):
        'Remove a file or directory: rm path'
        if not arg:
            print("Error: Missing path")
            return
        
        if self.fs.delete(arg):
            print(f"Deleted '{arg}'")
        else:
            print(f"Error: Could not delete '{arg}'")

    def do_find(self, arg):
        'Find files by name: find pattern'
        if not arg:
            print("Error: Missing search pattern")
            return
        
        results = self.fs.search_by_name(arg)
        if not results:
            print("No matches found")
        else:
            print("Found matches:")
            for path in results:
                print(path)

    def do_grep(self, arg):
        'Search for text in files: grep text'
        if not arg:
            print("Error: Missing search text")
            return
        
        results = self.fs.search_by_content(arg)
        if not results:
            print("No matches found")
        else:
            print("Found in files:")
            for path in results:
                print(path)

    def do_ln(self, arg):
        'Create symbolic link: ln -s target_path link_path'
        args = arg.split()
        
        if len(args) < 3 or args[0] != '-s':
            print("Usage: ln -s target_path link_path")
            return
        
        target_path = args[1]
        link_path = args[2]
        
        if self.fs.create_symlink(link_path, target_path) is None:
            print(f"Error: Could not create symbolic link '{link_path}' -> '{target_path}'")
        else:
            print(f"Created symbolic link '{link_path}' -> '{target_path}'")

    def do_su(self, arg):
        'Switch user: su username'
        if not arg:
            print("Error: Missing username")
            return
            
        if self.fs.user_manager.switch_user(arg):
            print(f"Switched to user '{arg}'")
            self.update_prompt()
        else:
            print(f"Error: User '{arg}' not found")

    def do_whoami(self, arg):
        'Display current user name'
        current_user = self.fs.user_manager.get_current_user()
        print(f"{current_user.username}")

    def do_useradd(self, arg):
        'Add a new user: useradd username'
        if not arg:
            print("Error: Missing username")
            return
        
        current_user = self.fs.user_manager.get_current_user()
        if 'root' not in current_user.groups:
            print("Error: Only root can add users")
            return
        
        try:
            # Find next available user ID
            next_id = max([u.user_id for u in self.fs.user_manager.users.values()]) + 1
            user = self.fs.user_manager.add_user(arg, next_id)
            print(f"User '{arg}' added successfully")
        except ValueError as e:
            print(f"Error: {str(e)}")