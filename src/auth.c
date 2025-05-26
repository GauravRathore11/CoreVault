#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "corevault.h"

#define PASSWORD_FILE ".corevault_pass"
#define MAX_PASS_LEN 256

void set_password(const char *password) {
    FILE *file = fopen(PASSWORD_FILE, "w");
    if (!file) {
        perror("Failed to set password");
        return;
    }
    fprintf(file, "%s", password);
    fclose(file);
    printf("Password set successfully.\n");
}

int login(const char *password) {
    FILE *file = fopen(PASSWORD_FILE, "r");
    if (!file) {
        perror("No password set");
        return 0;
    }
    char stored_pass[MAX_PASS_LEN];
    if (fgets(stored_pass, MAX_PASS_LEN, file) == NULL) {
        fclose(file);
        printf("Error reading password.\n");
        return 0;
    }
    fclose(file);
    stored_pass[strcspn(stored_pass, "\n")] = 0; // Remove newline
    if (strcmp(password, stored_pass) == 0) {
        printf("Login successful.\n");
        return 1;
    }
    printf("Incorrect password.\n");
    return 0;
}