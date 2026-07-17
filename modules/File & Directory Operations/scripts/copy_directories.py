#!/usr/bin/env python3
"""
copy_directories.py
----------------------
Recursively copies an entire directory tree to a new location.

Usage:
    python copy_directories.py <source_dir> <destination_dir>

Example:
    python copy_directories.py /home/user/Project /home/user/Project_backup
"""

import argparse
import os
import shutil
import sys


def copy_directory(source: str, destination: str) -> None:
    if not os.path.isdir(source):
        print(f"Error: source '{source}' is not a valid directory.")
        sys.exit(1)

    if os.path.exists(destination):
        print(f"Error: destination '{destination}' already exists.")
        sys.exit(1)

    try:
        shutil.copytree(source, destination)
        print(f"Copied directory: '{source}' -> '{destination}'")
    except (OSError, shutil.Error) as e:
        print(f"Error copying directory: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Recursively copy a directory tree.")
    parser.add_argument("source", help="Source directory")
    parser.add_argument("destination", help="Destination directory (must not already exist)")
    args = parser.parse_args()

    copy_directory(args.source, args.destination)


if __name__ == "__main__":
    main()
