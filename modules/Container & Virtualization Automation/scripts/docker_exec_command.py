#!/usr/bin/env python3
"""
docker_exec_command.py
Run a shell command directly inside a running container's filesystem, for
quick administration or troubleshooting tasks.

USAGE
    python docker_exec_command.py --name web --cmd "ls -la /app"
    python docker_exec_command.py --name web --cmd "cat /etc/os-release" --user root
    python docker_exec_command.py --name web --cmd "env" --workdir /app

REQUIREMENTS
    - Docker Engine/Desktop installed and running
    - The target container must already be running
    - pip install -r requirements.txt

EXPECTED OUTPUT
    The stdout/stderr produced by the command inside the container, followed
    by the exit code, e.g.:
        total 24
        drwxr-xr-x 3 root root 4096 Jul 17 10:00 .
        ...
        Exit code: 0
"""

import argparse
import shlex

import docker
from docker.errors import APIError, NotFound


def exec_command(args):
    client = docker.from_env()
    try:
        container = client.containers.get(args.name)
    except NotFound:
        print(f"Container '{args.name}' not found.")
        return

    if container.status != "running":
        print(f"Container '{args.name}' is not running (status={container.status}).")
        return

    cmd = shlex.split(args.cmd)
    try:
        result = container.exec_run(
            cmd,
            user=args.user or "",
            workdir=args.workdir or None,
            environment=None,
        )
        output = result.output.decode("utf-8", errors="replace")
        print(output)
        print(f"Exit code: {result.exit_code}")
    except APIError as e:
        print(f"Exec failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="Execute a command inside a running Docker container.")
    parser.add_argument("--name", required=True, help="Container name or id")
    parser.add_argument("--cmd", required=True, help="Command to run, e.g. \"ls -la /app\"")
    parser.add_argument("--user", help="Run the command as this user, e.g. root")
    parser.add_argument("--workdir", help="Working directory inside the container")
    args = parser.parse_args()
    exec_command(args)


if __name__ == "__main__":
    main()
