#include<string.h>
#include<unistd.h>
#include<stdio.h>
#include "corevault.h"

int main(int argc, char *argv[]) {
    if(argc < 2) {
        printf("Usage : %s <command> [args]\n", argv[1]);
        printf("Commands : \ncreate <filename>\nread <filename>\ndelete <filename>\nlist [path]\n");
        return 1;
    }

    if(strcmp(argv[1], "create") == 0 && argc==3) create_file(argv[2]);
    else if(strcmp(argv[1], "read") == 0 && argc==3) read_file(argv[2]);
    else if(strcmp(argv[1], "delete") == 0 && argc==3) delete_file(argv[2]);
    else if(strcmp(argv[1], "list") == 0 && argc==3) {
        const char *path = (argc==3) ? argv[2] : '.';
        list_directory(path);
    }
    else if(strcmp(argv[1], "rename") == 0 && argc==3) rename_file(argv[2], argv[3]);
    else if(strcmp(argv[1], "renamedir") == 0  && argc==4) rename_directory(argv[2], argv[3]);
    else if(strcmp(argv[1], "createdir") == 0 && argc==3) create_directory(argv[2]);
    else if(strcmp(argv[1], "deletedir") == 0 && argc==3) delete_directory(argv[2]);
    else {
        printf("Unknown commandor wrong argument\n");
        return 1;
    }

    return 0;
}