#!/usr/bin/env python3
"""
clean_temporary_files.py
------------------------------
Scans a directory tree and deletes common temporary/junk files
(e.g. .tmp, .bak, .log, __pycache__ folders). Asks for confirmation unless --force is used.

Usage:
    python clean_temporary_files.py <directory_path> [--force]

Example:
    python clean_temporary_files.py /home/user/Project
    python clean_temporary_files.py /home/user/Project --force
"""

import argparse
import os
import shutil
import sys

TEMP_EXTENSIONS = (".tmp", ".bak", ".log", ".cache", ".swp")
TEMP_DIR_NAMES = ("__pycache__", ".pytest_cache", "node_modules_tmp")


def find_temp_items(path: str):
    temp_files = []
    temp_dirs = []

    for root, dirs, files in os.walk(path):
        for d in list(dirs):
            if d in TEMP_DIR_NAMES:
                temp_dirs.append(os.path.join(root, d))
                dirs.remove(d)  # don't descend into it

        for f in files:
            if f.lower().endswith(TEMP_EXTENSIONS):
                temp_files.append(os.path.join(root, f))

    return temp_files, temp_dirs


def clean_temp_files(path: str, force: bool) -> None:
    if not os.path.isdir(path):
        print(f"Error: '{path}' is not a valid directory.")
        sys.exit(1)

    temp_files, temp_dirs = find_temp_items(path)

    if not temp_files and not temp_dirs:
        print("No temporary files or folders found.")
        return

    print("The following will be deleted:\n")
    for f in temp_files:
        print(f"  FILE: {f}")
    for d in temp_dirs:
        print(f"  DIR:  {d}")

    if not force:
        answer = input(f"\nDelete these {len(temp_files) + len(temp_dirs)} item(s)? [y/N]: ").strip().lower()
        if answer != "y":
            print("Aborted.")
            return

    for f in temp_files:
        try:
            os.remove(f)
            print(f"Deleted file: {f}")
        except OSError as e:
            print(f"Error deleting '{f}': {e}")

    for d in temp_dirs:
        try:
            shutil.rmtree(d)
            print(f"Deleted directory: {d}")
        except OSError as e:
            print(f"Error deleting '{d}': {e}")

    print("\nCleanup complete.")


def main():
    parser = argparse.ArgumentParser(description="Clean temporary/junk files from a directory tree.")
    parser.add_argument("path", help="Directory to clean")
    parser.add_argument("--force", action="store_true", help="Delete without confirmation prompt")
    args = parser.parse_args()

    clean_temp_files(args.path, args.force)


if __name__ == "__main__":
    main()
