#!/usr/bin/env python3
"""
generate_xml_report.py

Generates a well-formed, indented XML report in a format compatible
with legacy enterprise tooling (a root <report> element containing
<metadata> and a <records> collection of <record> elements). Uses
only the Python standard library (xml.etree.ElementTree).

Usage:
    python generate_xml_report.py
    python generate_xml_report.py --input data.csv --output report.xml --title "My Report"

Expected output:
    An .xml file, UTF-8 encoded, with a declaration line, a <report>
    root element, a <metadata> block (title, generated_at, count),
    and a <records> block with one <record> per row, each field as
    a child element named after the CSV column header.
"""

import argparse
import csv
import datetime
import os
import re
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom


def load_sample_data():
    headers = ["order_id", "customer", "total", "currency", "status"]
    rows = [
        ["ORD-001", "Zainab Traders", "1200.00", "USD", "Shipped"],
        ["ORD-002", "Khan Enterprises", "875.50", "USD", "Pending"],
        ["ORD-003", "Malik & Co", "430.00", "USD", "Delivered"],
    ]
    return headers, rows


def load_csv_data(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if not rows:
        raise ValueError("CSV file is empty.")
    return rows[0], rows[1:]


def sanitize_tag(name):
    """XML element names can't contain spaces or start with a digit."""
    tag = re.sub(r"[^0-9a-zA-Z_]", "_", name.strip())
    if not tag or tag[0].isdigit():
        tag = f"field_{tag}"
    return tag


def build_xml(headers, rows, title):
    root = ET.Element("report")

    metadata = ET.SubElement(root, "metadata")
    ET.SubElement(metadata, "title").text = title
    ET.SubElement(metadata, "generated_at").text = datetime.datetime.now().isoformat()
    ET.SubElement(metadata, "record_count").text = str(len(rows))

    tags = [sanitize_tag(h) for h in headers]

    records = ET.SubElement(root, "records")
    for row in rows:
        record = ET.SubElement(records, "record")
        for tag, value in zip(tags, row):
            ET.SubElement(record, tag).text = str(value)

    rough_string = ET.tostring(root, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", encoding="UTF-8")


def main():
    parser = argparse.ArgumentParser(description="Generate a legacy-compatible XML report from CSV data.")
    parser.add_argument("--input", "-i", help="Path to input CSV file. If omitted, sample data is used.")
    parser.add_argument("--output", "-o", default="report.xml", help="Path to output XML file (default: report.xml)")
    parser.add_argument("--title", "-t", default="Order Summary Report", help="Report title")
    args = parser.parse_args()

    if args.input:
        if not os.path.isfile(args.input):
            print(f"Error: input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        headers, rows = load_csv_data(args.input)
    else:
        headers, rows = load_sample_data()
        print("No --input provided, using built-in sample data.")

    xml_bytes = build_xml(headers, rows, args.title)

    with open(args.output, "wb") as f:
        f.write(xml_bytes)

    print(f"XML report written to: {os.path.abspath(args.output)}")
    print("Valid, well-formed XML. Open in a browser, text editor, or parse with any XML library.")


if __name__ == "__main__":
    main()
