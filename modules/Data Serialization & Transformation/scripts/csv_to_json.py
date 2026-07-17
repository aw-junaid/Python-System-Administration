#!/usr/bin/env python3
"""
csv_to_json.py
---------------
Topic 340: Convert CSV to JSON

Transforms tabular CSV data into a JSON array of objects. Column
names containing a dot (e.g. "address.city") are automatically
nested back into sub-objects. Numeric-looking values are converted
to int/float, "true"/"false" to booleans.

USAGE
    # Run built-in demo (no arguments needed)
    python3 csv_to_json.py

    # Convert a specific file
    python3 csv_to_json.py --input data.csv --output data.json

EXPECTED OUTPUT
    A pretty-printed JSON array printed to the terminal (and written
    to --output if given).
"""
import argparse
import csv
import io
import json
import sys
from pathlib import Path

DEMO_CSV = """id,name,address.city,address.zip,active
1,Alice,Lahore,54000,true
2,Bob,Karachi,74000,false
"""


def coerce(value: str):
    if value == "":
        return None
    low = value.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def nest(flat_row: dict) -> dict:
    result = {}
    for key, value in flat_row.items():
        parts = key.split(".")
        d = result
        for part in parts[:-1]:
            d = d.setdefault(part, {})
        d[parts[-1]] = coerce(value)
    return result


def main():
    parser = argparse.ArgumentParser(description="Convert CSV to nested JSON")
    parser.add_argument("--input", help="Path to a CSV file")
    parser.add_argument("--output", help="Path to write the JSON file")
    parser.add_argument("--indent", type=int, default=2)
    args = parser.parse_args()

    text = Path(args.input).read_text(encoding="utf-8") if args.input else DEMO_CSV
    reader = csv.DictReader(io.StringIO(text))
    rows = [nest(row) for row in reader]

    if not rows:
        sys.exit("ERROR: no rows found in CSV input")

    json_text = json.dumps(rows, indent=args.indent)
    print(json_text)
    if args.output:
        Path(args.output).write_text(json_text, encoding="utf-8")
        print(f"[written to {args.output}]", file=sys.stderr)


if __name__ == "__main__":
    main()
