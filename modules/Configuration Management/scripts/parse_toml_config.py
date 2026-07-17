#!/usr/bin/env python3
"""
parse_toml_config.py

Purpose:
    Parse a TOML configuration file (e.g. pyproject.toml-style files)
    and pretty-print its structure.

Usage:
    python3 parse_toml_config.py <path_to_file.toml>

    If no path is given, this script creates and parses a demo
    demo_config.toml file in the current directory.

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
    - On Python 3.11+, this script uses the built-in 'tomllib' module
      (read-only). On Python 3.10 and earlier, it falls back to the
      third-party 'tomli' library (see requirements.txt).
    - TOML files must be opened in binary mode for tomllib/tomli; this
      script handles that for you.
    - This script only reads/parses; it makes no changes to the file.
"""

import json
import os
import sys

try:
    import tomllib as toml_reader  # Python 3.11+
    _BINARY_MODE = True
except ImportError:
    try:
        import tomli as toml_reader  # Python <=3.10 fallback
        _BINARY_MODE = True
    except ImportError:
        print("Error: this script requires 'tomli' on Python <3.11. Install with:")
        print("    pip install -r requirements.txt")
        sys.exit(1)

DEMO_FILE = "demo_config.toml"
DEMO_CONTENT = (
    "debug = true\n\n"
    "[server]\n"
    "host = \"127.0.0.1\"\n"
    "port = 8080\n"
)


def parse_toml(path: str) -> None:
    if not os.path.isfile(path):
        print(f"Error: file not found: {path}")
        return

    try:
        with open(path, "rb") as f:
            data = toml_reader.load(f)
    except Exception as e:  # tomllib/tomli raise their own decode errors
        print(f"Error parsing TOML file: {e}")
        return

    print("Parsed configuration:")
    print(json.dumps(data, indent=2, default=str))
    if isinstance(data, dict):
        print(f"\nTop-level keys: {list(data.keys())}")


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        print("No file path given, creating and parsing a demo TOML file.\n")
        if not os.path.isfile(DEMO_FILE):
            with open(DEMO_FILE, "w", encoding="utf-8") as f:
                f.write(DEMO_CONTENT)
        path = DEMO_FILE
    parse_toml(path)


if __name__ == "__main__":
    main()
