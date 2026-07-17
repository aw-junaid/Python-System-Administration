#!/usr/bin/env python3
"""
parse_xml_config.py

Purpose:
    Parse an XML configuration file using Python's built-in
    xml.etree.ElementTree module and print its tree structure.

Usage:
    python3 parse_xml_config.py <path_to_file.xml>

    If no path is given, this script creates and parses a demo
    demo_config.xml file in the current directory.

Expected Output:
    Root tag: configuration
    configuration
      server
        host: 127.0.0.1
        port: 8080
      debug: true

Caution:
    - This script uses xml.etree.ElementTree, which is safe against the
      most dangerous XML attacks (like external entity expansion) as
      long as you stick to the standard library's default settings, as
      used here. Avoid third-party XML parsers with entity resolution
      enabled on untrusted files.
    - This script only reads/parses; it makes no changes to the file.
    - Deeply nested or attribute-heavy XML may need custom traversal
      logic beyond this simple demo printer.
"""

import os
import sys
import xml.etree.ElementTree as ET

DEMO_FILE = "demo_config.xml"
DEMO_CONTENT = (
    "<configuration>\n"
    "  <server>\n"
    "    <host>127.0.0.1</host>\n"
    "    <port>8080</port>\n"
    "  </server>\n"
    "  <debug>true</debug>\n"
    "</configuration>\n"
)


def print_element(element, indent=0):
    label = element.tag
    if len(element) == 0:
        text = (element.text or "").strip()
        print("  " * indent + f"{label}: {text}")
    else:
        print("  " * indent + label)
        for child in element:
            print_element(child, indent + 1)


def parse_xml(path: str) -> None:
    if not os.path.isfile(path):
        print(f"Error: file not found: {path}")
        return

    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")
        return

    root = tree.getroot()
    print(f"Root tag: {root.tag}")
    print_element(root)


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        print("No file path given, creating and parsing a demo XML file.\n")
        if not os.path.isfile(DEMO_FILE):
            with open(DEMO_FILE, "w", encoding="utf-8") as f:
                f.write(DEMO_CONTENT)
        path = DEMO_FILE
    parse_xml(path)


if __name__ == "__main__":
    main()
