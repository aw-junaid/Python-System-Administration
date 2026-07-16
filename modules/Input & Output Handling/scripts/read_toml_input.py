#!/usr/bin/env python3
"""
Topic: Read TOML Input

Reads and parses a TOML file (creating a sample one if none is given).
Uses Python's built-in 'tomllib' on Python 3.11+, or falls back to the
third-party 'toml' package on older Python versions.

Requires (Python < 3.11 only): toml  (see requirements.txt)

Usage:
    python read_toml_input.py [path_to_file.toml]

Expected Output:
    The parsed TOML content printed as a Python dictionary.
"""

import sys
import os

try:
    import tomllib  # Python 3.11+
    _USE_TOMLLIB = True
except ImportError:
    _USE_TOMLLIB = False
    try:
        import toml
    except ImportError:
        print(
            "Error: no TOML parser available. On Python < 3.11 install it with: pip install toml",
            file=sys.stderr,
        )
        sys.exit(1)


def main() -> None:
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "sample_data.toml"
        if not os.path.exists(file_path):
            sample = """\
name = "Junaid"
role = "Automation Engineer"
active = true

[server]
host = "127.0.0.1"
port = 8080
"""
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(sample)
        print(f"No file given, using generated sample: {file_path}\n")

    if not os.path.isfile(file_path):
        print(f"Error: file not found -> {file_path}", file=sys.stderr)
        sys.exit(1)

    if _USE_TOMLLIB:
        with open(file_path, "rb") as f:
            data = tomllib.load(f)
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            data = toml.load(f)

    print("Parsed TOML data:")
    print(data)


if __name__ == "__main__":
    main()
