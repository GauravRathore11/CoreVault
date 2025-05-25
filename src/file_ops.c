#include<fcntl.h>
#include<unistd.h>
#include<errno.h>
#include<string.h>
#include<stdio.h>
#include<sys/stat.h>
#include "corevault.h"

void create_file(const char *file_name) {
    //fd=file descriptor, for a valid fd its valye is non negative integer
    printf("trying to create %s\n", file_name);
    int fd = open(file_name, O_CREAT | O_WRONLY | O_TRUNC, 0644);
    if(fd==-1) {
        perror("Failed to create file\n");
        return;
    }

    const char *data = "This file is created using system call";
    if(write(fd, data, strlen(data)) == -1) {
        perror("Error writing to file\n");
        return;
    }
    close(fd);
    printf("File %s has been created\n", file_name);
}

void read_file(const char *file_name) {
    int fd = open(file_name, O_RDONLY);
    if(fd==-1) {
        perror("Error opening the file");
        return;
    }
    char buffer[1000];
    ssize_t bytes_read = read(fd, buffer, sizeof(buffer)-1);
    
    if(bytes_read==-1) {
        perror("Error reading the data from file\n");
        return;
    }

    buffer[bytes_read]='\0';
    printf("File Contents : %s\n", buffer);
    close(fd);
}

void delete_file(const char *file_name) {
    if(unlink(file_name) == -1) {
        perror("Error deleting the file\n");
        return;
    }
    else {
        printf("file %s deleted\n", file_name);
    }
}

void rename_file(const char *old_name, const char *new_name) {
    if(rename(old_name, new_name) == -1) {
        perror("Error renaming the file\n");
        return;
    }
    printf("File renamed from %s to %s\n", old_name, new_name);
}

void copy_file(const char *src, const char *dest) {
    struct stat st;
    char dest_path[256];
    char clean_dest[256];

    // Remove trailing slash from dest
    strncpy(clean_dest, dest, sizeof(clean_dest));
    clean_dest[sizeof(clean_dest) - 1] = '\0';
    size_t len = strlen(clean_dest);
    if (len > 0 && clean_dest[len - 1] == '/') {
        clean_dest[len - 1] = '\0';
    }

    // Check if dest is a directory
    if (stat(clean_dest, &st) == 0 && S_ISDIR(st.st_mode)) {
        // Extract filename from src
        const char *filename = strrchr(src, '/');
        filename = (filename == NULL) ? src : filename + 1;
        // Construct destination path
        if (snprintf(dest_path, sizeof(dest_path), "%s/%s", clean_dest, filename) >= sizeof(dest_path)) {
            fprintf(stderr, "Error: Destination path too long\n");
            return;
        }
    } else {
        strncpy(dest_path, clean_dest, sizeof(dest_path));
        dest_path[sizeof(dest_path) - 1] = '\0';
    }

    int src_fd = open(src, O_RDONLY);
    if (src_fd == -1) {
        perror("Failed to open source file");
        return;
    }

    int dest_fd = open(dest_path, O_CREAT | O_WRONLY | O_TRUNC, 0644);
    if (dest_fd == -1) {
        perror("Failed to open destination file");
        close(src_fd);
        return;
    }

    char buffer[1024];
    ssize_t bytes_read;
    while ((bytes_read = read(src_fd, buffer, sizeof(buffer))) > 0) {
        if (write(dest_fd, buffer, bytes_read) != bytes_read) {
            perror("Error copying file");
            close(src_fd);
            close(dest_fd);
            return;
        }
    }

    if (bytes_read == -1) {
        perror("Error reading source file");
        close(src_fd);
        close(dest_fd);
        return;
    }

    close(src_fd);
    close(dest_fd);
    printf("File copied from %s to %s\n", src, dest_path);
}