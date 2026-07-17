#!/usr/bin/env python3
"""
xml_to_csv.py
----------------
Topic 346: Convert XML to CSV

Flattens XML document data into row-based CSV, one row per repeated
child element under a chosen "row tag" (e.g. every <record> under
<records>). Uses only the standard library.

USAGE
    python3 xml_to_csv.py
    python3 xml_to_csv.py --input data.xml --output data.csv --row record

EXPECTED OUTPUT
    A CSV table printed to the terminal (and written to --output if
    given), one column per unique child-tag found across rows.
"""
import argparse
import csv
import io
import sys
from pathlib import Path
from xml.etree.ElementTree import fromstring

DEMO_XML = """<records>
  <record>
    <id>1</id>
    <name>Alice</name>
    <city>Lahore</city>
  </record>
  <record>
    <id>2</id>
    <name>Bob</name>
    <city>Karachi</city>
  </record>
</records>
"""


def main():
    parser = argparse.ArgumentParser(description="Convert XML to CSV")
    parser.add_argument("--input", help="Path to an XML file")
    parser.add_argument("--output", help="Path to write the CSV file")
    parser.add_argument("--row", default="record", help="Tag name of repeated row elements (default: record)")
    args = parser.parse_args()

    text = Path(args.input).read_text(encoding="utf-8") if args.input else DEMO_XML

    try:
        root = fromstring(text)
    except Exception as exc:
        sys.exit(f"ERROR: could not parse XML: {exc}")

    rows = root.findall(f".//{args.row}")
    if not rows:
        sys.exit(f"ERROR: no elements named <{args.row}> found in the XML")

    flat_rows = []
    fieldnames = []
    for row_el in rows:
        flat = {}
        for child in row_el:
            flat[child.tag] = child.text or ""
            if child.tag not in fieldnames:
                fieldnames.append(child.tag)
        flat_rows.append(flat)

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
