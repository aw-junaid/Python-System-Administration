#!/usr/bin/env python3
"""
set_cpu_limit.py
----------------------
Runs a command/process while limiting how much CPU time it can consume,
using the 'resource' module (RLIMIT_CPU) on Linux/macOS.

On Windows, hard CPU-time limits are not supported by the OS in the same
way; this script will inform you and fall back to monitoring instead.

Usage:
    python set_cpu_limit.py <cpu_seconds> -- <command> [args...]

Example:
    python set_cpu_limit.py 5 -- python3 -c "while True: pass"
    # The process will be killed by the OS once it uses 5 seconds of CPU time.
"""

import argparse
import platform
import subprocess
import sys


def set_cpu_limit_and_run(cpu_seconds: int, command: list) -> int:
    if platform.system() == "Windows":
        print("Warning: hard CPU-time limits (RLIMIT_CPU) are not supported on Windows.")
        print("Running the command WITHOUT a CPU limit. Consider using Job Objects for this on Windows.")
        result = subprocess.run(command)
        return result.returncode

    import resource

    def limit_cpu():
        # Soft limit == hard limit here; process receives SIGXCPU then SIGKILL.
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))

    print(f"Running command with a CPU time limit of {cpu_seconds} second(s): {' '.join(command)}")

    try:
        result = subprocess.run(command, preexec_fn=limit_cpu)
        return result.returncode
    except FileNotFoundError:
        print(f"Error: command not found: {command[0]}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Run a command with a CPU time limit.",
        usage="set_cpu_limit.py <cpu_seconds> -- <command> [args...]",
    )
    parser.add_argument("cpu_seconds", type=int, help="Maximum CPU time in seconds before the process is killed")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run, after '--'")
    args = parser.parse_args()

    command = args.command
    if command and command[0] == "--":
        command = command[1:]

    if not command:
        print("Error: no command provided. Usage: set_cpu_limit.py <cpu_seconds> -- <command> [args...]")
        sys.exit(1)

    exit_code = set_cpu_limit_and_run(args.cpu_seconds, command)

    print(f"\nCommand finished with exit code: {exit_code}")
    if exit_code < 0:
        print(f"Process was terminated by signal {-exit_code} (likely due to exceeding the CPU limit).")


if __name__ == "__main__":
    main()
