#!/usr/bin/env python3
"""
docker_registry_transfer.py
Authenticate to a Docker registry (Docker Hub, AWS ECR, or any private
registry) and pull or push images programmatically.

USAGE
    Login:
        python docker_registry_transfer.py login --registry docker.io \
            --username myuser --password mypassword

    Pull:
        python docker_registry_transfer.py pull --image nginx:latest

    Push (tag your local image with the registry path first, e.g.
    myrepo/myapp:latest, then push it):
        python docker_registry_transfer.py push --image myrepo/myapp:latest

REQUIREMENTS
    - Docker Engine/Desktop installed and running
    - Valid credentials for the target registry
      (for AWS ECR, generate a temporary password with:
       aws ecr get-login-password --region <region>)
    - pip install -r requirements.txt

EXPECTED OUTPUT
    login -> "Login succeeded for registry 'docker.io' as 'myuser'."
    pull  -> streamed pull progress, then "Pulled image: nginx:latest"
    push  -> streamed push progress, then "Pushed image: myrepo/myapp:latest"

CAUTION
    Never hardcode real credentials in scripts or commit them to version
    control. Prefer environment variables or a secrets manager, e.g.:
        python docker_registry_transfer.py login --registry docker.io \
            --username myuser --password "$DOCKER_PASSWORD"
"""

import argparse

import docker
from docker.errors import APIError


def login(args):
    client = docker.from_env()
    try:
        resp = client.login(username=args.username, password=args.password, registry=args.registry)
        print(f"Login succeeded for registry '{args.registry}' as '{args.username}'. ({resp.get('Status', '')})")
    except APIError as e:
        print(f"Login failed: {e}")


def pull(args):
    client = docker.from_env()
    try:
        for line in client.api.pull(args.image, stream=True, decode=True):
            if "status" in line:
                progress = line.get("progress", "")
                print(f"{line['status']} {progress}")
        print(f"Pulled image: {args.image}")
    except APIError as e:
        print(f"Pull failed: {e}")


def push(args):
    client = docker.from_env()
    try:
        for line in client.api.push(args.image, stream=True, decode=True):
            if "status" in line:
                progress = line.get("progress", "")
                print(f"{line['status']} {progress}")
        print(f"Pushed image: {args.image}")
    except APIError as e:
        print(f"Push failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="Pull/push Docker images to/from a registry.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_login = sub.add_parser("login")
    p_login.add_argument("--registry", required=True, help="e.g. docker.io or <account>.dkr.ecr.<region>.amazonaws.com")
    p_login.add_argument("--username", required=True)
    p_login.add_argument("--password", required=True)
    p_login.set_defaults(func=login)

    p_pull = sub.add_parser("pull")
    p_pull.add_argument("--image", required=True, help="e.g. nginx:latest or registry/repo:tag")
    p_pull.set_defaults(func=pull)

    p_push = sub.add_parser("push")
    p_push.add_argument("--image", required=True, help="Must already be tagged with the registry path")
    p_push.set_defaults(func=push)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
