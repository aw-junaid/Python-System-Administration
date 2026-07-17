#!/usr/bin/env python3
"""
ini_to_json_yaml.py
----------------------
Topic 348: Convert INI to JSON/YAML

Migrates legacy INI configuration files (as read by configparser)
into modern structured JSON or YAML. Each INI section becomes a
top-level key; keys inside become nested fields.

USAGE
    python3 ini_to_json_yaml.py
    python3 ini_to_json_yaml.py --input app.ini --format yaml --output app.yaml
    python3 ini_to_json_yaml.py --input app.ini --format json --output app.json

EXPECTED OUTPUT
    The converted config printed to the terminal (and written to
    --output if given) in the chosen --format (json by default).
"""
import argparse
import configparser
import json
import sys
from pathlib import Path

DEMO_INI = """[server]
host = 0.0.0.0
port = 8080
debug = false

[database]
engine = postgresql
name = app_db
"""


def coerce(value: str):
    low = value.lower()
    if low in ("true", "false"):
        return low == "true"
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def ini_to_dict(text: str) -> dict:
    parser = configparser.ConfigParser()
    parser.read_string(text)
    result = {}
    for section in parser.sections():
        result[section] = {k: coerce(v) for k, v in parser.items(section)}
    return result


def main():
    parser = argparse.ArgumentParser(description="Convert INI to JSON or YAML")
    parser.add_argument("--input", help="Path to an INI file")
    parser.add_argument("--output", help="Path to write the output file")
    parser.add_argument("--format", choices=["json", "yaml"], default="json")
    args = parser.parse_args()

    text = Path(args.input).read_text(encoding="utf-8") if args.input else DEMO_INI
    data = ini_to_dict(text)

    if args.format == "yaml":
        try:
            import yaml
        except ImportError:
            sys.exit(
                "ERROR: PyYAML is not installed.\n"
                "Install dependencies first:  pip install -r requirements.txt"
            )
        out_text = yaml.dump(data, sort_keys=False, default_flow_style=False)
    else:
        out_text = json.dumps(data, indent=2)

    print(out_text)
    if args.output:
        Path(args.output).write_text(out_text, encoding="utf-8")
        print(f"[written to {args.output}]", file=sys.stderr)


if __name__ == "__main__":
    main()
