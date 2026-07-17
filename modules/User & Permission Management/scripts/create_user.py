#!/usr/bin/env python3
"""
create_user.py
--------------------
Creates a new system user account. Wraps 'useradd' on Linux and 'net user'
on Windows.

Platform: Linux (via useradd) and Windows (via 'net user').
Requires: root/sudo on Linux, Administrator on Windows.

Usage:
    python create_user.py <username> [--password PASS] [--shell /bin/bash] [--home /home/username] [--create-home]

Example:
    sudo python3 create_user.py johndoe --create-home --shell /bin/bash
    # Windows (as Administrator):
    python create_user.py johndoe --password MyPass123
"""

import argparse
import platform
import subprocess
import sys


def check_root_linux():
    import os
    if os.geteuid() != 0:
        print("Error: this script must be run as root (use sudo) on Linux.")
        sys.exit(1)


def create_user_linux(username: str, password: str, shell: str, home: str, create_home: bool) -> None:
    check_root_linux()

    cmd = ["useradd"]
    if create_home:
        cmd.append("-m")
    if home:
        cmd.extend(["-d", home])
    if shell:
        cmd.extend(["-s", shell])
    cmd.append(username)

    print(f"Creating user '{username}'...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("Error creating user:")
        print(result.stderr.strip())
        sys.exit(1)

    print(f"User '{username}' created successfully.")

    if password:
        proc = subprocess.run(
            ["chpasswd"], input=f"{username}:{password}", capture_output=True, text=True
        )
        if proc.returncode == 0:
            print("Password set successfully.")
        else:
            print("Warning: user created, but setting password failed:")
            print(proc.stderr.strip())


def create_user_windows(username: str, password: str) -> None:
    cmd = ["net", "user", username]
    if password:
        cmd.append(password)
    else:
        cmd.append("*")  # prompts for password interactively
    cmd.append("/add")

    print(f"Creating user '{username}'...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"User '{username}' created successfully.")
        print(result.stdout.strip())
    else:
        print("Error creating user (are you running as Administrator?):")
        print(result.stderr.strip() or result.stdout.strip())
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Create a new system user account.")
    parser.add_argument("username", help="Username to create")
    parser.add_argument("--password", default=None, help="Password to set for the new user")
    parser.add_argument("--shell", default="/bin/bash", help="Login shell (Linux only, default: /bin/bash)")
    parser.add_argument("--home", default=None, help="Custom home directory path (Linux only)")
    parser.add_argument("--create-home", action="store_true", help="Create the user's home directory (Linux only)")
    args = parser.parse_args()

    system = platform.system()

    if system == "Windows":
        create_user_windows(args.username, args.password)
    elif system in ("Linux", "Darwin"):
        create_user_linux(args.username, args.password, args.shell, args.home, args.create_home)
    else:
        print(f"Error: unsupported platform '{system}'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
