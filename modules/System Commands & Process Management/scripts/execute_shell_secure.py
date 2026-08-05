#!/usr/bin/env python3
"""
execute_shell_secure.py

Purpose:
    Execute a shell command SECURELY by passing arguments as a list
    (shell=False) instead of a raw string, avoiding shell injection risks.

Usage:
    python execute_shell_secure.py ls -la
    python execute_shell_secure.py echo Hello Secure World

    If no arguments are given, a safe built-in demo runs instead.

Expected Output:
    STDOUT: <output of the command>
    STDERR: <error output, if any>
    Exit Code: <integer>

Caution:
    - This script deliberately avoids shell=True to reduce injection risk.
      Because of this, shell features like pipes (|), redirects (>), and
      wildcards (*) will NOT be interpreted -- each argument is passed
      literally to the program.
    - Still validate/whitelist any command coming from an untrusted source
      (e.g. user input in a web app) before running it.
"""

import subprocess
import sys


def run_command_secure(args: list) -> None:
    print(f"Running command securely: {' '.join(args)}\n")
    try:
        result = subprocess.run(
            args,
            shell=False,
            capture_output=True,
            text=True
        )
        print("STDOUT:")
        print(result.stdout if result.stdout else "(no output)")
        print("STDERR:")
        print(result.stderr if result.stderr else "(no errors)")
        print(f"Exit Code: {result.returncode}")
    except FileNotFoundError:
        print(f"Error: command '{args[0]}' not found on this system.")


def main():
    if len(sys.argv) > 1:
        args = sys.argv[1:]
    else:
        # Safe demo command if user provides none
        args = ["echo", "Hello", "from", "execute_shell_secure.py"]
    run_command_secure(args)


if __name__ == "__main__":
    main()
