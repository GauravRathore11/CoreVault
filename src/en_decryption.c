#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/aes.h>

void encrypt_file(const char *filename, const char *key) {
    FILE *file = fopen(filename, "rb+");
    if (!file) {
        perror("Failed to open file");
        return;
    }

    unsigned char aes_key[16];  // AES-128
    memset(aes_key, 0, 16);
    strncpy((char*)aes_key, key, 16);

    AES_KEY encryptKey;
    AES_set_encrypt_key(aes_key, 128, &encryptKey);

    unsigned char buffer[16];
    size_t bytes_read;

    fseek(file, 0, SEEK_SET);
    while ((bytes_read = fread(buffer, 1, 16, file)) > 0) {
        // Pad if needed
        if (bytes_read < 16) {
            memset(buffer + bytes_read, 16 - bytes_read, 16 - bytes_read);  // PKCS padding
        }

        unsigned char encrypted[16];
        AES_encrypt(buffer, encrypted, &encryptKey);

        fseek(file, -bytes_read, SEEK_CUR);
        fwrite(encrypted, 1, 16, file);
    }

    fclose(file);
    printf("File %s encrypted with AES.\n", filename);
}

void decrypt_file(const char *filename, const char *key) {
    FILE *file = fopen(filename, "rb+");
    if (!file) {
        perror("Failed to open file");
        return;
    }

    unsigned char aes_key[16];
    memset(aes_key, 0, 16);
    strncpy((char*)aes_key, key, 16);

    AES_KEY decryptKey;
    AES_set_decrypt_key(aes_key, 128, &decryptKey);

    unsigned char buffer[16];
    size_t bytes_read;

    fseek(file, 0, SEEK_SET);
    while ((bytes_read = fread(buffer, 1, 16, file)) > 0) {
        unsigned char decrypted[16];
        AES_decrypt(buffer, decrypted, &decryptKey);

        fseek(file, -bytes_read, SEEK_CUR);
        fwrite(decrypted, 1, 16, file);
    }

    fclose(file);
    printf("File %s decrypted with AES.\n", filename);
}