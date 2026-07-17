#!/usr/bin/env python3
"""
parse_yaml_config.py

Purpose:
    Parse a YAML configuration file using the third-party PyYAML
    library and pretty-print its structure.

Usage:
    python3 parse_yaml_config.py <path_to_file.yaml>

    If no path is given, this script creates and parses a demo
    demo_config.yaml file in the current directory.

Expected Output:
    Parsed configuration:
    {'server': {'host': '127.0.0.1', 'port': 8080}, 'debug': True}

    Top-level keys: ['server', 'debug']

Caution:
    - Requires the third-party 'PyYAML' library (see requirements.txt).
    - This script uses yaml.safe_load(), which is intentionally safer
      than yaml.load() because it does not execute arbitrary Python
      objects/tags embedded in the file. Do not switch to yaml.load()
      on untrusted YAML files.
    - YAML is indentation-sensitive; a single misplaced space can
      change structure or cause a parse error. This script reports
      parse errors clearly instead of crashing with a raw traceback.
"""

import os
import sys

try:
    import yaml
except ImportError:
    print("Error: this script requires 'PyYAML'. Install with:")
    print("    pip install -r requirements.txt")
    sys.exit(1)

DEMO_FILE = "demo_config.yaml"
DEMO_CONTENT = (
    "server:\n"
    "  host: 127.0.0.1\n"
    "  port: 8080\n"
    "debug: true\n"
)


def parse_yaml(path: str) -> None:
    if not os.path.isfile(path):
        print(f"Error: file not found: {path}")
        return

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return

    print("Parsed configuration:")
    print(data)
    if isinstance(data, dict):
        print(f"\nTop-level keys: {list(data.keys())}")


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        print("No file path given, creating and parsing a demo YAML file.\n")
        if not os.path.isfile(DEMO_FILE):
            with open(DEMO_FILE, "w", encoding="utf-8") as f:
                f.write(DEMO_CONTENT)
        path = DEMO_FILE
    parse_yaml(path)


if __name__ == "__main__":
    main()
