#!/usr/bin/env python3
"""
execute_external_command.py

Purpose:
    Execute an external system command (e.g. "ls -la", "whoami", "echo hello")
    and print its stdout, stderr, and exit code.

Usage:
    python execute_external_command.py "echo Hello World"
    python execute_external_command.py "ls -la"

    If no command is given, a safe built-in demo command runs instead.

Expected Output:
    STDOUT: <output of the command>
    STDERR: <error output, if any>
    Exit Code: <integer>

Caution:
    - This script runs whatever command string you pass to it. Do not pass
      commands from untrusted input (e.g. web forms) without validation,
      since this can lead to arbitrary command execution.
    - shell=True is used here for convenience with full command strings;
      for security-sensitive contexts prefer passing arguments as a list
      with shell=False.
"""

import subprocess
import sys


def run_command(command: str) -> None:
    print(f"Running command: {command}\n")
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )
    print("STDOUT:")
    print(result.stdout if result.stdout else "(no output)")
    print("STDERR:")
    print(result.stderr if result.stderr else "(no errors)")
    print(f"Exit Code: {result.returncode}")


def main():
    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
    else:
        # Safe demo command if user provides none
        command = "echo Hello from execute_external_command.py"
    run_command(command)


if __name__ == "__main__":
    main()
