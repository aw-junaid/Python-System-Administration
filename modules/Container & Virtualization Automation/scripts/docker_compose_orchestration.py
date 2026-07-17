#!/usr/bin/env python3
"""
docker_compose_orchestration.py
Define and control the entire lifecycle of a multi-service application
programmatically, driving Docker Compose through the python-on-whales library
(a Python wrapper around the `docker compose` CLI).

USAGE
    python docker_compose_orchestration.py up --file docker-compose.yml
    python docker_compose_orchestration.py ps --file docker-compose.yml
    python docker_compose_orchestration.py logs --file docker-compose.yml --service web
    python docker_compose_orchestration.py down --file docker-compose.yml

REQUIREMENTS
    - Docker Engine/Desktop installed and running, with the Compose plugin
      available (`docker compose version` should work in your terminal)
    - A valid docker-compose.yml file in your project
    - pip install -r requirements.txt   (installs python-on-whales)

EXPECTED OUTPUT
    up     -> builds/pulls images, starts all services, prints running service names
    ps     -> table of service name, status and exposed ports
    logs   -> streamed log lines for the requested service (or all services)
    down   -> stops and removes containers/networks created by `up`
"""

import argparse

from python_on_whales import DockerClient


def up(args):
    docker = DockerClient(compose_files=[args.file])
    docker.compose.up(detach=True, build=args.build)
    print("Services started:")
    for c in docker.compose.ps():
        print(f"  - {c.name} ({c.state.status})")


def down(args):
    docker = DockerClient(compose_files=[args.file])
    docker.compose.down(volumes=args.volumes)
    print("Compose stack stopped and removed.")


def ps(args):
    docker = DockerClient(compose_files=[args.file])
    containers = docker.compose.ps()
    if not containers:
        print("No running services.")
        return
    print(f"{'SERVICE':20} {'STATUS':15} {'PORTS'}")
    for c in containers:
        ports = ", ".join(f"{p}" for p in (c.network_settings.ports or {}))
        print(f"{c.name:20} {c.state.status:15} {ports}")


def logs(args):
    docker = DockerClient(compose_files=[args.file])
    services = [args.service] if args.service else None
    for line in docker.compose.logs(services=services, follow=args.follow, stream=True):
        print(line)


def main():
    parser = argparse.ArgumentParser(description="Control a Docker Compose stack programmatically.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_up = sub.add_parser("up", help="Start all services defined in the compose file")
    p_up.add_argument("--file", default="docker-compose.yml")
    p_up.add_argument("--build", action="store_true", help="Rebuild images before starting")
    p_up.set_defaults(func=up)

    p_down = sub.add_parser("down", help="Stop and remove the compose stack")
    p_down.add_argument("--file", default="docker-compose.yml")
    p_down.add_argument("--volumes", action="store_true", help="Also remove named volumes")
    p_down.set_defaults(func=down)

    p_ps = sub.add_parser("ps", help="List running services")
    p_ps.add_argument("--file", default="docker-compose.yml")
    p_ps.set_defaults(func=ps)

    p_logs = sub.add_parser("logs", help="Stream logs for a service (or all)")
    p_logs.add_argument("--file", default="docker-compose.yml")
    p_logs.add_argument("--service", help="Specific service name; omit for all services")
    p_logs.add_argument("--follow", action="store_true", help="Keep streaming new log lines")
    p_logs.set_defaults(func=logs)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
