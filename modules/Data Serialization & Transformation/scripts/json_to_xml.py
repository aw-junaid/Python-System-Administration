#!/usr/bin/env python3
"""
json_to_xml.py
-----------------
Topic 344: Convert JSON to XML

Builds an XML document from a JSON data structure using xmltodict's
unparse(). The JSON must have a single root key (XML requires exactly
one root element) -- the demo and README show the expected shape.

USAGE
    python3 json_to_xml.py
    python3 json_to_xml.py --input data.json --output data.xml --root company

EXPECTED OUTPUT
    An XML document printed to the terminal (and written to --output
    if given).
"""
import argparse
import json
import sys
from pathlib import Path

try:
    import xmltodict
except ImportError:
    sys.exit(
        "ERROR: xmltodict is not installed.\n"
        "Install dependencies first:  pip install -r requirements.txt"
    )

DEMO_DATA = {
    "company": {
        "@name": "Acme Corp",
        "employees": {
            "employee": [
                {"@id": "1", "name": "Alice", "role": "Engineer"},
                {"@id": "2", "name": "Bob", "role": "Designer"},
            ]
        },
    }
}


def main():
    parser = argparse.ArgumentParser(description="Convert JSON to XML")
    parser.add_argument("--input", help="Path to a JSON file")
    parser.add_argument("--output", help="Path to write the XML file")
    parser.add_argument(
        "--root",
        help="If the JSON has multiple top-level keys, wrap it under this root element name",
    )
    args = parser.parse_args()

    if args.input:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    else:
        data = DEMO_DATA

    if args.root:
        data = {args.root: data}

    if not isinstance(data, dict) or len(data) != 1:
        sys.exit(
            "ERROR: XML requires exactly one root element.\n"
            "Wrap your JSON under a single top-level key, or pass --root NAME."
        )

    try:
        xml_text = xmltodict.unparse(data, pretty=True, indent="  ")
    except Exception as exc:
        sys.exit(f"ERROR: could not build XML: {exc}")

    print(xml_text)
    if args.output:
        Path(args.output).write_text(xml_text, encoding="utf-8")
        print(f"\n[written to {args.output}]", file=sys.stderr)


if __name__ == "__main__":
    main()
