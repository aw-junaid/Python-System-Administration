#!/usr/bin/env python3
"""
Topic: Read Multiline Input

Reads multiple lines of text from the user until an empty line or EOF is
entered, then prints a summary.

Usage:
    python read_multiline_input.py

Expected Output:
    Prompts you to type multiple lines. Type an empty line (just press
    Enter) or press Ctrl+D to finish. Then prints the number of lines and
    the combined text.
"""

import sys


def main() -> None:
    print("Enter multiple lines of text.")
    print("Press Enter on an empty line, or Ctrl+D, to finish.\n")

    lines = []
    try:
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
    except EOFError:
        pass

    print("\n--- Summary ---")
    print(f"Total lines entered: {len(lines)}")
    print("Combined text:")
    print("\n".join(lines) if lines else "(no input given)")


if __name__ == "__main__":
    main()
