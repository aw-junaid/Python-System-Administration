#!/usr/bin/env python3
"""
find_files_by_extension.py
-------------------------------
Searches a directory tree for files matching a given extension.

Usage:
    python find_files_by_extension.py <directory_path> <extension>

Example:
    python find_files_by_extension.py /home/user/Documents .pdf
"""

import argparse
import os
import sys


def find_files_by_extension(path: str, extension: str) -> None:
    if not os.path.isdir(path):
        print(f"Error: '{path}' is not a valid directory.")
        sys.exit(1)

    if not extension.startswith("."):
        extension = "." + extension

    matches = []

    for root, _, files in os.walk(path):
        for f in files:
            if f.lower().endswith(extension.lower()):
                matches.append(os.path.join(root, f))

    if matches:
        print(f"Found {len(matches)} file(s) with extension '{extension}':\n")
        for m in matches:
            print(m)
    else:
        print(f"No files with extension '{extension}' found in '{path}'.")


def main():
    parser = argparse.ArgumentParser(description="Find files by extension in a directory tree.")
    parser.add_argument("path", help="Directory to search")
    parser.add_argument("extension", help="File extension to search for (e.g. .txt or txt)")
    args = parser.parse_args()

    find_files_by_extension(args.path, args.extension)


if __name__ == "__main__":
    main()
