#!/usr/bin/env python3
"""
create_temporary_files.py
-------------------------------
Creates a temporary file using Python's tempfile module.
By default the file is deleted automatically after the script finishes,
unless --keep is specified.

Usage:
    python create_temporary_files.py [--content "text"] [--keep] [--suffix .txt]

Example:
    python create_temporary_files.py --content "scratch data" --keep
"""

import argparse
import tempfile


def create_temp_file(content: str, keep: bool, suffix: str) -> None:
    if keep:
        fd, path = tempfile.mkstemp(suffix=suffix)
        with open(fd, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Temporary file created and KEPT at: {path}")
    else:
        with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=True, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            print(f"Temporary file created at: {f.name}")
            print("This file will be deleted automatically when the script exits.")


def main():
    parser = argparse.ArgumentParser(description="Create a temporary file.")
    parser.add_argument("--content", default="", help="Content to write into the temp file")
    parser.add_argument("--keep", action="store_true", help="Keep the file after the script exits")
    parser.add_argument("--suffix", default=".tmp", help="File suffix/extension (default: .tmp)")
    args = parser.parse_args()

    create_temp_file(args.content, args.keep, args.suffix)


if __name__ == "__main__":
    main()
