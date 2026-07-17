#!/usr/bin/env python3
"""
change_file_ownership.py
------------------------------
Changes a file or directory's owner (UID) and/or group (GID) using
Python's os.chown (equivalent to the 'chown' command). Accepts either
names (resolved via pwd/grp) or numeric UID/GID.

Platform: Linux/macOS only (os.chown is not available on Windows).
Requires: root/sudo (to change ownership to a different user).

Usage:
    python change_file_ownership.py <path> [--owner USER_OR_UID] [--group GROUP_OR_GID] [--recursive]

Example:
    sudo python3 change_file_ownership.py /var/www/html --owner www-data --group www-data --recursive
    sudo python3 change_file_ownership.py myfile.txt --owner 1000
"""

import argparse
import grp
import os
import platform
import pwd
import sys


def resolve_uid(owner: str) -> int:
    if owner is None:
        return -1  # -1 means "don't change" for os.chown
    try:
        return int(owner)
    except ValueError:
        try:
            return pwd.getpwnam(owner).pw_uid
        except KeyError:
            print(f"Error: user '{owner}' not found.")
            sys.exit(1)


def resolve_gid(group: str) -> int:
    if group is None:
        return -1
    try:
        return int(group)
    except ValueError:
        try:
            return grp.getgrnam(group).gr_gid
        except KeyError:
            print(f"Error: group '{group}' not found.")
            sys.exit(1)


def change_ownership(path: str, uid: int, gid: int, recursive: bool) -> None:
    if not os.path.exists(path):
        print(f"Error: '{path}' does not exist.")
        sys.exit(1)

    def apply(target: str) -> bool:
        try:
            os.chown(target, uid, gid)
            return True
        except OSError as e:
            print(f"Error changing ownership of '{target}': {e}")
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

    print(f"\nOwnership updated on {changed} item(s).")
    if failed:
        print(f"Failed on {failed} item(s). This usually requires root/sudo.")
        sys.exit(1)


def main():
    if platform.system() == "Windows":
        print("Error: os.chown is not available on Windows. This script only supports Linux/macOS.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Change file/directory ownership (like chown).")
    parser.add_argument("path", help="Path to the file or directory")
    parser.add_argument("--owner", default=None, help="New owner (username or UID)")
    parser.add_argument("--group", default=None, help="New group (group name or GID)")
    parser.add_argument("--recursive", action="store_true", help="Apply recursively to all contents (directories only)")
    args = parser.parse_args()

    if args.owner is None and args.group is None:
        print("Error: specify at least --owner or --group.")
        sys.exit(1)

    uid = resolve_uid(args.owner)
    gid = resolve_gid(args.group)

    change_ownership(args.path, uid, gid, args.recursive)


if __name__ == "__main__":
    main()
