Folder structure for the project : 

CoreVault/
├── src/                  # Source code
│   ├── main.c            # Entry point (CLI parsing)
│   ├── file_ops.c        # File operation implementations
│   └── dir_ops.c         # Directory operation implementations
├── include/              # Header files
│   └── corevault.h       # Function prototypes and structs
├── docs/                 # Documentation
│   ├── usage.md          # How to use CoreVault
│   ├── development.md    # Design and implementation details
│   └── testing.md        # Test cases
├── tests/                # Test scripts or programs
├── Makefile              # Build automation
├── README.md             # Project overview
└── .gitignore            # Ignore build artifacts

# Development Notes
## Structure
- `src/main.c`: CLI and entry point.
- `src/file_ops.c`: File operations (create, read, delete).
- `src/dir_ops.c`: Directory operations (list).
- `include/corevault.h`: Function prototypes.

## Design
- Uses POSIX system calls for low-level operations.
- Modular design with separate files for different functionalities.