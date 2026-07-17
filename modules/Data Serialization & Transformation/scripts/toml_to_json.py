#!/usr/bin/env python3
"""
toml_to_json.py
------------------
Topic 349: Convert TOML to JSON

Transforms TOML files (e.g. Python's pyproject.toml) into widely
compatible JSON. Uses the standard-library `tomllib` on Python
3.11+, and falls back to the third-party `toml` package on older
Python versions (see requirements.txt).

USAGE
    python3 toml_to_json.py
    python3 toml_to_json.py --input pyproject.toml --output pyproject.json

EXPECTED OUTPUT
    Pretty-printed JSON printed to the terminal (and written to
    --output if given).
"""
import argparse
import json
import sys
from pathlib import Path

try:
    import tomllib  # Python 3.11+
    _read_mode = "rb"

    def _load(text_bytes):
        return tomllib.loads(text_bytes.decode("utf-8"))

except ModuleNotFoundError:
    try:
        import toml
    except ImportError:
        sys.exit(
            "ERROR: no TOML parser available.\n"
            "On Python < 3.11, install the fallback:  pip install -r requirements.txt"
        )
    _read_mode = "r"

    def _load(text_str):
        return toml.loads(text_str)

DEMO_TOML = """
[project]
name = "example-app"
version = "1.0.0"

[project.dependencies]
requests = "^2.31"
pyyaml = "^6.0"

[tool.settings]
debug = false
max_connections = 10
"""


def main():
    parser = argparse.ArgumentParser(description="Convert TOML to JSON")
    parser.add_argument("--input", help="Path to a TOML file")
    parser.add_argument("--output", help="Path to write the JSON file")
    parser.add_argument("--indent", type=int, default=2)
    args = parser.parse_args()

    if args.input:
        mode = _read_mode
        with open(args.input, mode) as f:
            raw = f.read()
    else:
        raw = DEMO_TOML.encode("utf-8") if _read_mode == "rb" else DEMO_TOML

    data = _load(raw)
    json_text = json.dumps(data, indent=args.indent)
    print(json_text)
    if args.output:
        Path(args.output).write_text(json_text, encoding="utf-8")
        print(f"[written to {args.output}]", file=sys.stderr)


if __name__ == "__main__":
    main()
