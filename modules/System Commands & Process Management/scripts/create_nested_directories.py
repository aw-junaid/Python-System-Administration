#!/usr/bin/env python3
"""
create_nested_directories.py
--------------------------------
Creates a nested directory structure (like mkdir -p).

Usage:
    python create_nested_directories.py <path>

Example:
    python create_nested_directories.py projects/2026/january/reports
"""

import argparse
import os
import sys


def create_nested_dirs(path: str) -> None:
    try:
        os.makedirs(path, exist_ok=True)
        print(f"Created nested directory structure: {path}")
    except OSError as e:
        print(f"Error creating directories: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Create nested (multi-level) directories.")
    parser.add_argument("path", help="Full nested directory path to create")
    args = parser.parse_args()

    create_nested_dirs(args.path)


if __name__ == "__main__":
    main()
