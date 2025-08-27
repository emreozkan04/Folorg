import os
import shutil
from pathlib import Path
import json
import argparse
from datetime import datetime
import utils

def organize_files(directory_path):
    """
    Organizes files in a given directory into subfolders based on file type.
    It also creates a log file to enable safe reversal of changes.
    """
    if not os.path.isdir(directory_path):
        print(f"Error: Directory '{directory_path}' not found.")
        return

    print(f"Starting file organization in '{directory_path}'...")
    

    try:
        file_types = utils.load_config('code\config.json')
    except FileNotFoundError:
        print("Error: config.json not found. Please create one with your sorting rules.")
        return


    log_data = []
    
    try:
        for filename in os.listdir(directory_path):
            original_path = Path(directory_path) / filename
            
            if original_path.is_dir():
                continue

            file_extension = original_path.suffix.lower()

            if file_extension in file_types:
                destination_folder_name = file_types[file_extension]
            else:
                destination_folder_name = 'Others'

            new_path = Path(directory_path) / destination_folder_name / filename
                
            if not new_path.parent.exists():
                os.makedirs(new_path.parent)

            try:
                shutil.move(original_path, new_path)
                log_data.append({
                    "original": str(original_path),
                    "new": str(new_path)
                })
                print(f"Moved '{filename}' to '{destination_folder_name}'")
            except Exception as e:
                print(f"Failed to move '{filename}': {e}")
                continue

        with open(Path(directory_path) / 'undo_log.json', 'w') as f:
            json.dump(log_data, f, indent=4)
        
        print("Files have been organized successfully!")
        print("Organization complete. Undo log created.")

    except Exception as e:
        print(f"An error occurred: {e}")

def date_sort_files(directory_path):
    """
    Organizes files into subfolders based on their creation/modification date.
    It also creates a log file to enable safe reversal of changes.
    """
    if not os.path.isdir(directory_path):
        print(f"Error: Directory '{directory_path}' not found.")
        return

    print(f"Starting date-based sorting in '{directory_path}'...")
    
    log_data = []

    try:
        for filename in os.listdir(directory_path):
            file_path = Path(directory_path) / filename

            if file_path.is_dir():
                continue
            
            timestamp = os.path.getmtime(file_path)
            date = datetime.fromtimestamp(timestamp)
            
            year_folder = date.strftime('%Y')
            month_folder = date.strftime('%B')
            
            destination_path = Path(directory_path) / year_folder / month_folder
            
            if not destination_path.exists():
                os.makedirs(destination_path)
                print(f"Created folder: '{year_folder}/{month_folder}'")
            
            try:
                shutil.move(file_path, destination_path / filename)
                log_data.append({
                    "original": str(file_path),
                    "new": str(destination_path / filename)
                })
                print(f"Moved '{filename}' to '{year_folder}/{month_folder}'")
            except Exception as e:
                print(f"Failed to move '{filename}': {e}")
                continue

        with open(Path(directory_path) / 'date_sort_log.json', 'w') as f:
            json.dump(log_data, f, indent=4)
        
        print("Date-based sorting complete. Undo log created.")

    except Exception as e:
        print(f"An error occurred: {e}")


def reverse_changes(directory_path):
    """
    Reverses file organization by automatically detecting the correct log file.
    It prioritizes the most recent log file if both exist.
    """
    undo_log_path = Path(directory_path) / 'undo_log.json'
    date_sort_log_path = Path(directory_path) / 'date_sort_log.json'

    if date_sort_log_path.exists() and undo_log_path.exists():
        if os.path.getmtime(date_sort_log_path) > os.path.getmtime(undo_log_path):
            print("Multiple logs found. Reverting date-based sorting...")
            utils._reverse_from_log(date_sort_log_path)
        else:
            print("Multiple logs found. Reverting file-type sorting...")
            utils._reverse_from_log(undo_log_path)
    elif date_sort_log_path.exists():
        print("Reverting date-based sorting...")
        utils._reverse_from_log(date_sort_log_path)
    elif undo_log_path.exists():
        print("Reverting file-type sorting...")
        utils._reverse_from_log(undo_log_path)
    else:
        print("No organization logs found in the specified directory.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Organize or unorganize files in a directory.")
    parser.add_argument("PATH", help="The path to the directory you want to organize/unorganize.")
    parser.add_argument("--undo", help="Reverses the most recent file organization.", action="store_true")
    parser.add_argument("--cleanup", help="Finds and deletes duplicate files.", action="store_true")
    parser.add_argument("--date-sort", help="Organize files into folders by year and month.", action="store_true")
    
    args = parser.parse_args()
    target_path = args.PATH

    if args.undo:
        reverse_changes(target_path)
    elif args.cleanup:
        duplicates = utils.find_duplicates(target_path)
        utils._delete_duplicates(duplicates)
    elif args.date_sort:
        date_sort_files(target_path)
    else:
        organize_files(target_path)