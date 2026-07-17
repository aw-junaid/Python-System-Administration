#!/usr/bin/env python3
"""
flatten_json.py
-------------------
Topic 355: Flatten Nested JSON Structures

Transforms deeply nested JSON objects/arrays into flat key-value
pairs (dot/bracket notation keys), suitable for database insertion
or CSV export. Also supports the reverse operation (unflatten) to
rebuild the original nested structure.

USAGE
    # Run built-in demo (no arguments needed)
    python3 flatten_json.py

    # Flatten a specific file
    python3 flatten_json.py --input data.json --output flat.json

    # Unflatten a previously flattened file back to nested JSON
    python3 flatten_json.py --mode unflatten --input flat.json --output nested.json

    # Use a custom separator (default is ".")
    python3 flatten_json.py --sep "_"

EXPECTED OUTPUT
    Pretty-printed JSON (flat or nested, depending on --mode) printed
    to the terminal (and written to --output if given).
"""
import argparse
import json
import re
import sys
from pathlib import Path

DEMO_DATA = {
    "user": {
        "id": 101,
        "name": "Alice",
        "address": {"city": "Lahore", "zip": "54000"},
        "roles": ["admin", "editor"],
    },
    "active": True,
}

INDEX_RE = re.compile(r"\[(\d+)\]$")


def flatten(obj, parent_key="", sep=".", out=None):
    if out is None:
        out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else str(k)
            flatten(v, new_key, sep, out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            new_key = f"{parent_key}[{i}]"
            flatten(v, new_key, sep, out)
    else:
        out[parent_key] = obj
    return out


def unflatten(flat: dict, sep="."):
    result = {}
    for compound_key, value in flat.items():
        parts = re.split(rf"{re.escape(sep)}|(?=\[)", compound_key)
        parts = [p for p in parts if p != ""]
        cursor = result
        for i, part in enumerate(parts):
            m = INDEX_RE.match(part)
            is_last = i == len(parts) - 1
            if m:
                idx = int(m.group(1))
                # cursor must be a list at this point
                if not isinstance(cursor, list):
                    raise ValueError(f"Cannot apply index on non-list at '{part}'")
                while len(cursor) <= idx:
                    cursor.append(None)
                if is_last:
                    cursor[idx] = value
                else:
                    nxt = parts[i + 1]
                    if cursor[idx] is None:
                        cursor[idx] = [] if INDEX_RE.match(nxt) else {}
                    cursor = cursor[idx]
            else:
                if is_last:
                    cursor[part] = value
                else:
                    nxt = parts[i + 1]
                    if part not in cursor or cursor[part] is None:
                        cursor[part] = [] if INDEX_RE.match(nxt) else {}
                    cursor = cursor[part]
    return result


def main():
    parser = argparse.ArgumentParser(description="Flatten or unflatten JSON structures")
    parser.add_argument("--mode", choices=["flatten", "unflatten"], default="flatten")
    parser.add_argument("--input", help="Path to a JSON file")
    parser.add_argument("--output", help="Path to write the resulting JSON file")
    parser.add_argument("--sep", default=".", help="Separator for nested keys (default: '.')")
    parser.add_argument("--indent", type=int, default=2)
    args = parser.parse_args()

    if args.input:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    else:
        data = DEMO_DATA

    if args.mode == "flatten":
        result = flatten(data, sep=args.sep)
    else:
        if not isinstance(data, dict):
            sys.exit("ERROR: unflatten mode requires a flat JSON object as input")
        result = unflatten(data, sep=args.sep)

    json_text = json.dumps(result, indent=args.indent)
    print(json_text)
    if args.output:
        Path(args.output).write_text(json_text, encoding="utf-8")
        print(f"[written to {args.output}]", file=sys.stderr)


if __name__ == "__main__":
    main()
