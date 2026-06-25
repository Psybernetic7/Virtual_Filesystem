# src/cli/filesystem_cli.py

import cmd
import os
import subprocess
import sys
import termios
from typing import Optional, List
from ..core.directory import Directory
from ..core.filesystem import FileSystem
from ..permissions.user_manager import UserManager
from ..core.file import File
from ..container.container import Container
from ..container.rootfs import RootfsManager

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

    def do_save(self, arg):
        'Save encrypted filesystem state: save filename'
        if not arg:
            print("Error: Missing filename")
            return
        
        if self.fs.save_state(arg):
            print(f"Filesystem state encrypted and saved")
        else:
            print(f"Error: Could not save state")

    def do_load(self, arg):
        'Load encrypted filesystem state: load filename'
        if not arg:
            print("Error: Missing filename")
            return
        
        if self.fs.load_state(arg):
            print(f"Filesystem state loaded and decrypted")
            self.update_prompt()
        else:
            print(f"Error: Could not load state")

    def do_contain(self, arg):
        'Container operations: contain run <rootfs> <cmd> | contain export <dest> | contain info'
        args = arg.split()
        if not args:
            print("Usage:")
            print("  contain run <rootfs_path> <command> [args...]")
            print("  contain export <real_path>")
            print("  contain info")
            return

        subcmd = args[0]

        if subcmd == 'run':
            if len(args) < 3:
                print("Usage: contain run <rootfs_path> <command> [args...]")
                return
            rootfs_path = args[1]
            command = args[2:]

            try:
                saved_term = termios.tcgetattr(sys.stdin.fileno())
            except (termios.error, OSError):
                saved_term = None

            container = Container(rootfs_path=rootfs_path, command=command)
            try:
                exit_code = container.run()
            except Exception as e:
                exit_code = 1
                print(f"Container error: {e}")
            finally:
                subprocess.run(['stty', 'sane'], stdin=sys.stdin, stderr=subprocess.DEVNULL)
                if saved_term is not None:
                    try:
                        termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, saved_term)
                    except (termios.error, OSError):
                        pass
                try:
                    os.tcsetpgrp(sys.stdin.fileno(), os.getpgrp())
                except OSError:
                    pass
                sys.stdout.flush()
                sys.stderr.flush()

            print(f"Container exited with code {exit_code}", flush=True)
            self.update_prompt()

        elif subcmd == 'export':
            if len(args) < 2:
                print("Usage: contain export <real_path>")
                return
            target_dir = args[1]
            RootfsManager.export_vfs_to_rootfs(self.fs, target_dir)
            print(f"Virtual filesystem exported to '{target_dir}'")

        elif subcmd == 'info':
            print("Container capabilities:")
            print(f"  Root: {'yes' if os.geteuid() == 0 else 'no (container run requires root)'}")
            print(f"  os.unshare: {'available' if hasattr(os, 'unshare') else 'unavailable'}")
            namespaces = ['uts', 'pid', 'mount', 'net', 'user', 'ipc', 'cgroup']
            for ns in namespaces:
                flag = f'CLONE_NEW{ns.upper()}' if ns != 'mount' else 'CLONE_NEWNS'
                available = hasattr(os, flag)
                print(f"  {ns:>8} namespace: {'available' if available else 'unavailable'}")
            try:
                with open('/proc/sys/kernel/cap_last_cap') as f:
                    print(f"  Capabilities: {int(f.read().strip()) + 1} supported")
            except OSError:
                print("  Capabilities: unknown")
            cgroup_v2 = os.path.exists('/sys/fs/cgroup/cgroup.controllers')
            print(f"  cgroup v2: {'available' if cgroup_v2 else 'unavailable'}")

        else:
            print(f"Unknown subcommand: {subcmd}")
            print("Valid subcommands: run, export, info")