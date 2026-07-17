#!/usr/bin/env python3
"""
monitor_disk.py
-------------------
Checks disk usage for a given path and warns if usage exceeds a
threshold percentage. Requires the `psutil` library.

Usage:
    python3 monitor_disk.py --path / --threshold 80
"""

import argparse
import psutil


def check_disk(path, threshold):
    usage = psutil.disk_usage(path)
    percent = usage.percent

    print(f"Disk usage for '{path}': {percent}%")
    print(f"  Total: {usage.total / (1024**3):.2f} GB")
    print(f"  Used:  {usage.used / (1024**3):.2f} GB")
    print(f"  Free:  {usage.free / (1024**3):.2f} GB")

    if percent >= threshold:
        print(f"[WARNING] Disk usage ({percent}%) exceeds threshold ({threshold}%)")
        return False
    else:
        print(f"[OK] Disk usage is within the {threshold}% threshold")
        return True


def main():
    parser = argparse.ArgumentParser(description="Monitor disk usage")
    parser.add_argument("--path", default="/", help="Path/mount point to check")
    parser.add_argument("--threshold", type=float, default=80.0, help="Warning threshold percent")
    args = parser.parse_args()

    check_disk(args.path, args.threshold)


if __name__ == "__main__":
    main()
