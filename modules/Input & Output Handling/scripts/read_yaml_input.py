#!/usr/bin/env python3
"""
Topic: Read YAML Input

Reads and parses a YAML file (creating a sample one if none is given) using
the third-party 'PyYAML' library.

Requires: PyYAML  (see requirements.txt)

Usage:
    python read_yaml_input.py [path_to_file.yaml]

Expected Output:
    The parsed YAML content printed as a Python dictionary.
"""

import sys
import os

try:
    import yaml
except ImportError:
    print("Error: PyYAML is not installed. Install it with: pip install PyYAML", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "sample_data.yaml"
        if not os.path.exists(file_path):
            sample = """\
name: Junaid
role: Automation Engineer
tools:
  - python
  - bash
  - git
active: true
"""
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(sample)
        print(f"No file given, using generated sample: {file_path}\n")

    if not os.path.isfile(file_path):
        print(f"Error: file not found -> {file_path}", file=sys.stderr)
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    print("Parsed YAML data:")
    print(data)


if __name__ == "__main__":
    main()
