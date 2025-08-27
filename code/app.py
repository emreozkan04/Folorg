import tkinter as tk
from tkinter import filedialog, messagebox
from ttkthemes import ThemedTk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os
import shutil
import json
from datetime import datetime
import utils
from organizer import (
    organize_files, 
    date_sort_files, 
    reverse_changes, 
)

class FileOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Folorg")
        self.root.geometry("600x400")
        
        self.style = ttk.Style(theme="litera")

        self.directory_path = tk.StringVar()

        main_frame = ttk.Frame(root, padding=20)
        main_frame.pack(fill=BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="Folorg", font=("Helvetica", 24, "bold"), anchor="center")
        title_label.pack(pady=(0, 20))

        dir_frame = ttk.Frame(main_frame)
        dir_frame.pack(pady=10, fill=X)

        dir_label = ttk.Label(dir_frame, text="Selected Directory:", font=("Helvetica", 12))
        dir_label.pack(side=LEFT, padx=(0, 10))

        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.directory_path, font=("Helvetica", 10))
        self.dir_entry.pack(side=LEFT, fill=X, expand=True)

        browse_button = ttk.Button(dir_frame, text="Browse", command=self.browse_directory, style="info.TButton")
        browse_button.pack(side=LEFT, padx=(10, 0))

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20, fill=X)

        organize_label = ttk.Label(button_frame, text="Organize Files", font=("Helvetica", 14, "bold"))
        organize_label.grid(row=0, column=0, columnspan=2, pady=(10, 5))

        self.organize_button = ttk.Button(button_frame, text="By Type", command=self.organize_by_type, style="primary.TButton")
        self.organize_button.grid(row=1, column=0, padx=5, pady=5, sticky=EW)

        self.date_sort_button = ttk.Button(button_frame, text="By Date", command=self.organize_by_date, style="primary.TButton")
        self.date_sort_button.grid(row=1, column=1, padx=5, pady=5, sticky=EW)

        utility_label = ttk.Label(button_frame, text="Utilities", font=("Helvetica", 14, "bold"))
        utility_label.grid(row=2, column=0, columnspan=2, pady=(10, 5))

        self.cleanup_button = ttk.Button(button_frame, text="Find Duplicates", command=self.find_duplicates_action, style="warning.TButton")
        self.cleanup_button.grid(row=3, column=0, padx=5, pady=5, sticky=EW)

        self.undo_button = ttk.Button(button_frame, text="Undo", command=self.undo_last_action, style="danger.TButton")
        self.undo_button.grid(row=3, column=1, padx=5, pady=5, sticky=EW)

        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

    def browse_directory(self):
        """Opens a dialog to select a directory and updates the path."""
        selected_dir = filedialog.askdirectory()
        if selected_dir:
            self.directory_path.set(selected_dir)

    def run_organizer(self, action_func, action_name):
        """A generic function to run organizer actions and handle messages."""
        path = self.directory_path.get()
        if not path:
            messagebox.showerror("Error", "Please select a directory first.")
            return

        try:
            action_func(path)
            messagebox.showinfo("Success", f"{action_name} completed successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during {action_name.lower()}: {e}")

    def organize_by_type(self):
        self.run_organizer(organize_files, "File-Type Organization")

    def organize_by_date(self):
        self.run_organizer(date_sort_files, "Date-Based Organization")

    def find_duplicates_action(self):
        """Calls the duplicate finder and opens a new window for cleanup."""
        path = self.directory_path.get()
        if not path:
            messagebox.showerror("Error", "Please select a directory first.")
            return
        
        try:
            duplicates = utils.find_duplicates(path)
            if not duplicates:
                messagebox.showinfo("No Duplicates", "No duplicate files found in the selected directory.")
            else:
                self.show_duplicate_cleanup_window(duplicates)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while finding duplicates: {e}")

    def undo_last_action(self):
        self.run_organizer(reverse_changes, "Undo Action")
    
    def show_duplicate_cleanup_window(self, duplicates):
        cleanup_window = tk.Toplevel(self.root)
        cleanup_window.title("Duplicate Cleanup")
        cleanup_window.geometry("600x400")
        
        frame = ttk.Frame(cleanup_window, padding="10")
        frame.pack(fill=BOTH, expand=True)

        listbox_frame = ttk.Frame(frame)
        listbox_frame.pack(fill=BOTH, expand=True)

        listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, font=("Helvetica", 9))
        listbox.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        listbox.config(yscrollcommand=scrollbar.set)
        
        for file_hash, file_paths in duplicates.items():
            listbox.insert(tk.END, f"--- Duplicates (Hash: {file_hash[:8]}...) ---")
            listbox.itemconfig(tk.END, {'fg': 'blue'})
            for file_path in file_paths:
                listbox.insert(tk.END, f"  {file_path}")
        
        def delete_selected_duplicates():
            selected_indices = listbox.curselection()
            
            if not selected_indices:
                messagebox.showerror("Error", "Please select at least one file to delete.")
                return

            files_to_delete = []
            for index in selected_indices:
                file_path = listbox.get(index).strip()
                if not file_path.startswith('---'):
                    files_to_delete.append(file_path)
            
            if not files_to_delete:
                messagebox.showerror("Error", "No valid files were selected for deletion.")
                return

            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {len(files_to_delete)} selected files? This action is permanent."):
                for file_path in files_to_delete:
                    try:
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")
                    except Exception as e:
                        print(f"Failed to delete {file_path}: {e}")
                
                messagebox.showinfo("Success", "Selected duplicates have been deleted.")
                cleanup_window.destroy()

        delete_button = ttk.Button(frame, text="Delete Selected", command=delete_selected_duplicates, style="danger.TButton")
        delete_button.pack(pady=10)

if __name__ == "__main__":
    root = ThemedTk(theme="litera")
    app = FileOrganizerApp(root)
    root.mainloop()