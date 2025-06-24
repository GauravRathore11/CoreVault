#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include "corevault.h"

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