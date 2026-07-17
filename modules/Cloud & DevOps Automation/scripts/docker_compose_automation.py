#!/usr/bin/env python3
"""
docker_compose_automation.py
----------------------------------
Manages multi-container applications by programmatically reading/modifying
a docker-compose.yml file and invoking the 'docker compose' CLI. Useful
for scripting compose changes (e.g. add a service, change an image tag)
before starting a stack.

Requires: pip install pyyaml
Requires: Docker Desktop or Docker Engine with the 'docker compose' plugin installed.

Usage:
    python docker_compose_automation.py up <compose_file> [--detach]
    python docker_compose_automation.py down <compose_file>
    python docker_compose_automation.py list-services <compose_file>
    python docker_compose_automation.py set-image <compose_file> <service_name> <new_image>
    python docker_compose_automation.py add-env <compose_file> <service_name> <KEY=VALUE>

Example:
    python docker_compose_automation.py list-services docker-compose.yml
    python docker_compose_automation.py set-image docker-compose.yml web nginx:1.25
    python docker_compose_automation.py add-env docker-compose.yml web DEBUG=true
    python docker_compose_automation.py up docker-compose.yml --detach
    python docker_compose_automation.py down docker-compose.yml
"""

import argparse
import os
import subprocess
import sys

try:
    import yaml
except ImportError:
    print("Error: the 'pyyaml' package is required.")
    print("Install it with: pip install -r requirements.txt")
    sys.exit(1)


def load_compose_file(path: str) -> dict:
    if not os.path.isfile(path):
        print(f"Error: compose file '{path}' does not exist.")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data or "services" not in data:
        print(f"Error: '{path}' does not look like a valid docker-compose file (no 'services' key).")
        sys.exit(1)

    return data


def save_compose_file(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)


def compose_up(compose_file: str, detach: bool) -> None:
    cmd = ["docker", "compose", "-f", compose_file, "up"]
    if detach:
        cmd.append("-d")

    print(f"Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd)

    if result.returncode != 0:
        print(f"\n'docker compose up' exited with code {result.returncode}.")
        sys.exit(result.returncode)


def compose_down(compose_file: str) -> None:
    cmd = ["docker", "compose", "-f", compose_file, "down"]
    print(f"Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd)

    if result.returncode != 0:
        print(f"\n'docker compose down' exited with code {result.returncode}.")
        sys.exit(result.returncode)


def list_services(compose_file: str) -> None:
    data = load_compose_file(compose_file)
    services = data.get("services", {})

    if not services:
        print("No services defined in this compose file.")
        return

    print(f"Services in '{compose_file}' ({len(services)}):\n")
    for name, config in services.items():
        image = config.get("image", "(built from Dockerfile)")
        ports = config.get("ports", [])
        print(f"{name:<20} image: {image:<30} ports: {ports}")


def set_image(compose_file: str, service_name: str, new_image: str) -> None:
    data = load_compose_file(compose_file)
    services = data.get("services", {})

    if service_name not in services:
        print(f"Error: service '{service_name}' not found in '{compose_file}'.")
        print(f"Available services: {', '.join(services.keys())}")
        sys.exit(1)

    old_image = services[service_name].get("image", "(none)")
    services[service_name]["image"] = new_image

    save_compose_file(compose_file, data)
    print(f"Service '{service_name}': image changed from '{old_image}' to '{new_image}'.")
    print(f"Updated '{compose_file}'.")


def add_env(compose_file: str, service_name: str, key_value: str) -> None:
    if "=" not in key_value:
        print("Error: environment variable must be in KEY=VALUE format.")
        sys.exit(1)

    data = load_compose_file(compose_file)
    services = data.get("services", {})

    if service_name not in services:
        print(f"Error: service '{service_name}' not found in '{compose_file}'.")
        print(f"Available services: {', '.join(services.keys())}")
        sys.exit(1)

    key, value = key_value.split("=", 1)

    env = services[service_name].get("environment", [])
    if isinstance(env, dict):
        env[key] = value
    else:
        env = [e for e in env if not str(e).startswith(f"{key}=")]
        env.append(f"{key}={value}")

    services[service_name]["environment"] = env

    save_compose_file(compose_file, data)
    print(f"Service '{service_name}': set environment variable {key}={value}.")
    print(f"Updated '{compose_file}'.")


def main():
    parser = argparse.ArgumentParser(description="Manage docker-compose files and stacks.")
    subparsers = parser.add_subparsers(dest="action", required=True)

    p = subparsers.add_parser("up", help="Start the compose stack ('docker compose up')")
    p.add_argument("compose_file", help="Path to docker-compose.yml")
    p.add_argument("--detach", action="store_true", help="Run in detached mode (-d)")

    p = subparsers.add_parser("down", help="Stop the compose stack ('docker compose down')")
    p.add_argument("compose_file", help="Path to docker-compose.yml")

    p = subparsers.add_parser("list-services", help="List services defined in the compose file")
    p.add_argument("compose_file", help="Path to docker-compose.yml")

    p = subparsers.add_parser("set-image", help="Change a service's image in the compose file")
    p.add_argument("compose_file", help="Path to docker-compose.yml")
    p.add_argument("service_name", help="Service to modify")
    p.add_argument("new_image", help="New image (e.g. nginx:1.25)")

    p = subparsers.add_parser("add-env", help="Add/update an environment variable for a service")
    p.add_argument("compose_file", help="Path to docker-compose.yml")
    p.add_argument("service_name", help="Service to modify")
    p.add_argument("key_value", help="Environment variable in KEY=VALUE format")

    args = parser.parse_args()

    if args.action == "up":
        compose_up(args.compose_file, args.detach)
    elif args.action == "down":
        compose_down(args.compose_file)
    elif args.action == "list-services":
        list_services(args.compose_file)
    elif args.action == "set-image":
        set_image(args.compose_file, args.service_name, args.new_image)
    elif args.action == "add-env":
        add_env(args.compose_file, args.service_name, args.key_value)


if __name__ == "__main__":
    main()
