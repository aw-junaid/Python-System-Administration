#!/usr/bin/env python3
"""
run_command_with_timeout.py

Purpose:
    Run a command but automatically stop waiting for it (and treat it
    as timed out) if it takes longer than a specified number of seconds.

Usage:
    python run_command_with_timeout.py --timeout 3 --command "sleep 10"
    python run_command_with_timeout.py --timeout 5 --command "echo quick"

    If no arguments are given, a safe built-in demo runs a command that
    intentionally times out after 2 seconds.

Expected Output:
    Success case:
        STDOUT: quick
        Exit Code: 0
    Timeout case:
        Error: Command timed out after 2 seconds and was terminated.

Caution:
    - When a command times out, this script terminates the underlying
      process for you; any partial work that command was doing will be
      lost, and any files it had open may not be closed/flushed
      cleanly.
    - Choose a timeout value generously if the command normally takes
      a variable amount of time (e.g. network calls under load).
"""

import subprocess
import sys


def run_with_timeout(command: str, timeout_seconds: float) -> None:
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds
        )
        print("STDOUT:", result.stdout.strip() if result.stdout else "(no output)")
        if result.stderr.strip():
            print("STDERR:", result.stderr.strip())
        print(f"Exit Code: {result.returncode}")
    except subprocess.TimeoutExpired:
        print(f"Error: Command timed out after {timeout_seconds} seconds and was terminated.")


def parse_args():
    args = sys.argv[1:]
    timeout = None
    command = None
    i = 0
    while i < len(args):
        if args[i] == "--timeout" and i + 1 < len(args):
            timeout = float(args[i + 1]); i += 2
        elif args[i] == "--command" and i + 1 < len(args):
            command = args[i + 1]; i += 2
        else:
            i += 1
    return timeout, command


def main():
    timeout, command = parse_args()
    if timeout is None or command is None:
        timeout, command = 2, "sleep 10"
        print("No arguments given, running demo mode (expects a timeout).")
    run_with_timeout(command, timeout)


if __name__ == "__main__":
    main()
