#!/usr/bin/env python3
"""
merge_config_files.py

Purpose:
    Merge two or more JSON configuration files into one, with later
    files overriding matching keys from earlier files (deep merge for
    nested dictionaries).

Usage:
    python3 merge_config_files.py base.json override.json > merged.json
    python3 merge_config_files.py base.json override.json --output merged.json

    If no files are given, this script merges two small built-in demo
    configs and prints the result (base + environment-specific override).

Expected Output:
    Merged configuration:
    {
      "server": {
        "host": "127.0.0.1",
        "port": 9090
      },
      "debug": false
    }

    (Here "port" and "debug" from the override file replaced the base
    file's values, while "host" was kept from the base file since the
    override didn't specify it.)

Caution:
    - This script performs a DEEP merge for nested dictionaries but a
      SHALLOW replace for lists (a list in a later file fully replaces
      a list in an earlier file, it does not concatenate them).
    - If you use --output, an existing file at that path will be
      OVERWRITTEN without a prompt. Use backup_config.py first if you
      want a safety copy.
    - Files are merged in the order given on the command line; put your
      base/default config first and environment-specific overrides
      after it.
"""

import json
import os
import sys

DEMO_BASE = {
    "server": {"host": "127.0.0.1", "port": 8080},
    "debug": True
}
DEMO_OVERRIDE = {
    "server": {"port": 9090},
    "debug": False
}


def deep_merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    output_path = None
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    if len(args) >= 2:
        merged = {}
        for path in args:
            if not os.path.isfile(path):
                print(f"Error: file not found: {path}")
                return
            try:
                data = load_json(path)
            except json.JSONDecodeError as e:
                print(f"Error parsing {path}: {e}")
                return
            merged = deep_merge(merged, data)
    else:
        print("No files given (need at least 2), merging demo configs.\n")
        merged = deep_merge(DEMO_BASE, DEMO_OVERRIDE)

    output_text = json.dumps(merged, indent=2)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output_text + "\n")
        print(f"Merged configuration written to: {output_path}")
    else:
        print("Merged configuration:")
        print(output_text)


if __name__ == "__main__":
    main()
