#!/usr/bin/env python3
"""
move_files.py
---------------
Moves one or more files/folders into a destination directory.

Usage:
    python move_files.py <destination_dir> <source1> [source2 ...]

Example:
    python move_files.py /home/user/Archive report.txt notes.txt
"""

import argparse
import os
import shutil
import sys


def move_files(sources, destination: str) -> None:
    if not os.path.exists(destination):
        os.makedirs(destination)
        print(f"Created destination directory: {destination}")

    if not os.path.isdir(destination):
        print(f"Error: destination '{destination}' is not a directory.")
        sys.exit(1)

    for src in sources:
        if not os.path.exists(src):
            print(f"Skipped (not found): {src}")
            continue

        try:
            shutil.move(src, destination)
            print(f"Moved: '{src}' -> '{destination}'")
        except (OSError, shutil.Error) as e:
            print(f"Error moving '{src}': {e}")


def main():
    parser = argparse.ArgumentParser(description="Move files/folders into a destination directory.")
    parser.add_argument("destination", help="Destination directory")
    parser.add_argument("sources", nargs="+", help="File(s)/folder(s) to move")
    args = parser.parse_args()

    move_files(args.sources, args.destination)


if __name__ == "__main__":
    main()
