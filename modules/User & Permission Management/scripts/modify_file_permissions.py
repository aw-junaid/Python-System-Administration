#!/usr/bin/env python3
"""
modify_file_permissions.py
--------------------------------
Changes a file or directory's permissions using an octal mode, applied
programmatically via Python's os.chmod (equivalent to the 'chmod' command).

Platform: Linux/macOS (full support). On Windows, permission bits are
          limited to a much smaller effective set by the OS itself.

Usage:
    python modify_file_permissions.py <path> <octal_mode> [--recursive]

Example:
    python modify_file_permissions.py myscript.sh 755
    python modify_file_permissions.py ./project 644 --recursive
"""

import argparse
import os
import stat
import sys


def parse_octal_mode(mode_str: str) -> int:
    try:
        return int(mode_str, 8)
    except ValueError:
        print(f"Error: '{mode_str}' is not a valid octal mode (e.g. 755, 644, 0700).")
        sys.exit(1)


def modify_permissions(path: str, mode: int, recursive: bool) -> None:
    if not os.path.exists(path):
        print(f"Error: '{path}' does not exist.")
        sys.exit(1)

    def apply(target: str):
        try:
            os.chmod(target, mode)
            return True
        except OSError as e:
            print(f"Error setting permissions on '{target}': {e}")
            return False

    changed = 0
    failed = 0

    if recursive and os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            if apply(root):
                changed += 1
            else:
                failed += 1
            for f in files:
                full_path = os.path.join(root, f)
                if apply(full_path):
                    changed += 1
                else:
                    failed += 1
    else:
        if apply(path):
            changed += 1
        else:
            failed += 1

    octal_str = oct(mode)[2:].zfill(4)
    print(f"\nPermissions set to {octal_str} on {changed} item(s).")
    if failed:
        print(f"Failed on {failed} item(s).")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Modify file/directory permissions (like chmod).")
    parser.add_argument("path", help="Path to the file or directory")
    parser.add_argument("octal_mode", help="Octal permission mode, e.g. 755, 644, 0700")
    parser.add_argument("--recursive", action="store_true", help="Apply recursively to all contents (directories only)")
    args = parser.parse_args()

    mode = parse_octal_mode(args.octal_mode)
    modify_permissions(args.path, mode, args.recursive)


if __name__ == "__main__":
    main()
