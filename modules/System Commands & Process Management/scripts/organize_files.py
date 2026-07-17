#!/usr/bin/env python3
"""
organize_files.py
------------------------
Automatically organizes files in a directory into subfolders based on file extension/type
(e.g. Images, Documents, Videos, Music, Archives, Others).

Usage:
    python organize_files.py <directory_path>

Example:
    python organize_files.py /home/user/Downloads
"""

import argparse
import os
import shutil
import sys

CATEGORY_MAP = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".odt", ".rtf", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
    "Music": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
    "Archives": [".zip", ".rar", ".tar", ".gz", ".7z", ".bz2"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".sh", ".json", ".xml"],
}


def get_category(extension: str) -> str:
    for category, extensions in CATEGORY_MAP.items():
        if extension.lower() in extensions:
            return category
    return "Others"


def organize_files(path: str) -> None:
    if not os.path.isdir(path):
        print(f"Error: '{path}' is not a valid directory.")
        sys.exit(1)

    moved_count = 0

    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)

        if not os.path.isfile(full_path):
            continue

        extension = os.path.splitext(entry)[1]
        category = get_category(extension)
        category_dir = os.path.join(path, category)

        os.makedirs(category_dir, exist_ok=True)

        destination = os.path.join(category_dir, entry)
        try:
            shutil.move(full_path, destination)
            print(f"Moved: {entry} -> {category}/")
            moved_count += 1
        except (OSError, shutil.Error) as e:
            print(f"Error moving '{entry}': {e}")

    print(f"\nOrganized {moved_count} file(s) in '{path}'.")


def main():
    parser = argparse.ArgumentParser(description="Automatically organize files into category subfolders.")
    parser.add_argument("path", help="Directory to organize")
    args = parser.parse_args()

    organize_files(args.path)


if __name__ == "__main__":
    main()
