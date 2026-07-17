#!/usr/bin/env python3
"""
batch_rename_files.py
---------------------------
Batch renames all files in a directory using a prefix and sequential numbering.

Usage:
    python batch_rename_files.py <directory_path> <prefix> [--start 1] [--extension .jpg]

Example:
    python batch_rename_files.py /home/user/Photos vacation_
    # vacation_001.jpg, vacation_002.jpg, ...

    python batch_rename_files.py /home/user/Photos photo_ --start 100 --extension .png
"""

import argparse
import os
import sys


def batch_rename(path: str, prefix: str, start: int, extension_filter: str = None) -> None:
    if not os.path.isdir(path):
        print(f"Error: '{path}' is not a valid directory.")
        sys.exit(1)

    files = sorted(os.listdir(path))

    if extension_filter:
        if not extension_filter.startswith("."):
            extension_filter = "." + extension_filter
        files = [f for f in files if f.lower().endswith(extension_filter.lower())]

    files = [f for f in files if os.path.isfile(os.path.join(path, f))]

    if not files:
        print("No matching files found to rename.")
        return

    counter = start
    renamed = 0

    for f in files:
        ext = os.path.splitext(f)[1]
        new_name = f"{prefix}{counter:03d}{ext}"
        old_path = os.path.join(path, f)
        new_path = os.path.join(path, new_name)

        if os.path.exists(new_path):
            print(f"Skipped (target exists): {new_name}")
            continue

        try:
            os.rename(old_path, new_path)
            print(f"Renamed: {f} -> {new_name}")
            renamed += 1
            counter += 1
        except OSError as e:
            print(f"Error renaming '{f}': {e}")

    print(f"\nRenamed {renamed} file(s).")


def main():
    parser = argparse.ArgumentParser(description="Batch rename files with a prefix and sequential numbers.")
    parser.add_argument("path", help="Directory containing files to rename")
    parser.add_argument("prefix", help="Prefix for new filenames")
    parser.add_argument("--start", type=int, default=1, help="Starting number (default: 1)")
    parser.add_argument("--extension", default=None, help="Only rename files with this extension (e.g. .jpg)")
    args = parser.parse_args()

    batch_rename(args.path, args.prefix, args.start, args.extension)


if __name__ == "__main__":
    main()
