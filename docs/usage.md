# Usage

## CLI
Build the CLI executable:
```bash
make
```
Run the CLI:
```bash
./cv
```
Enter commands at the prompt (`>`):
- Set password: `setpass <password>`
- Login: `login <password>`
- Create a file: `create <filename>`
- Open a file: `open <filename>`
- Delete a file: `delete <filename>`
- Show metadata: `metadata <filename>`
- List directory: `list [path]`
- Copy a file: `copy <source> <destination>`
- Move a file: `move <source> <destination>`
- Rename a file: `rename <oldname> <newname>`
- Rename a directory: `renamedir <oldname> <newname>`
- Create a directory: `createdir <dirname>`
- Delete a directory: `deletedir <dirname>` (prompts for non-empty)
- Search for files/directories: `search <path> <name>`
- Change directory: `cd <dirname>`
- Encrypt a file: `encrypt <filename> <key>`
- Decrypt a file: `decrypt <filename> <key>`
- Exit: `exit`
- Show help: `help`

## GUI
Build the shared library:
```bash
make
```
Run the GUI:
```bash
python3 src/gui.py
```
- **Login**: Enter a password and click "Set Password" or "Login".
- **System Monitor**: View CPU and memory usage at the top.
- **File Tree**: Double-click directories to navigate, right-click for delete/rename/metadata.
- **Command Input**: Enter CLI commands and press Enter or click "Execute."
- **Output**: View results in the text area.