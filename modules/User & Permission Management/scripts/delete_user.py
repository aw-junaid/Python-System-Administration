#!/usr/bin/env python3
"""
delete_user.py
--------------------
Deletes a system user account, optionally removing their home directory
too. Wraps 'userdel' on Linux and 'net user /delete' on Windows.

Platform: Linux (via userdel) and Windows (via 'net user').
Requires: root/sudo on Linux, Administrator on Windows.

Usage:
    python delete_user.py <username> [--remove-home] [--force]

Example:
    sudo python3 delete_user.py johndoe --remove-home
    # Windows (as Administrator):
    python delete_user.py johndoe
"""

import argparse
import os
import platform
import subprocess
import sys


def check_root_linux():
    if os.geteuid() != 0:
        print("Error: this script must be run as root (use sudo) on Linux.")
        sys.exit(1)


def delete_user_linux(username: str, remove_home: bool, force: bool) -> None:
    check_root_linux()

    if not force:
        answer = input(
            f"Delete user '{username}'" +
            (" AND their home directory" if remove_home else "") +
            "? [y/N]: "
        ).strip().lower()
        if answer != "y":
            print("Aborted.")
            return

    cmd = ["userdel"]
    if remove_home:
        cmd.append("-r")
    cmd.append(username)

    print(f"Deleting user '{username}'...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"User '{username}' deleted successfully.")
        if remove_home:
            print("Home directory removed.")
    else:
        print("Error deleting user:")
        print(result.stderr.strip())
        sys.exit(1)


def delete_user_windows(username: str, force: bool) -> None:
    if not force:
        answer = input(f"Delete user '{username}'? [y/N]: ").strip().lower()
        if answer != "y":
            print("Aborted.")
            return

    print(f"Deleting user '{username}'...")
    result = subprocess.run(["net", "user", username, "/delete"], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"User '{username}' deleted successfully.")
        print("Note: on Windows, the user's profile folder is NOT automatically removed.")
        print("Delete it manually from C:\\Users\\<username> if needed.")
    else:
        print("Error deleting user (are you running as Administrator?):")
        print(result.stderr.strip() or result.stdout.strip())
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Delete a system user account.")
    parser.add_argument("username", help="Username to delete")
    parser.add_argument("--remove-home", action="store_true", help="Also remove the user's home directory (Linux only)")
    parser.add_argument("--force", action="store_true", help="Delete without confirmation prompt")
    args = parser.parse_args()

    system = platform.system()

    if system == "Windows":
        delete_user_windows(args.username, args.force)
    elif system in ("Linux", "Darwin"):
        delete_user_linux(args.username, args.remove_home, args.force)
    else:
        print(f"Error: unsupported platform '{system}'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
