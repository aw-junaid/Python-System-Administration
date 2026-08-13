#!/usr/bin/env python3
"""
boot_time.py
-------------
Prints a precise timestamp of when the system was powered on
(booted), along with the resulting system uptime.

Usage:
    python3 boot_time.py

Requires:
    pip install -r requirements.txt   (psutil)
"""

import sys
from datetime import datetime, timedelta

try:
    import psutil
except ImportError:
    print("[!] psutil is not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


def main():
    print("=" * 50)
    print(" BOOT TIME")
    print("=" * 50)

    boot_timestamp = psutil.boot_time()
    boot_datetime = datetime.fromtimestamp(boot_timestamp)
    now = datetime.now()
    uptime = now - boot_datetime

    print(f"{'Boot time':<15}: {boot_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'Current time':<15}: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'Uptime':<15}: {str(timedelta(seconds=int(uptime.total_seconds())))}")

    print("=" * 50)


if __name__ == "__main__":
    main()
