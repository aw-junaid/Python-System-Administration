#!/usr/bin/env python3
"""
Topic: Write to Standard Error (stderr)

Demonstrates writing error/diagnostic messages to stderr instead of stdout,
which is the correct practice for errors and warnings in CLI tools.

Usage:
    python write_stderr.py
    python write_stderr.py 2> errors.log   (redirect only stderr to a file)

Expected Output:
    A normal message on stdout, and a warning/error message on stderr.
    If you redirect stderr (2>), only the stdout message appears on screen.
"""

import sys


def main() -> None:
    print("This is a normal informational message (stdout).")

    print("Warning: this is a non-fatal warning message (stderr).", file=sys.stderr)

    try:
        1 / 0
    except ZeroDivisionError as e:
        print(f"Error: {e} (stderr)", file=sys.stderr)


if __name__ == "__main__":
    main()
