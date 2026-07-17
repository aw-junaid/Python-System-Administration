#!/usr/bin/env python3
"""
limit_disk_usage.py
--------------------------
Monitors a directory's total disk usage and takes action (warn or block
further writes by exiting) if it exceeds a specified limit. Since Python
cannot enforce OS-level disk quotas without root/admin tools (like
'setquota'), this script works by periodically checking directory size
and alerting/stopping a companion process if the limit is exceeded.

Usage:
    python limit_disk_usage.py <directory_path> <limit_mb> [--interval 5] [--watch]

Example:
    python limit_disk_usage.py /home/user/uploads 500
    python limit_disk_usage.py /home/user/uploads 500 --watch --interval 10
"""

import argparse
import os
import sys
import time


def get_directory_size(path: str) -> int:
    total_size = 0
    for root, _, files in os.walk(path):
        for f in files:
            full_path = os.path.join(root, f)
            try:
                total_size += os.path.getsize(full_path)
            except OSError:
                continue
    return total_size


def check_once(path: str, limit_mb: int) -> bool:
    size_bytes = get_directory_size(path)
    size_mb = size_bytes / (1024 * 1024)
    percent = (size_mb / limit_mb) * 100 if limit_mb > 0 else 0

    print(f"Directory: {path}")
    print(f"Current size: {size_mb:.2f} MB")
    print(f"Limit:        {limit_mb} MB")
    print(f"Usage:        {percent:.1f}%")

    if size_mb > limit_mb:
        print("\nStatus: LIMIT EXCEEDED")
        return False
    elif percent >= 90:
        print("\nStatus: WARNING — approaching limit (90%+)")
        return True
    else:
        print("\nStatus: OK")
        return True


def watch(path: str, limit_mb: int, interval: int) -> None:
    print(f"Watching '{path}' every {interval} second(s). Press Ctrl+C to stop.\n")
    try:
        while True:
            within_limit = check_once(path, limit_mb)
            if not within_limit:
                print("\nDisk usage limit exceeded! Consider cleaning up files.")
            print("-" * 50)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped watching.")


def main():
    parser = argparse.ArgumentParser(description="Monitor and limit disk usage for a directory.")
    parser.add_argument("directory", help="Directory to monitor")
    parser.add_argument("limit_mb", type=int, help="Maximum allowed size in megabytes")
    parser.add_argument("--interval", type=int, default=5, help="Check interval in seconds when using --watch (default: 5)")
    parser.add_argument("--watch", action="store_true", help="Continuously monitor instead of checking once")
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: '{args.directory}' is not a valid directory.")
        sys.exit(1)

    if args.watch:
        watch(args.directory, args.limit_mb, args.interval)
    else:
        within_limit = check_once(args.directory, args.limit_mb)
        sys.exit(0 if within_limit else 1)


if __name__ == "__main__":
    main()
