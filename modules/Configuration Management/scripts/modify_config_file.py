#!/usr/bin/env python3
"""
modify_config_file.py

Purpose:
    Modify a single key's value in an existing JSON configuration file,
    using dot notation to reach nested keys, then save the file back.

Usage:
    python3 modify_config_file.py <path.json> --key server.port --value 9090
    python3 modify_config_file.py <path.json> --key debug --value true

    If no arguments are given, this script creates a demo config file,
    modifies one of its values, and shows the before/after result.

Expected Output:
    Before:
    {
      "server": {
        "host": "127.0.0.1",
        "port": 8080
      },
      "debug": false
    }

    After setting 'server.port' = 9090:
    {
      "server": {
        "host": "127.0.0.1",
        "port": 9090
      },
      "debug": false
    }

    Saved to: demo_config_to_modify.json

Caution:
    - This OVERWRITES the original file with the modified version.
      Consider running backup_config.py on the file first if it's
      important.
    - Values are auto-converted: "true"/"false" become booleans,
      numeric strings become int/float, everything else stays a
      string. If you need a literal string like "true", this simple
      script cannot preserve that distinction.
    - Dot notation (e.g. "server.port") only works for nested
      dictionaries, not for list indices.
"""

import json
import os
import sys

DEMO_FILE = "demo_config_to_modify.json"
DEMO_CONTENT = {
    "server": {"host": "127.0.0.1", "port": 8080},
    "debug": False
}


def convert_value(raw: str):
    if raw.lower() == "true":
        return True
    if raw.lower() == "false":
        return False
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except ValueError:
        return raw


def set_nested_value(data: dict, dotted_key: str, value) -> None:
    keys = dotted_key.split(".")
    current = data
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value


def parse_args():
    args = sys.argv[1:]
    path = None
    key = None
    value = None
    positional = []
    i = 0
    while i < len(args):
        if args[i] == "--key" and i + 1 < len(args):
            key = args[i + 1]; i += 2
        elif args[i] == "--value" and i + 1 < len(args):
            value = args[i + 1]; i += 2
        else:
            positional.append(args[i]); i += 1
    if positional:
        path = positional[0]
    return path, key, value


def main():
    path, key, raw_value = parse_args()

    if not path or not key or raw_value is None:
        print("No arguments given, running demo mode.\n")
        if not os.path.isfile(DEMO_FILE):
            with open(DEMO_FILE, "w", encoding="utf-8") as f:
                json.dump(DEMO_CONTENT, f, indent=2)
        path, key, raw_value = DEMO_FILE, "server.port", "9090"

    if not os.path.isfile(path):
        print(f"Error: file not found: {path}")
        return

    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON file: {e}")
            return

    print("Before:")
    print(json.dumps(data, indent=2))

    value = convert_value(raw_value)
    set_nested_value(data, key, value)

    print(f"\nAfter setting '{key}' = {value!r}:")
    print(json.dumps(data, indent=2))

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"\nSaved to: {path}")


if __name__ == "__main__":
    main()
