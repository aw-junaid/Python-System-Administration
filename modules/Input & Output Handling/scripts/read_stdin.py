#!/usr/bin/env python3
"""
Topic: Read from Standard Input (stdin)

Reads a single line of input from standard input using input() and echoes
it back, converted to uppercase.

Usage:
    python read_stdin.py
    echo "hello" | python read_stdin.py

Expected Output:
    Prompts for a line of text (unless piped), then prints it in uppercase.
"""

import sys


def main() -> None:
    try:
        if sys.stdin.isatty():
            line = input("Enter some text: ")
        else:
            line = sys.stdin.readline().rstrip("\n")
    except EOFError:
        line = ""

    print(f"You entered: {line}")
    print(f"Uppercase:   {line.upper()}")


if __name__ == "__main__":
    main()
