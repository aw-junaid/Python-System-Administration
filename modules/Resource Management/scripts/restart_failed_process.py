#!/usr/bin/env python3
"""
restart_failed_process.py
-------------------------------
Runs a command and automatically restarts it if it crashes (exits with a
non-zero code) or if it hangs beyond an optional per-run timeout. Includes
a maximum retry count and a delay between restarts to avoid restart storms.

Usage:
    python restart_failed_process.py <command> [args...] [--max-retries 5] [--delay 3] [--timeout 0]

Example:
    python restart_failed_process.py python3 my_server.py
    python restart_failed_process.py python3 my_server.py --max-retries 10 --delay 5
    python restart_failed_process.py python3 flaky_job.py --timeout 30
"""

import argparse
import subprocess
import sys
import time
from datetime import datetime


def run_and_restart(command: list, max_retries: int, delay: int, timeout: int) -> None:
    attempt = 0

    while attempt < max_retries or max_retries == 0:
        attempt += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Starting process (attempt {attempt}): {' '.join(command)}")

        try:
            if timeout > 0:
                result = subprocess.run(command, timeout=timeout)
                exit_code = result.returncode
            else:
                process = subprocess.Popen(command)
                exit_code = process.wait()
        except FileNotFoundError:
            print(f"Error: command not found: {command[0]}")
            sys.exit(1)
        except subprocess.TimeoutExpired:
            print(f"Process exceeded the {timeout}-second timeout and was terminated.")
            exit_code = -1

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if exit_code == 0:
            print(f"[{timestamp}] Process exited normally (code 0). Stopping — no restart needed.")
            return

        print(f"[{timestamp}] Process exited with code {exit_code}.")

        if max_retries != 0 and attempt >= max_retries:
            print(f"Maximum retry limit ({max_retries}) reached. Giving up.")
            sys.exit(1)

        print(f"Restarting in {delay} second(s)... (Ctrl+C to stop)\n")
        try:
            time.sleep(delay)
        except KeyboardInterrupt:
            print("\nStopped by user.")
            sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="Run a command and automatically restart it if it fails.",
        usage="restart_failed_process.py <command> [args...] [--max-retries N] [--delay N] [--timeout N]",
    )
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run (and restart on failure)")
    parser.add_argument("--max-retries", type=int, default=5,
                         help="Maximum number of restart attempts, 0 = unlimited (default: 5)")
    parser.add_argument("--delay", type=int, default=3, help="Seconds to wait before restarting (default: 3)")
    parser.add_argument("--timeout", type=int, default=0,
                         help="Per-run timeout in seconds; 0 = no timeout, run until it exits (default: 0)")
    args = parser.parse_args()

    command = args.command
    if command and command[0] == "--":
        command = command[1:]

    if not command:
        print("Error: no command provided.")
        print("Usage: restart_failed_process.py <command> [args...] [--max-retries N] [--delay N] [--timeout N]")
        sys.exit(1)

    run_and_restart(command, args.max_retries, args.delay, args.timeout)


if __name__ == "__main__":
    main()
