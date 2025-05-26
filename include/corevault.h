#ifndef COREVAULT_H
#define COREVAULT_H

#ifdef __cplusplus
extern "C" {
#endif

void create_file(const char *filename);
void open_file(const char *filename);
void delete_file(const char *filename);
void metadata(const char *filename);
void list_directory(const char *path);
void copy_file(const char *src, const char *dest);
void move_file(const char *src, const char *dest);
void rename_file(const char *oldname, const char *newname);
void rename_directory(const char *oldname, const char *newname);
void createdir(const char *dirname);
int deletedir(const char *dirname);
int deletedir_force(const char *dirname);
void search(const char *path, const char *name);
void change_directory(const char *dirname);
void set_password(const char *password);
int login(const char *password);
void encrypt_file(const char *filename, const char *key);
void decrypt_file(const char *filename, const char *key);

#ifdef __cplusplus
}
#endif

#endif