#!/usr/bin/env python3
"""
set_process_priority.py
-----------------------------
Sets the CPU scheduling priority (niceness) of a running process by PID,
or launches a new command at a given priority.

On Linux/macOS, priority ("niceness") ranges from -20 (highest priority)
to 19 (lowest priority). Setting negative values usually requires root/sudo.

On Windows, priority classes are used instead (via psutil).

Requires: pip install psutil

Usage:
    python set_process_priority.py --pid <pid> --priority <value>
    python set_process_priority.py --priority <value> -- <command> [args...]

Example:
    python set_process_priority.py --pid 1234 --priority 10
    python set_process_priority.py --priority -5 -- python3 my_script.py
"""

import argparse
import platform
import subprocess
import sys

try:
    import psutil
except ImportError:
    print("Error: the 'psutil' package is required.")
    print("Install it with: pip install -r requirements.txt")
    sys.exit(1)


def set_priority_by_pid(pid: int, priority: int) -> None:
    try:
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        print(f"Error: no process found with PID {pid}.")
        sys.exit(1)

    try:
        if platform.system() == "Windows":
            priority_map = {
                -20: psutil.REALTIME_PRIORITY_CLASS,
                -15: psutil.HIGH_PRIORITY_CLASS,
                -5: psutil.ABOVE_NORMAL_PRIORITY_CLASS,
                0: psutil.NORMAL_PRIORITY_CLASS,
                10: psutil.BELOW_NORMAL_PRIORITY_CLASS,
                19: psutil.IDLE_PRIORITY_CLASS,
            }
            closest = min(priority_map.keys(), key=lambda k: abs(k - priority))
            proc.nice(priority_map[closest])
            print(f"Set process {pid} ({proc.name()}) to Windows priority class matching niceness ~{closest}.")
        else:
            proc.nice(priority)
            print(f"Set process {pid} ({proc.name()}) niceness to {priority}.")
    except psutil.AccessDenied:
        print("Error: permission denied. Setting this priority may require root/administrator privileges.")
        sys.exit(1)


def launch_with_priority(priority: int, command: list) -> None:
    print(f"Launching command with priority {priority}: {' '.join(command)}")

    try:
        process = subprocess.Popen(command)
    except FileNotFoundError:
        print(f"Error: command not found: {command[0]}")
        sys.exit(1)

    try:
        proc = psutil.Process(process.pid)
        if platform.system() == "Windows":
            priority_map = {
                -20: psutil.REALTIME_PRIORITY_CLASS,
                -15: psutil.HIGH_PRIORITY_CLASS,
                -5: psutil.ABOVE_NORMAL_PRIORITY_CLASS,
                0: psutil.NORMAL_PRIORITY_CLASS,
                10: psutil.BELOW_NORMAL_PRIORITY_CLASS,
                19: psutil.IDLE_PRIORITY_CLASS,
            }
            closest = min(priority_map.keys(), key=lambda k: abs(k - priority))
            proc.nice(priority_map[closest])
        else:
            proc.nice(priority)
        print(f"Process launched with PID {process.pid} at the requested priority.")
    except psutil.AccessDenied:
        print("Warning: could not set priority (permission denied). Process is still running at default priority.")

    process.wait()
    print(f"\nProcess finished with exit code: {process.returncode}")


def main():
    parser = argparse.ArgumentParser(description="Set process priority (niceness) for a running or new process.")
    parser.add_argument("--pid", type=int, default=None, help="PID of an existing process to re-prioritize")
    parser.add_argument("--priority", type=int, required=True,
                         help="Priority/niceness value (-20 highest to 19 lowest on Linux/macOS)")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to launch (if not using --pid), after '--'")
    args = parser.parse_args()

    if args.pid:
        set_priority_by_pid(args.pid, args.priority)
    else:
        command = args.command
        if command and command[0] == "--":
            command = command[1:]

        if not command:
            print("Error: provide either --pid <pid> or a command to launch after '--'.")
            sys.exit(1)

        launch_with_priority(args.priority, command)


if __name__ == "__main__":
    main()
