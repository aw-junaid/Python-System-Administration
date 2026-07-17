#!/usr/bin/env python3
"""
docker_manage_volumes.py
Programmatically create, inspect, list, and remove Docker volumes used for
persistent storage in containerized applications.

USAGE
    python docker_manage_volumes.py create --name app_data
    python docker_manage_volumes.py list
    python docker_manage_volumes.py inspect --name app_data
    python docker_manage_volumes.py remove --name app_data
    python docker_manage_volumes.py prune

REQUIREMENTS
    - Docker Engine/Desktop installed and running
    - pip install -r requirements.txt

EXPECTED OUTPUT
    create   -> "Volume 'app_data' created (driver=local)."
    list     -> a table of existing volume names and drivers
    inspect  -> the raw JSON metadata of the volume (mountpoint, labels, etc.)
    remove   -> "Volume 'app_data' removed."
    prune    -> number of unused volumes deleted and space reclaimed
"""

import argparse
import json

import docker
from docker.errors import APIError, NotFound


def create_volume(args):
    client = docker.from_env()
    volume = client.volumes.create(name=args.name, driver=args.driver)
    print(f"Volume '{volume.name}' created (driver={args.driver}).")


def list_volumes(args):
    client = docker.from_env()
    volumes = client.volumes.list()
    if not volumes:
        print("No volumes found.")
        return
    print(f"{'NAME':30} {'DRIVER':10}")
    for v in volumes:
        print(f"{v.name:30} {v.attrs.get('Driver', ''):10}")


def inspect_volume(args):
    client = docker.from_env()
    try:
        volume = client.volumes.get(args.name)
        print(json.dumps(volume.attrs, indent=2))
    except NotFound:
        print(f"Volume '{args.name}' not found.")


def remove_volume(args):
    client = docker.from_env()
    try:
        volume = client.volumes.get(args.name)
        volume.remove(force=args.force)
        print(f"Volume '{args.name}' removed.")
    except NotFound:
        print(f"Volume '{args.name}' not found.")
    except APIError as e:
        print(f"Could not remove volume: {e}")


def prune_volumes(args):
    client = docker.from_env()
    result = client.volumes.prune()
    reclaimed = result.get("SpaceReclaimed", 0)
    deleted = result.get("VolumesDeleted", []) or []
    print(f"Pruned {len(deleted)} unused volume(s), reclaimed {reclaimed} bytes.")


def main():
    parser = argparse.ArgumentParser(description="Manage Docker volumes programmatically.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create")
    p_create.add_argument("--name", required=True)
    p_create.add_argument("--driver", default="local")
    p_create.set_defaults(func=create_volume)

    p_list = sub.add_parser("list")
    p_list.set_defaults(func=list_volumes)

    p_inspect = sub.add_parser("inspect")
    p_inspect.add_argument("--name", required=True)
    p_inspect.set_defaults(func=inspect_volume)

    p_remove = sub.add_parser("remove")
    p_remove.add_argument("--name", required=True)
    p_remove.add_argument("--force", action="store_true")
    p_remove.set_defaults(func=remove_volume)

    p_prune = sub.add_parser("prune")
    p_prune.set_defaults(func=prune_volumes)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
