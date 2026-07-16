#!/usr/bin/env python3
"""
Topic: Accept Input from a File

Reads and prints the contents of a text file given as a command-line argument.
If no file is given, it creates and reads a small sample file so the script
still runs out of the box.

Usage:
    python input_from_file.py [path_to_file]

Expected Output:
    Prints each line of the file, prefixed with its line number.
"""

import sys
import os


def read_file(path: str) -> None:
    if not os.path.isfile(path):
        print(f"Error: file not found -> {path}", file=sys.stderr)
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            print(f"{line_number}: {line.rstrip()}")


def main() -> None:
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # No file given -> create a sample file so the demo works
        file_path = "sample_input.txt"
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("Hello from line one\n")
                f.write("This is line two\n")
                f.write("Python file input demo - line three\n")
        print(f"No file given, using generated sample: {file_path}\n")

    read_file(file_path)


if __name__ == "__main__":
    main()
