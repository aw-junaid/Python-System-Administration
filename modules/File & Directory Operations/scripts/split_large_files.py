#!/usr/bin/env python3
"""
split_large_files.py
--------------------------
Splits a large file into smaller chunks of a specified size (in MB).
Produces files named <original_name>.part0, .part1, .part2, etc.

Usage:
    python split_large_files.py <file_path> <chunk_size_mb>

Example:
    python split_large_files.py bigvideo.mp4 100
"""

import argparse
import os
import sys


def split_file(file_path: str, chunk_size_mb: float) -> None:
    if not os.path.isfile(file_path):
        print(f"Error: '{file_path}' does not exist.")
        sys.exit(1)

    chunk_size_bytes = int(chunk_size_mb * 1024 * 1024)
    if chunk_size_bytes <= 0:
        print("Error: chunk size must be greater than 0.")
        sys.exit(1)

    part_num = 0
    total_size = os.path.getsize(file_path)

    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size_bytes)
            if not chunk:
                break

            part_path = f"{file_path}.part{part_num}"
            with open(part_path, "wb") as part_file:
                part_file.write(chunk)

            print(f"Created: {part_path} ({len(chunk)} bytes)")
            part_num += 1

    print(f"\nSplit '{file_path}' ({total_size} bytes) into {part_num} part(s).")
    print("Use merge_split_files.py to reassemble them.")


def main():
    parser = argparse.ArgumentParser(description="Split a large file into smaller chunks.")
    parser.add_argument("file_path", help="File to split")
    parser.add_argument("chunk_size_mb", type=float, help="Size of each chunk in megabytes (e.g. 100)")
    args = parser.parse_args()

    split_file(args.file_path, args.chunk_size_mb)


if __name__ == "__main__":
    main()
