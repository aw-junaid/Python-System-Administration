#!/usr/bin/env python3
"""
generate_config_file.py

Purpose:
    Generate a new configuration file from a Python dictionary, in
    your choice of format: JSON, YAML, or INI.

Usage:
    python3 generate_config_file.py --format json --output config.json
    python3 generate_config_file.py --format yaml --output config.yaml
    python3 generate_config_file.py --format ini  --output config.ini

    If no arguments are given, this script generates a demo JSON config
    file (generated_demo_config.json) in the current directory.

Expected Output:
    Generated config.json:
    {
      "server": {
        "host": "127.0.0.1",
        "port": 8080
      },
      "debug": false
    }
    Written to: config.json

Caution:
    - If the output file already exists, it will be OVERWRITTEN without
      a prompt. Use backup_config.py first if you want a safety copy.
    - The YAML output option requires the third-party 'PyYAML' library
      (see requirements.txt); JSON and INI only use the standard
      library.
    - Edit the DEFAULT_CONFIG dictionary inside this script to change
      what gets generated for your own project.
"""

import configparser
import json
import os
import sys

DEFAULT_CONFIG = {
    "server": {
        "host": "127.0.0.1",
        "port": 8080
    },
    "debug": False
}


def generate_json(config: dict) -> str:
    return json.dumps(config, indent=2)


def generate_yaml(config: dict) -> str:
    try:
        import yaml
    except ImportError:
        print("Error: YAML output requires 'PyYAML'. Install with:")
        print("    pip install -r requirements.txt")
        sys.exit(1)
    return yaml.dump(config, default_flow_style=False, sort_keys=False)


def generate_ini(config: dict) -> str:
    parser = configparser.ConfigParser()
    for section, values in config.items():
        if isinstance(values, dict):
            parser[section] = {k: str(v) for k, v in values.items()}
        else:
            # top-level scalar values go under a generic [general] section
            if "general" not in parser:
                parser["general"] = {}
            parser["general"][section] = str(values)
    import io
    buf = io.StringIO()
    parser.write(buf)
    return buf.getvalue()


def parse_args():
    args = sys.argv[1:]
    fmt = None
    output = None
    i = 0
    while i < len(args):
        if args[i] == "--format" and i + 1 < len(args):
            fmt = args[i + 1].lower(); i += 2
        elif args[i] == "--output" and i + 1 < len(args):
            output = args[i + 1]; i += 2
        else:
            i += 1
    return fmt, output


def main():
    fmt, output = parse_args()

    if not fmt:
        fmt = "json"
        output = output or "generated_demo_config.json"
        print("No --format given, generating a demo JSON config file.\n")

    generators = {"json": generate_json, "yaml": generate_yaml, "ini": generate_ini}
    if fmt not in generators:
        print(f"Error: unsupported format '{fmt}'. Choose from: json, yaml, ini")
        return

    content = generators[fmt](DEFAULT_CONFIG)

    if not output:
        output = f"generated_config.{fmt}"

    if os.path.isfile(output):
        print(f"Note: '{output}' already exists and will be overwritten.")

    with open(output, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Generated {fmt} config:")
    print(content)
    print(f"Written to: {output}")


if __name__ == "__main__":
    main()
