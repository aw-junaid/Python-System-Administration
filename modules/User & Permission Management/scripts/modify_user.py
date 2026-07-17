#!/usr/bin/env python3
"""
modify_user.py
---------------------
Modifies an existing user account: login shell, primary/secondary groups,
or account expiry date. Wraps 'usermod' on Linux.

Platform: Linux only (Windows account modification varies too much by
          property to wrap generically here — use 'net user' directly
          for simple Windows changes, e.g. 'net user <name> /expires:date').
Requires: root/sudo.

Usage:
    python modify_user.py <username> [--shell /bin/zsh] [--groups group1,group2] [--append-groups] [--expiry YYYY-MM-DD]

Example:
    sudo python3 modify_user.py johndoe --shell /bin/zsh
    sudo python3 modify_user.py johndoe --groups sudo,docker --append-groups
    sudo python3 modify_user.py johndoe --expiry 2027-01-01
"""

import argparse
import os
import platform
import subprocess
import sys


def check_root():
    if os.geteuid() != 0:
        print("Error: this script must be run as root (use sudo).")
        sys.exit(1)


def modify_user(username: str, shell: str, groups: str, append_groups: bool, expiry: str) -> None:
    check_root()

    cmd = ["usermod"]
    changes = []

    if shell:
        cmd.extend(["-s", shell])
        changes.append(f"shell -> {shell}")

    if groups:
        if append_groups:
            cmd.append("-aG")
        else:
            cmd.append("-G")
        cmd.append(groups)
        changes.append(f"groups {'appended' if append_groups else 'set'} -> {groups}")

    if expiry:
        cmd.extend(["-e", expiry])
        changes.append(f"expiry -> {expiry}")

    if not changes:
        print("Error: no changes specified. Use --shell, --groups, and/or --expiry.")
        sys.exit(1)

    cmd.append(username)

    print(f"Modifying user '{username}': {', '.join(changes)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"User '{username}' modified successfully.")
    else:
        print("Error modifying user:")
        print(result.stderr.strip())
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Modify an existing user account (shell, groups, expiry).")
    parser.add_argument("username", help="Username to modify")
    parser.add_argument("--shell", default=None, help="New login shell, e.g. /bin/zsh")
    parser.add_argument("--groups", default=None, help="Comma-separated list of groups, e.g. sudo,docker")
    parser.add_argument("--append-groups", action="store_true",
                         help="Add to the given groups instead of replacing all secondary groups")
    parser.add_argument("--expiry", default=None, help="Account expiry date in YYYY-MM-DD format")
    args = parser.parse_args()

    if platform.system() != "Linux":
        print("Error: this script only supports Linux (via 'usermod').")
        print("On Windows, use 'net user <name> /expires:date' or similar commands directly.")
        sys.exit(1)

    modify_user(args.username, args.shell, args.groups, args.append_groups, args.expiry)


if __name__ == "__main__":
    main()
