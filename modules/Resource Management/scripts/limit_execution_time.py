#!/usr/bin/env python3
"""
limit_execution_time.py
-----------------------------
Runs a command and forcibly terminates it if it runs longer than a
specified wall-clock time limit (a timeout), regardless of platform.

Usage:
    python limit_execution_time.py <timeout_seconds> -- <command> [args...]

Example:
    python limit_execution_time.py 10 -- ping -c 100 example.com
    # The command is killed if it runs longer than 10 seconds.
"""

import argparse
import subprocess
import sys


def run_with_timeout(timeout_seconds: int, command: list) -> int:
    print(f"Running command with a {timeout_seconds}-second time limit: {' '.join(command)}\n")

    try:
        result = subprocess.run(command, timeout=timeout_seconds)
        return result.returncode
    except subprocess.TimeoutExpired:
        print(f"\nProcess exceeded the {timeout_seconds}-second time limit and was terminated.")
        return 124  # Conventional timeout exit code (matches GNU 'timeout' command)
    except FileNotFoundError:
        print(f"Error: command not found: {command[0]}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Run a command with a wall-clock execution time limit.",
        usage="limit_execution_time.py <timeout_seconds> -- <command> [args...]",
    )
    parser.add_argument("timeout_seconds", type=float, help="Maximum execution time in seconds")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run, after '--'")
    args = parser.parse_args()

    command = args.command
    if command and command[0] == "--":
        command = command[1:]

    if not command:
        print("Error: no command provided. Usage: limit_execution_time.py <timeout_seconds> -- <command> [args...]")
        sys.exit(1)

    exit_code = run_with_timeout(args.timeout_seconds, command)

    print(f"\nCommand finished with exit code: {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
