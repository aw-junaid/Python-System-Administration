#!/usr/bin/env python3
"""
lxc_manage.py
Manage lightweight LXD system containers (full OS environments with
near-native performance) programmatically via the pylxd library.

USAGE
    python lxc_manage.py launch --name test-ct --image ubuntu:22.04
    python lxc_manage.py list
    python lxc_manage.py stop --name test-ct
    python lxc_manage.py start --name test-ct
    python lxc_manage.py delete --name test-ct --force

REQUIREMENTS
    - LXD installed and initialized on this machine:
        sudo snap install lxd
        sudo lxd init
    - Your user must be in the 'lxd' group, or run with sudo
    - pip install -r requirements.txt   (installs pylxd)
    - LXD's local UNIX socket must be reachable (default: /var/snap/lxd/common/lxd/unix.socket)

EXPECTED OUTPUT
    launch -> "Container 'test-ct' launched from image 'ubuntu:22.04' (status=Running)."
    list   -> table of container names and statuses
    stop   -> "Container 'test-ct' stopped."
    start  -> "Container 'test-ct' started."
    delete -> "Container 'test-ct' deleted."
"""

import argparse
import sys

import pylxd
from pylxd.exceptions import LXDAPIException, NotFound


def get_client():
    try:
        return pylxd.Client()
    except Exception as e:
        print(f"Could not connect to the local LXD daemon: {e}")
        sys.exit(1)


def launch(args):
    client = get_client()
    config = {
        "name": args.name,
        "source": {"type": "image", "alias": args.image},
    }
    container = client.containers.create(config, wait=True)
    container.start(wait=True)
    container.sync()
    print(f"Container '{args.name}' launched from image '{args.image}' (status={container.status}).")


def list_containers(args):
    client = get_client()
    containers = client.containers.all()
    if not containers:
        print("No containers found.")
        return
    print(f"{'NAME':25} {'STATUS':15}")
    for c in containers:
        print(f"{c.name:25} {c.status:15}")


def stop(args):
    client = get_client()
    try:
        container = client.containers.get(args.name)
        container.stop(wait=True)
        print(f"Container '{args.name}' stopped.")
    except NotFound:
        print(f"Container '{args.name}' not found.")


def start(args):
    client = get_client()
    try:
        container = client.containers.get(args.name)
        container.start(wait=True)
        print(f"Container '{args.name}' started.")
    except NotFound:
        print(f"Container '{args.name}' not found.")


def delete(args):
    client = get_client()
    try:
        container = client.containers.get(args.name)
        if container.status == "Running" and args.force:
            container.stop(wait=True)
        container.delete(wait=True)
        print(f"Container '{args.name}' deleted.")
    except NotFound:
        print(f"Container '{args.name}' not found.")
    except LXDAPIException as e:
        print(f"Could not delete container (is it still running? use --force): {e}")


def main():
    parser = argparse.ArgumentParser(description="Manage LXC/LXD containers programmatically.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_launch = sub.add_parser("launch")
    p_launch.add_argument("--name", required=True)
    p_launch.add_argument("--image", required=True, help="Image alias, e.g. ubuntu:22.04")
    p_launch.set_defaults(func=launch)

    p_list = sub.add_parser("list")
    p_list.set_defaults(func=list_containers)

    p_stop = sub.add_parser("stop")
    p_stop.add_argument("--name", required=True)
    p_stop.set_defaults(func=stop)

    p_start = sub.add_parser("start")
    p_start.add_argument("--name", required=True)
    p_start.set_defaults(func=start)

    p_delete = sub.add_parser("delete")
    p_delete.add_argument("--name", required=True)
    p_delete.add_argument("--force", action="store_true", help="Stop the container first if it is running")
    p_delete.set_defaults(func=delete)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
