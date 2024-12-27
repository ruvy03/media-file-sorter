import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
from typing import Dict, List
from scanner import FileScanner
from organizer import FileOrganizer
from utils import generate_thumbnail
import threading

class DarkTheme:
    """Dark theme color scheme"""
    BG = "#2b2b2b"
    FG = "#ffffff"
    SELECTED = "#404040"
    BUTTON_BG = "#404040"
    BUTTON_FG = "#ffffff"
    ACCENT = "#5294e2"
    
class FileOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File Organizer")
        self.root.geometry("1800x1000")  # Increased window size
        
        self.scanner = FileScanner()
        self.organizer = FileOrganizer()
        self.current_files: List[Dict] = []
        self.selected_file: Dict = None
        self.output_folders: Dict[str, str] = {}  # name: path
        self.current_thumbnail = None  # Keep reference to prevent garbage collection
        
        self.setup_theme()
        self.setup_gui()
        
    def setup_theme(self):
        """Configure dark theme"""
        style = ttk.Style()
        style.theme_use('default')
        
        # Configure colors
        style.configure('.',
            background=DarkTheme.BG,
            foreground=DarkTheme.FG,
            fieldbackground=DarkTheme.BG)
            
        style.configure('Treeview',
            background=DarkTheme.BG,
            foreground=DarkTheme.FG,
            fieldbackground=DarkTheme.BG)
            
        style.configure('Treeview.Heading',
            background=DarkTheme.BUTTON_BG,
            foreground=DarkTheme.BUTTON_FG)
            
        style.map('Treeview',
            background=[('selected', DarkTheme.SELECTED)],
            foreground=[('selected', DarkTheme.FG)])
            
        # Configure button style
        style.configure('TButton',
            background=DarkTheme.BUTTON_BG,
            foreground=DarkTheme.BUTTON_FG)
            
        # Set window background
        self.root.configure(bg=DarkTheme.BG)
        
    def setup_gui(self):
        # Create main containers
        self.create_toolbar()
        self.create_main_content()
        self.create_status_bar()
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.loading_indicator = ttk.Progressbar(
        self.root,
        mode='indeterminate',
        style='Loading.Horizontal.TProgressbar'
        )
        
    def create_toolbar(self):
        toolbar = ttk.Frame(self.root)
        toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ttk.Button(toolbar, text="Scan Directory", command=self.scan_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Add Output Folder", command=self.add_output_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Undo", command=self.undo_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Redo", command=self.redo_action).pack(side=tk.LEFT, padx=5)
        
        # Search frame
        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side=tk.RIGHT, padx=5)
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_files())
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, padx=5)
        
    def create_main_content(self):
        main_frame = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # File list frame (left side)
        list_frame = ttk.Frame(main_frame)
        self.file_list = ttk.Treeview(list_frame, columns=("Name", "Type", "Size"), show="headings")
        self.file_list.heading("Name", text="Name")
        self.file_list.heading("Type", text="Type")
        self.file_list.heading("Size", text="Size")
        self.file_list.bind('<<TreeviewSelect>>', self.on_file_select)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_list.yview)
        self.file_list.configure(yscrollcommand=scrollbar.set)
        
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        preview_frame = ttk.Frame(main_frame)
        
        # Create preview container with fixed size
        self.preview_container = ttk.Frame(preview_frame)
        self.preview_container.pack(pady=10)
        
        # Create canvas for preview with dark theme background
        self.preview_canvas = tk.Canvas(
            self.preview_container,
            width=800,
            height=600,
            bg=DarkTheme.BG,
            highlightthickness=0
        )
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create preview label
        self.preview_label = ttk.Label(self.preview_canvas)
        
        rename_frame = ttk.Frame(preview_frame)
        rename_frame.pack(pady=5, fill=tk.X, padx=10)
        ttk.Label(rename_frame, text="New name:").pack(side=tk.LEFT)
        self.rename_var = tk.StringVar()
        ttk.Entry(rename_frame, textvariable=self.rename_var).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Metadata area
        metadata_frame = ttk.LabelFrame(preview_frame, text="Metadata")
        metadata_frame.pack(pady=5, fill=tk.X, padx=10)
        self.metadata_text = tk.Text(metadata_frame, height=6, width=40, bg=DarkTheme.BG, fg=DarkTheme.FG)
        self.metadata_text.pack(pady=5, fill=tk.X, padx=5)
        
        # Output folders area
        folders_frame = ttk.LabelFrame(preview_frame, text="Output Folders")
        folders_frame.pack(pady=5, fill=tk.BOTH, padx=10)
        
        # Scrollable frame for folder buttons
        self.folders_canvas = tk.Canvas(folders_frame, bg=DarkTheme.BG, height=150)
        scrollbar = ttk.Scrollbar(folders_frame, orient="vertical", command=self.folders_canvas.yview)
        self.folders_container = ttk.Frame(self.folders_canvas)
        
        self.folders_container.bind(
            "<Configure>",
            lambda e: self.folders_canvas.configure(scrollregion=self.folders_canvas.bbox("all"))
        )
        
        self.folders_canvas.create_window((0, 0), window=self.folders_container, anchor="nw")
        self.folders_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.folders_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        main_frame.add(list_frame, weight=1)
        main_frame.add(preview_frame, weight=3)
        
    def update_preview(self):
        """Update the preview display with the selected file."""
        if not self.selected_file:
            return
            
        file_path = self.selected_file['path']
        container_size = (800, 600)
        
        # Clear existing preview
        self.preview_label.configure(image='')
        self.preview_canvas.delete("all")
        
        thumbnail = generate_thumbnail(file_path, container_size)
        if thumbnail:
            self.current_thumbnail = ImageTk.PhotoImage(thumbnail)
            
            # Create preview label in the center of canvas
            self.preview_canvas.create_image(
                400,  # Half of canvas width
                300,  # Half of canvas height
                image=self.current_thumbnail,
                anchor="center"
            )
        else:
            self.current_thumbnail = None
        
    def create_status_bar(self):
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, sticky="ew")
        self.status_var.set("Ready")
        
    def add_output_folder(self):
        folder_path = filedialog.askdirectory(title="Select Output Folder")
        if folder_path:
            folder_name = os.path.basename(folder_path)
            if not folder_name:  # If root directory was selected
                folder_name = folder_path
            
            self.output_folders[folder_name] = folder_path
            self.update_folder_buttons()
            
    def update_folder_buttons(self):
        # Clear existing buttons
        for widget in self.folders_container.winfo_children():
            widget.destroy()
            
        # Create new buttons for each folder
        for folder_name, folder_path in self.output_folders.items():
            frame = ttk.Frame(self.folders_container)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            btn = ttk.Button(
                frame,
                text=folder_name,
                command=lambda p=folder_path, n=folder_name: self.organize_to_folder(p, n)
            )
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            del_btn = ttk.Button(
                frame,
                text="×",
                command=lambda n=folder_name: self.remove_output_folder(n),
                width=3
            )
            del_btn.pack(side=tk.RIGHT, padx=2)
            
    def remove_output_folder(self, folder_name):
        if folder_name in self.output_folders:
            del self.output_folders[folder_name]
            self.update_folder_buttons()
            
    def organize_to_folder(self, folder_path, folder_name):
        """Organize file to folder and automatically advance to next file."""
        if not self.selected_file:
            messagebox.showwarning("Warning", "Please select a file first")
            return
            
        new_name = self.rename_var.get()
        result = self.organizer.organize_file(
            self.selected_file,
            folder_path,
            new_name
        )
        
        if result['success']:
            self.status_var.set(f"Moved to {folder_name}: {os.path.basename(result['destination'])}")
            
            # Store the current selection before removing it
            selection = self.file_list.selection()
            if selection:
                current_idx = self.file_list.index(selection[0])
                
                # Remove the current item
                self.file_list.delete(selection[0])
                self.current_files.remove(self.selected_file)
                
                # Select the next item if available
                if self.current_files:
                    next_idx = min(current_idx, len(self.current_files) - 1)
                    next_item = self.file_list.get_children()[next_idx]
                    self.file_list.selection_set(next_item)
                    self.file_list.see(next_item)  # Ensure the item is visible
                    self.on_file_select(None)
                else:
                    self.selected_file = None
                    self.update_preview()
                    self.update_metadata()
        else:
            self.status_var.set("Failed to organize file")

            
    def remove_organized_file(self):
        selection = self.file_list.selection()
        if not selection:
            return
            
        current_index = self.file_list.index(selection[0])
        self.file_list.delete(selection[0])
        
        # Select next item
        if current_index < len(self.current_files):
            self.file_list.selection_set(current_index)
            self.on_file_select(None)
        
        # Remove from current_files list
        if self.selected_file in self.current_files:
            self.current_files.remove(self.selected_file)
            
    def scan_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            # Show loading indicator
            self.loading_indicator.grid(row=3, column=0, sticky="ew", padx=5)
            self.loading_indicator.start(10)
            self.root.update()
            
            def scan_thread():
                self.current_files = self.scanner.scan_directory(directory)
                
                # Update UI in main thread
                self.root.after(0, self.finish_scanning)
            
            threading.Thread(target=scan_thread, daemon=True).start()
            
    def finish_scanning(self):
        """Complete the scanning process and update UI."""
        self.update_file_list()
        self.status_var.set(f"Scanned {len(self.current_files)} files")
        self.loading_indicator.stop()
        self.loading_indicator.grid_remove()

            
    def update_file_list(self):
        """Update the file list display with current files."""
        self.file_list.delete(*self.file_list.get_children())
        for file_info in self.current_files:
            metadata = file_info['metadata']
            self.file_list.insert("", "end", values=(
                metadata['name'],
                metadata['type'],
                f"{metadata['size'] / 1024:.1f} KB"
            ))
            
    def on_file_select(self, event):
        """Handle file selection event."""
        selection = self.file_list.selection()
        if not selection:
            return
            
        index = self.file_list.index(selection[0])
        self.selected_file = self.current_files[index]
        self.update_preview()
        self.update_metadata()
        self.rename_var.set(self.selected_file['metadata']['name'])
            
    def update_metadata(self):
        """Update the metadata display for the selected file."""
        if not self.selected_file:
            return
            
        self.metadata_text.delete(1.0, tk.END)
        for key, value in self.selected_file['metadata'].items():
            self.metadata_text.insert(tk.END, f"{key}: {value}\n")
        
        # Disable text editing
        self.metadata_text.configure(state='disabled')
            
    def filter_files(self):
        """Filter files based on search term."""
        search_term = self.search_var.get().lower()
        self.current_files = self.scanner.filter_files(keyword=search_term)
        self.update_file_list()
        
    def undo_action(self):
        """Undo the last file organization action."""
        result = self.organizer.undo_last_action()
        if result:
            self.status_var.set(f"Undid: {result['type']} - {os.path.basename(result['destination'])}")
        else:
            self.status_var.set("Nothing to undo")
            
    def redo_action(self):
        """Redo the last undone file organization action."""
        result = self.organizer.redo_last_action()
        if result:
            self.status_var.set(f"Redid: {result['type']} - {os.path.basename(result['destination'])}")
        else:
            self.status_var.set("Nothing to redo")  