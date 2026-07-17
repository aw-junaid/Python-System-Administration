#!/usr/bin/env python3
"""
schedule_with_library.py
------------------------------
Schedules and runs a command repeatedly using the 'schedule' library —
a lightweight, in-process Python job scheduler (no cron/OS integration
required). The script itself must keep running for jobs to fire.

Requires: pip install schedule

Usage:
    python schedule_with_library.py <command> --every <N> --unit <seconds|minutes|hours|days>

Example:
    python schedule_with_library.py "echo Hello" --every 10 --unit seconds
    python schedule_with_library.py "python3 backup.py" --every 1 --unit hours
"""

import argparse
import shlex
import subprocess
import sys
from datetime import datetime

try:
    import schedule
except ImportError:
    print("Error: the 'schedule' package is required.")
    print("Install it with: pip install -r requirements.txt")
    sys.exit(1)

import time


def run_command(command: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Running: {command}")

    try:
        result = subprocess.run(shlex.split(command), capture_output=True, text=True)
        if result.stdout:
            print(result.stdout.strip())
        if result.returncode != 0:
            print(f"[{timestamp}] Command exited with code {result.returncode}")
            if result.stderr:
                print(result.stderr.strip())
    except FileNotFoundError:
        print(f"[{timestamp}] Error: command not found: {command}")


def build_job(command: str, every: int, unit: str):
    job = getattr(schedule.every(every), unit)
    job.do(run_command, command)


def main():
    parser = argparse.ArgumentParser(description="Schedule a recurring command using the 'schedule' library.")
    parser.add_argument("command", help="Command to run (quote it if it has spaces/args)")
    parser.add_argument("--every", type=int, default=1, help="Run every N units (default: 1)")
    parser.add_argument("--unit", default="minutes",
                         choices=["seconds", "minutes", "hours", "days"],
                         help="Time unit for the interval (default: minutes)")
    args = parser.parse_args()

    build_job(args.command, args.every, args.unit)

    print(f"Scheduled '{args.command}' to run every {args.every} {args.unit}.")
    print("This script must keep running for the schedule to fire. Press Ctrl+C to stop.\n")

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nScheduler stopped.")


if __name__ == "__main__":
    main()
