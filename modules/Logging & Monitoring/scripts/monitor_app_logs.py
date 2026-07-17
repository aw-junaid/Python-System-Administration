#!/usr/bin/env python3
"""
monitor_app_logs.py
----------------------
Tails an application log file in real time (like `tail -f`) and
flags lines containing keywords such as ERROR, CRITICAL, or FAILED.

Usage:
    python3 monitor_app_logs.py --file logs/warnings_errors.log

Arguments:
    --file       Path to the log file to monitor (required)
    --keywords   Comma-separated keywords to flag (default: ERROR,CRITICAL,FAILED,EXCEPTION)
"""

import argparse
import os
import time


def tail_file(filepath, keywords):
    print(f"Monitoring '{filepath}' for keywords: {', '.join(keywords)}")
    print("Press Ctrl+C to stop.\n")

    with open(filepath, "r") as f:
        # Move to the end of the file so we only see new lines
        f.seek(0, os.SEEK_END)

        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue

            for keyword in keywords:
                if keyword.upper() in line.upper():
                    print(f"[ALERT] Matched '{keyword}': {line.strip()}")
                    break


def main():
    parser = argparse.ArgumentParser(description="Tail and monitor a log file for keywords")
    parser.add_argument("--file", required=True, help="Path to log file")
    parser.add_argument(
        "--keywords",
        default="ERROR,CRITICAL,FAILED,EXCEPTION",
        help="Comma-separated keywords to flag",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"Log file not found: {args.file}")
        print("Tip: create the file first, or run log_warnings_errors.py to generate one.")
        return

    keywords = [k.strip() for k in args.keywords.split(",")]

    try:
        tail_file(args.file, keywords)
    except KeyboardInterrupt:
        print("\nStopped monitoring.")


if __name__ == "__main__":
    main()
