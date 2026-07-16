#!/usr/bin/env python3
"""
Topic: Read JSON Input

Reads and parses a JSON file (creating a sample one if none is given),
then prints selected values from it.

Usage:
    python read_json_input.py [path_to_file.json]

Expected Output:
    The parsed JSON content, plus a couple of extracted fields.
"""

import json
import sys
import os


def main() -> None:
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "sample_data.json"
        if not os.path.exists(file_path):
            sample = {
                "name": "Junaid",
                "role": "Automation Engineer",
                "tools": ["python", "bash", "git"]
            }
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(sample, f, indent=2)
        print(f"No file given, using generated sample: {file_path}\n")

    if not os.path.isfile(file_path):
        print(f"Error: file not found -> {file_path}", file=sys.stderr)
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: invalid JSON -> {e}", file=sys.stderr)
            sys.exit(1)

    print("Parsed JSON data:")
    print(json.dumps(data, indent=2))

    if isinstance(data, dict):
        print(f"\nName value: {data.get('name', 'N/A')}")


if __name__ == "__main__":
    main()
