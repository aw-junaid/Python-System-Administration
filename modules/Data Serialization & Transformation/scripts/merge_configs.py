#!/usr/bin/env python3
"""
merge_configs.py
--------------------
Topic 356: Merge JSON/YAML Data Sources

Combines multiple JSON and/or YAML configuration files using a deep
merge: nested dicts are merged key-by-key, lists and scalars from
later files override earlier ones. Later files in the list win on
conflicts. Requires PyYAML for .yaml/.yml files (see requirements.txt).

USAGE
    # Run built-in demo (merges two built-in sample configs)
    python3 merge_configs.py

    # Merge specific files (order matters: later files override earlier)
    python3 merge_configs.py --inputs base.json override.yaml local.json \\
        --output merged.json

EXPECTED OUTPUT
    The deep-merged configuration, pretty-printed as JSON to the
    terminal (and written to --output if given).
"""
import argparse
import json
import sys
from pathlib import Path

DEMO_BASE = {
    "server": {"host": "0.0.0.0", "port": 8080, "debug": False},
    "features": ["auth", "logging"],
}
DEMO_OVERRIDE = {
    "server": {"port": 9090},
    "features": ["auth", "logging", "metrics"],
    "database": {"engine": "postgresql"},
}


def load_file(path: str):
    text = Path(path).read_text(encoding="utf-8")
    if path.endswith((".yaml", ".yml")):
        try:
            import yaml
        except ImportError:
            sys.exit(
                "ERROR: PyYAML is not installed.\n"
                "Install dependencies first:  pip install -r requirements.txt"
            )
        return yaml.safe_load(text)
    return json.loads(text)


def deep_merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description="Deep-merge multiple JSON/YAML config files")
    parser.add_argument("--inputs", nargs="+", help="Paths to config files, in override order")
    parser.add_argument("--output", help="Path to write the merged JSON file")
    parser.add_argument("--indent", type=int, default=2)
    args = parser.parse_args()

    if args.inputs:
        configs = [load_file(p) for p in args.inputs]
    else:
        configs = [DEMO_BASE, DEMO_OVERRIDE]

    merged = {}
    for cfg in configs:
        merged = deep_merge(merged, cfg)

    json_text = json.dumps(merged, indent=args.indent)
    print(json_text)
    if args.output:
        Path(args.output).write_text(json_text, encoding="utf-8")
        print(f"[written to {args.output}]", file=sys.stderr)


if __name__ == "__main__":
    main()
