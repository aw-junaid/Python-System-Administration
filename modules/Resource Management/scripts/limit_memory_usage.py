#!/usr/bin/env python3
"""
limit_memory_usage.py
----------------------------
Runs a command/process while limiting how much memory (RAM) it can use,
using the 'resource' module (RLIMIT_AS) on Linux/macOS.

On Windows, hard memory limits via RLIMIT are not supported; this script
will inform you and fall back to running without a hard limit.

Usage:
    python limit_memory_usage.py <memory_mb> -- <command> [args...]

Example:
    python limit_memory_usage.py 200 -- python3 -c "x = 'a' * (500 * 1024 * 1024)"
    # The process will fail to allocate memory once it exceeds 200 MB.
"""

import argparse
import platform
import subprocess
import sys


def limit_memory_and_run(memory_mb: int, command: list) -> int:
    if platform.system() == "Windows":
        print("Warning: hard memory limits (RLIMIT_AS) are not supported on Windows.")
        print("Running the command WITHOUT a memory limit. Consider using Job Objects for this on Windows.")
        result = subprocess.run(command)
        return result.returncode

    import resource

    memory_bytes = memory_mb * 1024 * 1024

    def limit_memory():
        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))

    print(f"Running command with a memory limit of {memory_mb} MB: {' '.join(command)}")

    try:
        result = subprocess.run(command, preexec_fn=limit_memory)
        return result.returncode
    except FileNotFoundError:
        print(f"Error: command not found: {command[0]}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Run a command with a memory usage limit.",
        usage="limit_memory_usage.py <memory_mb> -- <command> [args...]",
    )
    parser.add_argument("memory_mb", type=int, help="Maximum memory in megabytes")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run, after '--'")
    args = parser.parse_args()

    command = args.command
    if command and command[0] == "--":
        command = command[1:]

    if not command:
        print("Error: no command provided. Usage: limit_memory_usage.py <memory_mb> -- <command> [args...]")
        sys.exit(1)

    exit_code = limit_memory_and_run(args.memory_mb, command)

    print(f"\nCommand finished with exit code: {exit_code}")
    if exit_code != 0:
        print("Non-zero exit code may indicate the process hit the memory limit (e.g. MemoryError, SIGKILL, SIGSEGV).")


if __name__ == "__main__":
    main()
