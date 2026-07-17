#!/usr/bin/env python3
"""
change_password.py
-------------------------
Forcefully changes or resets a user's password. Wraps 'chpasswd' on Linux
and 'net user <name> <password>' on Windows.

Platform: Linux (via chpasswd) and Windows (via 'net user').
Requires: root/sudo on Linux, Administrator on Windows.

Usage:
    python change_password.py <username> [--password NEWPASS] [--force-change-at-login]

Example:
    sudo python3 change_password.py johndoe --password NewSecurePass123
    sudo python3 change_password.py johndoe --password TempPass1 --force-change-at-login

If --password is omitted, you will be prompted to enter it securely (hidden input).
"""

import argparse
import getpass
import os
import platform
import subprocess
import sys


def check_root_linux():
    if os.geteuid() != 0:
        print("Error: this script must be run as root (use sudo) on Linux.")
        sys.exit(1)


def get_password_securely() -> str:
    password = getpass.getpass("Enter new password: ")
    confirm = getpass.getpass("Confirm new password: ")

    if password != confirm:
        print("Error: passwords do not match.")
        sys.exit(1)

    if not password:
        print("Error: password cannot be empty.")
        sys.exit(1)

    return password


def change_password_linux(username: str, password: str, force_change: bool) -> None:
    check_root_linux()

    result = subprocess.run(
        ["chpasswd"], input=f"{username}:{password}", capture_output=True, text=True
    )

    if result.returncode != 0:
        print("Error changing password:")
        print(result.stderr.strip())
        sys.exit(1)

    print(f"Password for '{username}' changed successfully.")

    if force_change:
        expire_result = subprocess.run(["chage", "-d", "0", username], capture_output=True, text=True)
        if expire_result.returncode == 0:
            print("User will be required to change their password at next login.")
        else:
            print("Warning: password changed, but could not force change-at-login:")
            print(expire_result.stderr.strip())


def change_password_windows(username: str, password: str) -> None:
    result = subprocess.run(["net", "user", username, password], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"Password for '{username}' changed successfully.")
    else:
        print("Error changing password (are you running as Administrator?):")
        print(result.stderr.strip() or result.stdout.strip())
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Change or reset a user's password.")
    parser.add_argument("username", help="Username whose password will be changed")
    parser.add_argument("--password", default=None, help="New password (omit to be prompted securely)")
    parser.add_argument("--force-change-at-login", action="store_true",
                         help="Force the user to change their password on next login (Linux only)")
    args = parser.parse_args()

    password = args.password or get_password_securely()

    system = platform.system()

    if system == "Windows":
        change_password_windows(args.username, password)
    elif system in ("Linux", "Darwin"):
        change_password_linux(args.username, password, args.force_change_at_login)
    else:
        print(f"Error: unsupported platform '{system}'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
