#!/usr/bin/env python3
"""
json_serialize.py
------------------
Topic 337: Serialize Python Objects to JSON

Converts Python dictionaries, lists, and custom objects (dataclasses /
plain classes with __dict__) into a JSON string, and optionally writes
the result to a file.

USAGE
    # Run built-in demo (no arguments needed)
    python3 json_serialize.py

    # Serialize a custom "input" python literal file (a .py file that
    # defines a variable called DATA) and write JSON to output.json
    python3 json_serialize.py --input mydata.py --output out.json

    # Pretty print with custom indent
    python3 json_serialize.py --indent 4

EXPECTED OUTPUT
    A JSON string printed to the terminal (and written to --output
    if given). The demo serializes a dict, a list, a dataclass
    instance and a datetime object.
"""
import argparse
import importlib.util
import json
import sys
from dataclasses import asdict, is_dataclass, dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class Employee:
    name: str
    role: str
    hired: datetime


class DemoJSONEncoder(json.JSONEncoder):
    """Encoder that knows how to serialize dataclasses, datetimes and
    generic objects that expose __dict__."""

    def default(self, obj):
        if is_dataclass(obj):
            return asdict(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return super().default(obj)


def build_demo_data():
    return {
        "company": "Acme Corp",
        "employees": [
            Employee("Alice", "Engineer", datetime(2022, 3, 1)),
            Employee("Bob", "Designer", datetime(2023, 7, 15)),
        ],
        "tags": ["python", "json", "serialization"],
        "active": True,
        "headcount": 2,
    }


def load_input_module(path: str):
    """Load a .py file and return its DATA attribute."""
    spec = importlib.util.spec_from_file_location("user_input", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "DATA"):
        sys.exit(f"ERROR: {path} must define a top-level variable named DATA")
    return module.DATA


def main():
    parser = argparse.ArgumentParser(description="Serialize Python objects to JSON")
    parser.add_argument("--input", help="Path to a .py file defining a DATA variable")
    parser.add_argument("--output", help="Path to write the resulting JSON file")
    parser.add_argument("--indent", type=int, default=2, help="Indent width (default: 2)")
    args = parser.parse_args()

    data = load_input_module(args.input) if args.input else build_demo_data()

    json_text = json.dumps(data, cls=DemoJSONEncoder, indent=args.indent)
    print(json_text)

    if args.output:
        Path(args.output).write_text(json_text, encoding="utf-8")
        print(f"\n[written to {args.output}]", file=sys.stderr)


if __name__ == "__main__":
    main()
