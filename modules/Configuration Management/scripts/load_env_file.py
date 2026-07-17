#!/usr/bin/env python3
"""
load_env_file.py

Purpose:
    Load key=value pairs from a .env-style file into the current
    process's environment variables, without requiring any third-party
    library (a minimal hand-rolled parser).

Usage:
    python3 load_env_file.py <path_to_.env_file>

    If no path is given, this script creates and loads a demo .env
    file in the current directory.

Expected Output:
    Loaded 3 variable(s) from .env:
      DEBUG=true
      DATABASE_URL=postgres://localhost/mydb
      SECRET_KEY=demo-secret-value

    Verifying via os.environ:
      os.environ['DEBUG'] = true
      os.environ['DATABASE_URL'] = postgres://localhost/mydb

Caution:
    - Environment variables set by this script only affect THIS Python
      process (and any child processes it launches afterward) — they
      do not persist in your shell/terminal once the script exits.
    - This script does NOT overwrite a variable that's already set in
      the environment by default, matching common .env-loader
      behavior; pass --override to force overwriting existing values.
    - Do not commit real .env files containing secrets to version
      control; this script is for LOADING them locally, not for
      generating or sharing them.
    - This minimal parser supports simple KEY=VALUE lines and '#'
      comments; it does not support multi-line values or advanced
      interpolation like some third-party .env libraries do.
"""

import os
import sys

DEMO_FILE = ".env"
DEMO_CONTENT = (
    "# Demo environment file\n"
    "DEBUG=true\n"
    "DATABASE_URL=postgres://localhost/mydb\n"
    "SECRET_KEY=demo-secret-value\n"
)


def parse_env_file(path: str) -> dict:
    variables = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            variables[key] = value
    return variables


def load_into_environment(variables: dict, override: bool = False) -> None:
    for key, value in variables.items():
        if override or key not in os.environ:
            os.environ[key] = value


def main():
    override = "--override" in sys.argv
    positional = [a for a in sys.argv[1:] if not a.startswith("--")]

    if positional:
        path = positional[0]
    else:
        print("No file path given, creating and loading a demo .env file.\n")
        if not os.path.isfile(DEMO_FILE):
            with open(DEMO_FILE, "w", encoding="utf-8") as f:
                f.write(DEMO_CONTENT)
        path = DEMO_FILE

    if not os.path.isfile(path):
        print(f"Error: file not found: {path}")
        return

    variables = parse_env_file(path)
    load_into_environment(variables, override=override)

    print(f"Loaded {len(variables)} variable(s) from {path}:")
    for key, value in variables.items():
        print(f"  {key}={value}")

    print("\nVerifying via os.environ:")
    for key in list(variables.keys())[:2]:
        print(f"  os.environ['{key}'] = {os.environ.get(key)}")


if __name__ == "__main__":
    main()
