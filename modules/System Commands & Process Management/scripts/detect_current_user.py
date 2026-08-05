#!/usr/bin/env python3
"""
detect_current_user.py

Purpose:
    Detect and print the username of the account currently running
    this script.

Usage:
    python detect_current_user.py

Expected Output:
    Current User: your_username

Caution:
    - This script only reads information; it makes no system changes.
    - Behavior can differ slightly between OSes: on some systems the
      username may reflect the login user, while in certain sandboxed
      or containerized environments it may show a generic/service
      account name instead of a real person's name.
"""

import getpass
import os


def detect_current_user() -> None:
    try:
        user = getpass.getuser()
    except Exception:
        user = os.environ.get("USER") or os.environ.get("USERNAME") or "unknown"
    print(f"Current User: {user}")


def main():
    detect_current_user()


if __name__ == "__main__":
    main()
