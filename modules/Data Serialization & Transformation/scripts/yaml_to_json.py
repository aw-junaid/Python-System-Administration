#!/usr/bin/env python3
"""
yaml_to_json.py
-----------------
Topic 342: Convert YAML to JSON

Parses a YAML configuration file and outputs equivalent JSON, useful
for feeding config files into web services that expect JSON.
Requires PyYAML (see requirements.txt).

USAGE
    python3 yaml_to_json.py
    python3 yaml_to_json.py --input config.yaml --output config.json

EXPECTED OUTPUT
    Pretty-printed JSON printed to the terminal (and written to
    --output if given).
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

DEMO_YAML = """
server:
  host: 0.0.0.0
  port: 8080
  debug: false
database:
  engine: postgresql
  name: app_db
allowed_hosts:
  - localhost
  - 127.0.0.1
  - example.com
"""


def main():
    parser = argparse.ArgumentParser(description="Convert YAML to JSON")
    parser.add_argument("--input", help="Path to a YAML file")
    parser.add_argument("--output", help="Path to write the JSON file")
    parser.add_argument("--indent", type=int, default=2)
    args = parser.parse_args()

    text = Path(args.input).read_text(encoding="utf-8") if args.input else DEMO_YAML
    data = yaml.safe_load(text)

    json_text = json.dumps(data, indent=args.indent)
    print(json_text)
    if args.output:
        Path(args.output).write_text(json_text, encoding="utf-8")
        print(f"[written to {args.output}]", file=sys.stderr)


if __name__ == "__main__":
    main()
