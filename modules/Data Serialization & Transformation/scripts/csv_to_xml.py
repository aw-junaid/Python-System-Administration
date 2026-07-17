#!/usr/bin/env python3
"""
csv_to_xml.py
----------------
Topic 345: Convert CSV to XML

Transforms tabular CSV data into hierarchical XML markup, useful for
feeding legacy systems that expect XML. Uses only the standard
library (csv + xml.etree.ElementTree).

USAGE
    python3 csv_to_xml.py
    python3 csv_to_xml.py --input data.csv --output data.xml \\
        --root records --row record

EXPECTED OUTPUT
    An XML document printed to the terminal (and written to --output
    if given), with one <row-tag> element per CSV row and one child
    element per column.
"""
import argparse
import csv
import io
import sys
from pathlib import Path
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

DEMO_CSV = """id,name,city,active
1,Alice,Lahore,true
2,Bob,Karachi,false
"""


def csv_to_xml(csv_text: str, root_tag: str, row_tag: str) -> str:
    reader = csv.DictReader(io.StringIO(csv_text))
    root = Element(root_tag)
    for row in reader:
        row_el = SubElement(root, row_tag)
        for key, value in row.items():
            child = SubElement(row_el, key)
            child.text = value
    rough = tostring(root, encoding="unicode")
    return minidom.parseString(rough).toprettyxml(indent="  ")


def main():
    parser = argparse.ArgumentParser(description="Convert CSV to XML")
    parser.add_argument("--input", help="Path to a CSV file")
    parser.add_argument("--output", help="Path to write the XML file")
    parser.add_argument("--root", default="records", help="Root element tag (default: records)")
    parser.add_argument("--row", default="record", help="Per-row element tag (default: record)")
    args = parser.parse_args()

    text = Path(args.input).read_text(encoding="utf-8") if args.input else DEMO_CSV
    xml_text = csv_to_xml(text, args.root, args.row)

    print(xml_text)
    if args.output:
        Path(args.output).write_text(xml_text, encoding="utf-8")
        print(f"[written to {args.output}]", file=sys.stderr)


if __name__ == "__main__":
    main()
