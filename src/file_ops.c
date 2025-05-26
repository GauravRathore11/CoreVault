#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#include <time.h>
#include "corevault.h"

void create_file(const char *filename) {
    int fd = open(filename, O_CREAT | O_WRONLY, 0644);
    if (fd == -1) {
        perror("Failed to create file");
        return;
    }
    close(fd);
    printf("File %s created.\n", filename);
}

void open_file(const char *filename) {
    char command[512];
    snprintf(command, sizeof(command), "xdg-open %s", filename);
    if (system(command) == -1) {
        perror("Failed to open file");
        return;
    }
    printf("File %s opened.\n", filename);
}

void delete_file(const char *filename) {
    if (unlink(filename) == -1) {
        perror("Failed to delete file");
        return;
    }
    printf("File %s deleted.\n", filename);
}

void metadata(const char *filename) {
    struct stat st;
    if (stat(filename, &st) == -1) {
        perror("Failed to get file metadata");
        return;
    }
    printf("File: %s\n", filename);
    printf("Size: %lld bytes\n", (long long)st.st_size);
    printf("Permissions: %o\n", st.st_mode & 0777);
    printf("Last modified: %s", ctime(&st.st_mtime));
}

void copy_file(const char *src, const char *dest) {
    FILE *source = fopen(src, "rb");
    if (!source) {
        perror("Failed to open source file");
        return;
    }
    FILE *destination = fopen(dest, "wb");
    if (!destination) {
        perror("Failed to open destination file");
        fclose(source);
        return;
    }
    char buffer[4096];
    size_t bytes;
    while ((bytes = fread(buffer, 1, sizeof(buffer), source)) > 0) {
        if (fwrite(buffer, 1, bytes, destination) != bytes) {
            perror("Failed to write to destination file");
            fclose(source);
            fclose(destination);
            return;
        }
    }
    fclose(source);
    fclose(destination);
    printf("File copied from %s to %s\n", src, dest);
}

void move_file(const char *src, const char *dest) {
    if (rename(src, dest) == -1) {
        perror("Failed to move file");
        return;
    }
    printf("File moved from %s to %s\n", src, dest);
}

void rename_file(const char *oldname, const char *newname) {
    if (rename(oldname, newname) == -1) {
        perror("Failed to rename file");
        return;
    }
    printf("File renamed from %s to %s\n", oldname, newname);
}

void encrypt_file(const char *filename, const char *key) {
    FILE *input = fopen(filename, "rb+");
    if (!input) {
        perror("Failed to open file for encryption");
        return;
    }
    size_t key_len = strlen(key);
    size_t key_idx = 0;
    int ch;
    fseek(input, 0, SEEK_SET);
    while ((ch = fgetc(input)) != EOF) {
        fseek(input, -1, SEEK_CUR);
        fputc(ch ^ key[key_idx % key_len], input);
        fseek(input, 0, SEEK_CUR);
        key_idx++;
    }
    fclose(input);
    printf("File %s encrypted.\n", filename);
}

void decrypt_file(const char *filename, const char *key) {
    encrypt_file(filename, key); // XOR is symmetric
    printf("File %s decrypted.\n", filename);
}