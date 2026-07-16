#!/usr/bin/env python3
"""
Topic: Accept Input from a Pipe

Reads data piped into the script from another command and processes it
(here: counts lines, words, and characters, similar to `wc`).

Usage:
    echo "hello world" | python input_from_pipe.py
    cat somefile.txt | python input_from_pipe.py

Expected Output:
    Lines: <n>
    Words: <n>
    Characters: <n>

Note:
    If you run the script directly with no piped input, it will wait for
    you to type text manually. Press Ctrl+D (Linux/Mac) or Ctrl+Z then
    Enter (Windows) to signal end of input.
"""

import sys


def main() -> None:
    if sys.stdin.isatty():
        print("No piped input detected. Type text and press Ctrl+D (EOF) when done:")

    data = sys.stdin.read()

    lines = data.splitlines()
    words = data.split()
    chars = len(data)

    print(f"Lines: {len(lines)}")
    print(f"Words: {len(words)}")
    print(f"Characters: {chars}")


if __name__ == "__main__":
    main()
