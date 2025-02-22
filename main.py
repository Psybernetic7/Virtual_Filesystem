from src.cli.filesystem_cli import FilesystemCLI

if __name__ == '__main__':
    try:
        cli = FilesystemCLI()
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\nShutting down...")