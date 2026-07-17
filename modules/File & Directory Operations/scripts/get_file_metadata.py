#!/usr/bin/env python3
"""
get_file_metadata.py
--------------------------
Displays metadata about a file: size, creation/modification time, permissions, etc.

Usage:
    python get_file_metadata.py <file_path>

Example:
    python get_file_metadata.py report.pdf
"""

import argparse
import os
import stat
import sys
from datetime import datetime


def get_file_metadata(path: str) -> None:
    if not os.path.exists(path):
        print(f"Error: '{path}' does not exist.")
        sys.exit(1)

    info = os.stat(path)

    print(f"Metadata for: {path}\n")
    print(f"Size:              {info.st_size} bytes")
    print(f"Created:           {datetime.fromtimestamp(info.st_ctime)}")
    print(f"Last Modified:     {datetime.fromtimestamp(info.st_mtime)}")
    print(f"Last Accessed:     {datetime.fromtimestamp(info.st_atime)}")
    print(f"Permissions:       {stat.filemode(info.st_mode)}")
    print(f"Is Directory:      {os.path.isdir(path)}")
    print(f"Is File:           {os.path.isfile(path)}")
    print(f"Is Symbolic Link:  {os.path.islink(path)}")
    print(f"Absolute Path:     {os.path.abspath(path)}")


def main():
    parser = argparse.ArgumentParser(description="Get metadata for a file or directory.")
    parser.add_argument("path", help="Path to the file or directory")
    args = parser.parse_args()

    get_file_metadata(args.path)


if __name__ == "__main__":
    main()
