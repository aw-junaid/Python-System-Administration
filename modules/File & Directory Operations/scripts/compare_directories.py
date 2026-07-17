#!/usr/bin/env python3
"""
compare_directories.py
----------------------------
Compares two directories and reports files that are only in one, or that differ.

Usage:
    python compare_directories.py <directory1> <directory2>

Example:
    python compare_directories.py /home/user/ProjectA /home/user/ProjectB
"""

import argparse
import filecmp
import os
import sys


def compare_directories(dir1: str, dir2: str) -> None:
    if not os.path.isdir(dir1) or not os.path.isdir(dir2):
        print("Error: both arguments must be valid directories.")
        sys.exit(1)

    comparison = filecmp.dircmp(dir1, dir2)
    _print_report(comparison, dir1, dir2)


def _print_report(comparison: filecmp.dircmp, dir1: str, dir2: str, indent: str = "") -> None:
    if comparison.left_only:
        print(f"{indent}Only in {dir1}:")
        for item in sorted(comparison.left_only):
            print(f"{indent}  {item}")

    if comparison.right_only:
        print(f"{indent}Only in {dir2}:")
        for item in sorted(comparison.right_only):
            print(f"{indent}  {item}")

    if comparison.diff_files:
        print(f"{indent}Files that differ:")
        for item in sorted(comparison.diff_files):
            print(f"{indent}  {item}")

    if comparison.same_files:
        print(f"{indent}Identical files: {len(comparison.same_files)}")

    for sub_dir, sub_comparison in comparison.subdirs.items():
        print(f"{indent}Subdirectory: {sub_dir}")
        _print_report(sub_comparison, os.path.join(dir1, sub_dir), os.path.join(dir2, sub_dir), indent + "  ")


def main():
    parser = argparse.ArgumentParser(description="Compare two directories recursively.")
    parser.add_argument("directory1", help="First directory")
    parser.add_argument("directory2", help="Second directory")
    args = parser.parse_args()

    compare_directories(args.directory1, args.directory2)


if __name__ == "__main__":
    main()
