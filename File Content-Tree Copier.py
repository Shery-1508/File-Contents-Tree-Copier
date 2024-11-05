import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk, messagebox
import os

class FileAggregatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Content-Tree Copier")
        self.root.geometry("1000x600")  # Set window size
        self.root.resizable(True, True)

        icon_path = os.path.join(os.path.dirname(__file__), "file_content-tree_copier.ico")
        self.root.iconbitmap(icon_path)

        # Style
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#4CAF50", font=("Arial", 10))
        self.style.configure("Accent.TButton", background="#45a049")
        self.style.configure("TCheckbutton", font=("Arial", 10), padding=5)
        self.style.configure("TLabel", font=("Arial", 12), padding=5)

        # Create a frame for the top controls (buttons, checkboxes)
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Create the buttons for selecting files and directories first
        self.select_files_button = ttk.Button(self.control_frame, text="Select Files", command=self.select_files)
        self.select_files_button.pack(side=tk.LEFT, padx=5)

        self.select_directory_button = ttk.Button(self.control_frame, text="Select Directory", command=self.select_directory)
        self.select_directory_button.pack(side=tk.LEFT, padx=5)

        # Create checkboxes for Show Tree and Show Contents
        self.show_tree_var = tk.BooleanVar(value=True)
        self.show_contents_var = tk.BooleanVar(value=True)

        self.show_tree_checkbox = tk.Checkbutton(self.control_frame, text="Show Tree", variable=self.show_tree_var, command=self.toggle_tree)
        self.show_tree_checkbox.pack(side=tk.LEFT, padx=5)

        self.show_contents_checkbox = tk.Checkbutton(self.control_frame, text="Show Contents", variable=self.show_contents_var, command=self.toggle_contents)
        self.show_contents_checkbox.pack(side=tk.LEFT, padx=5)

        # Add an Info button to show information about the app in the top-right corner
        self.info_button = ttk.Button(self.control_frame, text="Info", command=self.show_info)
        self.info_button.pack(side=tk.RIGHT, padx=5)

        # Create a frame for the listbox and text area below the control frame
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create a frame for the listbox (file tree)
        self.listbox_frame = tk.Frame(self.main_frame)
        self.listbox_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Create a listbox to display file structure
        self.listbox = tk.Listbox(self.listbox_frame, height=20, width=40, font=("Courier New", 10))
        self.listbox.pack(side=tk.LEFT, fill=tk.Y)

        # Scrollbar for the listbox
        self.listbox_scroll = tk.Scrollbar(self.listbox_frame, orient="vertical", command=self.listbox.yview)
        self.listbox_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.configure(yscrollcommand=self.listbox_scroll.set)

        # Create the copy button for the tree structure
        self.copy_tree_button = ttk.Button(self.listbox_frame, text="Copy Tree", command=self.copy_tree_to_clipboard)
        self.copy_tree_button.pack(pady=5)
        self.copy_tree_button.place(relx=0.94, rely=0.005, anchor='ne')

        # Create a frame for the text area (file contents)
        self.text_area_frame = tk.Frame(self.main_frame)
        self.text_area_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create a text area to display file contents
        self.text_area = scrolledtext.ScrolledText(self.text_area_frame, wrap=tk.WORD, width=80, height=20, font=("Arial", 10))
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create the copy button for file contents and place it in the top-right corner of the text area
        self.copy_contents_button = ttk.Button(self.text_area_frame, text="Copy", command=self.copy_to_clipboard)
        self.copy_contents_button.place(relx=0.975, rely=0.005, anchor='ne')  # Position button in top-right corner of text area

        # Create a new button to copy both tree and contents
        self.copy_both_button = ttk.Button(self.control_frame, text="Copy Tree & Contents", command=self.copy_tree_and_contents)
        self.copy_both_button.pack(side=tk.RIGHT, padx=5)

        # Disable the new button by default
        self.update_copy_both_button_state()

    def select_files(self):
        file_paths = filedialog.askopenfilenames(title="Select Files")
        if file_paths:
            all_text = self.get_files_text(file_paths)
            self.display_text(all_text)
            self.build_listbox(file_paths, show_files=True)

    def select_directory(self):
        dir_path = filedialog.askdirectory(title="Select Directory")
        if dir_path:
            self.build_listbox([dir_path], show_files=False)  # Build list for the selected directory
            all_text = self.get_files_text_in_directory(dir_path)
            self.display_text(all_text)

    def get_files_text(self, file_paths):
        all_text = ""
        ignored_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.mp4', '.avi', '.mov', '.wmv', '.zip', '.tar', '.gz']
        for file_path in file_paths:
            if os.path.exists(file_path) and os.path.isfile(file_path):
                if not any(file_path.endswith(ext) for ext in ignored_extensions):
                    all_text += f"{os.path.basename(file_path)}:\n"
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            all_text += file.read() + "\n\n"
                    except (UnicodeDecodeError, IOError):
                        all_text += f"[Could not read file: {os.path.basename(file_path)}]\n\n"
        return all_text

    def get_files_text_in_directory(self, dir_path):
        all_text = ""
        ignored_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.mp4', '.avi', '.mov', '.wmv', '.zip', '.tar', '.gz']
        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                if not any(file_path.endswith(ext) for ext in ignored_extensions):
                    try:
                        relative_path = os.path.relpath(file_path, dir_path)
                        all_text += f"{relative_path}:\n"
                        with open(file_path, 'r', encoding='utf-8') as f:
                            all_text += f.read() + "\n\n"
                    except (UnicodeDecodeError, IOError):
                        all_text += f"[Could not read file: {relative_path}]\n\n"
        return all_text

    def display_text(self, text):
        self.text_area.delete(1.0, tk.END)  # Clear the text area
        self.text_area.insert(tk.END, text)  # Insert the new text

    def copy_to_clipboard(self):
        text_to_copy = self.text_area.get("1.0", "end-1c")
        self.root.clipboard_clear()
        self.root.clipboard_append(text_to_copy)
        self.copy_contents_button.config(text="Copied!", style="Accent.TButton")
        self.root.after(2000, lambda: self.copy_contents_button.config(text="Copy"))

    def copy_tree_to_clipboard(self):
        self.root.clipboard_clear()
        tree_text = self.listbox.get(0, tk.END)
        tree_contents = "\n".join(tree_text)
        self.root.clipboard_append(tree_contents)
        self.copy_tree_button.config(text="Copied!", style="Accent.TButton")
        self.root.after(2000, lambda: self.copy_tree_button.config(text="Copy Tree"))

    def copy_tree_and_contents(self):
        # Check if both show tree and show contents are enabled
        if self.show_tree_var.get() and self.show_contents_var.get():
            # Get tree structure and file contents
            tree_text = "\n".join(self.listbox.get(0, tk.END))
            file_contents = self.text_area.get("1.0", "end-1c")
            # Prepare the combined content
            combined_text = f"{tree_text}\n\nAnd here is the file's code in detail:\n\n{file_contents}"
            # Copy to clipboard
            self.root.clipboard_clear()
            self.root.clipboard_append(combined_text)
            self.copy_both_button.config(text="Copied!", style="Accent.TButton")
            self.root.after(2000, lambda: self.copy_both_button.config(text="Copy Tree & Contents"))
        else:
            messagebox.showwarning("Warning", "Please enable both Show Tree and Show Contents to use this feature.")

    def build_listbox(self, paths, show_files=False):
        self.listbox.delete(0, tk.END)
        if show_files:
            # Add "The File(s):" message before file tree
            self.listbox.insert(tk.END, "The File(s):")
        for path in paths:
            if os.path.isfile(path):
                self.listbox.insert(tk.END, os.path.basename(path))
            elif os.path.isdir(path):
                structure = self.get_tree_structure(path)
                self.listbox.insert(tk.END, "The Contents")
                for line in structure.splitlines():
                    self.listbox.insert(tk.END, line)

    def get_tree_structure(self, dir_path, prefix="", include_parent=True):
        structure = ""
        parent_dir = os.path.basename(dir_path) if include_parent else ""
        items = sorted(os.listdir(dir_path))
        
        if include_parent:
            structure += f"{prefix}{parent_dir}/\n"

        for index, item in enumerate(items):
            path = os.path.join(dir_path, item)
            is_last = index == len(items) - 1
            if os.path.isdir(path):
                structure += f"{prefix}{'└── ' if is_last else '├── '}{item}/\n"
                next_prefix = prefix + ("    " if is_last else "│   ")
                structure += self.get_tree_structure(path, next_prefix, include_parent=False)
            else:
                structure += f"{prefix}{'└── ' if is_last else '├── '}{item}\n"
        return structure

    def toggle_tree(self):
        self.update_copy_both_button_state()
        if self.show_tree_var.get():
            self.listbox_frame.pack(side=tk.LEFT, fill=tk.Y)
        else:
            self.listbox_frame.pack_forget()

    def toggle_contents(self):
        self.update_copy_both_button_state()
        if self.show_contents_var.get():
            self.text_area_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        else:
            self.text_area_frame.pack_forget()

    def update_copy_both_button_state(self):
        if self.show_tree_var.get() and self.show_contents_var.get():
            self.copy_both_button.config(state=tk.NORMAL)
        else:
            self.copy_both_button.config(state=tk.DISABLED)

    def show_info(self):
        info_message = (
            "File Aggregator App\n\n"
            "This application allows you to:\n"
            "- Select and view text files from your computer\n"
            "- See the directory structure in a tree view\n"
            "- Copy the contents of selected files or the entire tree structure to the clipboard.\n\n"
            "Why is this useful?\n"
            "Sometimes, for debugging purposes, developers might need to provide the entire code or contents of multiple files to an AI model like GPT. "
            "If there are many files involved, this can become a tedious task, especially when you need to copy and paste from each file manually. "
            "This app streamlines that process by allowing you to select multiple files or directories, view their contents in one place, "
            "and easily copy all the content or the file tree structure at once, saving time and effort.\n\n"
            "Developed with love using Python's Tkinter library!"
        )
        messagebox.showinfo("Info", info_message)


if __name__ == "__main__":
    root = tk.Tk()
    app = FileAggregatorApp(root)
    root.mainloop()
