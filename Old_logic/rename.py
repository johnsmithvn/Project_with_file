import os
import ctypes
from ctypes import wintypes
from functools import cmp_to_key
from tkinter import Tk
from tkinter.filedialog import askdirectory

# Load the Windows API function StrCmpLogicalW
shlwapi = ctypes.WinDLL("Shlwapi")
StrCmpLogicalW = shlwapi.StrCmpLogicalW
StrCmpLogicalW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
StrCmpLogicalW.restype = wintypes.INT


def windows_explorer_compare(a, b):
    """
    Comparison function using Windows API StrCmpLogicalW.
    """
    return StrCmpLogicalW(a, b)


def rename_files_in_folder(directory):
    """
    Traverse all subfolders, sort files like Windows Explorer, and prepend sequential numbers.
    Only processes image files (jpg, png, jpeg, gif, webp).
    """
    try:
        # List all files and folders in the directory
        entries = os.listdir(directory)

        # Separate files and folders
        image_extensions = (".jpg", ".png", ".jpeg", ".gif", ".webp")
        files = [
            f
            for f in entries
            if os.path.isfile(os.path.join(directory, f))
            and f.lower().endswith(image_extensions)
        ]
        folders = [f for f in entries if os.path.isdir(os.path.join(directory, f))]

        # Sort files using Windows Explorer's logic
        sorted_files = sorted(files, key=cmp_to_key(windows_explorer_compare))

        # Reset counter for each folder
        counter = 1
        ######################
        # Rename files with original name prepended
        # This will prepend the original name to the new name.
        # # Rename files
        ######################
        # for file in sorted_files:
        #     old_path = os.path.join(directory, file)
        #     new_name = f"{counter:03d} {file}"  # Prepend sequential number
        #     new_path = os.path.join(directory, new_name)
        #     os.rename(old_path, new_path)
        #     print(f"Renamed: {old_path} -> {new_path}")
        #     counter += 1

        # # Recursively process subfolders
        # for folder in folders:
        #     rename_files_in_folder(os.path.join(directory, folder))


        ############
        # Rename files without prepending the original name
        # This will only use the counter and the file extension
        # and will not include the original name in the new name.
        ############
        for file in sorted_files:
            old_path = os.path.join(directory, file)
            # Generate a new name using only the counter and the file extension
            file_extension = os.path.splitext(file)[1]  # Get the file extension
            new_name = (
                f"{counter:03d}{file_extension}"  # Use only the counter and extension
            )
            new_path = os.path.join(directory, new_name)
            os.rename(old_path, new_path)
            # print(f"Renamed: {old_path} -> {new_path}")
            counter += 1

        # Recursively process subfolders
        for folder in folders:
            rename_files_in_folder(os.path.join(directory, folder))

    except Exception as e:
        print(f"Error: {e}")


def main():
    # Show dialog to choose folder
    Tk().withdraw()  # Hide the root Tkinter window
    folder_path = askdirectory(title="Select Folder to Rename Files")
    if not folder_path:
        print("No folder selected. Exiting.")
        return

    # Start renaming files
    print(f"Processing folder: {folder_path}")
    rename_files_in_folder(folder_path)
    print("Renaming completed.")


if __name__ == "__main__":
    main()
