#!/usr/bin/env python3
"""
compare_two_files.py
--------------------------
Compares two files and reports whether they are identical, plus a line-by-line diff for text files.

Usage:
    python compare_two_files.py <file1> <file2>

Example:
    python compare_two_files.py old_version.txt new_version.txt
"""

import argparse
import difflib
import filecmp
import os
import sys


def compare_files(file1: str, file2: str) -> None:
    for f in (file1, file2):
        if not os.path.isfile(f):
            print(f"Error: '{f}' does not exist or is not a file.")
            sys.exit(1)

    identical = filecmp.cmp(file1, file2, shallow=False)

    if identical:
        print(f"Files are IDENTICAL: '{file1}' == '{file2}'")
        return

    print(f"Files DIFFER: '{file1}' != '{file2}'\n")

    try:
        with open(file1, "r", encoding="utf-8", errors="ignore") as f1, \
             open(file2, "r", encoding="utf-8", errors="ignore") as f2:
            lines1 = f1.readlines()
            lines2 = f2.readlines()

        diff = difflib.unified_diff(lines1, lines2, fromfile=file1, tofile=file2, lineterm="")
        diff_output = list(diff)

        if diff_output:
            print("Line-by-line diff:")
            for line in diff_output:
                print(line)
        else:
            print("Binary or non-text files: content differs but no text diff available.")
    except UnicodeDecodeError:
        print("Could not generate text diff (binary file detected).")


def main():
    parser = argparse.ArgumentParser(description="Compare two files and show differences.")
    parser.add_argument("file1", help="First file")
    parser.add_argument("file2", help="Second file")
    args = parser.parse_args()

    compare_files(args.file1, args.file2)


if __name__ == "__main__":
    main()
