#!/usr/bin/env python3
"""
execute_at_specific_time.py
---------------------------------
Waits until a specific clock time (or a specific future date/time) and
then runs a command once. Useful for "run this at 3 AM tonight" style
one-off scheduling without needing cron or Task Scheduler.

Usage:
    python execute_at_specific_time.py <command> --time HH:MM
    python execute_at_specific_time.py <command> --datetime "YYYY-MM-DD HH:MM:SS"

Example:
    python execute_at_specific_time.py "python3 backup.py" --time 23:30
    # Waits until 23:30 today (or tomorrow if that time already passed today), then runs.

    python execute_at_specific_time.py "python3 report.py" --datetime "2026-08-01 09:00:00"
    # Waits until that exact date and time, then runs.
"""

import argparse
import shlex
import subprocess
import sys
import time
from datetime import datetime, timedelta


def compute_target_time(time_str: str = None, datetime_str: str = None) -> datetime:
    now = datetime.now()

    if datetime_str:
        try:
            target = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            print("Error: --datetime must be in format 'YYYY-MM-DD HH:MM:SS'")
            sys.exit(1)

        if target <= now:
            print(f"Error: target datetime '{datetime_str}' is in the past.")
            sys.exit(1)

        return target

    else:
        try:
            hour, minute = map(int, time_str.split(":"))
        except ValueError:
            print("Error: --time must be in format 'HH:MM' (24-hour)")
            sys.exit(1)

        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if target <= now:
            target += timedelta(days=1)  # If time already passed today, schedule for tomorrow

        return target


def wait_and_execute(command: str, target: datetime) -> None:
    now = datetime.now()
    wait_seconds = (target - now).total_seconds()

    print(f"Command:     {command}")
    print(f"Target time: {target}")
    print(f"Waiting:     {wait_seconds / 60:.1f} minute(s)")
    print("\nPress Ctrl+C to cancel.\n")

    try:
        while True:
            remaining = (target - datetime.now()).total_seconds()
            if remaining <= 0:
                break
            time.sleep(min(remaining, 30))
    except KeyboardInterrupt:
        print("\nCancelled before execution.")
        sys.exit(0)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Target time reached. Running command now: {command}\n")

    try:
        result = subprocess.run(shlex.split(command), capture_output=True, text=True)
        if result.stdout:
            print(result.stdout.strip())
        if result.returncode != 0:
            print(f"Exit code: {result.returncode}")
            if result.stderr:
                print(result.stderr.strip())
    except FileNotFoundError:
        print(f"Error: command not found: {command}")
        sys.exit(1)

    print("\nDone.")


def main():
    parser = argparse.ArgumentParser(description="Wait until a specific time, then run a command once.")
    parser.add_argument("command", help="Command to run (quote it if it has spaces/args)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--time", help="Time today/tomorrow in HH:MM 24-hour format")
    group.add_argument("--datetime", help="Exact date and time in 'YYYY-MM-DD HH:MM:SS' format")
    args = parser.parse_args()

    target = compute_target_time(time_str=args.time, datetime_str=args.datetime)
    wait_and_execute(args.command, target)


if __name__ == "__main__":
    main()
