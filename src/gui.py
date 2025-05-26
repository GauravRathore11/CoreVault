import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Scrollbar
import ctypes
import os
import sys
import psutil
from contextlib import contextmanager
import threading
import time

# Redirect stdout and stderr to capture C function output
@contextmanager
def stdout_redirector():
    output = []
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    class OutputRedirector:
        def write(self, text):
            if text.strip():  # Ignore empty strings
                output.append(text)
        def flush(self):
            pass
    sys.stdout = OutputRedirector()
    sys.stderr = OutputRedirector()
    try:
        yield output
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr

# Load shared library
try:
    lib = ctypes.CDLL("./libcorevault.so")
except OSError as e:
    print(f"Error loading libcorevault.so: {e}")
    # For demo purposes, create a mock library
    class MockLib:
        def __getattr__(self, name):
            def mock_func(*args, **kwargs):
                print(f"Mock {name} called with args: {args}")
                if name == "login":
                    return 1  # Success
                elif name in ["deletedir", "deletedir_force"]:
                    return 0  # Success
                return None
            return mock_func
    lib = MockLib()

# Define function prototypes for all corevault.h functions
try:
    lib.create_file.argtypes = [ctypes.c_char_p]
    lib.open_file.argtypes = [ctypes.c_char_p]
    lib.delete_file.argtypes = [ctypes.c_char_p]
    lib.metadata.argtypes = [ctypes.c_char_p]
    lib.list_directory.argtypes = [ctypes.c_char_p]
    lib.copy_file.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    lib.move_file.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    lib.rename_file.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    lib.rename_directory.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    lib.createdir.argtypes = [ctypes.c_char_p]
    lib.deletedir.argtypes = [ctypes.c_char_p]
    lib.deletedir.restype = ctypes.c_int
    lib.deletedir_force.argtypes = [ctypes.c_char_p]
    lib.deletedir_force.restype = ctypes.c_int
    lib.search.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    lib.change_directory.argtypes = [ctypes.c_char_p]
    lib.set_password.argtypes = [ctypes.c_char_p]
    lib.login.argtypes = [ctypes.c_char_p]
    lib.login.restype = ctypes.c_int
    lib.encrypt_file.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    lib.decrypt_file.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
except:
    pass  # Mock library doesn't need these

