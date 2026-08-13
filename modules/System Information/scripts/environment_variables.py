#!/usr/bin/env python3
"""
environment_variables.py
--------------------------
Reads and prints environment variables available to the current
user session (includes PATH and other global/user-scoped variables
inherited by the Python process).

Note: This script can only see the environment of the process it runs
in (and anything inherited from its parent shell). It cannot read
another user's session environment directly - that requires elevated
privileges and OS-specific APIs.

Usage:
    python3 environment_variables.py
    python3 environment_variables.py --key PATH   # show a single variable

Requires:
    No third-party packages. Uses only the Python standard library.
"""

import argparse
import os


def print_all_env():
    for key in sorted(os.environ.keys()):
        print(f"{key}={os.environ[key]}")
    print(f"\nTotal variables: {len(os.environ)}")


def print_single_env(key):
    value = os.environ.get(key)
    if value is None:
        print(f"[!] '{key}' is not set in the current environment.")
    else:
        print(f"{key}={value}")


def print_path_entries():
    path_var = os.environ.get("PATH", "")
    separator = ";" if os.name == "nt" else ":"
    entries = path_var.split(separator)
    print("\nPATH entries:")
    for entry in entries:
        print(f"  - {entry}")


def main():
    parser = argparse.ArgumentParser(description="Display environment variables.")
    parser.add_argument("--key", type=str, default=None,
                         help="Show only the value of a specific variable (e.g. PATH)")
    args = parser.parse_args()

    print("=" * 60)
    print(" ENVIRONMENT VARIABLES")
    print("=" * 60)

    if args.key:
        print_single_env(args.key)
    else:
        print_all_env()
        print_path_entries()

    print("=" * 60)


if __name__ == "__main__":
    main()
