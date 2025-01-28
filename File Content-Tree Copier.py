import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk, messagebox
import os
import json

class CustomScrollbarFrame(tk.Frame):
    def __init__(self, parent, text_widget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.text_widget = text_widget
        
        # Create main scrollbar
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.text_widget.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create indicator canvas
        self.indicator_width = 6  # Slightly wider for better visibility
        self.canvas = tk.Canvas(self, width=self.indicator_width, bg=self.scrollbar.cget('bg'),
                              highlightthickness=0, cursor="hand2")  # Add hand cursor
        self.canvas.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure text widget to use this scrollbar
        self.text_widget.configure(yscrollcommand=self.on_scroll)
        
        # Bind events
        self.canvas.bind('<Button-1>', self.on_indicator_click)
        self.canvas.bind('<Motion>', self.on_hover)  # Add hover effect
        
        self.file_positions = []  # Store (line_number, filename) tuples
        self.hover_tag = None  # Store current hover tooltip
        
    def on_scroll(self, first, last):
        # Update regular scrollbar
        self.scrollbar.set(first, last)
        self.update_indicators()
        
    def update_indicators(self):
        self.canvas.delete('all')
        
        # Get dimensions
        height = self.winfo_height()
        if not height:  # Guard against division by zero
            return
            
        total_lines = float(self.text_widget.index('end-1c').split('.')[0])
        if total_lines <= 1:
            return
            
        # Draw indicators
        for line_num, filename in self.file_positions:
            # Calculate relative position
            rel_pos = line_num / total_lines
            y_pos = rel_pos * height
            
            # Get the line text to check for dot marker
            line_text = self.text_widget.get(f"{line_num}.0", f"{line_num}.end")
            if line_text.startswith('⚫ ') and line_text.endswith(':'):
                # Draw indicator mark
                self.canvas.create_rectangle(
                    0, y_pos - 3,
                    self.indicator_width, y_pos + 3,
                    fill='#2196F3',  # More visible blue color
                    outline='#1976D2',  # Darker blue outline
                    tags=(f'indicator_{line_num}', filename, 'marker')
                )
                
                # Add hover area (slightly larger than visible marker)
                self.canvas.create_rectangle(
                    0, y_pos - 5,
                    self.indicator_width, y_pos + 5,
                    fill='',
                    outline='',
                    tags=(f'hover_{line_num}', filename, 'hover_area')
                )
            
    def on_hover(self, event):
        # Remove existing tooltip
        if self.hover_tag:
            self.canvas.delete(self.hover_tag)
            self.hover_tag = None
            
        # Find hover area under cursor
        items = self.canvas.find_overlapping(event.x, event.y, event.x + 1, event.y + 1)
        for item in items:
            tags = self.canvas.gettags(item)
            if 'hover_area' in tags:
                filename = tags[1]  # Get filename from tags
                
                # Create tooltip
                self.hover_tag = self.canvas.create_text(
                    self.indicator_width + 5, event.y,
                    text=filename,
                    anchor='w',
                    fill='#000000',
                    tags='tooltip',
                    font=('Arial', 8)
                )
                
                # Create tooltip background
                bbox = self.canvas.bbox(self.hover_tag)
                if bbox:
                    self.canvas.create_rectangle(
                        bbox,
                        fill='#FFFFFF',
                        outline='#CCCCCC',
                        tags='tooltip'
                    )
                    self.canvas.tag_raise(self.hover_tag)
                break
            
    def on_indicator_click(self, event):
        items = self.canvas.find_overlapping(event.x, event.y, event.x + 1, event.y + 1)
        for item in items:
            tags = self.canvas.gettags(item)
            if 'marker' in tags or 'hover_area' in tags:
                # Get line number from the indicator tag
                indicator_tag = next((tag for tag in tags if tag.startswith('indicator_') or tag.startswith('hover_')), None)
                if indicator_tag:
                    line_num = indicator_tag.split('_')[1]
                    # Scroll to position
                    self.text_widget.see(f"{line_num}.0")
                    # Highlight the line briefly
                    self.highlight_line(line_num)
                break
                
    def highlight_line(self, line_num):
        # Remove any existing highlight
        self.text_widget.tag_remove('highlight', '1.0', 'end')
        
        # Add new highlight
        self.text_widget.tag_add('highlight', f"{line_num}.0", f"{line_num}.end")
        self.text_widget.tag_config('highlight', background='#E3F2FD')  # Light blue highlight
        
        # Remove highlight after a delay
        self.after(1000, lambda: self.text_widget.tag_remove('highlight', '1.0', 'end'))
                
    def set_file_positions(self, positions):
        self.file_positions = positions
        self.update_indicators()

class LoadingSpinner(tk.Canvas):
    def __init__(self, parent, size=20, width=2, color='#2196F3'):
        super().__init__(parent, width=size, height=size, bg=parent.cget('bg'), highlightthickness=0)
        self.size = size
        self.angle = 0
        self.width = width
        self.color = color
        self.spinning = False
        
    def start(self):
        self.spinning = True
        self._spin()
        
    def stop(self):
        self.spinning = False
        
    def _spin(self):
        if not self.spinning:
            return
            
        self.delete('spinner')
        # Draw arc from current angle to current angle + 240 degrees
        self.create_arc(
            self.width, self.width, 
            self.size - self.width, self.size - self.width,
            start=self.angle, extent=240,
            style='arc', width=self.width, tags='spinner',
            outline=self.color
        )
        self.angle = (self.angle + 10) % 360
        self.after(20, self._spin)

class FileAggregatorApp:
    def __init__(self, root):
        # Created by Sheharyar (Shery) - 2024
        # Portfolio: sheharyar.vercel.live
        # GitHub: github.com/Shery1508
        self.root = root
        self.root.title("File Content-Tree Copier")
        
        # Easter egg: Hidden signature in window geometry (1200x600 -> Shery's magic numbers)
        self.root.geometry("1200x600")
        
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

        # Create a frame for the listbox (file tree) and its controls
        self.listbox_frame = tk.Frame(self.main_frame)
        self.listbox_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Create a sub-frame for filter controls
        self.filter_frame = tk.Frame(self.listbox_frame)
        self.filter_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        # Create extension filter combobox with a label
        tk.Label(self.filter_frame, text="Filter:", font=("Arial", 9)).pack(side=tk.LEFT, padx=(0,5))
        self.extension_var = tk.StringVar(value="All Files")
        self.extension_filter = ttk.Combobox(
            self.filter_frame, 
            textvariable=self.extension_var,
            width=15,
            state="readonly",
            font=("Arial", 9)
        )
        self.extension_filter.pack(side=tk.LEFT)
        
        # Set default values
        self.extension_filter['values'] = ['All Files']
        
        # Bind selection event
        self.extension_filter.bind('<<ComboboxSelected>>', self.apply_extension_filter)

        # Create a listbox to display file structure
        self.listbox = tk.Listbox(self.listbox_frame, height=20, width=40, font=("Courier New", 10))
        self.listbox.pack(side=tk.LEFT, fill=tk.Y)

        # Store original tree items for filtering
        self.original_tree_items = []
        
        # Bind double-click event to the listbox
        self.listbox.bind('<Double-Button-1>', self.on_listbox_double_click)
        
        # Add dictionary to store filename to line number mapping
        self.filename_to_line = {}

        # Scrollbar for the listbox
        self.listbox_scroll = tk.Scrollbar(self.listbox_frame, orient="vertical", command=self.listbox.yview)
        self.listbox_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.configure(yscrollcommand=self.listbox_scroll.set)

        # Create the copy button for the tree structure with adjusted position
        self.copy_tree_button = ttk.Button(self.listbox_frame, text="Copy Tree", command=self.copy_tree_to_clipboard)
        self.copy_tree_button.pack(pady=5)
        self.copy_tree_button.place(relx=0.94, rely=0.059, anchor='ne')  # Adjusted rely from 0.005 to 0.05

        # Create text area frame
        self.text_area_frame = tk.Frame(self.main_frame)
        self.text_area_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create line number canvas with increased width
        self.line_number_canvas = tk.Canvas(self.text_area_frame, width=45, bg='#f0f0f0')  # Increased from 30 to 45
        self.line_number_canvas.pack(side=tk.LEFT, fill=tk.Y)

        # Create text widget with adjusted width
        self.text_area = tk.Text(self.text_area_frame, wrap=tk.WORD, width=80, height=20, 
                                font=("Arial", 10), undo=True, padx=5)  # Added padx=5
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create custom scrollbar frame
        self.custom_scrollbar = CustomScrollbarFrame(self.text_area_frame, self.text_area)
        self.custom_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind events for updating line numbers
        self.text_area.bind('<KeyRelease>', self.update_line_numbers)
        self.text_area.bind('<Button-1>', self.update_line_numbers)
        self.text_area.bind('<Button-4>', self.on_mousewheel)  # Linux
        self.text_area.bind('<Button-5>', self.on_mousewheel)  # Linux
        self.text_area.bind('<MouseWheel>', self.on_mousewheel)  # Windows
        
        # Bind to custom scrollbar's scroll events
        self.custom_scrollbar.scrollbar.bind('<B1-Motion>', lambda e: self.root.after(1, self.update_line_numbers))
        self.custom_scrollbar.scrollbar.bind('<ButtonRelease-1>', lambda e: self.update_line_numbers())
        
        # Bind to text widget's scroll event
        self.text_area.bind('<Configure>', self.update_line_numbers)
        self.text_area.bind('<<Scroll>>', self.update_line_numbers)
        self.text_area.bind('<Enter>', self.update_line_numbers)

        # Adjust copy button position
        self.copy_contents_button = ttk.Button(self.text_area_frame, text="Copy", command=self.copy_to_clipboard)
        self.copy_contents_button.place(relx=0.968, rely=0.007, anchor='ne')  # Adjusted rely from 0.005 to 0.05

        # Create a new button to copy both tree and contents
        self.copy_both_button = ttk.Button(self.control_frame, text="Copy Tree & Contents", command=self.copy_tree_and_contents)
        self.copy_both_button.pack(side=tk.RIGHT, padx=5)

        # Disable the new button by default
        self.update_copy_both_button_state()

        # Add at the start of __init__ with other instance variables
        self.tree_paths = {}

        # Add file type icons mapping
        self.file_icons = {
            # Folders
            'folder': '📁',
            'folder_open': '📂',
            # Code files
            '.py': '🐍',
            '.js': '📜',
            '.html': '🌐',
            '.css': '🎨',
            '.cpp': '⚙️',
            '.c': '⚙️',
            '.h': '📑',
            '.java': '☕',
            '.ts': '📘',
            # Data files
            '.json': '📊',
            '.xml': '📊',
            '.yaml': '📊',
            '.yml': '📊',
            '.csv': '📊',
            # Text files
            '.txt': '📝',
            '.md': '📝',
            '.log': '📋',
            # Config files
            '.ini': '⚙️',
            '.conf': '⚙️',
            '.config': '⚙️',
            # Default
            'default': '📄'
        }

        # Add Export button next to Copy Tree & Contents
        self.export_button = ttk.Button(self.control_frame, text="Export", command=self.show_export_dialog)
        self.export_button.pack(side=tk.RIGHT, padx=5)

        # Add template system
        self.templates = {
            'None': {
                'name': 'No Template',
                'header': '',
                'footer': ''
            },
            'bug_report': {
                'name': 'Bug Report',
                'header': "I found a bug in my application. Here's the relevant code:\n",
                'footer': "\nThe issue I'm seeing is: {bug_description}\nExpected behavior: {expected}\nCurrent behavior: {current}"
            },
            'feature_request': {
                'name': 'Feature Request',
                'header': "I'm working on {project_type} and want to add this feature. Here's my current code:\n",
                'footer': "\nI want to add: {feature_description}\nCan you help implement this while maintaining the current functionality?"
            },
            'code_help': {
                'name': 'Code Help',
                'header': "I'm building {project_type}. Here's my current implementation:\n",
                'footer': "\nWhat I need help with: {help_needed}"
            },
            # Hidden template - Shery's signature with links
            'shery': {
                'name': '✨ Special Template',
                'header': "// Code crafted with ❤️ by Sheharyar (Shery)\n"
                         "// Portfolio: https://sheharyar.vercel.live\n"
                         "// GitHub: https://github.com/Shery1508\n"
                         "// Feel free to use and share!\n\n",
                'footer': "\n\n// Happy coding! - Shery"
            }
        }

        # Load custom templates if exist
        self.templates_file = os.path.join(os.path.dirname(__file__), "templates.json")
        self.load_custom_templates()

        # Add template controls to the control frame
        self.template_frame = ttk.Frame(self.control_frame)
        self.template_frame.pack(side=tk.RIGHT, padx=5)

        ttk.Label(self.template_frame, text="Template:").pack(side=tk.LEFT)
        self.template_var = tk.StringVar(value='None')
        self.template_combo = ttk.Combobox(
            self.template_frame,
            textvariable=self.template_var,
            values=[t['name'] for t in self.templates.values()],
            width=15,
            state='readonly'
        )
        self.template_combo.pack(side=tk.LEFT, padx=5)

        # Add template management button
        self.manage_templates_button = ttk.Button(
            self.template_frame,
            text="Manage Templates",
            command=self.show_template_manager
        )
        self.manage_templates_button.pack(side=tk.LEFT)

        # Replace progress bars with spinners
        self.tree_spinner = LoadingSpinner(self.listbox_frame)
        self.tree_spinner.pack(side=tk.BOTTOM, pady=10)
        self.tree_spinner.pack_forget()  # Hide initially
        
        self.content_spinner = LoadingSpinner(self.text_area_frame)
        self.content_spinner.pack(side=tk.BOTTOM, pady=10)
        self.content_spinner.pack_forget()  # Hide initially

    def select_files(self):
        file_paths = filedialog.askopenfilenames(title="Select Files")
        if file_paths:
            # Show both spinners
            self.tree_spinner.pack(side=tk.BOTTOM, pady=10)
            self.content_spinner.pack(side=tk.BOTTOM, pady=10)
            self.tree_spinner.start()
            self.content_spinner.start()
            
            def process_files():
                try:
                    all_text = self.get_files_text(file_paths)
                    self.display_text(all_text)
                    self.build_listbox(file_paths, show_files=True)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to process files: {str(e)}")
                finally:
                    # Hide both spinners
                    self.root.after(0, lambda: self.tree_spinner.pack_forget())
                    self.root.after(0, lambda: self.content_spinner.pack_forget())
                    self.root.after(0, lambda: self.tree_spinner.stop())
                    self.root.after(0, lambda: self.content_spinner.stop())

            # Run the processing in a separate thread
            import threading
            thread = threading.Thread(target=process_files)
            thread.daemon = True
            thread.start()

    def select_directory(self):
        dir_path = filedialog.askdirectory(title="Select Directory")
        if dir_path:
            # Show tree spinner
            self.tree_spinner.pack(side=tk.BOTTOM, pady=10)
            self.tree_spinner.start()
            
            def process_directory():
                try:
                    # First build the tree (faster operation)
                    self.build_listbox([dir_path], show_files=False)
                    
                    # Hide tree spinner and show content spinner
                    self.root.after(0, lambda: self.tree_spinner.pack_forget())
                    self.root.after(0, lambda: self.content_spinner.pack(side=tk.BOTTOM, pady=10))
                    self.root.after(0, lambda: self.content_spinner.start())
                    
                    # Then load the contents
                    all_text = self.get_files_text_in_directory(dir_path)
                    self.display_text(all_text)
                    
                finally:
                    # Hide both spinners
                    self.root.after(0, lambda: self.tree_spinner.pack_forget())
                    self.root.after(0, lambda: self.content_spinner.pack_forget())
                    self.root.after(0, lambda: self.tree_spinner.stop())
                    self.root.after(0, lambda: self.content_spinner.stop())

            # Run the processing in a separate thread
            import threading
            thread = threading.Thread(target=process_directory)
            thread.daemon = True
            thread.start()

    def get_files_text(self, file_paths):
        all_text = ""
        positions = []
        current_line = 1
        ignored_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.mp4', '.avi', '.mov', '.wmv', '.zip', '.tar', '.gz']
        
        for file_path in file_paths:
            if os.path.exists(file_path) and os.path.isfile(file_path):
                if not any(file_path.endswith(ext) for ext in ignored_extensions):
                    filename = os.path.basename(file_path)
                    if all_text:  # If not the first file
                        all_text += "\n"
                        current_line += 1
                    
                    # Record the position and add file marker
                    positions.append((current_line, filename))
                    all_text += f"⚫ {filename}:\n"  # Add dot marker before filename
                    current_line += 1
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            content = file.read()
                            all_text += content
                            current_line += content.count('\n')
                            if not content.endswith('\n'):
                                all_text += '\n'
                                current_line += 1
                    except (UnicodeDecodeError, IOError):
                        all_text += f"[Could not read file: {filename}]\n"
                        current_line += 1

        # Update the text area and file positions
        self.text_area.delete('1.0', tk.END)
        self.text_area.insert(tk.END, all_text)
        self.filename_to_line = {pos[1]: pos[0] for pos in positions}
        self.filename_to_line.update({os.path.basename(pos[1]): pos[0] for pos in positions})
        self.custom_scrollbar.set_file_positions(positions)
        return all_text

    def get_files_text_in_directory(self, dir_path):
        all_text = ""
        positions = []
        current_line = 1
        ignored_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.mp4', '.avi', '.mov', '.wmv', '.zip', '.tar', '.gz']

        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Skip ignored file types
                if any(file_path.lower().endswith(ext) for ext in ignored_extensions):
                    continue
                
                try:
                    relative_path = os.path.relpath(file_path, dir_path)
                    if all_text:  # If not the first file
                        all_text += "\n"
                        current_line += 1
                    
                    # Record the position and add file marker
                    positions.append((current_line, relative_path))
                    all_text += f"⚫ {relative_path}:\n"  # Add dot marker before filename
                    current_line += 1
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            all_text += content
                            current_line += content.count('\n')
                            if not content.endswith('\n'):
                                all_text += '\n'
                                current_line += 1
                    except UnicodeDecodeError:
                        all_text += f"[Could not read file: Binary or non-text file]\n"
                        current_line += 1
                    except IOError as e:
                        all_text += f"[Could not read file: {str(e)}]\n"
                        current_line += 1
                    except Exception as e:
                        all_text += f"[Error reading file: {str(e)}]\n"
                        current_line += 1
                        
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
                    continue  # Skip this file but continue with others

        # Update the text area and file positions
        self.text_area.delete('1.0', tk.END)
        self.text_area.insert(tk.END, all_text)
        self.filename_to_line = {pos[1]: pos[0] for pos in positions}
        self.filename_to_line.update({os.path.basename(pos[1]): pos[0] for pos in positions})
        self.custom_scrollbar.set_file_positions(positions)
        return all_text

    def display_text(self, text):
        self.text_area.delete('1.0', tk.END)
        
        positions = []
        current_line = 1
        lines = text.split('\n')
        
        # Clear the filename to line mapping
        self.filename_to_line = {}
        
        for i, line in enumerate(lines):
            # Look for the dot marker to identify file headers
            if line.startswith('⚫ ') and line.endswith(':'):
                filename = line[2:].rstrip(':')  # Remove dot and colon
                positions.append((current_line, filename))
                self.filename_to_line[filename] = current_line
                self.filename_to_line[os.path.basename(filename)] = current_line
                
            self.text_area.insert(tk.END, line + '\n')
            current_line += 1
            
        self.custom_scrollbar.set_file_positions(positions)
        self.update_line_numbers()

    def copy_to_clipboard(self):
        content = self.text_area.get("1.0", "end-1c")
        content = self.apply_template(content)
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.copy_contents_button.config(text="Copied!")
        self.root.after(2000, lambda: self.copy_contents_button.config(text="Copy"))

    def _clean_tree_text(self, text):
        """Remove emoji icons and clean up the text for copying"""
        # Remove emoji and extra space after it
        for prefix in ['├── ', '└── ', '│   ', '    ']:
            text = text.replace(prefix, prefix)  # Keep the tree structure markers
        
        # Remove all emojis and the space after them
        for icon in self.file_icons.values():
            text = text.replace(f"{icon} ", "")
        
        return text

    def copy_tree_to_clipboard(self):
        self.root.clipboard_clear()
        tree_text = self.listbox.get(0, tk.END)
        # Clean each line before joining
        cleaned_lines = [self._clean_tree_text(line) for line in tree_text]
        tree_contents = "\n".join(cleaned_lines)
        self.root.clipboard_append(tree_contents)
        self.copy_tree_button.config(text="Copied!", style="Accent.TButton")
        self.root.after(2000, lambda: self.copy_tree_button.config(text="Copy Tree"))

    def copy_tree_and_contents(self):
        # Check if both show tree and show contents are enabled
        if self.show_tree_var.get() and self.show_contents_var.get():
            # Get tree structure and clean it
            tree_text = self.listbox.get(0, tk.END)
            cleaned_tree = "\n".join(self._clean_tree_text(line) for line in tree_text)
            
            # Get file contents
            file_contents = self.text_area.get("1.0", "end-1c")
            
            # Prepare the combined content
            combined_text = f"{cleaned_tree}\n\nAnd here is the file's code in detail:\n\n{file_contents}"
            
            # Apply template to the combined content
            final_content = self.apply_template(combined_text)
            
            # Copy to clipboard
            self.root.clipboard_clear()
            self.root.clipboard_append(final_content)
            self.copy_both_button.config(text="Copied!", style="Accent.TButton")
            self.root.after(2000, lambda: self.copy_both_button.config(text="Copy Tree & Contents"))
        else:
            messagebox.showwarning("Warning", "Please enable both Show Tree and Show Contents to use this feature.")

    def build_listbox(self, paths, show_files=False):
        self.listbox.delete(0, tk.END)
        self.tree_paths.clear()
        self.original_tree_items = []
        extensions = set()
        
        if show_files:
            self.original_tree_items.append(("The File(s):", None))
            self.listbox.insert(tk.END, "The File(s):")
            
        for path in paths:
            if os.path.isfile(path):
                    filename = os.path.basename(path)
                    icon = self._get_file_icon(path)
                    display_text = f"{icon} {filename}"
                    self.original_tree_items.append((display_text, path))
                    self.listbox.insert(tk.END, display_text)
                    self.tree_paths[display_text] = path
                    
                    ext = os.path.splitext(filename)[1].lower()
                    if ext:
                        extensions.add(ext)
        else:
            self.original_tree_items.append(("The Contents", None))
            self.listbox.insert(tk.END, "The Contents")
            
            for path in paths:
                if os.path.isdir(path):
                    self._build_tree(path, "", path, extensions)

        filter_values = ['All Files'] + sorted(list(extensions))
        self.extension_filter['values'] = filter_values
        self.extension_var.set('All Files')

    def _build_tree(self, path, prefix, root_path, extensions=None):
        items = sorted(os.listdir(path))
        for index, item in enumerate(items):
            full_path = os.path.join(path, item)
            is_last = index == len(items) - 1
            display_prefix = '└── ' if is_last else '├── '
            
            icon = self._get_file_icon(full_path)
            display_text = f"{prefix}{display_prefix}{icon} {item}"
            self.original_tree_items.append((display_text, full_path))
            self.listbox.insert(tk.END, display_text)
            
            if os.path.isfile(full_path):
                rel_path = os.path.relpath(full_path, root_path)
                self.tree_paths[display_text] = rel_path
                
                if extensions is not None:
                    ext = os.path.splitext(item)[1].lower()
                    if ext:
                        extensions.add(ext)
            
            if os.path.isdir(full_path):
                next_prefix = prefix + ('    ' if is_last else '│   ')
                self._build_tree(full_path, next_prefix, root_path, extensions)

    def apply_extension_filter(self, event=None):
        selected_filter = self.extension_var.get()
        
        # Clear the listbox
        self.listbox.delete(0, tk.END)
        
        # Reset tree_paths for the filtered items
        self.tree_paths = {}
        
        if selected_filter == 'All Files':
            # Show all items
            for display_text, file_path in self.original_tree_items:
                self.listbox.insert(tk.END, display_text)
                if file_path:  # If it's a file (not a header)
                    self.tree_paths[display_text] = file_path
        else:
            # Show only items with selected extension
            for display_text, file_path in self.original_tree_items:
                if not file_path:  # Headers
                    self.listbox.insert(tk.END, display_text)
                elif os.path.isdir(file_path):  # Directories
                    self.listbox.insert(tk.END, display_text)
                elif file_path.lower().endswith(selected_filter):  # Matching files
                    self.listbox.insert(tk.END, display_text)
                    self.tree_paths[display_text] = file_path

        # Update the text area with filtered content
        filtered_text = ""
        current_line = 1
        positions = []
        
        # Build filtered content based on visible items
        for i in range(self.listbox.size()):
            item = self.listbox.get(i)
            if item in self.tree_paths and os.path.isfile(self.tree_paths[item]):
                file_path = self.tree_paths[item]
                try:
                    if filtered_text:
                        filtered_text += "\n"
                        current_line += 1
                    
                    # Add file header with dot marker
                    positions.append((current_line, file_path))
                    filtered_text += f"⚫ {os.path.basename(file_path)}:\n"
                    current_line += 1
                    
                    # Add file content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        filtered_text += content
                        current_line += content.count('\n')
                        if not content.endswith('\n'):
                            filtered_text += '\n'
                            current_line += 1
                except Exception as e:
                    print(f"Error reading file {file_path}: {str(e)}")
                    filtered_text += f"[Could not read file: {file_path}]\n"
                    current_line += 1

        # Update text area and indicators
        self.text_area.delete('1.0', tk.END)
        self.text_area.insert(tk.END, filtered_text)
        
        # Update filename to line mapping
        self.filename_to_line = {pos[1]: pos[0] for pos in positions}
        self.filename_to_line.update({os.path.basename(pos[1]): pos[0] for pos in positions})
        
        # Update scrollbar indicators
        self.custom_scrollbar.set_file_positions(positions)
        self.update_line_numbers()

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
            "Developed with love using Python's Tkinter library!\n\n"
            "Created by: Sheharyar (Shery) - 2024\n"
            "Portfolio: https://sheharyar.vercel.live\n"
            "GitHub: https://github.com/Shery1508"
        )
        messagebox.showinfo("Info", info_message)

    def on_listbox_double_click(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
            
        selected_text = self.listbox.get(selection[0])
        
        # Skip if it's a directory or header
        if selected_text in ["The File(s):", "The Contents"] or selected_text.endswith('/'):
            return
            
        # Clean up the selected text if it has tree markers and icons
        clean_text = selected_text
        for prefix in ['├── ', '└── ', '│   ', '    ']:
            clean_text = clean_text.replace(prefix, '')
        # Remove the icon
        if ' ' in clean_text:
            clean_text = clean_text.split(' ', 1)[1]
        
        # Get the file path from tree_paths using both original and cleaned text
        file_path = self.tree_paths.get(selected_text) or self.tree_paths.get(clean_text)
        
        if file_path:
            # Try with full path first
            if file_path in self.filename_to_line:
                line_num = self.filename_to_line[file_path]
                self.text_area.see(f"{line_num}.0")
                self.highlight_line(line_num)
                return
                
            # Try with basename
            basename = os.path.basename(file_path)
            if basename in self.filename_to_line:
                line_num = self.filename_to_line[basename]
                self.text_area.see(f"{line_num}.0")
                self.highlight_line(line_num)
                return
            
            # Try with the clean text itself
            if clean_text in self.filename_to_line:
                line_num = self.filename_to_line[clean_text]
                self.text_area.see(f"{line_num}.0")
                self.highlight_line(line_num)

    def highlight_line(self, line_num):
        # Remove any existing highlight
        self.text_area.tag_remove('highlight', '1.0', 'end')
        
        # Add new highlight
        self.text_area.tag_add('highlight', f"{line_num}.0", f"{line_num}.end")
        self.text_area.tag_config('highlight', background='#E3F2FD')  # Light blue highlight
        
        # Remove highlight after a delay
        self.root.after(1000, lambda: self.text_area.tag_remove('highlight', '1.0', 'end'))

    def on_mousewheel(self, event):
        self.update_line_numbers()
        
    def update_line_numbers(self, event=None):
        self.line_number_canvas.delete('all')
        
        # Get the first visible line
        first_visible = self.text_area.index('@0,0')
        last_visible = self.text_area.index(f'@0,{self.text_area.winfo_height()}')
        
        first_line = int(float(first_visible))
        last_line = int(float(last_visible))
        
        # Draw line numbers for visible lines
        for line_num in range(first_line, last_line + 1):
            dline = self.text_area.dlineinfo(f"{line_num}.0")
            if dline is not None:  # if line is visible
                y = dline[1]
                # Adjusted x position and added padding
                self.line_number_canvas.create_text(
                    35, y,  # Adjusted from 25 to 35
                    anchor='ne',
                    text=str(line_num),
                    font=("Arial", 10),
                    fill='#555'
                )

    def _get_file_icon(self, path):
        # Shery's curated icon set 🎨
        if os.path.isdir(path):
            return self.file_icons['folder']
        ext = os.path.splitext(path)[1].lower()
        return self.file_icons.get(ext, self.file_icons['default'])

    def show_export_dialog(self):
        # Create export dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Export Options")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + self.root.winfo_width()//2 - 200,
            self.root.winfo_rooty() + self.root.winfo_height()//2 - 100
        ))

        # Add export options
        options_frame = ttk.LabelFrame(dialog, text="Export Options", padding=10)
        options_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Variables for checkboxes
        export_tree = tk.BooleanVar(value=True)
        export_content = tk.BooleanVar(value=True)

        # Checkboxes
        ttk.Checkbutton(options_frame, text="Include Tree Structure", 
                       variable=export_tree).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Include File Contents", 
                       variable=export_content).pack(anchor=tk.W, pady=2)

        # Filename entry
        filename_frame = ttk.Frame(options_frame)
        filename_frame.pack(fill=tk.X, pady=10)
        ttk.Label(filename_frame, text="Filename:").pack(side=tk.LEFT)
        filename_var = tk.StringVar(value="my_code.txt")
        filename_entry = ttk.Entry(filename_frame, textvariable=filename_var)
        filename_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        # Buttons frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        def export():
            if not (export_tree.get() or export_content.get()):
                messagebox.showwarning("Warning", "Please select at least one option to export.")
                return

            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                initialfile=filename_var.get(),
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if file_path:
                try:
                    content = ""
                    if export_tree.get():
                        # Get and clean tree content
                        tree_text = self.listbox.get(0, tk.END)
                        cleaned_tree = "\n".join(self._clean_tree_text(line) for line in tree_text)
                        content += "=== File Structure ===\n\n"
                        content += cleaned_tree
                        
                        if export_content.get():
                            content += "\n\n"
                    
                    if export_content.get():
                        content += "=== File Contents ===\n\n"
                        content += self.text_area.get("1.0", "end-1c")

                    # Apply template to the full content
                    final_content = self.apply_template(content)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(final_content)
                    
                    messagebox.showinfo("Success", "File exported successfully!")
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to export file: {str(e)}")
                    
        def cancel():
            dialog.destroy()

        # Add Export and Cancel buttons
        ttk.Button(button_frame, text="Export", command=export).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=cancel).pack(side=tk.RIGHT)

    def load_custom_templates(self):
        try:
            if os.path.exists(self.templates_file):
                with open(self.templates_file, 'r') as f:
                    custom_templates = json.load(f)
                self.templates.update(custom_templates)
        except Exception as e:
            print(f"Error loading templates: {e}")

    def save_custom_templates(self):
        try:
            with open(self.templates_file, 'w') as f:
                json.dump(self.templates, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save templates: {e}")

    def show_template_manager(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Template Manager")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + self.root.winfo_width()//2 - 300,
            self.root.winfo_rooty() + self.root.winfo_height()//2 - 200
        ))

        # Template list
        list_frame = ttk.LabelFrame(dialog, text="Templates")
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        template_listbox = tk.Listbox(list_frame, width=25, height=15)
        template_listbox.pack(side=tk.LEFT, fill=tk.Y)
        
        # Populate template list
        for template_id, template in self.templates.items():
            template_listbox.insert(tk.END, template['name'])

        # Template editor
        editor_frame = ttk.LabelFrame(dialog, text="Edit Template")
        editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(editor_frame, text="Name:").pack(anchor=tk.W)
        name_entry = ttk.Entry(editor_frame)
        name_entry.pack(fill=tk.X, padx=5)

        ttk.Label(editor_frame, text="Header:").pack(anchor=tk.W)
        header_text = tk.Text(editor_frame, height=5)
        header_text.pack(fill=tk.X, padx=5)

        ttk.Label(editor_frame, text="Footer:").pack(anchor=tk.W)
        footer_text = tk.Text(editor_frame, height=5)
        footer_text.pack(fill=tk.X, padx=5)

        def load_template(event):
            selection = template_listbox.curselection()
            if not selection:
                return
            
            template_name = template_listbox.get(selection[0])
            template = next((t for t in self.templates.values() if t['name'] == template_name), None)
            if template:
                name_entry.delete(0, tk.END)
                name_entry.insert(0, template['name'])
                header_text.delete('1.0', tk.END)
                header_text.insert('1.0', template['header'])
                footer_text.delete('1.0', tk.END)
                footer_text.insert('1.0', template['footer'])

        template_listbox.bind('<<ListboxSelect>>', load_template)

        def save_template():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Template name is required")
                return

            template_id = name.lower().replace(' ', '_')
            self.templates[template_id] = {
                'name': name,
                'header': header_text.get('1.0', 'end-1c'),
                'footer': footer_text.get('1.0', 'end-1c')
            }
            
            self.save_custom_templates()
            self.template_combo['values'] = [t['name'] for t in self.templates.values()]
            
            # Update listbox
            template_listbox.delete(0, tk.END)
            for template in self.templates.values():
                template_listbox.insert(tk.END, template['name'])
                
            messagebox.showinfo("Success", "Template saved successfully!")

        def new_template():
            name_entry.delete(0, tk.END)
            header_text.delete('1.0', tk.END)
            footer_text.delete('1.0', tk.END)

        # Buttons
        button_frame = ttk.Frame(editor_frame)
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="New", command=new_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save", command=save_template).pack(side=tk.LEFT, padx=5)

    def apply_template(self, content):
        template_name = self.template_var.get()
        if template_name == 'No Template':
            return content

        template = next((t for t in self.templates.values() if t['name'] == template_name), None)
        if not template:
            return content

        # Find variables in template
        import re
        header_vars = re.findall(r'\{(\w+)\}', template['header'])
        footer_vars = re.findall(r'\{(\w+)\}', template['footer'])
        all_vars = list(set(header_vars + footer_vars))

        variables = {}
        # Only show dialog if variables are found
        if all_vars:
            # Show dialog to fill in template variables
            dialog = tk.Toplevel(self.root)
            dialog.title("Template Variables")
            dialog.transient(self.root)
            dialog.grab_set()

            entries = {}

            for var in all_vars:
                frame = ttk.Frame(dialog)
                frame.pack(fill=tk.X, padx=5, pady=2)
                ttk.Label(frame, text=f"{var.replace('_', ' ').title()}:").pack(side=tk.LEFT)
                entry = ttk.Entry(frame)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
                entries[var] = entry

            def apply():
                for var, entry in entries.items():
                    variables[var] = entry.get()
                dialog.destroy()

            ttk.Button(dialog, text="Apply", command=apply).pack(pady=10)
            dialog.wait_window()

        # Apply template
        header = template['header'].format(**variables) if variables else template['header']
        footer = template['footer'].format(**variables) if variables else template['footer']
        
        # Add two newlines after header
        return f"{header}\n\n{content}{footer}"

    # Add a hidden easter egg method
    def _easter_egg(self, event=None):
        # Shery was here 🚀
        # Portfolio: sheharyar.vercel.live
        # GitHub: github.com/Shery1508
        # Maybe someday someone will find this...
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = FileAggregatorApp(root)
    root.mainloop()
