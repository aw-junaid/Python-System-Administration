#!/usr/bin/env python3
"""
windows_task_scheduler.py
-------------------------------
Adds, lists, or removes a Windows Task Scheduler task to run a command
on a schedule, using the built-in 'schtasks' command-line tool via subprocess.

Platform: Windows only.

Usage:
    python windows_task_scheduler.py add <task_name> <command> --schedule <DAILY|WEEKLY|HOURLY|ONCE> --time HH:MM
    python windows_task_scheduler.py list
    python windows_task_scheduler.py remove <task_name>

Example:
    python windows_task_scheduler.py add "DailyBackup" "C:\\Python312\\python.exe C:\\scripts\\backup.py" --schedule DAILY --time 02:00
    python windows_task_scheduler.py list
    python windows_task_scheduler.py remove "DailyBackup"
"""

import argparse
import platform
import subprocess
import sys


def check_platform():
    if platform.system() != "Windows":
        print("Error: this script only works on Windows (it wraps the 'schtasks' command).")
        print("Use schedule_with_cron.py for Linux/macOS, or schedule_with_library.py for a cross-platform option.")
        sys.exit(1)


def add_task(task_name: str, command: str, schedule_type: str, time_str: str) -> None:
    cmd = [
        "schtasks", "/Create",
        "/TN", task_name,
        "/TR", command,
        "/SC", schedule_type,
        "/ST", time_str,
        "/F",  # Force overwrite if it already exists
    ]

    print(f"Creating scheduled task '{task_name}'...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"Task '{task_name}' created successfully.")
        print(result.stdout.strip())
    else:
        print("Error creating task:")
        print(result.stderr.strip())
        sys.exit(1)


def list_tasks() -> None:
    result = subprocess.run(["schtasks", "/Query", "/FO", "LIST"], capture_output=True, text=True)

    if result.returncode == 0:
        print(result.stdout)
    else:
        print("Error listing tasks:")
        print(result.stderr.strip())
        sys.exit(1)


def remove_task(task_name: str) -> None:
    result = subprocess.run(["schtasks", "/Delete", "/TN", task_name, "/F"], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"Task '{task_name}' removed successfully.")
    else:
        print("Error removing task:")
        print(result.stderr.strip())
        sys.exit(1)


def main():
    check_platform()

    parser = argparse.ArgumentParser(description="Manage Windows Task Scheduler tasks (add/list/remove).")
    subparsers = parser.add_subparsers(dest="action", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new scheduled task")
    add_parser.add_argument("task_name", help="Name for the scheduled task")
    add_parser.add_argument("command", help="Full command to run (quote if it has spaces)")
    add_parser.add_argument("--schedule", default="DAILY",
                             choices=["MINUTE", "HOURLY", "DAILY", "WEEKLY", "ONCE"],
                             help="Schedule type (default: DAILY)")
    add_parser.add_argument("--time", default="09:00", help="Start time in HH:MM 24-hour format (default: 09:00)")

    subparsers.add_parser("list", help="List all scheduled tasks")

    remove_parser = subparsers.add_parser("remove", help="Remove a scheduled task by name")
    remove_parser.add_argument("task_name", help="Name of the task to remove")

    args = parser.parse_args()

    if args.action == "add":
        add_task(args.task_name, args.command, args.schedule, args.time)
    elif args.action == "list":
        list_tasks()
    elif args.action == "remove":
        remove_task(args.task_name)


if __name__ == "__main__":
    main()
