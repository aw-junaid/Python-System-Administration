#!/usr/bin/env python3
"""
watch_directories.py
--------------------------
Watches a directory for file additions, deletions, and modifications.
Press Ctrl+C to stop.

Usage:
    python watch_directories.py <directory_path> [--interval 2]

Example:
    python watch_directories.py /home/user/Downloads
    python watch_directories.py /home/user/Downloads --interval 5
"""

import argparse
import os
import sys
import time
from datetime import datetime


def snapshot(path: str) -> dict:
    state = {}
    for root, _, files in os.walk(path):
        for f in files:
            full_path = os.path.join(root, f)
            try:
                state[full_path] = os.path.getmtime(full_path)
            except OSError:
                continue
    return state


def watch_directory(path: str, interval: int) -> None:
    if not os.path.isdir(path):
        print(f"Error: '{path}' is not a valid directory.")
        sys.exit(1)

    print(f"Watching '{path}' for changes every {interval} second(s). Press Ctrl+C to stop.\n")

    previous_state = snapshot(path)

    try:
        while True:
            time.sleep(interval)
            current_state = snapshot(path)

            added = current_state.keys() - previous_state.keys()
            removed = previous_state.keys() - current_state.keys()
            modified = {
                f for f in current_state.keys() & previous_state.keys()
                if current_state[f] != previous_state[f]
            }

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for f in added:
                print(f"[{timestamp}] ADDED:    {f}")
            for f in removed:
                print(f"[{timestamp}] REMOVED:  {f}")
            for f in modified:
                print(f"[{timestamp}] MODIFIED: {f}")

            previous_state = current_state

    except KeyboardInterrupt:
        print("\nStopped watching.")


def main():
    parser = argparse.ArgumentParser(description="Watch a directory for file changes.")
    parser.add_argument("path", help="Directory to watch")
    parser.add_argument("--interval", type=int, default=2, help="Check interval in seconds (default: 2)")
    args = parser.parse_args()

    watch_directory(args.path, args.interval)


if __name__ == "__main__":
    main()
