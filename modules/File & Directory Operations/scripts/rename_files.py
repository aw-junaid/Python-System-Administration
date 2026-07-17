#!/usr/bin/env python3
"""
rename_files.py
-----------------
Renames a single file or folder.

Usage:
    python rename_files.py <old_name> <new_name>

Example:
    python rename_files.py report.txt final_report.txt
"""

import argparse
import os
import sys


def rename_file(old_path: str, new_path: str) -> None:
    if not os.path.exists(old_path):
        print(f"Error: '{old_path}' does not exist.")
        sys.exit(1)

    if os.path.exists(new_path):
        print(f"Error: target '{new_path}' already exists.")
        sys.exit(1)

    try:
        os.rename(old_path, new_path)
        print(f"Renamed: '{old_path}' -> '{new_path}'")
    except OSError as e:
        print(f"Error renaming file: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Rename a file or directory.")
    parser.add_argument("old_name", help="Current name/path")
    parser.add_argument("new_name", help="New name/path")
    args = parser.parse_args()

    rename_file(args.old_name, args.new_name)


if __name__ == "__main__":
    main()
