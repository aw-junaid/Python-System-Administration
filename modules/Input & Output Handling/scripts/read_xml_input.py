#!/usr/bin/env python3
"""
Topic: Read XML Input

Reads and parses an XML file (creating a sample one if none is given) using
Python's built-in xml.etree.ElementTree module.

Usage:
    python read_xml_input.py [path_to_file.xml]

Expected Output:
    The XML tree traversed and printed as tag/attribute/text info.
"""

import sys
import os
import xml.etree.ElementTree as ET


def main() -> None:
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "sample_data.xml"
        if not os.path.exists(file_path):
            sample = """<?xml version="1.0"?>
<people>
    <person id="1">
        <name>Junaid</name>
        <role>Automation Engineer</role>
    </person>
    <person id="2">
        <name>Sara</name>
        <role>Sysadmin</role>
    </person>
</people>
"""
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(sample)
        print(f"No file given, using generated sample: {file_path}\n")

    if not os.path.isfile(file_path):
        print(f"Error: file not found -> {file_path}", file=sys.stderr)
        sys.exit(1)

    tree = ET.parse(file_path)
    root = tree.getroot()

    print(f"Root tag: {root.tag}")
    for child in root:
        attrs = child.attrib
        print(f"\n<{child.tag}> attributes: {attrs}")
        for field in child:
            print(f"  {field.tag}: {field.text}")


if __name__ == "__main__":
    main()
