#!/usr/bin/env python3
"""
validate_json_schema.py
---------------------------
Topic 357: Validate JSON Against JSON Schema

Verifies that JSON data conforms to a JSON Schema (type checking,
required fields, constraints like min/max, patterns, enums, etc).
Requires the `jsonschema` package (see requirements.txt).

USAGE
    # Run built-in demo (validates a sample record against a sample
    # schema, then shows a deliberately invalid record failing)
    python3 validate_json_schema.py

    # Validate your own files
    python3 validate_json_schema.py --schema schema.json --data record.json

EXPECTED OUTPUT
    "VALID" with no errors if the data conforms, or a list of
    validation error messages (path + reason) if it does not.
"""
import argparse
import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft7Validator
except ImportError:
    sys.exit(
        "ERROR: jsonschema is not installed.\n"
        "Install dependencies first:  pip install -r requirements.txt"
    )

DEMO_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "age": {"type": "integer", "minimum": 0},
        "email": {"type": "string", "pattern": r"^[^@]+@[^@]+\.[^@]+$"},
    },
    "required": ["name", "age", "email"],
}

DEMO_VALID = {"name": "Alice", "age": 30, "email": "alice@example.com"}
DEMO_INVALID = {"name": "", "age": -5, "email": "not-an-email"}


def validate(schema: dict, data) -> list:
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    return [
        f"{'.'.join(str(p) for p in err.path) or '(root)'}: {err.message}"
        for err in errors
    ]


def report(label, schema, data):
    print(f"--- {label} ---")
    errors = validate(schema, data)
    if not errors:
        print("VALID: data conforms to the schema.\n")
    else:
        print("INVALID: the following problems were found:")
        for e in errors:
            print(f"  - {e}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Validate JSON data against a JSON Schema")
    parser.add_argument("--schema", help="Path to a JSON Schema file")
    parser.add_argument("--data", help="Path to the JSON data file to validate")
    args = parser.parse_args()

    if bool(args.schema) != bool(args.data):
        sys.exit("ERROR: --schema and --data must be provided together")

    if args.schema and args.data:
        schema = json.loads(Path(args.schema).read_text(encoding="utf-8"))
        data = json.loads(Path(args.data).read_text(encoding="utf-8"))
        report(f"Validating {args.data} against {args.schema}", schema, data)
    else:
        report("Demo: valid record", DEMO_SCHEMA, DEMO_VALID)
        report("Demo: invalid record", DEMO_SCHEMA, DEMO_INVALID)


if __name__ == "__main__":
    main()
