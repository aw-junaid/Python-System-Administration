#!/usr/bin/env python3
"""
run_scheduled_jobs.py

Purpose:
    Run a command repeatedly on a fixed interval (like a simple
    in-process cron job), for a limited number of repetitions.

Usage:
    python run_scheduled_jobs.py --interval 5 --repeats 3 --command "echo tick"

    If no arguments are given, a safe built-in demo runs "echo tick"
    every 2 seconds, 3 times total.

Expected Output:
    [Run 1/3] echo tick
    STDOUT: tick
    [Run 2/3] echo tick
    STDOUT: tick
    [Run 3/3] echo tick
    STDOUT: tick
    Scheduled job finished after 3 run(s).

Caution:
    - This script BLOCKS the terminal for the entire duration
      (interval * repeats seconds approximately); it's meant for short
      demos/tests, not long-running production job scheduling.
    - For real production scheduling that survives reboots and doesn't
      require keeping a Python process alive, use native OS schedulers:
      cron (Linux/macOS) or Task Scheduler (Windows) — see
      execute_startup_scripts.py and manage_system_services.py for
      related concepts.
    - Press Ctrl+C to stop early if you set a large --repeats value.
"""

import subprocess
import sys
import time


def run_scheduled(interval_seconds: float, repeats: int, command: str) -> None:
    for i in range(1, repeats + 1):
        print(f"[Run {i}/{repeats}] {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print("STDOUT:", result.stdout.strip() if result.stdout else "(no output)")
        if result.stderr.strip():
            print("STDERR:", result.stderr.strip())
        if i < repeats:
            time.sleep(interval_seconds)
    print(f"Scheduled job finished after {repeats} run(s).")


def parse_args():
    args = sys.argv[1:]
    interval = None
    repeats = None
    command = None
    i = 0
    while i < len(args):
        if args[i] == "--interval" and i + 1 < len(args):
            interval = float(args[i + 1]); i += 2
        elif args[i] == "--repeats" and i + 1 < len(args):
            repeats = int(args[i + 1]); i += 2
        elif args[i] == "--command" and i + 1 < len(args):
            command = args[i + 1]; i += 2
        else:
            i += 1
    return interval, repeats, command


def main():
    interval, repeats, command = parse_args()
    if interval is None or repeats is None or command is None:
        interval, repeats, command = 2, 3, "echo tick"
        print("No arguments given, running demo mode.")
    try:
        run_scheduled(interval, repeats, command)
    except KeyboardInterrupt:
        print("\nStopped early by user (Ctrl+C).")


if __name__ == "__main__":
    main()
