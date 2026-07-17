#!/usr/bin/env python3
"""
list_directory.py
------------------
Lists the contents of a directory (files and subdirectories).

Usage:
    python list_directory.py <directory_path> [--long]

Example:
    python list_directory.py .
    python list_directory.py /home/user/Documents --long
"""

import argparse
import os
import sys
from datetime import datetime


def list_directory(path: str, long_format: bool = False) -> None:
    if not os.path.exists(path):
        print(f"Error: Path '{path}' does not exist.")
        sys.exit(1)

    if not os.path.isdir(path):
        print(f"Error: '{path}' is not a directory.")
        sys.exit(1)

    entries = sorted(os.listdir(path))

    if not entries:
        print(f"Directory '{path}' is empty.")
        return

    print(f"Contents of '{path}':\n")

    for entry in entries:
        full_path = os.path.join(path, entry)
        entry_type = "DIR " if os.path.isdir(full_path) else "FILE"

        if long_format:
            size = os.path.getsize(full_path)
            mtime = datetime.fromtimestamp(os.path.getmtime(full_path))
            print(f"[{entry_type}] {entry:<40} {size:>10} bytes  {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"[{entry_type}] {entry}")

    print(f"\nTotal items: {len(entries)}")


def main():
    parser = argparse.ArgumentParser(description="List contents of a directory.")
    parser.add_argument("path", help="Path to the directory to list")
    parser.add_argument("--long", action="store_true", help="Show detailed info (size, modified time)")
    args = parser.parse_args()

    list_directory(args.path, args.long)


if __name__ == "__main__":
    main()