class CoreVaultGUI:
    def __init__(self, root):
        # Initialize main window
        self.root = root
        self.root.title("CoreVault")
        self.root.geometry("1000x700")
        self.is_authenticated = False
        self.current_dir = os.getcwd()

        # Configure dark theme
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2e2e2e", foreground="white", fieldbackground="#2e2e2e")
        style.configure("Treeview.Heading", background="#3e3e3e", foreground="white")
        style.configure("TButton", background="#3e3e3e", foreground="white")
        style.configure("TEntry", fieldbackground="#2e2e2e", foreground="white")
        style.configure("TLabel", background="#1e1e1e", foreground="white")
        style.configure("TFrame", background="#1e1e1e")
        self.root.configure(bg="#1e1e1e")

        # Login frame (centered)
        self.login_frame = ttk.Frame(self.root)
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Login widgets
        ttk.Label(self.login_frame, text="CoreVault Login", font=("Arial", 14), foreground="#00ff00").grid(row=0, column=0, columnspan=2, pady=10)
        self.pass_entry = ttk.Entry(self.login_frame, show="*", width=30)
        self.pass_entry.grid(row=1, column=0, columnspan=2, pady=5)
        self.pass_entry.bind("<Return>", lambda e: self.login())
        ttk.Button(self.login_frame, text="Set Password", command=self.set_password).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(self.login_frame, text="Login", command=self.login).grid(row=2, column=1, padx=5, pady=5)

        # Main frame (hidden until login)
        self.main_frame = ttk.Frame(self.root)
        
        # System monitor at top
        self.monitor_frame = ttk.Frame(self.main_frame)
        self.monitor_frame.pack(fill="x", padx=5, pady=5)
        self.cpu_label = ttk.Label(self.monitor_frame, text="CPU: 0%", foreground="#00ff00")
        self.cpu_label.pack(side="left", padx=5)
        self.mem_label = ttk.Label(self.monitor_frame, text="Memory: 0%", foreground="#00ff00")
        self.mem_label.pack(side="left", padx=5)

        # Paned window for file tree (left) and content (right)
        self.paned = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned.pack(fill="both", expand=True, padx=5, pady=5)

        # File tree on left
        self.tree_frame = ttk.Frame(self.paned)
        self.paned.add(self.tree_frame, weight=1)
        
        # Add scrollbar for tree
        tree_scroll = ttk.Scrollbar(self.tree_frame)
        tree_scroll.pack(side="right", fill="y")
        
        self.tree = ttk.Treeview(self.tree_frame, height=20, yscrollcommand=tree_scroll.set)
        self.tree.pack(fill="both", expand=True, side="left")
        tree_scroll.config(command=self.tree.yview)
        
        self.tree.heading("#0", text="File Explorer")
        self.tree.bind("<Double-1>", self.on_double_click)

        # Context menu for file tree
        self.context_menu = tk.Menu(self.root, tearoff=0, bg="#2e2e2e", fg="white")
        self.context_menu.add_command(label="Delete", command=self.context_delete)
        self.context_menu.add_command(label="Rename", command=self.context_rename)
        self.context_menu.add_command(label="Metadata", command=self.context_metadata)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Right content frame (output and command input)
        self.content_frame = ttk.Frame(self.paned)
        self.paned.add(self.content_frame, weight=3)

        # Output text area with scrollbar
        self.output_frame = ttk.Frame(self.content_frame)
        self.output_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.output_scroll = ttk.Scrollbar(self.output_frame)
        self.output_scroll.pack(side="right", fill="y")
        
        self.output = tk.Text(self.output_frame, height=15, bg="#2e2e2e", fg="white", 
                             yscrollcommand=self.output_scroll.set, wrap=tk.WORD)
        self.output.pack(fill="both", expand=True, side="left")
        self.output_scroll.config(command=self.output.yview)
        
        # Configure colored text tags
        self.output.tag_configure("command", foreground="#00ff00")  # Green for commands
        self.output.tag_configure("output", foreground="white")     # White for output
        self.output.tag_configure("error", foreground="#ff0000")    # Red for errors
        self.output.tag_configure("warning", foreground="#ffff00")  # Yellow for warnings

        # Command input at bottom
        self.cmd_frame = ttk.Frame(self.content_frame)
        self.cmd_frame.pack(fill="x", padx=5, pady=5)
        ttk.Label(self.cmd_frame, text="Command:", foreground="#00ff00").pack(side="left")
        self.cmd_entry = ttk.Entry(self.cmd_frame)
        self.cmd_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.cmd_entry.bind("<Return>", self.execute_command)
        ttk.Button(self.cmd_frame, text="Execute", command=self.execute_command).pack(side="left")

        # Start system monitoring
        self.start_monitoring()

    def start_monitoring(self):
        # Run CPU and memory usage updates in a background thread
        def update_monitor():
            while True:
                try:
                    cpu = psutil.cpu_percent(interval=0.1)
                    mem = psutil.virtual_memory().percent
                    # Use after_idle to safely update GUI from thread
                    self.root.after_idle(lambda: self.cpu_label.config(text=f"CPU: {cpu:.1f}%"))
                    self.root.after_idle(lambda: self.mem_label.config(text=f"Memory: {mem:.1f}%"))
                    time.sleep(2)
                except:
                    break
        threading.Thread(target=update_monitor, daemon=True).start()

    def set_password(self):
        # Set a new password using C function
        password = self.pass_entry.get()
        if not password:
            messagebox.showerror("Error", "Password cannot be empty")
            return
        with stdout_redirector() as output:
            lib.set_password(password.encode())
        output_text = "".join(output) if output else "Password set successfully"
        self.display_output(output_text + "\n", "output")

    def login(self):
        # Attempt login using C function
        password = self.pass_entry.get()
        if not password:
            messagebox.showerror("Error", "Password cannot be empty")
            return
        with stdout_redirector() as output:
            success = lib.login(password.encode())
        output_text = "".join(output) if output else ("Login successful" if success else "Login failed")
        self.display_output(output_text + "\n", "output" if success else "error")
        if success:
            self.is_authenticated = True
            self.login_frame.place_forget()
            self.main_frame.pack(fill="both", expand=True)
            self.update_tree()
            self.display_output("Welcome to CoreVault!\n", "output")

    def display_output(self, text, tag):
        # Append text to output area with appropriate tag and newline
        if text:
            self.output.insert(tk.END, text, tag)
            if not text.endswith('\n'):
                self.output.insert(tk.END, '\n', tag)
            self.output.see(tk.END)  # Scroll to end

    def update_tree(self):
        # Refresh file tree with current directory contents
        if not self.is_authenticated:
            return
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # Try to use the library function first
            with stdout_redirector() as output:
                lib.list_directory(self.current_dir.encode())
            
            if output and "".join(output).strip():
                # Parse library output
                files = "".join(output).strip().split("\n")
                for item in files:
                    item = item.strip()
                    if item and item not in [".", ".."]:
                        full_path = os.path.join(self.current_dir, item)
                        is_dir = os.path.isdir(full_path) if os.path.exists(full_path) else False
                        icon = "📁" if is_dir else "📄"
                        self.tree.insert("", "end", text=f"{icon} {item}", values=(full_path, is_dir))
            else:
                # Fallback to standard directory listing
                self.fallback_tree_update()
        except Exception as e:
            # Fallback to standard directory listing
            self.fallback_tree_update()

    def fallback_tree_update(self):
        # Fallback method using standard Python os module
        try:
            items = []
            for item in os.listdir(self.current_dir):
                if not item.startswith('.'):  # Hide hidden files
                    full_path = os.path.join(self.current_dir, item)
                    is_dir = os.path.isdir(full_path)
                    items.append((item, full_path, is_dir))
            
            # Sort directories first, then files
            items.sort(key=lambda x: (not x[2], x[0].lower()))
            
            for item, full_path, is_dir in items:
                icon = "📁" if is_dir else "📄"
                self.tree.insert("", "end", text=f"{icon} {item}", values=(full_path, is_dir))
                
        except PermissionError:
            self.display_output(f"Permission denied accessing {self.current_dir}\n", "error")
        except Exception as e:
            self.display_output(f"Error listing directory: {str(e)}\n", "error")

    def on_double_click(self, event):
        # Navigate into directory on double-click
        item = self.tree.selection()
        if not item:
            return
        
        values = self.tree.item(item[0], "values")
        if values and len(values) >= 2 and (values[1] == "True" or values[1] is True):
            new_dir = values[0]
            try:
                with stdout_redirector() as output:
                    lib.change_directory(new_dir.encode())
                
                # Update current directory
                if os.path.exists(new_dir) and os.path.isdir(new_dir):
                    self.current_dir = os.path.abspath(new_dir)
                    self.display_output(f"Changed to {self.current_dir}\n", "output")
                    self.update_tree()
                else:
                    self.display_output(f"Directory {new_dir} does not exist\n", "error")
            except Exception as e:
                self.display_output(f"Error changing directory: {str(e)}\n", "error")

    def show_context_menu(self, event):
        # Show right-click menu for file tree
        if not self.is_authenticated:
            return
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def context_delete(self):
        # Delete file or directory via context menu
        item = self.tree.selection()
        if not item:
            return
        
        values = self.tree.item(item[0], "values")
        if not values:
            return
            
        path = values[0]
        is_dir = values[1] == "True" or values[1] is True
        
        if is_dir:
            if messagebox.askyesno("Confirm", f"Delete directory {path}?"):
                with stdout_redirector() as output:
                    result = lib.deletedir(path.encode())
                if result == 1:
                    if messagebox.askyesno("Confirm", f"Directory {path} is not empty. Delete all contents?"):
                        with stdout_redirector() as output:
                            lib.deletedir_force(path.encode())
                        output_text = "".join(output) if output else f"Directory {path} deleted (forced)"
                        self.display_output(output_text + "\n", "output")
                    else:
                        self.display_output("Deletion aborted.\n", "warning")
                else:
                    output_text = "".join(output) if output else f"Directory {path} deleted"
                    self.display_output(output_text + "\n", "output")
        else:
            if messagebox.askyesno("Confirm", f"Delete file {path}?"):
                with stdout_redirector() as output:
                    lib.delete_file(path.encode())
                output_text = "".join(output) if output else f"File {path} deleted"
                self.display_output(output_text + "\n", "output")
        
        self.update_tree()

    def context_rename(self):
        # Rename file or directory via context menu
        item = self.tree.selection()
        if not item:
            return
        
        values = self.tree.item(item[0], "values")
        if not values:
            return
            
        old_path = values[0]
        is_dir = values[1] == "True" or values[1] is True
        old_name = os.path.basename(old_path)
        
        new_name = simpledialog.askstring("Rename", f"Enter new name for {old_name}:", 
                                         initialvalue=old_name, parent=self.root)
        if new_name and new_name != old_name:
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            with stdout_redirector() as output:
                if is_dir:
                    lib.rename_directory(old_path.encode(), new_path.encode())
                else:
                    lib.rename_file(old_path.encode(), new_path.encode())
            output_text = "".join(output) if output else f"Renamed {old_name} to {new_name}"
            self.display_output(output_text + "\n", "output")
            self.update_tree()

    def context_metadata(self):
        # Show file/directory metadata via context menu
        item = self.tree.selection()
        if not item:
            return
        
        values = self.tree.item(item[0], "values")
        if not values:
            return
            
        path = values[0]
        with stdout_redirector() as output:
            lib.metadata(path.encode())
        output_text = "".join(output) if output else f"Metadata for {path}: (No output from library)"
        self.display_output(output_text + "\n", "output")

    def execute_command(self, event=None):
        # Execute command from input field and display history
        if not self.is_authenticated:
            messagebox.showerror("Error", "Please login first")
            return
        
        cmd = self.cmd_entry.get().strip()
        if not cmd:
            return
        
        tokens = cmd.split()
        self.cmd_entry.delete(0, tk.END)
        
        # Display the command typed with proper formatting
        self.output.insert(tk.END, f"> {cmd}\n", "command")
        self.output.see(tk.END)
        
        output = []
        try:
            if tokens[0] == "create" and len(tokens) == 2:
                with stdout_redirector() as out:
                    lib.create_file(tokens[1].encode())
                output = out if out else [f"Created file {tokens[1]}"]
                
            elif tokens[0] == "open" and len(tokens) == 2:
                with stdout_redirector() as out:
                    lib.open_file(tokens[1].encode())
                output = out if out else [f"Opened file {tokens[1]}"]
                
            elif tokens[0] == "delete" and len(tokens) == 2:
                with stdout_redirector() as out:
                    lib.delete_file(tokens[1].encode())
                output = out if out else [f"Deleted file {tokens[1]}"]
                
            elif tokens[0] == "metadata" and len(tokens) == 2:
                with stdout_redirector() as out:
                    lib.metadata(tokens[1].encode())
                output = out if out else [f"Metadata for {tokens[1]}: (No output)"]
                
            elif tokens[0] == "list" and len(tokens) in [1, 2]:
                path = tokens[1] if len(tokens) == 2 else "."
                with stdout_redirector() as out:
                    lib.list_directory(path.encode())
                output = out if out else [f"Listed directory {path}"]
                
            elif tokens[0] == "copy" and len(tokens) == 3:
                with stdout_redirector() as out:
                    lib.copy_file(tokens[1].encode(), tokens[2].encode())
                output = out if out else [f"Copied {tokens[1]} to {tokens[2]}"]
                
            elif tokens[0] == "move" and len(tokens) == 3:
                with stdout_redirector() as out:
                    lib.move_file(tokens[1].encode(), tokens[2].encode())
                output = out if out else [f"Moved {tokens[1]} to {tokens[2]}"]
                
            elif tokens[0] == "rename" and len(tokens) == 3:
                with stdout_redirector() as out:
                    lib.rename_file(tokens[1].encode(), tokens[2].encode())
                output = out if out else [f"Renamed {tokens[1]} to {tokens[2]}"]
                
            elif tokens[0] == "renamedir" and len(tokens) == 3:
                with stdout_redirector() as out:
                    lib.rename_directory(tokens[1].encode(), tokens[2].encode())
                output = out if out else [f"Renamed directory {tokens[1]} to {tokens[2]}"]
                
            elif tokens[0] == "createdir" and len(tokens) == 2:
                with stdout_redirector() as out:
                    lib.createdir(tokens[1].encode())
                output = out if out else [f"Created directory {tokens[1]}"]
                
            elif tokens[0] == "deletedir" and len(tokens) == 2:
                with stdout_redirector() as out:
                    result = lib.deletedir(tokens[1].encode())
                if result == 1:
                    if messagebox.askyesno("Confirm", f"Directory {tokens[1]} is not empty. Delete all contents?"):
                        with stdout_redirector() as out:
                            lib.deletedir_force(tokens[1].encode())
                        output = out if out else [f"Force deleted directory {tokens[1]}"]
                    else:
                        output = ["Deletion aborted."]
                else:
                    output = out if out else [f"Deleted directory {tokens[1]}"]
                    
            elif tokens[0] == "search" and len(tokens) == 3:
                with stdout_redirector() as out:
                    lib.search(tokens[1].encode(), tokens[2].encode())
                output = out if out else [f"Searched for {tokens[2]} in {tokens[1]}"]
                
            elif tokens[0] == "cd" and len(tokens) == 2:
                new_path = os.path.abspath(tokens[1])
                if os.path.exists(new_path) and os.path.isdir(new_path):
                    with stdout_redirector() as out:
                        lib.change_directory(tokens[1].encode())
                    self.current_dir = new_path
                    output = out if out else [f"Changed directory to {self.current_dir}"]
                else:
                    output = [f"Directory {tokens[1]} does not exist"]
                    
            elif tokens[0] == "encrypt" and len(tokens) == 3:
                with stdout_redirector() as out:
                    lib.encrypt_file(tokens[1].encode(), tokens[2].encode())
                output = out if out else [f"Encrypted {tokens[1]} with key {tokens[2]}"]
                
            elif tokens[0] == "decrypt" and len(tokens) == 3:
                with stdout_redirector() as out:
                    lib.decrypt_file(tokens[1].encode(), tokens[2].encode())
                output = out if out else [f"Decrypted {tokens[1]} with key {tokens[2]}"]
                
            elif tokens[0] == "exit" and len(tokens) == 1:
                self.root.quit()
                return
            else:
                output = [f"Unknown command '{tokens[0]}' or wrong number of arguments."]
                output.append("\nAvailable commands:")
                output.append("  create <filename>")
                output.append("  open <filename>") 
                output.append("  delete <filename>")
                output.append("  list [directory]")
                output.append("  copy <source> <destination>")
                output.append("  move <source> <destination>")
                output.append("  rename <oldname> <newname>")
                output.append("  createdir <dirname>")
                output.append("  deletedir <dirname>")
                output.append("  cd <directory>")
                output.append("  encrypt <file> <key>")
                output.append("  decrypt <file> <key>")
                output.append("  search <directory> <pattern>")
                output.append("  metadata <file>")
                output.append("  exit")
                
            # Determine output tag based on content
            output_text = "".join(output)
            tag = "output"
            if any(word in output_text.lower() for word in ["error", "failed", "not found", "permission denied"]):
                tag = "error"
            elif any(word in output_text.lower() for word in ["warning", "aborted"]):
                tag = "warning"
                
            self.display_output(output_text, tag)
            
        except Exception as e:
            self.display_output(f"Error executing command: {str(e)}", "error")
        
        # Always update the tree after command execution
        self.update_tree()

if __name__ == "__main__":
    root = tk.Tk()
    app = CoreVaultGUI(root)
    root.mainloop()