#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "corevault.h"

int authenticated = 0;

void print_usage() {
    printf("Commands:\n");
    printf("  setpass <password>           Set a password\n");
    printf("  login <password>             Login with password\n");
    printf("  create <filename>            Create a file\n");
    printf("  open <filename>              Open a file\n");
    printf("  delete <filename>            Delete a file\n");
    printf("  metadata <filename>          Show file metadata\n");
    printf("  list [path]                  List directory contents\n");
    printf("  copy <source> <dest>         Copy a file\n");
    printf("  move <source> <dest>         Move a file\n");
    printf("  rename <oldname> <newname>   Rename a file\n");
    printf("  renamedir <oldname> <newname> Rename a directory\n");
    printf("  createdir <dirname>          Create a directory\n");
    printf("  deletedir <dirname>          Delete a directory\n");
    printf("  search <path> <name>         Search for files/directories\n");
    printf("  cd <dirname>                 Change directory\n");
    printf("  encrypt <filename> <key>     Encrypt a file\n");
    printf("  decrypt <filename> <key>     Decrypt a file\n");
    printf("  exit                         Exit\n");
    printf("  help                         Show this help\n");
}

void parse_command(char *input) {
    char *tokens[5] = {NULL}; // Max 4 args + command
    int token_count = 0;
    char *token = strtok(input, " \n");
    while (token && token_count < 5) {
        tokens[token_count++] = token;
        token = strtok(NULL, " \n");
    }

    if (token_count == 0) {
        return;
    }

    char *command = tokens[0];
    if (command == NULL) {
        printf("Error: No command provided\n");
        return;
    }

    // Allow setpass, login, and help without authentication
    if (strcmp(command, "setpass") == 0 && token_count == 2) {
        if (tokens[1] == NULL) {
            printf("Error: Usage: setpass <password>\n");
            return;
        }
        set_password(tokens[1]);
        return;
    } else if (strcmp(command, "login") == 0 && token_count == 2) {
        if (tokens[1] == NULL) {
            printf("Error: Usage: login <password>\n");
            return;
        }
        authenticated = login(tokens[1]);
        return;
    } else if (strcmp(command, "help") == 0 && token_count == 1) {
        print_usage();
        return;
    }

    // All other commands require authentication
    if (!authenticated) {
        printf("Please login first. Use 'login <password>' or set a password with 'setpass <password>'.\n");
        return;
    }

    // Authenticated commands
    if (strcmp(command, "create") == 0 && token_count == 2) {
        if (tokens[1] == NULL) {
            printf("Error: No filename provided\n");
            return;
        }
        create_file(tokens[1]);
    } else if (strcmp(command, "open") == 0 && token_count == 2) {
        if (tokens[1] == NULL) {
            printf("Error: No filename provided\n");
            return;
        }
        open_file(tokens[1]);
    } else if (strcmp(command, "delete") == 0 && token_count == 2) {
        if (tokens[1] == NULL) {
            printf("Error: No filename provided\n");
            return;
        }
        delete_file(tokens[1]);
    } else if (strcmp(command, "metadata") == 0 && token_count == 2) {
        if (tokens[1] == NULL) {
            printf("Error: No filename provided\n");
            return;
        }
        metadata(tokens[1]);
    } else if (strcmp(command, "list") == 0 && (token_count == 1 || token_count == 2)) {
        const char *path = (token_count == 2 && tokens[1] != NULL) ? tokens[1] : ".";
        list_directory(path);
    } else if (strcmp(command, "copy") == 0 && token_count == 3) {
        if (tokens[1] == NULL || tokens[2] == NULL) {
            printf("Error: Source or destination missing\n");
            return;
        }
        copy_file(tokens[1], tokens[2]);
    } else if (strcmp(command, "move") == 0 && token_count == 3) {
        if (tokens[1] == NULL || tokens[2] == NULL) {
            printf("Error: Source or destination missing\n");
            return;
        }
        move_file(tokens[1], tokens[2]);
    } else if (strcmp(command, "rename") == 0 && token_count == 3) {
        if (tokens[1] == NULL || tokens[2] == NULL) {
            printf("Error: Oldname or newname missing\n");
            return;
        }
        rename_file(tokens[1], tokens[2]);
    } else if (strcmp(command, "renamedir") == 0 && token_count == 3) {
        if (tokens[1] == NULL || tokens[2] == NULL) {
            printf("Error: Oldname or newname missing\n");
            return;
        }
        rename_directory(tokens[1], tokens[2]);
    } else if (strcmp(command, "createdir") == 0 && token_count == 2) {
        if (tokens[1] == NULL) {
            printf("Error: No dirname provided\n");
            return;
        }
        createdir(tokens[1]);
    } else if (strcmp(command, "deletedir") == 0 && token_count == 2) {
        if (tokens[1] == NULL) {
            printf("Error: No dirname provided\n");
            return;
        }
        int result = deletedir(tokens[1]);
        if (result == 1) {
            printf("Directory %s is not empty. Delete all contents? (y/n): ", tokens[1]);
            char response;
            scanf(" %c", &response);
            if (response == 'y' || response == 'Y') {
                deletedir_force(tokens[1]);
            } else {
                printf("Deletion aborted.\n");
            }
        }
    } else if (strcmp(command, "search") == 0 && token_count == 3) {
        if (tokens[1] == NULL || tokens[2] == NULL) {
            printf("Error: Path or name missing\n");
            return;
        }
        search(tokens[1], tokens[2]);
    } else if (strcmp(command, "cd") == 0 && token_count == 2) {
        if (tokens[1] == NULL) {
            printf("Error: No dirname provided\n");
            return;
        }
        change_directory(tokens[1]);
    } else if (strcmp(command, "encrypt") == 0 && token_count == 3) {
        if (tokens[1] == NULL || tokens[2] == NULL) {
            printf("Error: Filename or key missing\n");
            return;
        }
        encrypt_file(tokens[1], tokens[2]);
    } else if (strcmp(command, "decrypt") == 0 && token_count == 3) {
        if (tokens[1] == NULL || tokens[2] == NULL) {
            printf("Error: Filename or key missing\n");
            return;
        }
        decrypt_file(tokens[1], tokens[2]);
    } else if (strcmp(command, "exit") == 0 && token_count == 1) {
        printf("Exiting CoreVault.\n");
        authenticated=0;
        exit(0);
    } else {
        printf("Unknown command or wrong arguments.\n");
        print_usage();
    }
}

int main() {
    printf("Welcome to CoreVault. Type 'help' for commands.\n");
    char input[256];
    while (1) {
        printf("> ");
        if (fgets(input, sizeof(input), stdin) == NULL) {
            printf("Error reading input\n");
            continue;
        }
        input[strcspn(input, "\n")] = 0; // Remove newline
        if (strlen(input) == 0) {
            continue;
        }
        parse_command(input);
    }
    return 0;
}