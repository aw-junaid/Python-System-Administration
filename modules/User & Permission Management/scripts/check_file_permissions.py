#!/usr/bin/env python3
"""
check_file_permissions.py
-------------------------------
Displays a file or directory's permissions in both octal (e.g. 0755) and
symbolic (e.g. rwxr-xr-x) form, plus owner/group info — a Python mapping
of the raw stat mode, similar to 'ls -l' and 'stat'.

Platform: Linux/macOS (owner/group names). Works on Windows too, but
          owner/group resolution is limited there.

Usage:
    python check_file_permissions.py <path>

Example:
    python check_file_permissions.py /etc/passwd
    python check_file_permissions.py ./myscript.sh
"""

import argparse
import os
import stat
import sys


def octal_permissions(mode: int) -> str:
    return oct(stat.S_IMODE(mode))[2:].zfill(4)


def symbolic_permissions(mode: int) -> str:
    return stat.filemode(mode)


def get_owner_group(path: str) -> tuple:
    try:
        import pwd
        import grp
        info = os.stat(path)
        owner = pwd.getpwuid(info.st_uid).pw_name
        group = grp.getgrgid(info.st_gid).gr_name
        return owner, group
    except (ImportError, KeyError):
        info = os.stat(path)
        return str(info.st_uid), str(info.st_gid)


def check_permissions(path: str) -> None:
    if not os.path.exists(path):
        print(f"Error: '{path}' does not exist.")
        sys.exit(1)

    info = os.stat(path)
    mode = info.st_mode

    owner, group = get_owner_group(path)

    print(f"Path:              {path}")
    print(f"Type:              {'Directory' if os.path.isdir(path) else 'File' if os.path.isfile(path) else 'Other'}")
    print(f"Octal permissions: {octal_permissions(mode)}")
    print(f"Symbolic form:     {symbolic_permissions(mode)}")
    print(f"Owner:             {owner} (uid={info.st_uid})")
    print(f"Group:             {group} (gid={info.st_gid})")
    print(f"Size:              {info.st_size} bytes")

    print("\nPermission breakdown:")
    perm_bits = stat.S_IMODE(mode)
    categories = [("Owner", 6), ("Group", 3), ("Other", 0)]
    for label, shift in categories:
        r = "r" if perm_bits & (0o4 << shift) else "-"
        w = "w" if perm_bits & (0o2 << shift) else "-"
        x = "x" if perm_bits & (0o1 << shift) else "-"
        print(f"  {label:<6}: {r}{w}{x}")


def main():
    parser = argparse.ArgumentParser(description="Check file/directory permissions (octal + symbolic).")
    parser.add_argument("path", help="Path to the file or directory to inspect")
    args = parser.parse_args()

    check_permissions(args.path)


if __name__ == "__main__":
    main()
