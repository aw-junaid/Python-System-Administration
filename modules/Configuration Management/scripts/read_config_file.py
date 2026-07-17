#!/usr/bin/env python3
"""
read_config_file.py

Purpose:
    Read a plain configuration/text file from disk and print its raw
    contents with line numbers. This is a generic, format-agnostic
    starting point before you parse a specific format (INI/JSON/YAML/
    TOML/XML) with the other scripts in this folder.

Usage:
    python3 read_config_file.py <path_to_file>

    If no path is given, this script creates and reads a small demo
    config file (demo_config.txt) in the current directory.

Expected Output:
    Reading file: demo_config.txt
    ------------------------------
      1: # Demo configuration file
      2: debug = true
      3: max_connections = 100
    ------------------------------
    Total lines: 3

Caution:
    - This script only reads files; it never modifies them.
    - Large files are read fully into memory; for very large log-like
      config files, consider reading in chunks instead.
    - If the file uses a non-UTF-8 encoding, decoding may fail. This
      script uses UTF-8 with errors="replace" to avoid crashing, but
      unusual characters may display as replacement symbols.
"""

import os
import sys

DEMO_FILE = "demo_config.txt"
DEMO_CONTENT = (
    "# Demo configuration file\n"
    "debug = true\n"
    "max_connections = 100\n"
)


def read_config(path: str) -> None:
    if not os.path.isfile(path):
        print(f"Error: file not found: {path}")
        return

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    print(f"Reading file: {path}")
    print("-" * 30)
    for i, line in enumerate(lines, start=1):
        print(f"{i:3}: {line.rstrip()}")
    print("-" * 30)
    print(f"Total lines: {len(lines)}")


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        print("No file path given, creating and reading a demo config file.\n")
        if not os.path.isfile(DEMO_FILE):
            with open(DEMO_FILE, "w", encoding="utf-8") as f:
                f.write(DEMO_CONTENT)
        path = DEMO_FILE
    read_config(path)


if __name__ == "__main__":
    main()
