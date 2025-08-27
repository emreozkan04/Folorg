File Organizer
A simple yet powerful tool to help you clean up and organize files in any directory. This project provides both a command-line interface and a sleek graphical user interface (GUI) to manage your files by type, date, or to find and remove duplicates.

Features
File-Type Sorting: Automatically moves files into subfolders based on their extension (e.g., Documents, Images, Videos).

Date-Based Sorting: Organizes files into a Year/Month folder structure based on their creation date.

Duplicate Cleanup: Identifies duplicate files using a fast, two-stage hashing algorithm and provides a GUI for safe deletion.

Getting Started
To get a copy of this project up and running on your local machine, follow these simple steps.

Prerequisites
Python 3.6 or later

----------------
Installation
Clone the repository to your local machine:
Bash

git clone https://github.com/YourUsername/file-organizer-tool.git
cd Folorg
----------------
Run the application:

To launch the GUI, run the app.py file:
Bash
python app.py
----------------

Usage
The tool can be used either through its GUI or via the command line for automation.

GUI Usage
Simply run python app.py and use the interface:

Click "Browse" to select the directory you want to organize.

Choose an action from the buttons provided (By Type, By Date, etc.).

Confirm the action when prompted.

----------------
Command-Line Interface (CLI)
Use the organizer.py script with the following flags. Replace "path/to/your/directory" with the actual path.
----------------

Organize by Type (Default):

Bash

python organizer.py "path/to/your/directory"
Organize by Date:

Bash

python organizer.py "path/to/your/directory" --date-sort
Undo the Last Action:

Bash

python organizer.py "path/to/your/directory" --undo
Find and Clean Up Duplicates:

Bash

python organizer.py "path/to/your/directory" --cleanup-duplicates

Contributing
Contributions are welcome! Feel free to open issues or submit pull requests.

License
This project is licensed under the MIT License.