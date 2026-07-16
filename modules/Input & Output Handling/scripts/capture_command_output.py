#!/usr/bin/env python3
"""
Topic: Capture and Process Command Output

Runs a shell command using subprocess, captures its stdout/stderr, and
processes the result in Python.

Usage:
    python capture_command_output.py
    python capture_command_output.py "ls -la"

Expected Output:
    Prints the return code, captured stdout, and captured stderr of the
    command that was run.
"""

import subprocess
import sys


def run_command(command: str):
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )
    return result


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else "echo Hello from subprocess"

    print(f"Running command: {command}\n")
    result = run_command(command)

    print(f"Return code: {result.returncode}")
    print("---- STDOUT ----")
    print(result.stdout.strip() or "(empty)")
    print("---- STDERR ----")
    print(result.stderr.strip() or "(empty)")


if __name__ == "__main__":
    main()
