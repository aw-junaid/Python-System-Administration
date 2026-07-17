#!/usr/bin/env python3
"""
docker_build_image.py
Build a Docker image programmatically using the Docker SDK for Python
(no need to run `docker build` manually).

USAGE
    python docker_build_image.py --path ./myapp --tag myapp:latest
    python docker_build_image.py --path ./myapp --tag myapp:latest \
        --dockerfile Dockerfile.prod --buildarg VERSION=1.0 --buildarg ENV=prod --no-cache

REQUIREMENTS
    - Docker Engine/Desktop installed and RUNNING on this machine
    - The account running this script must have permission to talk to the
      Docker socket (on Linux, be in the `docker` group or run with sudo)
    - pip install -r requirements.txt   (installs the `docker` package)

EXPECTED OUTPUT
    Streamed build log lines from the Docker daemon, ending with:
        Image built successfully: myapp:latest (id=sha256:xxxxxxx)
    On failure, the build log is printed and the script exits with code 1.
"""

import argparse
import sys

import docker
from docker.errors import APIError, BuildError


def parse_build_args(pairs):
    result = {}
    for pair in pairs or []:
        if "=" not in pair:
            print(f"Ignoring malformed --buildarg '{pair}', expected KEY=VALUE")
            continue
        k, v = pair.split("=", 1)
        result[k] = v
    return result


def build_image(path, tag, dockerfile, buildargs, nocache):
    client = docker.from_env()
    print(f"Building image '{tag}' from context '{path}' ...")
    try:
        image, logs = client.images.build(
            path=path,
            tag=tag,
            dockerfile=dockerfile,
            buildargs=buildargs,
            nocache=nocache,
            rm=True,
        )
        for chunk in logs:
            if "stream" in chunk:
                sys.stdout.write(chunk["stream"])
        print(f"\nImage built successfully: {tag} (id={image.short_id})")
        return image
    except BuildError as e:
        print(f"Build failed: {e}")
        for line in e.build_log:
            if "stream" in line:
                sys.stdout.write(line["stream"])
        sys.exit(1)
    except APIError as e:
        print(f"Docker API error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Build a Docker image programmatically.")
    parser.add_argument("--path", required=True, help="Build context directory (contains the Dockerfile)")
    parser.add_argument("--tag", required=True, help="Image tag, e.g. myapp:latest")
    parser.add_argument("--dockerfile", default="Dockerfile", help="Dockerfile name relative to --path")
    parser.add_argument("--buildarg", action="append", help="Build arg KEY=VALUE, repeatable")
    parser.add_argument("--no-cache", action="store_true", help="Disable the build cache")
    args = parser.parse_args()

    buildargs = parse_build_args(args.buildarg)
    build_image(args.path, args.tag, args.dockerfile, buildargs, args.no_cache)


if __name__ == "__main__":
    main()
