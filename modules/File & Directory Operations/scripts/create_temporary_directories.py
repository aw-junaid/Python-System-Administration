#!/usr/bin/env python3
"""
create_temporary_directories.py
-------------------------------------
Creates a temporary directory using Python's tempfile module.
By default it is deleted automatically after the script finishes,
unless --keep is specified.

Usage:
    python create_temporary_directories.py [--keep]

Example:
    python create_temporary_directories.py --keep
"""

import argparse
import shutil
import tempfile


def create_temp_dir(keep: bool) -> None:
    if keep:
        path = tempfile.mkdtemp()
        print(f"Temporary directory created and KEPT at: {path}")
    else:
        with tempfile.TemporaryDirectory() as path:
            print(f"Temporary directory created at: {path}")
            print("This directory will be deleted automatically when the script exits.")


def main():
    parser = argparse.ArgumentParser(description="Create a temporary directory.")
    parser.add_argument("--keep", action="store_true", help="Keep the directory after the script exits")
    args = parser.parse_args()

    create_temp_dir(args.keep)


if __name__ == "__main__":
    main()
