# Development

## Features
- **Authentication**: Password-based login with `setpass` and `login`.
- **Create File**: Creates empty files with `open`.
- **Open File**: Opens files in default application using `xdg-open`.
- **Delete File**: Removes files with `unlink`.
- **Metadata**: Shows file size, permissions, and timestamps.
- **List Directory**: Lists files/directories with `readdir`.
- **Copy/Move File**: Copies files with `fread`/`fwrite`, moves with `rename`.
- **Rename File/Directory**: Uses `rename` system call.
- **Create/Delete Directory**: Uses `mkdir` and `nftw` for recursive deletion.
- **Search**: Searches files/directories by name.
- **Change Directory**: Uses `chdir`.
- **Encryption/Decryption**: Uses XOR-based encryption (demo).

## CLI
- `main.c`: CLI interface with authentication.
- `file_ops.c`: File operations.
- `dir_ops.c`: Directory operations.
- `auth.c`: Authentication functions.
- `Makefile`: Builds CLI executable `corevault`.