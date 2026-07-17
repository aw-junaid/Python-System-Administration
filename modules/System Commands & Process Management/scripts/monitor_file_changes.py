#!/usr/bin/env python3
"""
monitor_file_changes.py
-----------------------------
Monitors a single file for changes (modification time / size) and prints a message when it changes.
Press Ctrl+C to stop.

Usage:
    python monitor_file_changes.py <file_path> [--interval 2]

Example:
    python monitor_file_changes.py config.json
    python monitor_file_changes.py config.json --interval 5
"""

import argparse
import os
import sys
import time
from datetime import datetime


def monitor_file(path: str, interval: int) -> None:
    if not os.path.isfile(path):
        print(f"Error: '{path}' does not exist or is not a file.")
        sys.exit(1)

    print(f"Monitoring '{path}' for changes every {interval} second(s). Press Ctrl+C to stop.\n")

    last_mtime = os.path.getmtime(path)
    last_size = os.path.getsize(path)

    try:
        while True:
            time.sleep(interval)

            if not os.path.exists(path):
                print(f"[{datetime.now()}] File was deleted!")
                break

            current_mtime = os.path.getmtime(path)
            current_size = os.path.getsize(path)

            if current_mtime != last_mtime or current_size != last_size:
                print(f"[{datetime.now()}] Change detected: size={current_size} bytes, modified={datetime.fromtimestamp(current_mtime)}")
                last_mtime = current_mtime
                last_size = current_size

    except KeyboardInterrupt:
        print("\nStopped monitoring.")


def main():
    parser = argparse.ArgumentParser(description="Monitor a file for changes.")
    parser.add_argument("path", help="File to monitor")
    parser.add_argument("--interval", type=int, default=2, help="Check interval in seconds (default: 2)")
    args = parser.parse_args()

    monitor_file(args.path, args.interval)


if __name__ == "__main__":
    main()
