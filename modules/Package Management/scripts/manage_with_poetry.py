#!/usr/bin/env python3
"""
manage_with_poetry.py
--------------------
Thin automation wrapper around modern dependency resolvers (Poetry or
Pipenv). Requires that `poetry` or `pipenv` is already installed and on
PATH -- this script does not install the tool itself, only drives it.

Usage:
    python manage_with_poetry.py --tool poetry --action init
    python manage_with_poetry.py --tool poetry --action add --package requests
    python manage_with_poetry.py --tool poetry --action install
    python manage_with_poetry.py --tool poetry --action lock
    python manage_with_poetry.py --tool pipenv --action install --package flask
    python manage_with_poetry.py --tool pipenv --action lock

Supported actions: init, install, add, remove, lock, show

Exit codes:
    0 -> command ran successfully
    1 -> command failed or tool not found
    2 -> bad arguments
"""

import argparse
import shutil
import subprocess
import sys

ACTIONS = {"init", "install", "add", "remove", "lock", "show"}


def build_command(tool, action, package):
    if tool == "poetry":
        mapping = {
            "init": ["poetry", "init", "--no-interaction"],
            "install": ["poetry", "install"],
            "add": ["poetry", "add", package] if package else None,
            "remove": ["poetry", "remove", package] if package else None,
            "lock": ["poetry", "lock"],
            "show": ["poetry", "show"],
        }
    else:  # pipenv
        mapping = {
            "init": ["pipenv", "--python", "3"],
            "install": ["pipenv", "install", package] if package else ["pipenv", "install"],
            "add": ["pipenv", "install", package] if package else None,
            "remove": ["pipenv", "uninstall", package] if package else None,
            "lock": ["pipenv", "lock"],
            "show": ["pipenv", "graph"],
        }
    return mapping.get(action)


def main():
    parser = argparse.ArgumentParser(description="Drive Poetry or Pipenv for dependency management.")
    parser.add_argument("--tool", choices=["poetry", "pipenv"], required=True)
    parser.add_argument("--action", choices=sorted(ACTIONS), required=True)
    parser.add_argument("--package", help="Package name, required for add/remove")
    args = parser.parse_args()

    if shutil.which(args.tool) is None:
        print(f"[manage] '{args.tool}' is not installed or not on PATH.")
        print(f"         Install it first, e.g.: pip install {args.tool}")
        sys.exit(1)

    if args.action in {"add", "remove"} and not args.package:
        print(f"[manage] --package is required for action '{args.action}'")
        sys.exit(2)

    cmd = build_command(args.tool, args.action, args.package)
    if cmd is None:
        print(f"[manage] Could not build a command for tool={args.tool} action={args.action}")
        sys.exit(2)

    print(f"[manage] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr.strip()[-1500:])
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
