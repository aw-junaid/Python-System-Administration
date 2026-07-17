#!/usr/bin/env python3
"""
delete_files.py
-----------------
Deletes one or more files. Asks for confirmation unless --force is used.

Usage:
    python delete_files.py <file1> [file2 ...] [--force]

Example:
    python delete_files.py old.txt
    python delete_files.py a.txt b.txt --force
"""

import argparse
import os
import sys


def delete_files(file_paths, force: bool = False) -> None:
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"Skipped (not found): {file_path}")
            continue

        if not os.path.isfile(file_path):
            print(f"Skipped (not a file): {file_path}")
            continue

        if not force:
            answer = input(f"Delete '{file_path}'? [y/N]: ").strip().lower()
            if answer != "y":
                print(f"Skipped: {file_path}")
                continue

        try:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        except OSError as e:
            print(f"Error deleting '{file_path}': {e}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Delete one or more files.")
    parser.add_argument("files", nargs="+", help="File path(s) to delete")
    parser.add_argument("--force", action="store_true", help="Delete without confirmation prompt")
    args = parser.parse_args()

    delete_files(args.files, args.force)


if __name__ == "__main__":
    main()
