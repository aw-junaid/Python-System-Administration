#!/usr/bin/env python3
"""
extract_zip_archives.py
-----------------------------
Extracts the contents of a ZIP archive to a destination directory.

Usage:
    python extract_zip_archives.py <zip_file> [destination_dir]

Example:
    python extract_zip_archives.py backup.zip
    python extract_zip_archives.py backup.zip ./extracted
"""

import argparse
import os
import sys
import zipfile


def extract_zip(zip_path: str, destination: str) -> None:
    if not os.path.isfile(zip_path):
        print(f"Error: '{zip_path}' does not exist.")
        sys.exit(1)

    if not zipfile.is_zipfile(zip_path):
        print(f"Error: '{zip_path}' is not a valid ZIP file.")
        sys.exit(1)

    os.makedirs(destination, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(destination)
            file_count = len(zf.namelist())

        print(f"Extracted {file_count} item(s) from '{zip_path}' to '{destination}'")
    except (OSError, zipfile.BadZipFile) as e:
        print(f"Error extracting archive: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Extract a ZIP archive.")
    parser.add_argument("zip_file", help="ZIP file to extract")
    parser.add_argument("destination", nargs="?", default=".", help="Destination directory (default: current directory)")
    args = parser.parse_args()

    extract_zip(args.zip_file, args.destination)


if __name__ == "__main__":
    main()
