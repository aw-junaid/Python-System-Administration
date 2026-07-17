#!/usr/bin/env python3
"""
docker_monitor_logs.py
Stream and filter real-time log output from a running container, useful for
debugging and monitoring.

USAGE
    python docker_monitor_logs.py --name web --follow
    python docker_monitor_logs.py --name web --tail 100
    python docker_monitor_logs.py --name web --follow --filter ERROR

REQUIREMENTS
    - Docker Engine/Desktop installed and running, with the target container
      already created (running or stopped)
    - pip install -r requirements.txt

EXPECTED OUTPUT
    Log lines from the container are printed to stdout as they arrive.
    If --filter is given, only lines containing that substring (case
    insensitive) are printed, e.g.:
        [2026-07-17 10:00:01] ERROR: connection refused
    Press Ctrl+C to stop following.
"""

import argparse

import docker
from docker.errors import NotFound


def monitor(args):
    client = docker.from_env()
    try:
        container = client.containers.get(args.name)
    except NotFound:
        print(f"Container '{args.name}' not found.")
        return

    print(f"Streaming logs for '{args.name}' (tail={args.tail}, follow={args.follow}) ...")
    try:
        for raw_line in container.logs(stream=True, follow=args.follow, tail=args.tail):
            line = raw_line.decode("utf-8", errors="replace").rstrip()
            if args.filter and args.filter.lower() not in line.lower():
                continue
            print(line)
    except KeyboardInterrupt:
        print("\nStopped following logs.")


def main():
    parser = argparse.ArgumentParser(description="Stream and filter logs from a Docker container.")
    parser.add_argument("--name", required=True, help="Container name or id")
    parser.add_argument("--tail", default="all", help="Number of lines to show from the end of the logs")
    parser.add_argument("--follow", action="store_true", help="Keep streaming new log lines")
    parser.add_argument("--filter", help="Only show lines containing this substring")
    args = parser.parse_args()
    monitor(args)


if __name__ == "__main__":
    main()
