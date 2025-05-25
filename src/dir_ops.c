#define _XOPEN_SOURCE 700
#include <dirent.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include <ftw.h>
#include "corevault.h"

// Callback for nftw to remove files and directories
static int remove_entry(const char *fpath, const struct stat *sb, int typeflag, struct FTW *ftwbuf) {
    if (typeflag == FTW_F || typeflag == FTW_SL) {
        if (unlink(fpath) == -1) {
            perror("Failed to delete file");
            return -1;
        }
    } else if (typeflag == FTW_D || typeflag == FTW_DP) {
        if (rmdir(fpath) == -1) {
            perror("Failed to delete directory");
            return -1;
        }
    }
    return 0;
}

// Check if directory is non-empty
static int is_directory_non_empty(const char *dirname) {
    DIR *dir = opendir(dirname);
    if (dir == NULL) {
        perror("Error opening directory");
        return -1;
    }
    struct dirent *entry;
    int count = 0;
    while ((entry = readdir(dir)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }
        count++;
        if (count > 0) {
            closedir(dir);
            return 1;
        }
    }
    closedir(dir);
    return 0;
}

int delete_directory(const char *dirname) {
    struct stat st;
    if (stat(dirname, &st) == -1) {
        perror("Error accessing directory");
        return -1;
    }
    if (!S_ISDIR(st.st_mode)) {
        fprintf(stderr, "%s is not a directory\n", dirname);
        return -1;
    }

    int non_empty = is_directory_non_empty(dirname);
    if (non_empty == -1) {
        return -1;
    }
    if (non_empty) {
        return 1;
    }

    if (nftw(dirname, remove_entry, 64, FTW_DEPTH | FTW_PHYS) == -1) {
        perror("Failed to delete directory tree");
        return -1;
    }
    printf("Directory %s deleted.\n", dirname);
    return 0;
}

void list_directory(const char *path) {
    DIR *dir = opendir(path);
    if (dir == NULL) {
        perror("Error opening directory");
        return;
    }
    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        printf("%s\n", entry->d_name);
    }
    closedir(dir);
}

void rename_directory(const char *oldname, const char *newname) {
    if (rename(oldname, newname) == -1) {
        perror("Failed to rename directory");
        return;
    }
    printf("Directory renamed from %s to %s\n", oldname, newname);
}

void search(const char *path, const char *name) {
    DIR *dir = opendir(path);
    if (dir == NULL) {
        perror("Error opening directory");
        return;
    }
    struct dirent *entry;
    struct stat st;
    char fullpath[256];

    while ((entry = readdir(dir)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }
        if (snprintf(fullpath, sizeof(fullpath), "%s/%s", path, entry->d_name) >= sizeof(fullpath)) {
            fprintf(stderr, "Error: Path too long for %s\n", entry->d_name);
            continue;
        }
        if (strstr(entry->d_name, name) != NULL) {
            if (stat(fullpath, &st) == -1) {
                perror("Failed to get file info");
                continue;
            }
            printf("%s (%s)\n", fullpath, S_ISDIR(st.st_mode) ? "directory" : "file");
        }
    }
    closedir(dir);
}

void create_directory(const char *dirname) {
    if (mkdir(dirname, 0755) == -1) {
        perror("Failed to create directory");
        return;
    }
    printf("Directory %s created.\n", dirname);
}