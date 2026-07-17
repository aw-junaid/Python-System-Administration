#!/usr/bin/env python3
"""
docker_manage_networks.py
Create, list, inspect, and remove Docker networks, and connect/disconnect
containers to control communication between containers and the outside world.

USAGE
    python docker_manage_networks.py create --name backend --driver bridge --internal
    python docker_manage_networks.py list
    python docker_manage_networks.py connect --network backend --container web
    python docker_manage_networks.py disconnect --network backend --container web
    python docker_manage_networks.py remove --name backend

REQUIREMENTS
    - Docker Engine/Desktop installed and running
    - pip install -r requirements.txt

EXPECTED OUTPUT
    create      -> "Network 'backend' created (driver=bridge, internal=True)."
    list        -> table of network names, drivers and scope
    connect     -> "Connected container 'web' to network 'backend'."
    disconnect  -> "Disconnected container 'web' from network 'backend'."
    remove      -> "Network 'backend' removed."
"""

import argparse

import docker
from docker.errors import APIError, NotFound


def create_network(args):
    client = docker.from_env()
    network = client.networks.create(
        name=args.name, driver=args.driver, internal=args.internal
    )
    print(f"Network '{network.name}' created (driver={args.driver}, internal={args.internal}).")


def list_networks(args):
    client = docker.from_env()
    networks = client.networks.list()
    print(f"{'NAME':25} {'DRIVER':10} {'SCOPE':10}")
    for n in networks:
        print(f"{n.name:25} {n.attrs.get('Driver',''):10} {n.attrs.get('Scope',''):10}")


def connect(args):
    client = docker.from_env()
    try:
        network = client.networks.get(args.network)
        network.connect(args.container)
        print(f"Connected container '{args.container}' to network '{args.network}'.")
    except (NotFound, APIError) as e:
        print(f"Could not connect: {e}")


def disconnect(args):
    client = docker.from_env()
    try:
        network = client.networks.get(args.network)
        network.disconnect(args.container)
        print(f"Disconnected container '{args.container}' from network '{args.network}'.")
    except (NotFound, APIError) as e:
        print(f"Could not disconnect: {e}")


def remove_network(args):
    client = docker.from_env()
    try:
        network = client.networks.get(args.name)
        network.remove()
        print(f"Network '{args.name}' removed.")
    except NotFound:
        print(f"Network '{args.name}' not found.")
    except APIError as e:
        print(f"Could not remove network: {e}")


def main():
    parser = argparse.ArgumentParser(description="Manage Docker networks programmatically.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create")
    p_create.add_argument("--name", required=True)
    p_create.add_argument("--driver", default="bridge")
    p_create.add_argument("--internal", action="store_true", help="Isolate network from external access")
    p_create.set_defaults(func=create_network)

    p_list = sub.add_parser("list")
    p_list.set_defaults(func=list_networks)

    p_conn = sub.add_parser("connect")
    p_conn.add_argument("--network", required=True)
    p_conn.add_argument("--container", required=True)
    p_conn.set_defaults(func=connect)

    p_disc = sub.add_parser("disconnect")
    p_disc.add_argument("--network", required=True)
    p_disc.add_argument("--container", required=True)
    p_disc.set_defaults(func=disconnect)

    p_remove = sub.add_parser("remove")
    p_remove.add_argument("--name", required=True)
    p_remove.set_defaults(func=remove_network)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
