#ifndef COREVAULT_H
#define COREVAULT_H

#ifdef __cplusplus
extern "C" {
#endif

void create_file(const char *filename);
void read_file(const char *filename);
void delete_file(const char *filename);
void list_directory(const char *path);
void copy_file(const char *src, const char *dest);
void rename_file(const char *oldname, const char *newname);
void rename_directory(const char *oldname, const char *newname);
void create_directory(const char *dirname);
int delete_directory(const char *dirname);
void search(const char *path, const char *name);

#ifdef __cplusplus
}
#endif

#endif