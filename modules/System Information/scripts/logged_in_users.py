#!/usr/bin/env python3
"""
logged_in_users.py
---------------------
Enumerates currently active/logged-in user sessions, including
terminal, host, and login time.

Usage:
    python3 logged_in_users.py

Requires:
    pip install -r requirements.txt   (psutil)
"""

import sys
from datetime import datetime

try:
    import psutil
except ImportError:
    print("[!] psutil is not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


def main():
    print("=" * 60)
    print(" LOGGED-IN USERS")
    print("=" * 60)

    users = psutil.users()

    if not users:
        print("No active user sessions found.")
        return

    for u in users:
        login_time = datetime.fromtimestamp(u.started).strftime("%Y-%m-%d %H:%M:%S")
        print(f"\nUser       : {u.name}")
        print(f"Terminal   : {u.terminal or 'N/A'}")
        print(f"Host       : {u.host or 'local'}")
        print(f"Login time : {login_time}")
        if hasattr(u, "pid") and u.pid:
            print(f"PID        : {u.pid}")

    print(f"\nTotal active sessions: {len(users)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
