#!/usr/bin/env python3
"""
docker_automation.py
---------------------------
Builds and runs Docker containers using the Docker SDK for Python,
which talks to the Docker daemon (must be installed and running).

Requires: pip install docker
Requires: Docker Desktop or the Docker Engine installed and running.

Usage:
    python docker_automation.py build <image_tag> <build_context_path> [--dockerfile Dockerfile]
    python docker_automation.py run <image_tag> [--name container_name] [--ports 8080:80] [--detach]
    python docker_automation.py list
    python docker_automation.py stop <container_name_or_id>
    python docker_automation.py remove <container_name_or_id>
    python docker_automation.py logs <container_name_or_id>

Example:
    python docker_automation.py build myapp:latest .
    python docker_automation.py run myapp:latest --name myapp-container --ports 8080:80 --detach
    python docker_automation.py list
    python docker_automation.py logs myapp-container
    python docker_automation.py stop myapp-container
    python docker_automation.py remove myapp-container
"""

import argparse
import sys

try:
    import docker
    from docker.errors import DockerException, ImageNotFound, NotFound, APIError
except ImportError:
    print("Error: the 'docker' package is required.")
    print("Install it with: pip install -r requirements.txt")
    sys.exit(1)


def get_client():
    try:
        return docker.from_env()
    except DockerException:
        print("Error: could not connect to the Docker daemon.")
        print("Make sure Docker Desktop/Engine is installed and running.")
        sys.exit(1)


def build_image(image_tag: str, context_path: str, dockerfile: str) -> None:
    client = get_client()
    print(f"Building image '{image_tag}' from '{context_path}'...")

    try:
        image, logs = client.images.build(path=context_path, tag=image_tag, dockerfile=dockerfile, rm=True)
        for chunk in logs:
            if "stream" in chunk:
                print(chunk["stream"].strip())
        print(f"\nImage '{image_tag}' built successfully (id: {image.short_id}).")
    except (DockerException, APIError) as e:
        print(f"Error building image: {e}")
        sys.exit(1)


def run_container(image_tag: str, name: str, ports: str, detach: bool) -> None:
    client = get_client()

    port_mapping = None
    if ports:
        try:
            host_port, container_port = ports.split(":")
            port_mapping = {f"{container_port}/tcp": int(host_port)}
        except ValueError:
            print("Error: --ports must be in format HOST_PORT:CONTAINER_PORT, e.g. 8080:80")
            sys.exit(1)

    print(f"Running container from image '{image_tag}'...")
    try:
        container = client.containers.run(
            image_tag, name=name, ports=port_mapping, detach=True
        )
        print(f"Container started: {container.name} (id: {container.short_id})")

        if not detach:
            print("Streaming logs (Ctrl+C to stop watching, container keeps running):\n")
            try:
                for line in container.logs(stream=True):
                    print(line.decode("utf-8", errors="replace").rstrip())
            except KeyboardInterrupt:
                print("\nStopped watching logs (container still running).")
    except ImageNotFound:
        print(f"Error: image '{image_tag}' not found locally. Build or pull it first.")
        sys.exit(1)
    except APIError as e:
        print(f"Error running container: {e}")
        sys.exit(1)


def list_containers() -> None:
    client = get_client()
    containers = client.containers.list(all=True)

    if not containers:
        print("No containers found.")
        return

    print(f"Containers ({len(containers)}):\n")
    for c in containers:
        image_name = c.image.tags[0] if c.image.tags else c.image.short_id
        print(f"{c.name:<25} {c.short_id}  Status: {c.status:<12} Image: {image_name}")


def stop_container(identifier: str) -> None:
    client = get_client()
    try:
        container = client.containers.get(identifier)
        container.stop()
        print(f"Container '{identifier}' stopped.")
    except NotFound:
        print(f"Error: container '{identifier}' not found.")
        sys.exit(1)


def remove_container(identifier: str) -> None:
    client = get_client()
    try:
        container = client.containers.get(identifier)
        container.remove(force=True)
        print(f"Container '{identifier}' removed.")
    except NotFound:
        print(f"Error: container '{identifier}' not found.")
        sys.exit(1)


def show_logs(identifier: str) -> None:
    client = get_client()
    try:
        container = client.containers.get(identifier)
        logs = container.logs().decode("utf-8", errors="replace")
        print(logs if logs else "(no logs)")
    except NotFound:
        print(f"Error: container '{identifier}' not found.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Build and run Docker containers via the Docker SDK.")
    subparsers = parser.add_subparsers(dest="action", required=True)

    p = subparsers.add_parser("build", help="Build a Docker image")
    p.add_argument("image_tag", help="Tag for the built image, e.g. myapp:latest")
    p.add_argument("build_context_path", help="Path to the build context (directory with Dockerfile)")
    p.add_argument("--dockerfile", default="Dockerfile", help="Dockerfile name (default: Dockerfile)")

    p = subparsers.add_parser("run", help="Run a container from an image")
    p.add_argument("image_tag", help="Image to run")
    p.add_argument("--name", default=None, help="Name for the container")
    p.add_argument("--ports", default=None, help="Port mapping HOST_PORT:CONTAINER_PORT, e.g. 8080:80")
    p.add_argument("--detach", action="store_true", help="Run in background without streaming logs")

    subparsers.add_parser("list", help="List all containers")

    p = subparsers.add_parser("stop", help="Stop a running container")
    p.add_argument("identifier", help="Container name or ID")

    p = subparsers.add_parser("remove", help="Remove a container")
    p.add_argument("identifier", help="Container name or ID")

    p = subparsers.add_parser("logs", help="Show logs for a container")
    p.add_argument("identifier", help="Container name or ID")

    args = parser.parse_args()

    if args.action == "build":
        build_image(args.image_tag, args.build_context_path, args.dockerfile)
    elif args.action == "run":
        run_container(args.image_tag, args.name, args.ports, args.detach)
    elif args.action == "list":
        list_containers()
    elif args.action == "stop":
        stop_container(args.identifier)
    elif args.action == "remove":
        remove_container(args.identifier)
    elif args.action == "logs":
        show_logs(args.identifier)


if __name__ == "__main__":
    main()
