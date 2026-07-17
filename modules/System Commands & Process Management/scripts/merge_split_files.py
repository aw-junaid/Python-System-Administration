#!/usr/bin/env python3
"""
merge_split_files.py
--------------------------
Merges files created by split_large_files.py (.part0, .part1, ...) back into the original file.

Usage:
    python merge_split_files.py <original_file_base_name> [--output output_file]

Example:
    python merge_split_files.py bigvideo.mp4
    # Looks for bigvideo.mp4.part0, bigvideo.mp4.part1, etc. in the current directory
    # and reassembles them into bigvideo.mp4 (or the --output path if given).
"""

import argparse
import glob
import os
import re
import sys


def merge_files(base_name: str, output_path: str) -> None:
    pattern = f"{base_name}.part*"
    parts = glob.glob(pattern)

    if not parts:
        print(f"Error: no part files found matching pattern '{pattern}'.")
        sys.exit(1)

    def part_number(path: str) -> int:
        match = re.search(r"\.part(\d+)$", path)
        return int(match.group(1)) if match else -1

    parts.sort(key=part_number)

    print(f"Found {len(parts)} part file(s). Merging in order:")
    for p in parts:
        print(f"  {p}")

    with open(output_path, "wb") as outfile:
        for part in parts:
            with open(part, "rb") as infile:
                outfile.write(infile.read())

    print(f"\nMerged into: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Merge split file parts back into the original file.")
    parser.add_argument("base_name", help="Original file base name (without .partN suffix)")
    parser.add_argument("--output", default=None, help="Output file path (default: same as base_name)")
    args = parser.parse_args()

    output_path = args.output if args.output else args.base_name
    merge_files(args.base_name, output_path)


if __name__ == "__main__":
    main()
