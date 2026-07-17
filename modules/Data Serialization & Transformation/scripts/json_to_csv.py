#!/usr/bin/env python3
"""
json_to_csv.py
---------------
Topic 339: Convert JSON to CSV

Flattens a JSON array of (possibly nested) objects into flat CSV rows.
Nested keys are joined with a dot, e.g. {"a": {"b": 1}} -> column "a.b".

USAGE
    # Run built-in demo (no arguments needed) -> prints CSV to stdout
    python3 json_to_csv.py

    # Convert a specific file
    python3 json_to_csv.py --input data.json --output data.csv

EXPECTED OUTPUT
    A CSV table printed to the terminal (and written to --output if
    given), one row per JSON object, one column per flattened field.
"""
import argparse
import csv
import io
import json
import sys
from pathlib import Path

DEMO_DATA = [
    {
        "id": 1,
        "name": "Alice",
        "address": {"city": "Lahore", "zip": "54000"},
        "skills": ["python", "sql"],
    },
    {
        "id": 2,
        "name": "Bob",
        "address": {"city": "Karachi", "zip": "74000"},
        "skills": ["go"],
    },
]


def flatten(obj, parent_key="", sep="."):
    items = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else str(k)
            items.update(flatten(v, new_key, sep))
    elif isinstance(obj, list):
        # join list of scalars with ';' ; lists of dicts get index-expanded
        if obj and isinstance(obj[0], (dict, list)):
            for i, v in enumerate(obj):
                items.update(flatten(v, f"{parent_key}[{i}]", sep))
        else:
            items[parent_key] = ";".join(str(v) for v in obj)
    else:
        items[parent_key] = obj
    return items


def main():
    parser = argparse.ArgumentParser(description="Convert JSON array to flat CSV")
    parser.add_argument("--input", help="Path to a JSON file (array of objects)")
    parser.add_argument("--output", help="Path to write the CSV file")
    args = parser.parse_args()

    if args.input:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    else:
        data = DEMO_DATA

    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        sys.exit("ERROR: input JSON must be an object or an array of objects")

    flat_rows = [flatten(row) for row in data]
    fieldnames = []
    for row in flat_rows:
        for k in row:
            if k not in fieldnames:
                fieldnames.append(k)

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(flat_rows)
    csv_text = buf.getvalue()

    print(csv_text)
    if args.output:
        Path(args.output).write_text(csv_text, encoding="utf-8")
        print(f"[written to {args.output}]", file=sys.stderr)


if __name__ == "__main__":
    main()
