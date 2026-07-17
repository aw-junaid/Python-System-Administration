#!/usr/bin/env python3
"""
use_getpass.py
--------------------
Focused example of Python's built-in 'getpass' module for reading
sensitive input (like passwords) without echoing it to the terminal.

Usage:
    python use_getpass.py

Example:
    python use_getpass.py
    # Password: (typing is hidden)
"""

import getpass
import sys


def main():
    print("Demo: reading a password using the getpass module.\n")

    if not sys.stdin.isatty():
        print("Warning: input is not coming from an interactive terminal.")
        print("getpass will fall back to a visible prompt in some environments (e.g. some IDEs).\n")

    try:
        username = input("Username: ")
        password = getpass.getpass("Password: ")
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        sys.exit(1)

    print(f"\nUsername entered: {username}")
    print(f"Password length: {len(password)} characters")
    print("(The password itself is never printed or stored.)")


if __name__ == "__main__":
    main()
