#!/usr/bin/env python3
"""
get_exit_status.py

Purpose:
    Run a command and report its exit status code, along with a plain
    English interpretation (success vs failure).

Usage:
    python get_exit_status.py "ls /nonexistent"
    python get_exit_status.py "echo hi"

    If no command is given, a safe built-in demo runs.

Expected Output:
    Command: ls /nonexistent
    Exit Code: 2
    Result: FAILURE (non-zero exit code)

Caution:
    - Exit code meaning is command-specific: 0 conventionally means
      success, and any non-zero value means some kind of failure, but
      the exact number's meaning depends on the program that was run.
    - This script uses shell=True for convenience with full command
      strings; avoid passing untrusted input directly as a command.
"""

import subprocess
import sys


def get_exit_status(command: str) -> None:
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(f"Command: {command}")
    print(f"Exit Code: {result.returncode}")
    if result.returncode == 0:
        print("Result: SUCCESS (exit code 0)")
    else:
        print("Result: FAILURE (non-zero exit code)")
    if result.stdout.strip():
        print(f"STDOUT: {result.stdout.strip()}")
    if result.stderr.strip():
        print(f"STDERR: {result.stderr.strip()}")


def main():
    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
    else:
        command = "ls /this/path/does/not/exist"
    get_exit_status(command)


if __name__ == "__main__":
    main()
