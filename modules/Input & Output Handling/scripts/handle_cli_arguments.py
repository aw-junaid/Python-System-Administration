#!/usr/bin/env python3
"""
Topic: Handle Command-Line Arguments

Shows how to access raw command-line arguments using sys.argv, without any
parsing library.

Usage:
    python handle_cli_arguments.py foo bar --flag=value

Expected Output:
    The script name, number of arguments, and each argument listed.
"""

import sys


def main() -> None:
    script_name = sys.argv[0]
    args = sys.argv[1:]

    print(f"Script name: {script_name}")
    print(f"Number of arguments: {len(args)}")

    if not args:
        print("No arguments given. Try: python handle_cli_arguments.py foo bar --flag=value")
        return

    for index, arg in enumerate(args, start=1):
        print(f"Argument {index}: {arg}")


if __name__ == "__main__":
    main()
