#!/usr/bin/env python3
"""
copy_files.py
---------------
Copies one or more files into a destination directory.

Usage:
    python copy_files.py <destination_dir> <source1> [source2 ...]

Example:
    python copy_files.py /home/user/Backup report.txt notes.txt
"""

import argparse
import os
import shutil
import sys


def copy_files(sources, destination: str) -> None:
    if not os.path.exists(destination):
        os.makedirs(destination)
        print(f"Created destination directory: {destination}")

    if not os.path.isdir(destination):
        print(f"Error: destination '{destination}' is not a directory.")
        sys.exit(1)

    for src in sources:
        if not os.path.isfile(src):
            print(f"Skipped (not a file or not found): {src}")
            continue

        try:
            shutil.copy2(src, destination)
            print(f"Copied: '{src}' -> '{destination}'")
        except (OSError, shutil.Error) as e:
            print(f"Error copying '{src}': {e}")


def main():
    parser = argparse.ArgumentParser(description="Copy files into a destination directory.")
    parser.add_argument("destination", help="Destination directory")
    parser.add_argument("sources", nargs="+", help="File(s) to copy")
    args = parser.parse_args()

    copy_files(args.sources, args.destination)


if __name__ == "__main__":
    main()
