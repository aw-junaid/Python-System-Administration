#!/usr/bin/env python3
"""
change_file_timestamps.py
-------------------------------
Changes the access and modification timestamps of a file (like the 'touch' command).
If no date is given, sets the timestamps to the current time.

Usage:
    python change_file_timestamps.py <file_path> [--date "YYYY-MM-DD HH:MM:SS"]

Example:
    python change_file_timestamps.py report.txt
    python change_file_timestamps.py report.txt --date "2025-01-15 10:30:00"
"""

import argparse
import os
import sys
import time
from datetime import datetime


def change_timestamp(file_path: str, date_str: str = None) -> None:
    if not os.path.exists(file_path):
        # Create the file if it doesn't exist (like 'touch')
        open(file_path, "a").close()
        print(f"File did not exist, created: {file_path}")

    if date_str:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            timestamp = time.mktime(dt.timetuple())
        except ValueError:
            print("Error: date must be in format 'YYYY-MM-DD HH:MM:SS'")
            sys.exit(1)
    else:
        timestamp = time.time()

    try:
        os.utime(file_path, (timestamp, timestamp))
        new_time = datetime.fromtimestamp(timestamp)
        print(f"Updated timestamps for '{file_path}' to {new_time}")
    except OSError as e:
        print(f"Error updating timestamps: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Change file access/modification timestamps.")
    parser.add_argument("file_path", help="File to update")
    parser.add_argument("--date", default=None, help="Target date/time in 'YYYY-MM-DD HH:MM:SS' format (default: now)")
    args = parser.parse_args()

    change_timestamp(args.file_path, args.date)


if __name__ == "__main__":
    main()
