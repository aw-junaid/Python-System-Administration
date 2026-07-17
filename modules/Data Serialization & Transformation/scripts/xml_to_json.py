#!/usr/bin/env python3
"""
xml_to_json.py
----------------
Topic 343: Convert XML to JSON

Extracts structured data from an XML document and represents it as a
JSON object. Uses xmltodict (see requirements.txt) which preserves
attributes (prefixed with "@") and text content (key "#text").

USAGE
    python3 xml_to_json.py
    python3 xml_to_json.py --input data.xml --output data.json

EXPECTED OUTPUT
    Pretty-printed JSON printed to the terminal (and written to
    --output if given).
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

DEMO_XML = """<?xml version="1.0"?>
<company name="Acme Corp">
  <employees>
    <employee id="1">
      <name>Alice</name>
      <role>Engineer</role>
    </employee>
    <employee id="2">
      <name>Bob</name>
      <role>Designer</role>
    </employee>
  </employees>
</company>
"""


def main():
    parser = argparse.ArgumentParser(description="Convert XML to JSON")
    parser.add_argument("--input", help="Path to an XML file")
    parser.add_argument("--output", help="Path to write the JSON file")
    parser.add_argument("--indent", type=int, default=2)
    args = parser.parse_args()

    text = Path(args.input).read_text(encoding="utf-8") if args.input else DEMO_XML

    try:
        data = xmltodict.parse(text)
    except Exception as exc:
        sys.exit(f"ERROR: could not parse XML: {exc}")

    json_text = json.dumps(data, indent=args.indent)
    print(json_text)
    if args.output:
        Path(args.output).write_text(json_text, encoding="utf-8")
        print(f"[written to {args.output}]", file=sys.stderr)


if __name__ == "__main__":
    main()
