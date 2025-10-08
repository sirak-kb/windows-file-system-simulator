import tkinter as tk
from tkinter import simpledialog, messagebox

class FileSystemObject:
    def __init__(self, name, is_directory=False):
        self.name = name
        self.is_directory = is_directory
        self.children = []

class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role

class AccessControlledVirtualFileSystem:
    def __init__(self):
        self.root = FileSystemObject("/", is_directory=True)
        self.current_directory = self.root
        self.clipboard = None
        self.history = [self.root]
        self.history_index = 0
        self.users = {
            "sirak": User("sirak", "admin", "admin"),
            "user": User("user", "user", "regular")
        }
        self.current_user = None

    def login(self, username, password):
        if username in self.users and self.users[username].password == password:
            self.current_user = self.users[username]
            return True
        else:
            return False

    def logout(self):
        self.current_user = None

    def has_permission(self, operation):
        if self.current_user:
            if self.current_user.role == "admin":
                return True  # Admin has permission for all operations
            elif self.current_user.role == "regular":
                if operation == "delete":
                    return False  # Regular user cannot delete files or directories
                else:
                    return True  # Regular user has permission for all other operations
        return False

    def create_directory(self, name):
        if self.has_permission("create"):
            new_directory = FileSystemObject(name, is_directory=True)
            self.current_directory.children.append(new_directory)
        else:
            messagebox.showerror("Access Denied", "You do not have permission to create directories.")

    def create_file(self, name):
        if self.has_permission("create"):
            new_file = FileSystemObject(name)
            self.current_directory.children.append(new_file)
        else:
            messagebox.showerror("Access Denied", "You do not have permission to create files.")

    def delete(self, name):
        if self.has_permission("delete"):
            for i, child in enumerate(self.current_directory.children):
                if child.name == name:
                    del self.current_directory.children[i]
                    return True
            return False
        else:
            messagebox.showerror("Access Denied", "You do not have permission to delete files or directories.")

    def rename(self, old_name, new_name):
        if self.has_permission("rename"):
            for child in self.current_directory.children:
                if child.name == old_name:
                    child.name = new_name
                    return True
            return False
        else:
            messagebox.showerror("Access Denied", "You do not have permission to rename files or directories.")

    def list_contents(self):
        return [child.name for child in self.current_directory.children]

    def change_directory(self, name):
        if self.has_permission("read"):
            if name == "..":
                if self.current_directory != self.root:
                    self.history_index -= 1
                    self.current_directory = self.history[self.history_index]
            else:
                for child in self.current_directory.children:
                    if child.name == name and child.is_directory:
                        self.history_index += 1
                        self.current_directory = child
                        self.history.append(self.current_directory)
                        break
        else:
            messagebox.showerror("Access Denied", "You do not have permission to read directories.")

    def copy(self, name):
        if self.has_permission("copy"):
            for child in self.current_directory.children:
                if child.name == name:
                    self.clipboard = child
                    return True
            return False
        else:
            messagebox.showerror("Access Denied", "You do not have permission to copy files or directories.")

    def cut(self, name):
        if self.has_permission("cut"):
            for child in self.current_directory.children:
                if child.name == name:
                    self.clipboard = child
                    return True
            return False
        else:
            return False 

    def paste(self):
        if self.has_permission("paste"):
            if self.clipboard:
                self.current_directory.children.append(self.clipboard)
                self.clipboard = None
        else:
            messagebox.showerror("Access Denied", "You do not have permission to paste files or directories.")

class AccessControlledFileExplorerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Explorer")
        self.virtual_fs = AccessControlledVirtualFileSystem()
        self.logged_in = False

        # Main Frame
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Login, Logout, Refresh, Back, Forward Buttons
        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(side=tk.TOP, fill=tk.X)

        self.login_button = tk.Button(self.button_frame, text="Login", command=self.login)
        self.login_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.logout_button = tk.Button(self.button_frame, text="Logout", command=self.logout)
        self.logout_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.logout_button.config(state=tk.DISABLED)

        self.refresh_button = tk.Button(self.button_frame, text="Refresh", command=self.populate_list)
        self.refresh_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.back_button = tk.Button(self.button_frame, text="Back", command=self.back)
        self.back_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.forward_button = tk.Button(self.button_frame, text="Forward", command=self.forward)
        self.forward_button.pack(side=tk.LEFT, padx=5, pady=5)

        # File Listbox
      
        self.file_listbox = tk.Listbox(self.main_frame, width=50, height=20, selectmode=tk.SINGLE)
        self.file_listbox.pack(side=tk.TOP, padx=10, pady=0, fill=tk.BOTH, expand=True)
        self.populate_list()
        self.file_listbox.bind("<Double-Button-1>", self.on_listbox_double_click)

        # Buttons
        self.create_buttons()

        # Search Bar
        self.search_frame = tk.Frame(self.main_frame)
        self.search_frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)

        self.search_entry_var = tk.StringVar()
        self.search_entry = tk.Entry(self.search_frame, textvariable=self.search_entry_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.bind("<Return>", self.search)

        self.search_button = tk.Button(self.search_frame, text="Search", command=self.search)
        self.search_button.pack(side=tk.LEFT)

    def populate_list(self):
        self.file_listbox.delete(0, tk.END)
      
        contents = self.virtual_fs.list_contents()
        for item in contents:
            symbol = "📁" if self.virtual_fs.current_directory.children[contents.index(item)].is_directory else "📄"
            self.file_listbox.insert(tk.END, f"{symbol} {item}")

    def on_listbox_double_click(self, event):
        selection = self.file_listbox.curselection()
        if selection:
            filename = self.file_listbox.get(selection[0]).split(" ")[1]  # Extracting filename from the item
            if not self.virtual_fs.current_directory.children[selection[0]].is_directory:
                self.open_file(filename)
            else:
                self.virtual_fs.change_directory(filename)
                self.populate_list()

    def delete_selected(self):
        selection = self.file_listbox.curselection()
        if selection:
            filename = self.file_listbox.get(selection[0]).split(" ")[1]  # Extracting filename from the item
            success = self.virtual_fs.delete(filename)
            if success:
                self.populate_list()
            else:
                messagebox.showerror("Error", "Failed to delete file or directory")

    def rename_selected(self):
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            old_name = self.file_listbox.get(index).split(" ")[1]  # Extracting filename from the item
            new_name = simpledialog.askstring("Rename", f"Enter new name for {old_name}:")
            if new_name:
                success = self.virtual_fs.rename(old_name, new_name)
                if success:
                    self.populate_list()
                else:
                    messagebox.showerror("Error", "Failed to rename file or directory")

    def copy_selected(self):
        selection = self.file_listbox.curselection()
        if selection:
            filename = self.file_listbox.get(selection[0]).split(" ")[1]  # Extracting filename from the item
            success = self.virtual_fs.copy(filename)
            if success:
                self.populate_list()
            else:
                messagebox.showerror("Error", "Failed to copy file or directory")

    def cut_selected(self):
        selection = self.file_listbox.curselection()
        if selection:
            filename = self.file_listbox.get(selection[0]).split(" ")[1]  # Extracting filename from the item
            if self.virtual_fs.has_permission("cut"):
                success = self.virtual_fs.cut(filename)
                if success:
                    self.populate_list()
                else:
                    pass
                    # messagebox.showerror("Error", "Failed to cut file or directory")
            else:
                messagebox.showerror("Access Denied", "You do not have permission to cut files or directories.")

    def paste(self):
        self.virtual_fs.paste()
        self.populate_list()

    def create_directory(self):
        directory_name = simpledialog.askstring("Create Directory", "Enter directory name:")
        if directory_name:
            self.virtual_fs.create_directory(directory_name)
            self.populate_list()

    def create_file(self):
        file_name = simpledialog.askstring("Create File", "Enter file name:")
        if file_name:
            file_size = simpledialog.askinteger("File Size", "Enter file size in MB:")
            if file_size:
                self.virtual_fs.create_file(file_name)
                self.populate_list()

    def open_file(self, filename):
        messagebox.showinfo("Open", f"Opening file: {filename}")

    def back(self):
        if self.virtual_fs.history_index > 0:
            self.virtual_fs.history_index -= 1
            self.virtual_fs.current_directory = self.virtual_fs.history[self.virtual_fs.history_index]
            self.populate_list()

    def forward(self):
        if self.virtual_fs.history_index < len(self.virtual_fs.history) - 1:
            self.virtual_fs.history_index += 1
            self.virtual_fs.current_directory = self.virtual_fs.history[self.virtual_fs.history_index]
            self.populate_list()

    def create_buttons(self):
        button_frame = tk.Frame(self.main_frame)
        button_frame.pack(side=tk.BOTTOM, padx=5, pady=5, fill=tk.X)

        create_directory_button = tk.Button(button_frame, text="Create Directory", command=self.create_directory)
        create_directory_button.pack(side=tk.LEFT)

        create_file_button = tk.Button(button_frame, text="Create File", command=self.create_file)
        create_file_button.pack(side=tk.LEFT)

        delete_button = tk.Button(button_frame, text="Delete", command=self.delete_selected)
        delete_button.pack(side=tk.LEFT)

        rename_button = tk.Button(button_frame, text="Rename", command=self.rename_selected)
        rename_button.pack(side=tk.LEFT)

        copy_button = tk.Button(button_frame, text="Copy", command=self.copy_selected)
        copy_button.pack(side=tk.LEFT)

        cut_button = tk.Button(button_frame, text="Cut", command=self.cut_selected)
        cut_button.pack(side=tk.LEFT)

        paste_button = tk.Button(button_frame, text="Paste", command=self.paste)
        paste_button.pack(side=tk.LEFT)

    def search(self, event=None):
        query = self.search_entry_var.get()
        if query:
            search_results = [child.name for child in self.virtual_fs.current_directory.children if query.lower() in child.name.lower()]
            self.file_listbox.delete(0, tk.END)
            for item in search_results:
                symbol = "📁" if self.virtual_fs.current_directory.children[search_results.index(item)].is_directory else "📄"
                self.file_listbox.insert(tk.END, f"{symbol} {item}")
        else:
            self.populate_list()

    def login(self):
        login_dialog = tk.Toplevel(self.root)
        login_dialog.title("Login")

        username_label = tk.Label(login_dialog, text="Username:")
        username_label.grid(row=0, column=0, padx=5, pady=5)
        username_entry = tk.Entry(login_dialog)
        username_entry.grid(row=0, column=1, padx=5, pady=5)

        password_label = tk.Label(login_dialog, text="Password:")
        password_label.grid(row=1, column=0, padx=5, pady=5)
        password_entry = tk.Entry(login_dialog, show="*")
        password_entry.grid(row=1, column=1, padx=5, pady=5)

        login_button = tk.Button(login_dialog, text="Login", command=lambda: self.process_login(login_dialog, username_entry.get(), password_entry.get()))
        login_button.grid(row=2, columnspan=2, padx=5, pady=5)

    def process_login(self, login_dialog, username, password):
        if self.virtual_fs.login(username, password):
            messagebox.showinfo("Login", f"Welcome, {username}!")
            self.populate_list()
            self.logged_in = True
            self.login_button.config(state=tk.DISABLED)
            self.logout_button.config(state=tk.NORMAL)
            login_dialog.destroy()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def logout(self):
        self.virtual_fs.logout()
        messagebox.showinfo("Logout", "Logged out successfully.")
        self.populate_list()
        self.logged_in = False
        self.login_button.config(state=tk.NORMAL)
        self.logout_button.config(state=tk.DISABLED)

    def run(self):
        self.root.mainloop()

# Example usage:
if __name__ == "__main__":
    root = tk.Tk()
    app = AccessControlledFileExplorerApp(root)
    app.run()