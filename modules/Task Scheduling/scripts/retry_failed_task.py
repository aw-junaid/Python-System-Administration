#!/usr/bin/env python3
"""
retry_failed_task.py
---------------------------
Runs a command and automatically retries it if it fails (non-zero exit
code), using an exponential backoff delay between attempts. Different
from restart_failed_process.py (Resource Management module) in that this
is intended for one-shot tasks (like an API call or upload) that should
eventually succeed and then stop — not long-running services.

Usage:
    python retry_failed_task.py <command> [--max-retries 5] [--base-delay 2] [--max-delay 60]

Example:
    python retry_failed_task.py "curl -f https://example.com/api/ping"
    python retry_failed_task.py "python3 upload.py" --max-retries 8 --base-delay 3
"""

import argparse
import shlex
import subprocess
import sys
import time
from datetime import datetime


def retry_task(command: str, max_retries: int, base_delay: int, max_delay: int) -> int:
    attempt = 0

    while attempt < max_retries:
        attempt += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Attempt {attempt}/{max_retries}: {command}")

        try:
            result = subprocess.run(shlex.split(command), capture_output=True, text=True)
        except FileNotFoundError:
            print(f"Error: command not found: {command}")
            sys.exit(1)

        if result.stdout:
            print(result.stdout.strip())

        if result.returncode == 0:
            print(f"\nSuccess on attempt {attempt}.")
            return 0

        print(f"Attempt {attempt} failed with exit code {result.returncode}.")
        if result.stderr:
            print(result.stderr.strip())

        if attempt >= max_retries:
            break

        delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
        print(f"Retrying in {delay} second(s)...\n")
        time.sleep(delay)

    print(f"\nGiving up after {max_retries} failed attempt(s).")
    return 1


def main():
    parser = argparse.ArgumentParser(description="Run a command and retry it (with exponential backoff) if it fails.")
    parser.add_argument("command", help="Command to run (quote it if it has spaces/args)")
    parser.add_argument("--max-retries", type=int, default=5, help="Maximum number of attempts (default: 5)")
    parser.add_argument("--base-delay", type=int, default=2, help="Initial retry delay in seconds (default: 2)")
    parser.add_argument("--max-delay", type=int, default=60, help="Maximum retry delay in seconds (default: 60)")
    args = parser.parse_args()

    exit_code = retry_task(args.command, args.max_retries, args.base_delay, args.max_delay)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
