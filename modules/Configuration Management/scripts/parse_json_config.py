#!/usr/bin/env python3
"""
parse_json_config.py

Purpose:
    Parse a JSON configuration file using Python's built-in json module
    and pretty-print its structure.

Usage:
    python3 parse_json_config.py <path_to_file.json>

    If no path is given, this script creates and parses a demo
    demo_config.json file in the current directory.

Expected Output:
    Parsed configuration:
    {
      "server": {
        "host": "127.0.0.1",
        "port": 8080
      },
      "debug": true
    }

    Top-level keys: ['server', 'debug']

Caution:
    - This script only reads/parses the file; it makes no changes.
    - JSON does not support comments or trailing commas; a config file
      with either will fail to parse with a clear error message from
      this script rather than a raw traceback.
    - Very large JSON files are loaded fully into memory.
"""

import json
import os
import sys

DEMO_FILE = "demo_config.json"
DEMO_CONTENT = {
    "server": {
        "host": "127.0.0.1",
        "port": 8080
    },
    "debug": True
}


def parse_json(path: str) -> None:
    if not os.path.isfile(path):
        print(f"Error: file not found: {path}")
        return

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        return

    print("Parsed configuration:")
    print(json.dumps(data, indent=2))
    if isinstance(data, dict):
        print(f"\nTop-level keys: {list(data.keys())}")


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        print("No file path given, creating and parsing a demo JSON file.\n")
        if not os.path.isfile(DEMO_FILE):
            with open(DEMO_FILE, "w", encoding="utf-8") as f:
                json.dump(DEMO_CONTENT, f, indent=2)
        path = DEMO_FILE
    parse_json(path)


if __name__ == "__main__":
    main()
