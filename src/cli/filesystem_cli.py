# src/cli/filesystem_cli.py

import cmd
from typing import Optional, List
from ..core.directory import Directory
from ..core.filesystem import FileSystem
from ..permissions.user_manager import UserManager

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
            
        if self.fs.create_directory(arg) is None:
            print(f"Error: Could not create directory '{arg}'")

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

    def do_EOF(self, arg):
        'Exit on Ctrl-D'
        print()
        return self.do_exit(arg)