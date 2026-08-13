#!/usr/bin/env python3
"""
disk_info.py
------------
Prints disk partition information: sizes, mount points, and
filesystem types.

Usage:
    python3 disk_info.py

Requires:
    pip install -r requirements.txt   (psutil)
"""

import sys

try:
    import psutil
except ImportError:
    print("[!] psutil is not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


def bytes_to_gb(value):
    return round(value / (1024 ** 3), 2)


def main():
    print("=" * 70)
    print(" DISK INFORMATION")
    print("=" * 70)

    partitions = psutil.disk_partitions(all=False)

    if not partitions:
        print("No partitions found.")
        return

    for p in partitions:
        print(f"\nDevice        : {p.device}")
        print(f"Mount point   : {p.mountpoint}")
        print(f"Filesystem    : {p.fstype}")
        print(f"Options       : {p.opts}")

        try:
            usage = psutil.disk_usage(p.mountpoint)
            print(f"Total size    : {bytes_to_gb(usage.total)} GB")
            print(f"Used          : {bytes_to_gb(usage.used)} GB")
            print(f"Free          : {bytes_to_gb(usage.free)} GB")
            print(f"Usage         : {usage.percent}%")
        except PermissionError:
            print("Usage         : Permission denied")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
