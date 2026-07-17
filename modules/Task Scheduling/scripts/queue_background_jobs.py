#!/usr/bin/env python3
"""
queue_background_jobs.py
------------------------------
A simple background job queue: add commands to a persistent queue (a local
JSON file), then run a worker that processes them one at a time in the
background, in order, logging results. Useful for queuing up several
one-off tasks (e.g. file conversions, uploads) to run sequentially without
overlapping.

Usage:
    python queue_background_jobs.py add "<command>"
    python queue_background_jobs.py list
    python queue_background_jobs.py worker [--once]

Example:
    python queue_background_jobs.py add "python3 convert.py file1.csv"
    python queue_background_jobs.py add "python3 convert.py file2.csv"
    python queue_background_jobs.py list
    python queue_background_jobs.py worker
    # Processes all queued jobs one by one, then exits.
    # Use without --once to keep watching for new jobs indefinitely.

Queue file: job_queue.json (created in the current directory)
Log file:   job_queue.log  (created in the current directory)
"""

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from datetime import datetime

QUEUE_FILE = "job_queue.json"
LOG_FILE = "job_queue.log"


def load_queue() -> list:
    if not os.path.exists(QUEUE_FILE):
        return []
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_queue(queue: list) -> None:
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2)


def log(message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def add_job(command: str) -> None:
    queue = load_queue()
    job = {
        "id": len(queue) + 1 if not queue else max(j["id"] for j in queue) + 1,
        "command": command,
        "status": "pending",
        "added_at": datetime.now().isoformat(timespec="seconds"),
    }
    queue.append(job)
    save_queue(queue)
    print(f"Job #{job['id']} added to queue: {command}")


def list_jobs() -> None:
    queue = load_queue()
    if not queue:
        print("Queue is empty.")
        return

    print(f"Jobs in queue ({len(queue)}):\n")
    for job in queue:
        print(f"#{job['id']:<4} [{job['status']:<10}] {job['command']}")


def process_job(job: dict) -> None:
    log(f"Starting job #{job['id']}: {job['command']}")

    try:
        result = subprocess.run(shlex.split(job["command"]), capture_output=True, text=True)
        job["status"] = "completed" if result.returncode == 0 else "failed"
        job["exit_code"] = result.returncode

        if result.stdout:
            log(f"Job #{job['id']} output: {result.stdout.strip()}")
        if result.returncode != 0 and result.stderr:
            log(f"Job #{job['id']} error: {result.stderr.strip()}")

    except FileNotFoundError:
        job["status"] = "failed"
        job["exit_code"] = -1
        log(f"Job #{job['id']} failed: command not found")

    log(f"Job #{job['id']} finished with status: {job['status']}")


def run_worker(run_once: bool, poll_interval: int = 5) -> None:
    print(f"Worker started. Log file: {LOG_FILE}")
    if run_once:
        print("Mode: process current queue once, then exit.\n")
    else:
        print(f"Mode: continuously poll for new jobs every {poll_interval}s. Press Ctrl+C to stop.\n")

    try:
        while True:
            queue = load_queue()
            pending = [j for j in queue if j["status"] == "pending"]

            if not pending:
                if run_once:
                    print("No pending jobs. Exiting.")
                    return
                time.sleep(poll_interval)
                continue

            for job in pending:
                process_job(job)
                save_queue(queue)

            if run_once:
                print("\nAll queued jobs processed.")
                return

    except KeyboardInterrupt:
        print("\nWorker stopped.")


def main():
    parser = argparse.ArgumentParser(description="Queue and process background jobs sequentially.")
    subparsers = parser.add_subparsers(dest="action", required=True)

    add_parser = subparsers.add_parser("add", help="Add a command to the job queue")
    add_parser.add_argument("command", help="Command to queue (quote it if it has spaces/args)")

    subparsers.add_parser("list", help="List all jobs in the queue")

    worker_parser = subparsers.add_parser("worker", help="Process jobs from the queue")
    worker_parser.add_argument("--once", action="store_true", help="Process current queue then exit (default: keep polling)")
    worker_parser.add_argument("--interval", type=int, default=5, help="Poll interval in seconds when not using --once (default: 5)")

    args = parser.parse_args()

    if args.action == "add":
        add_job(args.command)
    elif args.action == "list":
        list_jobs()
    elif args.action == "worker":
        run_worker(args.once, args.interval)


if __name__ == "__main__":
    main()
