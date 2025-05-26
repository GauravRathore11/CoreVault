CC = gcc
CFLAGS = -Wall -g -Iinclude -D_XOPEN_SOURCE=700
SRC = src/file_ops.c src/dir_ops.c src/auth.c
OBJ = $(SRC:.c=.o)
MAIN_SRC = src/main.c
MAIN_OUT = cv

all: $(MAIN_OUT)

$(MAIN_OUT): $(MAIN_SRC) $(OBJ) include/corevault.h
	$(CC) $(CFLAGS) $(MAIN_SRC) $(OBJ) -o $(MAIN_OUT)

src/%.o: src/%.c include/corevault.h
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(MAIN_OUT) $(OBJ) .corevault_pass