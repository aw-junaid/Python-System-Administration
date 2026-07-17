#!/usr/bin/env python3
"""
execute_periodically.py
-----------------------------
Runs a command repeatedly at a fixed interval, forever (or for a limited
number of runs), using only Python's standard library — no external
scheduler needed. Simpler alternative to schedule_with_library.py for
basic "run every N seconds" needs.

Usage:
    python execute_periodically.py <command> --interval <seconds> [--count N]

Example:
    python execute_periodically.py "echo Hello" --interval 5
    python execute_periodically.py "python3 healthcheck.py" --interval 60 --count 10
"""

import argparse
import shlex
import subprocess
import sys
import time
from datetime import datetime


def execute_periodically(command: str, interval: int, count: int) -> None:
    run_number = 0

    print(f"Running '{command}' every {interval} second(s)"
          + (f", {count} time(s) total." if count > 0 else ", indefinitely.") + "\n")
    print("Press Ctrl+C to stop.\n")

    try:
        while count == 0 or run_number < count:
            run_number += 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Run {run_number}: {command}")

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

            if count == 0 or run_number < count:
                time.sleep(interval)

    except KeyboardInterrupt:
        print(f"\nStopped after {run_number} run(s).")
        return

    print(f"\nCompleted {run_number} run(s).")


def main():
    parser = argparse.ArgumentParser(description="Run a command repeatedly at a fixed interval.")
    parser.add_argument("command", help="Command to run (quote it if it has spaces/args)")
    parser.add_argument("--interval", type=int, required=True, help="Seconds to wait between runs")
    parser.add_argument("--count", type=int, default=0, help="Number of times to run, 0 = run forever (default: 0)")
    args = parser.parse_args()

    execute_periodically(args.command, args.interval, args.count)


if __name__ == "__main__":
    main()
