#!/usr/bin/env python3
"""
docker_run_container.py
Launch and manage a container's lifecycle (run, stop, remove) with custom
ports, volumes, and environment variables via the Docker SDK for Python.

USAGE
    Run a container:
        python docker_run_container.py run --image nginx:latest --name web \
            --port 8080:80 --volume /host/data:/data --env KEY=VALUE --detach

    Stop a container:
        python docker_run_container.py stop --name web

    Remove a container:
        python docker_run_container.py rm --name web --force

REQUIREMENTS
    - Docker Engine/Desktop installed and running
    - pip install -r requirements.txt

EXPECTED OUTPUT
    run   -> prints the new container's id, name and status ("running")
    stop  -> prints "Container 'web' stopped."
    rm    -> prints "Container 'web' removed."
"""

import argparse

import docker
from docker.errors import APIError, NotFound


def parse_kv_list(pairs):
    result = {}
    for pair in pairs or []:
        if "=" not in pair:
            continue
        k, v = pair.split("=", 1)
        result[k] = v
    return result


def parse_ports(pairs):
    # host:container -> {"container/tcp": host}
    ports = {}
    for pair in pairs or []:
        host, container = pair.split(":")
        ports[f"{container}/tcp"] = int(host)
    return ports


def parse_volumes(pairs):
    # host:container[:mode] -> {"host": {"bind": "container", "mode": "rw"}}
    volumes = {}
    for pair in pairs or []:
        parts = pair.split(":")
        host, container = parts[0], parts[1]
        mode = parts[2] if len(parts) > 2 else "rw"
        volumes[host] = {"bind": container, "mode": mode}
    return volumes


def run_container(args):
    client = docker.from_env()
    try:
        container = client.containers.run(
            image=args.image,
            name=args.name,
            ports=parse_ports(args.port),
            volumes=parse_volumes(args.volume),
            environment=parse_kv_list(args.env),
            detach=True,
        )
        container.reload()
        print(f"Container started: id={container.short_id} name={container.name} status={container.status}")
    except APIError as e:
        print(f"Failed to run container: {e}")


def stop_container(args):
    client = docker.from_env()
    try:
        container = client.containers.get(args.name)
        container.stop()
        print(f"Container '{args.name}' stopped.")
    except NotFound:
        print(f"Container '{args.name}' not found.")


def remove_container(args):
    client = docker.from_env()
    try:
        container = client.containers.get(args.name)
        container.remove(force=args.force)
        print(f"Container '{args.name}' removed.")
    except NotFound:
        print(f"Container '{args.name}' not found.")


def main():
    parser = argparse.ArgumentParser(description="Manage the lifecycle of Docker containers.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="Run a new container")
    p_run.add_argument("--image", required=True)
    p_run.add_argument("--name", required=True)
    p_run.add_argument("--port", action="append", help="host:container, repeatable")
    p_run.add_argument("--volume", action="append", help="host:container[:mode], repeatable")
    p_run.add_argument("--env", action="append", help="KEY=VALUE, repeatable")
    p_run.add_argument("--detach", action="store_true", help="(kept for CLI familiarity; always detached)")
    p_run.set_defaults(func=run_container)

    p_stop = sub.add_parser("stop", help="Stop a running container")
    p_stop.add_argument("--name", required=True)
    p_stop.set_defaults(func=stop_container)

    p_rm = sub.add_parser("rm", help="Remove a container")
    p_rm.add_argument("--name", required=True)
    p_rm.add_argument("--force", action="store_true")
    p_rm.set_defaults(func=remove_container)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
