import hashlib
import json
import os
from pathlib import Path
import shutil

def load_config(config_path):
    """Loads a configuration file and returns the file types dictionary."""
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Invert the dictionary for easier lookups
    inverted_config = {}
    for folder, extensions in config.items():
        for ext in extensions:
            inverted_config[ext] = folder
    return inverted_config
def find_duplicates(directory_path):
    """
    Scans a directory for duplicate files using a two-stage approach.
    First, it groups files by size. Second, it performs a SHA-1 hash on same-sized files.
    Returns a dictionary of hashes and a list of paths for each duplicate.
    """
    if not os.path.isdir(directory_path):
        print(f"Error: Directory '{directory_path}' not found.")
        return {}

    # Stage 1: Group files by size
    size_groups = {}
    for dirpath, _, filenames in os.walk(directory_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if not os.path.isfile(file_path):
                continue
            
            file_size = os.path.getsize(file_path)
            if file_size not in size_groups:
                size_groups[file_size] = []
            size_groups[file_size].append(file_path)
            
    # Filter out sizes with only one file, as they can't have duplicates
    potential_duplicates = {size: paths for size, paths in size_groups.items() if len(paths) > 1}

    # Stage 2: Hash files in groups of the same size
    duplicates = {}
    for file_list in potential_duplicates.values():
        for file_path in file_list:
            hash_obj = hashlib.sha1()
            try:
                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(4096)
                        if not chunk:
                            break
                        hash_obj.update(chunk)
                
                file_hash = hash_obj.hexdigest()
                
                if file_hash in duplicates:
                    duplicates[file_hash].append(file_path)
                else:
                    duplicates[file_hash] = [file_path]
            except IOError:
                # Skip files that can't be opened (e.g., in use)
                continue
                
    # Filter out files that don't have duplicates
    return {k: v for k, v in duplicates.items() if len(v) > 1}

def _reverse_from_log(log_path):
    """
    A private helper function to reverse changes from a given log file.
    This version correctly handles nested directory deletion for date-based logs.
    """
    is_date_sort_log = "date_sort_log" in str(log_path)
    
    try:
        with open(log_path, 'r') as f:
            log_data = json.load(f)

        for entry in reversed(log_data):
            new_path = Path(entry['new'])
            original_path = Path(entry['original'])
            
            if new_path.exists():
                try:
                    shutil.move(new_path, original_path)
                    print(f"Moved '{new_path.name}' back to '{original_path.parent}'.")
                except Exception as e:
                    print(f"Failed to move '{new_path.name}': {e}")
                    continue

        for entry in log_data:
            current_dir_to_delete = Path(entry['new']).parent
            
            if current_dir_to_delete.exists() and not os.listdir(current_dir_to_delete):
                os.rmdir(current_dir_to_delete)
                print(f"Removed empty directory: '{current_dir_to_delete.name}'")
            
            if is_date_sort_log:
                year_dir = current_dir_to_delete.parent
                if year_dir.exists() and not os.listdir(year_dir):
                    os.rmdir(year_dir)
                    print(f"Removed empty directory: '{year_dir.name}'")
        
        os.remove(log_path)
        print(f"Reversal complete. Log '{log_path.name}' deleted.")
        return True
    except Exception as e:
        print(f"An error occurred during reversal: {e}")
        return False

def _delete_duplicates(duplicates):
    """
    Prompts the user to select and delete duplicate files.
    """
    if not duplicates:
        print("No duplicate files to clean up.")
        return

    print("\n--- Duplicate File Cleanup ---")
    deleted_files = []
    
    for file_hash, file_list in duplicates.items():
        print(f"\nHash: {file_hash}")
        print("The following files are duplicates:")
        
        for i, file_path in enumerate(file_list):
            print(f"  [{i+1}] {file_path}")
            
        try:
            choice = input("Enter the number of the file(s) to keep (e.g., '1' or '1,3'), or 'all' to delete all duplicates, or press Enter to skip: ").strip()
            
            if choice.lower() == 'all':
                files_to_delete = file_list
                files_to_keep = []
            elif choice:
                choices_to_keep = {int(c) - 1 for c in choice.split(',') if c.strip().isdigit()}
                files_to_delete = [f for i, f in enumerate(file_list) if i not in choices_to_keep]
                files_to_keep = [f for i, f in enumerate(file_list) if i in choices_to_keep]
            else:
                files_to_delete = []
                files_to_keep = file_list
            
            # Delete the selected files
            for file_to_delete in files_to_delete:
                if Path(file_to_delete).exists():
                    try:
                        os.remove(file_to_delete)
                        print(f"  Deleted: {file_to_delete}")
                        deleted_files.append({"deleted_path": file_to_delete})
                    except Exception as e:
                        print(f"  Failed to delete {file_to_delete}: {e}")
                else:
                    print(f"  Skipping: File not found at {file_to_delete}")
            
            if not files_to_keep and files_to_delete:
                print("Warning: All copies of this file were deleted.")
            
        except ValueError:
            print("Invalid input. Skipping this group of duplicates.")
            continue
            
    # Optionally log the deletions
    if deleted_files:
        log_path = Path(file_list[0]).parent / 'deleted_duplicates_log.json'
        with open(log_path, 'w') as f:
            json.dump(deleted_files, f, indent=4)
        print(f"\nDeletion log saved to '{log_path}'.")
    
    print("\nCleanup complete.")