import tkinter as tk
from tkinter import messagebox, scrolledtext
import ctypes
import os
import sys
from contextlib import contextmanager

class TerminalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CoreVault Terminal")
        self.root.geometry("800x600")

        # Load shared library
        try:
            self.lib = ctypes.CDLL("./libcorevault.so")
        except OSError as e:
            print(f"Error loading libcorevault.so: {e}")
            sys.exit(1)

        # Define function signatures
        self.lib.create_file.argtypes = [ctypes.c_char_p]
        self.lib.read_file.argtypes = [ctypes.c_char_p]
        self.lib.delete_file.argtypes = [ctypes.c_char_p]
        self.lib.list_directory.argtypes = [ctypes.c_char_p]
        self.lib.copy_file.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.lib.rename_file.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.lib.rename_directory.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.lib.create_directory.argtypes = [ctypes.c_char_p]
        self.lib.delete_directory.argtypes = [ctypes.c_char_p]
        self.lib.delete_directory.restype = ctypes.c_int
        self.lib.search.argtypes = [ctypes.c_char_p, ctypes.c_char_p]

        # Redirect stdout/stderr to capture printf/perror
        self.output_buffer = []
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

        # Output area
        self.output = scrolledtext.ScrolledText(root, state='disabled', height=20)
        self.output.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Input field
        self.input = tk.Entry(root)
        self.input.pack(padx=10, pady=5, fill=tk.X)
        self.input.bind('<Return>', self.execute_command)
        self.input.focus()

    @contextmanager
    def redirect_output(self):
        class OutputCapture:
            def __init__(self, app):
                self.app = app
            def write(self, text):
                self.app.output_buffer.append(text)
            def flush(self):
                pass
        sys.stdout = sys.stderr = OutputCapture(self)
        try:
            yield
        finally:
            sys.stdout = self.original_stdout
            sys.stderr = self.original_stderr
            self.flush_output()

    def flush_output(self):
        if self.output_buffer:
            self.output.config(state='normal')
            for text in self.output_buffer:
                self.output.insert(tk.END, text)
            self.output.config(state='disabled')
            self.output.see(tk.END)
            self.output_buffer.clear()

    def execute_command(self, event=None):
        cmd = self.input.get().strip()
        self.input.delete(0, tk.END)
        self.output.config(state='normal')
        self.output.insert(tk.END, f"> {cmd}\n")
        self.output.config(state='disabled')
        self.output.see(tk.END)

        if not cmd:
            self.output.config(state='normal')
            self.output.insert(tk.END, "No command entered.\n")
            self.output.config(state='disabled')
            self.output.see(tk.END)
            return

        args = cmd.split()
        command = args[0]

        with self.redirect_output():
            if command == "create" and len(args) == 2:
                self.lib.create_file(args[1].encode('utf-8'))
            elif command == "read" and len(args) == 2:
                self.lib.read_file(args[1].encode('utf-8'))
            elif command == "delete" and len(args) == 2:
                self.lib.delete_file(args[1].encode('utf-8'))
            elif command == "list" and (len(args) == 1 or len(args) == 2):
                path = args[1].encode('utf-8') if len(args) == 2 else b"."
                self.lib.list_directory(path)
            elif command == "copy" and len(args) == 3:
                self.lib.copy_file(args[1].encode('utf-8'), args[2].encode('utf-8'))
            elif command == "rename" and len(args) == 3:
                self.lib.rename_file(args[1].encode('utf-8'), args[2].encode('utf-8'))
            elif command == "renamedir" and len(args) == 3:
                self.lib.rename_directory(args[1].encode('utf-8'), args[2].encode('utf-8'))
            elif command == "mkdir" and len(args) == 2:
                self.lib.create_directory(args[1].encode('utf-8'))
            elif command == "rmdir" and len(args) == 2:
                result = self.lib.delete_directory(args[1].encode('utf-8'))
                if result == 1:  # Non-empty directory
                    if messagebox.askyesno("Confirm Deletion",
                                           f"Directory {args[1]} is not empty. Delete all contents?"):
                        # Call delete_directory again to perform deletion
                        self.lib.delete_directory(args[1].encode('utf-8'))
                    else:
                        print("Deletion aborted.")
            elif command == "search" and len(args) == 3:
                self.lib.search(args[1].encode('utf-8'), args[2].encode('utf-8'))
            elif command == "exit" and len(args) == 1:
                self.root.quit()
            else:
                print("Unknown command or wrong arguments.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TerminalApp(root)
    root.mainloop()