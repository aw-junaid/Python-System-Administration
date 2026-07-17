#!/usr/bin/env python3
"""
find_duplicate_files.py
-----------------------------
Finds duplicate files in a directory tree by comparing content hashes (SHA-256).

Usage:
    python find_duplicate_files.py <directory_path>

Example:
    python find_duplicate_files.py /home/user/Downloads
"""

import argparse
import hashlib
import os
import sys
from collections import defaultdict


def hash_file(path: str, block_size: int = 65536) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(block_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def find_duplicates(path: str) -> None:
    if not os.path.isdir(path):
        print(f"Error: '{path}' is not a valid directory.")
        sys.exit(1)

    hashes = defaultdict(list)

    for root, _, files in os.walk(path):
        for f in files:
            full_path = os.path.join(root, f)
            try:
                file_hash = hash_file(full_path)
                hashes[file_hash].append(full_path)
            except (OSError, PermissionError) as e:
                print(f"Skipping '{full_path}': {e}")

    duplicates_found = False
    for file_hash, paths in hashes.items():
        if len(paths) > 1:
            duplicates_found = True
            print(f"\nDuplicate group (hash {file_hash[:12]}...):")
            for p in paths:
                print(f"  {p}")

    if not duplicates_found:
        print("No duplicate files found.")


def main():
    parser = argparse.ArgumentParser(description="Find duplicate files by content hash.")
    parser.add_argument("path", help="Directory to search for duplicates")
    args = parser.parse_args()

    find_duplicates(args.path)


if __name__ == "__main__":
    main()
