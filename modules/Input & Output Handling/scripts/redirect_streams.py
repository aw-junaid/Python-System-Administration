#!/usr/bin/env python3
"""
Topic: Redirect Input/Output Streams

Demonstrates temporarily redirecting sys.stdout to a file, then restoring
it back to the original console output.

Usage:
    python redirect_streams.py

Expected Output:
    On the console: a message before and after redirection.
    A new file "redirected_output.txt" containing text that was written
    while stdout was redirected.
"""

import sys
import os


def main() -> None:
    output_file = "redirected_output.txt"

    print("This line prints normally to the console.")

    original_stdout = sys.stdout
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            sys.stdout = f
            print("This line was redirected into the file instead of the console.")
            print("Redirection works by swapping sys.stdout temporarily.")
    finally:
        sys.stdout = original_stdout

    print("This line prints normally again (stdout restored).")
    print(f"\nCheck the file '{os.path.abspath(output_file)}' for the redirected text.")


if __name__ == "__main__":
    main()
