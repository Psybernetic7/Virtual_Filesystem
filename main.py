import sys

if len(sys.argv) > 1 and sys.argv[1] == '--container-child':
    from src.container.container import container_child_entry
    container_child_entry()
else:
    from src.cli.filesystem_cli import FilesystemCLI
    try:
        cli = FilesystemCLI()
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\nShutting down...")
