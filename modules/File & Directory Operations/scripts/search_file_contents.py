#!/usr/bin/env python3
"""
search_file_contents.py
-----------------------------
Searches for a text string inside all files in a directory tree (like grep -r).

Usage:
    python search_file_contents.py <directory_path> <search_text> [--extension .txt]

Example:
    python search_file_contents.py /home/user/Project "TODO"
    python search_file_contents.py /home/user/Project "import os" --extension .py
"""

import argparse
import os
import sys


def search_file_contents(path: str, search_text: str, extension: str = None) -> None:
    if not os.path.isdir(path):
        print(f"Error: '{path}' is not a valid directory.")
        sys.exit(1)

    matches_found = 0

    for root, _, files in os.walk(path):
        for f in files:
            if extension and not f.lower().endswith(extension.lower()):
                continue

            full_path = os.path.join(root, f)
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as file_obj:
                    for line_num, line in enumerate(file_obj, start=1):
                        if search_text in line:
                            print(f"{full_path}:{line_num}: {line.strip()}")
                            matches_found += 1
            except (OSError, PermissionError):
                continue

    if matches_found == 0:
        print(f"No matches found for '{search_text}' in '{path}'.")
    else:
        print(f"\nTotal matches: {matches_found}")


def main():
    parser = argparse.ArgumentParser(description="Search for text inside all files in a directory tree.")
    parser.add_argument("path", help="Directory to search")
    parser.add_argument("search_text", help="Text string to search for")
    parser.add_argument("--extension", default=None, help="Only search files with this extension (e.g. .py)")
    args = parser.parse_args()

    search_file_contents(args.path, args.search_text, args.extension)


if __name__ == "__main__":
    main()
