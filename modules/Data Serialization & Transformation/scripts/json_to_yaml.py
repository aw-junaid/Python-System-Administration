#!/usr/bin/env python3
"""
json_to_yaml.py
-----------------
Topic 341: Convert JSON to YAML

Translates JSON data into human-readable YAML, suitable for
configuration files. Requires PyYAML (see requirements.txt).

USAGE
    python3 json_to_yaml.py
    python3 json_to_yaml.py --input data.json --output config.yaml

EXPECTED OUTPUT
    YAML text printed to the terminal (and written to --output if
    given).
"""
import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit(
        "ERROR: PyYAML is not installed.\n"
        "Install dependencies first:  pip install -r requirements.txt"
    )

DEMO_DATA = {
    "server": {
        "host": "0.0.0.0",
        "port": 8080,
        "debug": False,
    },
    "database": {
        "engine": "postgresql",
        "name": "app_db",
    },
    "allowed_hosts": ["localhost", "127.0.0.1", "example.com"],
}


def main():
    parser = argparse.ArgumentParser(description="Convert JSON to YAML")
    parser.add_argument("--input", help="Path to a JSON file")
    parser.add_argument("--output", help="Path to write the YAML file")
    args = parser.parse_args()

    if args.input:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    else:
        data = DEMO_DATA

    yaml_text = yaml.dump(data, sort_keys=False, default_flow_style=False)
    print(yaml_text)
    if args.output:
        Path(args.output).write_text(yaml_text, encoding="utf-8")
        print(f"[written to {args.output}]", file=sys.stderr)


if __name__ == "__main__":
    main()
