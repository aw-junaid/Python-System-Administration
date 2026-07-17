#!/usr/bin/env python3
"""
schedule_with_cron.py
---------------------------
Adds, lists, or removes an entry in the current user's crontab (Linux/macOS)
to run a command on a schedule using standard cron syntax. This script
manages OS-level cron jobs — it does not need to keep running itself.

Requires: pip install python-crontab
Platform: Linux/macOS only (cron is not available on Windows;
          see windows_task_scheduler.py for the Windows equivalent).

Usage:
    python schedule_with_cron.py add "<cron_expression>" "<command>" [--comment "label"]
    python schedule_with_cron.py list
    python schedule_with_cron.py remove --comment "label"

Example:
    python schedule_with_cron.py add "0 2 * * *" "python3 /home/user/backup.py" --comment "daily-backup"
    python schedule_with_cron.py list
    python schedule_with_cron.py remove --comment "daily-backup"
"""

import argparse
import platform
import sys

try:
    from crontab import CronTab
except ImportError:
    print("Error: the 'python-crontab' package is required.")
    print("Install it with: pip install -r requirements.txt")
    sys.exit(1)


def check_platform():
    if platform.system() == "Windows":
        print("Error: cron is not available on Windows.")
        print("Use windows_task_scheduler.py instead for scheduled tasks on Windows.")
        sys.exit(1)


def add_job(cron_expression: str, command: str, comment: str) -> None:
    cron = CronTab(user=True)

    job = cron.new(command=command, comment=comment or "")
    try:
        job.setall(cron_expression)
    except (KeyError, ValueError) as e:
        print(f"Error: invalid cron expression '{cron_expression}': {e}")
        sys.exit(1)

    if not job.is_valid():
        print(f"Error: cron expression '{cron_expression}' is not valid.")
        sys.exit(1)

    cron.write()
    print(f"Added cron job: '{cron_expression}' -> {command}")
    if comment:
        print(f"Comment/label: {comment}")
    print(f"Next run time: {job.schedule().get_next()}")


def list_jobs() -> None:
    cron = CronTab(user=True)
    jobs = list(cron)

    if not jobs:
        print("No cron jobs found for the current user.")
        return

    print(f"Cron jobs for current user ({len(jobs)}):\n")
    for job in jobs:
        status = "enabled" if job.is_enabled() else "disabled"
        print(f"[{status}] {job}")


def remove_jobs(comment: str) -> None:
    cron = CronTab(user=True)
    removed = cron.remove_all(comment=comment)
    cron.write()

    if removed:
        print(f"Removed {removed} job(s) with comment '{comment}'.")
    else:
        print(f"No jobs found with comment '{comment}'.")


def main():
    check_platform()

    parser = argparse.ArgumentParser(description="Manage cron jobs (add/list/remove).")
    subparsers = parser.add_subparsers(dest="action", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new cron job")
    add_parser.add_argument("cron_expression", help="Cron schedule expression, e.g. '0 2 * * *'")
    add_parser.add_argument("command", help="Command to run")
    add_parser.add_argument("--comment", default="", help="Label to identify this job later")

    subparsers.add_parser("list", help="List all cron jobs for the current user")

    remove_parser = subparsers.add_parser("remove", help="Remove cron job(s) by comment/label")
    remove_parser.add_argument("--comment", required=True, help="Label of the job(s) to remove")

    args = parser.parse_args()

    if args.action == "add":
        add_job(args.cron_expression, args.command, args.comment)
    elif args.action == "list":
        list_jobs()
    elif args.action == "remove":
        remove_jobs(args.comment)


if __name__ == "__main__":
    main()
