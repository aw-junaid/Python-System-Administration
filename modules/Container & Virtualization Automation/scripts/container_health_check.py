#!/usr/bin/env python3
"""
container_health_check.py
Define a Docker HEALTHCHECK on a running container's image and verify
readiness/liveness by polling the container's reported health status, to
confirm a service is actually operational (not just "running").

USAGE
    Run a container with a health check attached:
        python container_health_check.py run --image nginx:latest --name web \
            --test "curl -f http://localhost/ || exit 1" \
            --interval 10 --timeout 5 --retries 3 --start-period 5

    Poll the health status of an existing container until healthy or timeout:
        python container_health_check.py check --name web --wait 60

REQUIREMENTS
    - Docker Engine/Desktop installed and running
    - The container's image must have the tool used in --test available
      (e.g. curl or wget) or the health check will always fail
    - pip install -r requirements.txt

EXPECTED OUTPUT
    run   -> "Container 'web' started with health check attached."
    check -> polls every 2 seconds and prints status transitions, e.g.:
                [0s] status=starting
                [10s] status=healthy
             then "Container 'web' is healthy." or exits with an error after
             the --wait timeout if it never becomes healthy.
"""

import argparse
import sys
import time

import docker
from docker.errors import APIError, NotFound


def run_with_healthcheck(args):
    client = docker.from_env()
    healthcheck = {
        "test": ["CMD-SHELL", args.test],
        "interval": args.interval * 1_000_000_000,
        "timeout": args.timeout * 1_000_000_000,
        "retries": args.retries,
        "start_period": args.start_period * 1_000_000_000,
    }
    try:
        client.containers.run(
            image=args.image,
            name=args.name,
            detach=True,
            healthcheck=healthcheck,
        )
        print(f"Container '{args.name}' started with health check attached.")
    except APIError as e:
        print(f"Failed to start container: {e}")
        sys.exit(1)


def check_health(args):
    client = docker.from_env()
    try:
        container = client.containers.get(args.name)
    except NotFound:
        print(f"Container '{args.name}' not found.")
        sys.exit(1)

    elapsed = 0
    poll_interval = 2
    while elapsed <= args.wait:
        container.reload()
        health = container.attrs.get("State", {}).get("Health", {})
        status = health.get("Status", "unknown")
        print(f"[{elapsed}s] status={status}")
        if status == "healthy":
            print(f"Container '{args.name}' is healthy.")
            return
        if status == "unhealthy":
            print(f"Container '{args.name}' is unhealthy.")
            sys.exit(1)
        time.sleep(poll_interval)
        elapsed += poll_interval

    print(f"Timed out after {args.wait}s waiting for '{args.name}' to become healthy.")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Attach and verify Docker container health checks.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="Run a container with a HEALTHCHECK attached")
    p_run.add_argument("--image", required=True)
    p_run.add_argument("--name", required=True)
    p_run.add_argument("--test", required=True, help="Shell command; exit 0 = healthy, non-zero = unhealthy")
    p_run.add_argument("--interval", type=int, default=30, help="Seconds between checks")
    p_run.add_argument("--timeout", type=int, default=10, help="Seconds before a check itself times out")
    p_run.add_argument("--retries", type=int, default=3, help="Consecutive failures before marking unhealthy")
    p_run.add_argument("--start-period", type=int, default=0, help="Grace period in seconds before checks count")
    p_run.set_defaults(func=run_with_healthcheck)

    p_check = sub.add_parser("check", help="Poll an existing container's health status")
    p_check.add_argument("--name", required=True)
    p_check.add_argument("--wait", type=int, default=60, help="Max seconds to wait for a healthy status")
    p_check.set_defaults(func=check_health)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
