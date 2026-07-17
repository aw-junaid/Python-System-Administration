#!/usr/bin/env python3
"""
docker_prune_resources.py
Automatically clean up dangling images, stopped containers, unused networks,
and orphaned volumes to free disk space.

USAGE
    python docker_prune_resources.py --all
    python docker_prune_resources.py --containers --images
    python docker_prune_resources.py --volumes --networks

REQUIREMENTS
    - Docker Engine/Desktop installed and running
    - pip install -r requirements.txt

EXPECTED OUTPUT
    A summary for each resource type pruned, e.g.:
        Containers pruned: 3 removed
        Images pruned: 5 removed, 214582112 bytes reclaimed
        Volumes pruned: 1 removed, 10485760 bytes reclaimed
        Networks pruned: 2 removed
        Total space reclaimed: 225067872 bytes
"""

import argparse

import docker


def prune_containers(client):
    result = client.containers.prune()
    removed = result.get("ContainersDeleted", []) or []
    print(f"Containers pruned: {len(removed)} removed")
    return result.get("SpaceReclaimed", 0)


def prune_images(client, dangling_only):
    filters = {"dangling": True} if dangling_only else {}
    result = client.images.prune(filters=filters)
    removed = result.get("ImagesDeleted", []) or []
    space = result.get("SpaceReclaimed", 0)
    print(f"Images pruned: {len(removed)} removed, {space} bytes reclaimed")
    return space


def prune_volumes(client):
    result = client.volumes.prune()
    removed = result.get("VolumesDeleted", []) or []
    space = result.get("SpaceReclaimed", 0)
    print(f"Volumes pruned: {len(removed)} removed, {space} bytes reclaimed")
    return space


def prune_networks(client):
    result = client.networks.prune()
    removed = result.get("NetworksDeleted", []) or []
    print(f"Networks pruned: {len(removed)} removed")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Prune unused Docker resources.")
    parser.add_argument("--all", action="store_true", help="Prune containers, images, volumes and networks")
    parser.add_argument("--containers", action="store_true")
    parser.add_argument("--images", action="store_true")
    parser.add_argument("--volumes", action="store_true")
    parser.add_argument("--networks", action="store_true")
    parser.add_argument("--all-images", action="store_true", help="Prune ALL unused images, not just dangling ones")
    args = parser.parse_args()

    if not any([args.all, args.containers, args.images, args.volumes, args.networks]):
        parser.error("Specify --all or at least one of --containers/--images/--volumes/--networks")

    client = docker.from_env()
    total = 0

    if args.all or args.containers:
        total += prune_containers(client)
    if args.all or args.images:
        total += prune_images(client, dangling_only=not args.all_images)
    if args.all or args.volumes:
        total += prune_volumes(client)
    if args.all or args.networks:
        total += prune_networks(client)

    print(f"Total space reclaimed: {total} bytes")


if __name__ == "__main__":
    main()
