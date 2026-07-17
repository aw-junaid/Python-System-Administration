#!/usr/bin/env python3
"""
container_resource_limits.py
Set CPU and memory constraints on Docker containers, either at launch time
or on an already-running container, to prevent one service from starving
resources needed by others on the same host.

USAGE
    Run a new container with limits:
        python container_resource_limits.py run --image nginx:latest --name web \
            --cpus 1.5 --memory 512m --memory-swap 1g

    Update limits on an already-running container:
        python container_resource_limits.py update --name web --cpus 0.5 --memory 256m

    Inspect current limits:
        python container_resource_limits.py inspect --name web

REQUIREMENTS
    - Docker Engine/Desktop installed and running
    - pip install -r requirements.txt

EXPECTED OUTPUT
    run     -> "Container 'web' started with cpus=1.5 memory=512m."
    update  -> "Container 'web' updated with cpus=0.5 memory=256m."
    inspect -> current NanoCpus/CpuQuota and Memory limit values in bytes, e.g.:
                 CPU quota: 50000 / period: 100000 (~0.5 CPUs)
                 Memory limit: 268435456 bytes (256.0 MB)
"""

import argparse
import sys

import docker
from docker.errors import APIError, NotFound


def parse_memory(mem_str):
    """Return the human-readable string as-is; the Docker SDK accepts
    strings like '512m', '1g' directly for mem_limit/memswap_limit."""
    return mem_str


def cpus_to_quota(cpus):
    period = 100_000
    return int(cpus * period), period


def run_with_limits(args):
    client = docker.from_env()
    nano_cpus = int(args.cpus * 1_000_000_000) if args.cpus else None
    try:
        client.containers.run(
            image=args.image,
            name=args.name,
            detach=True,
            nano_cpus=nano_cpus,
            mem_limit=args.memory,
            memswap_limit=args.memory_swap,
        )
        print(f"Container '{args.name}' started with cpus={args.cpus} memory={args.memory}.")
    except APIError as e:
        print(f"Failed to start container: {e}")
        sys.exit(1)


def update_limits(args):
    client = docker.from_env()
    try:
        container = client.containers.get(args.name)
    except NotFound:
        print(f"Container '{args.name}' not found.")
        sys.exit(1)

    kwargs = {}
    if args.cpus:
        kwargs["nano_cpus"] = int(args.cpus * 1_000_000_000)
    if args.memory:
        kwargs["mem_limit"] = args.memory
    if args.memory_swap:
        kwargs["memswap_limit"] = args.memory_swap

    try:
        container.update(**kwargs)
        print(f"Container '{args.name}' updated with cpus={args.cpus} memory={args.memory}.")
    except APIError as e:
        print(f"Failed to update container: {e}")
        sys.exit(1)


def inspect_limits(args):
    client = docker.from_env()
    try:
        container = client.containers.get(args.name)
    except NotFound:
        print(f"Container '{args.name}' not found.")
        sys.exit(1)

    host_config = container.attrs.get("HostConfig", {})
    nano_cpus = host_config.get("NanoCpus", 0)
    cpu_quota = host_config.get("CpuQuota", 0)
    cpu_period = host_config.get("CpuPeriod", 0)
    memory = host_config.get("Memory", 0)

    if nano_cpus:
        print(f"CPU limit: {nano_cpus / 1_000_000_000} CPUs (NanoCpus)")
    elif cpu_quota and cpu_period:
        print(f"CPU quota: {cpu_quota} / period: {cpu_period} (~{cpu_quota / cpu_period} CPUs)")
    else:
        print("CPU limit: none set")

    if memory:
        print(f"Memory limit: {memory} bytes ({memory / (1024 * 1024):.1f} MB)")
    else:
        print("Memory limit: none set")


def main():
    parser = argparse.ArgumentParser(description="Set CPU and memory limits on Docker containers.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run")
    p_run.add_argument("--image", required=True)
    p_run.add_argument("--name", required=True)
    p_run.add_argument("--cpus", type=float, help="Number of CPUs, e.g. 1.5")
    p_run.add_argument("--memory", help="Memory limit, e.g. 512m, 1g")
    p_run.add_argument("--memory-swap", help="Total memory + swap limit, e.g. 1g")
    p_run.set_defaults(func=run_with_limits)

    p_update = sub.add_parser("update")
    p_update.add_argument("--name", required=True)
    p_update.add_argument("--cpus", type=float, help="Number of CPUs, e.g. 0.5")
    p_update.add_argument("--memory", help="Memory limit, e.g. 256m")
    p_update.add_argument("--memory-swap", help="Total memory + swap limit, e.g. 512m")
    p_update.set_defaults(func=update_limits)

    p_inspect = sub.add_parser("inspect")
    p_inspect.add_argument("--name", required=True)
    p_inspect.set_defaults(func=inspect_limits)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
