CC = gcc
CFLAGS = -Wall -g -Iinclude -fPIC
SRC = src/file_ops.c src/dir_ops.c
OBJ = $(SRC:.c=.o)
OUT = libcorevault.so

all: $(OUT)

$(OUT): $(OBJ)
	$(CC) -shared $(OBJ) -o $(OUT)

src/%.o: src/%.c include/corevault.h
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OUT) $(OBJ)