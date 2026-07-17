#!/usr/bin/env python3
"""
traverse_directories.py
---------------------------
Recursively walks through a directory tree and prints every file and folder.

Usage:
    python traverse_directories.py <directory_path>

Example:
    python traverse_directories.py /home/user/Documents
"""

import argparse
import os
import sys


def traverse_directory(path: str) -> None:
    if not os.path.isdir(path):
        print(f"Error: '{path}' is not a valid directory.")
        sys.exit(1)

    file_count = 0
    dir_count = 0

    for root, dirs, files in os.walk(path):
        level = root.replace(path, "").count(os.sep)
        indent = "  " * level
        print(f"{indent}[DIR] {os.path.basename(root) or root}")

        sub_indent = "  " * (level + 1)
        for f in files:
            print(f"{sub_indent}{f}")
            file_count += 1
        dir_count += len(dirs)

    print(f"\nTotal directories: {dir_count + 1}")
    print(f"Total files: {file_count}")


def main():
    parser = argparse.ArgumentParser(description="Recursively traverse a directory tree.")
    parser.add_argument("path", help="Directory to traverse")
    args = parser.parse_args()

    traverse_directory(args.path)


if __name__ == "__main__":
    main()
