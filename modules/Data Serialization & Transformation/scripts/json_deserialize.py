#!/usr/bin/env python3
"""
json_deserialize.py
--------------------
Topic 338: Deserialize JSON to Python Objects

Parses a JSON string / file back into native Python data structures
(dict, list, str, int, float, bool, None) and shows how to walk the
resulting structure.

USAGE
    # Run built-in demo (no arguments needed)
    python3 json_deserialize.py

    # Deserialize a specific JSON file
    python3 json_deserialize.py --input data.json

    # Deserialize a raw JSON string passed on the command line
    python3 json_deserialize.py --json '{"a": 1, "b": [1,2,3]}'

EXPECTED OUTPUT
    The parsed Python object printed with repr(), its type, and (for
    dict/list top level) a short structural summary.
"""
import argparse
import json
import sys
from pathlib import Path

DEMO_JSON = """
{
  "company": "Acme Corp",
  "employees": [
    {"name": "Alice", "role": "Engineer", "hired": "2022-03-01"},
    {"name": "Bob", "role": "Designer", "hired": "2023-07-15"}
  ],
  "tags": ["python", "json", "serialization"],
  "active": true,
  "headcount": 2,
  "notes": null
}
"""


def summarize(obj, depth=0):
    prefix = "  " * depth
    if isinstance(obj, dict):
        print(f"{prefix}dict with {len(obj)} keys: {list(obj.keys())}")
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                print(f"{prefix}  - {k}:")
                summarize(v, depth + 2)
    elif isinstance(obj, list):
        print(f"{prefix}list with {len(obj)} items")
        if obj and isinstance(obj[0], (dict, list)):
            summarize(obj[0], depth + 1)


def main():
    parser = argparse.ArgumentParser(description="Deserialize JSON into Python objects")
    parser.add_argument("--input", help="Path to a JSON file")
    parser.add_argument("--json", help="Raw JSON string")
    args = parser.parse_args()

    if args.json:
        raw = args.json
    elif args.input:
        raw = Path(args.input).read_text(encoding="utf-8")
    else:
        raw = DEMO_JSON

    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as exc:
        sys.exit(f"ERROR: invalid JSON input: {exc}")

    print(f"Top-level Python type: {type(obj).__name__}\n")
    print("repr():")
    print(repr(obj))
    print("\nStructure summary:")
    summarize(obj)


if __name__ == "__main__":
    main()
