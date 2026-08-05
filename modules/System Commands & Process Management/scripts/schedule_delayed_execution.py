#!/usr/bin/env python3
"""
schedule_delayed_execution.py

Purpose:
    Run a command after waiting a specified delay (in seconds), similar
    in spirit to the Unix "at" command, but implemented in pure Python.

Usage:
    python schedule_delayed_execution.py --delay 10 --command "echo Done waiting"

    If no arguments are given, a safe built-in demo runs a 3-second
    delay before printing a message.

Expected Output:
    Waiting 10 seconds before running: echo Done waiting
    (after the delay)
    STDOUT: Done waiting
    Exit Code: 0

Caution:
    - This script BLOCKS (sleeps) for the full delay duration before
      running the command; it does not return control to you until
      the command has executed. For non-blocking scheduling of many
      jobs, see run_scheduled_jobs.py in this same folder.
    - If you need the delay to survive a reboot or script restart, use
      your OS's native scheduler (cron on Linux/macOS, Task Scheduler
      on Windows) instead.
"""

import subprocess
import sys
import time


def schedule_delayed(delay_seconds: float, command: str) -> None:
    print(f"Waiting {delay_seconds} seconds before running: {command}")
    time.sleep(delay_seconds)
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print("STDOUT:", result.stdout.strip() if result.stdout else "(no output)")
    if result.stderr.strip():
        print("STDERR:", result.stderr.strip())
    print(f"Exit Code: {result.returncode}")


def parse_args():
    args = sys.argv[1:]
    delay = None
    command = None
    i = 0
    while i < len(args):
        if args[i] == "--delay" and i + 1 < len(args):
            delay = float(args[i + 1]); i += 2
        elif args[i] == "--command" and i + 1 < len(args):
            command = args[i + 1]; i += 2
        else:
            i += 1
    return delay, command


def main():
    delay, command = parse_args()
    if delay is None or command is None:
        delay = 3
        command = "echo Demo: delayed command executed"
        print("No --delay/--command given, running demo mode.")
    schedule_delayed(delay, command)


if __name__ == "__main__":
    main()
