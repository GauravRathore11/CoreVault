# Usage

## CLI
Build the CLI executable:
```bash
make
```
./corevault <command> [arguments]

Project Features

Commands:

    Set password: setpass <password>
    Login: login <password>
    Create a file: create <filename>
    Open a file: open <filename>
    Delete a file: delete <filename>
    Show metadata: metadata <filename>
    List directory: list [path]
    Copy a file: copy <source> <destination>
    Move a file: move <source> <destination>
    Rename a file: rename <oldname> <newname>
    Rename a directory: renamedir <oldname> <newname>
    Create a directory: createdir <dirname>
    Delete a directory: deletedir <dirname> (prompts for non-empty)
    Search for files/directories: search <path> <name>
    Change directory: cd <dirname>
    Encrypt a file: encrypt <filename> <key>
    Decrypt a file: decrypt <filename> <key>
    Exit: exit
    Show help: help