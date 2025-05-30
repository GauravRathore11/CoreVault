CC = gcc
CFLAGS = -Wall -g -Iinclude -fPIC -D_XOPEN_SOURCE=700
SOURCES = src/file_ops.c src/dir_ops.c src/auth.c
OBJECTS = $(SOURCES:.c=.o)
LIB_OUT = libcorevault.so
MAIN_SRC = src/main.c
MAIN_OUT = cv

all: $(LIB_OUT) $(MAIN_OUT)

$(LIB_OUT): $(OBJECTS)
	$(CC) -shared $(OBJECTS) -o $(LIB_OUT)

$(MAIN_OUT): $(MAIN_SRC) $(OBJECTS)
	$(CC) $(CFLAGS) $(MAIN_SRC) $(OBJECTS) -o $(MAIN_OUT)

clean:
	rm -f $(LIB_OUT) $(MAIN_OUT) $(OBJECTS) .corevault_pass