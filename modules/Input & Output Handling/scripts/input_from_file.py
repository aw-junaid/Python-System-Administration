#!/usr/bin/env python3
"""
Accept Input from a File
-------------------------
Reads the contents of a file passed as a command-line argument and
prints some basic stats about it (line count, word count, char count).

Usage:
    python 01_input_from_file.py path/to/file.txt
"""
import sys
from pathlib import Path


def read_file(path: str) -> str:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"No such file: {path}")
    return file_path.read_text(encoding="utf-8")


def main():
    if len(sys.argv) != 2:
        print("Usage: python 01_input_from_file.py <path>", file=sys.stderr)
        sys.exit(1)

    content = read_file(sys.argv[1])
    lines = content.splitlines()
    words = content.split()

    print(f"File: {sys.argv[1]}")
    print(f"Lines: {len(lines)}")
    print(f"Words: {len(words)}")
    print(f"Characters: {len(content)}")


if __name__ == "__main__":
    main()
