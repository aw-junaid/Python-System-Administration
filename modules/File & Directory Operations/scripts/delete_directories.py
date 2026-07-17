#!/usr/bin/env python3
"""
delete_directories.py
------------------------
Deletes a directory and all its contents. Asks for confirmation unless --force is used.

Usage:
    python delete_directories.py <directory_path> [--force]

Example:
    python delete_directories.py old_project
    python delete_directories.py old_project --force
"""

import argparse
import os
import shutil
import sys


def delete_directory(path: str, force: bool = False) -> None:
    if not os.path.exists(path):
        print(f"Error: '{path}' does not exist.")
        sys.exit(1)

    if not os.path.isdir(path):
        print(f"Error: '{path}' is not a directory.")
        sys.exit(1)

    if not force:
        answer = input(f"Delete directory '{path}' and ALL its contents? [y/N]: ").strip().lower()
        if answer != "y":
            print("Aborted.")
            return

    try:
        shutil.rmtree(path)
        print(f"Deleted directory: {path}")
    except OSError as e:
        print(f"Error deleting directory: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Delete a directory and all its contents.")
    parser.add_argument("path", help="Directory path to delete")
    parser.add_argument("--force", action="store_true", help="Delete without confirmation prompt")
    args = parser.parse_args()

    delete_directory(args.path, args.force)


if __name__ == "__main__":
    main()
