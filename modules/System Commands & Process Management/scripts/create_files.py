#!/usr/bin/env python3
"""
create_files.py
----------------
Creates one or more new files, optionally with content.

Usage:
    python create_files.py <file1> [file2 ...] [--content "text"]

Example:
    python create_files.py notes.txt
    python create_files.py a.txt b.txt c.txt --content "Hello World"
"""

import argparse
import os
import sys


def create_files(file_paths, content: str = "") -> None:
    for file_path in file_paths:
        try:
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            if os.path.exists(file_path):
                print(f"Skipped (already exists): {file_path}")
                continue

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"Created: {file_path}")
        except OSError as e:
            print(f"Error creating '{file_path}': {e}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Create one or more files.")
    parser.add_argument("files", nargs="+", help="File path(s) to create")
    parser.add_argument("--content", default="", help="Optional text content to write into each file")
    args = parser.parse_args()

    create_files(args.files, args.content)


if __name__ == "__main__":
    main()
