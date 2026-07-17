#!/usr/bin/env python3
"""
parse_xml.py
-----------------
Fetches XML from a URL (or reads a local XML file) and demonstrates
parsing it using Python's built-in `xml.etree.ElementTree` - no
extra dependency needed for basic XML parsing.

Usage:
    python3 parse_xml.py --url https://www.w3schools.com/xml/note.xml
    python3 parse_xml.py --file data.xml
"""

import argparse
import xml.etree.ElementTree as ET
import requests


def get_xml_root(url=None, filepath=None):
    if url:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return ET.fromstring(response.content)
    elif filepath:
        tree = ET.parse(filepath)
        return tree.getroot()
    else:
        raise ValueError("Either url or filepath must be provided")


def explore_xml(root, max_children=10):
    print(f"Root tag: <{root.tag}>")
    print(f"Root attributes: {root.attrib}\n")

    print("Children of root:")
    for i, child in enumerate(root):
        if i >= max_children:
            print(f"  ... ({len(root) - max_children} more)")
            break
        text = (child.text or "").strip()
        print(f"  <{child.tag}> attrib={child.attrib} text='{text[:60]}'")

    print("\nExample - find all elements matching a tag name:")
    if len(root) > 0:
        first_tag = root[0].tag
        matches = root.findall(f".//{first_tag}")
        print(f"  Found {len(matches)} element(s) with tag <{first_tag}>")


def main():
    parser = argparse.ArgumentParser(description="Fetch and parse an XML response")
    parser.add_argument("--url", help="URL returning XML")
    parser.add_argument("--file", help="Local XML file path")
    args = parser.parse_args()

    if not args.url and not args.file:
        print("Provide either --url or --file")
        return

    try:
        root = get_xml_root(url=args.url, filepath=args.file)
        explore_xml(root)
    except (requests.RequestException, ET.ParseError, FileNotFoundError) as e:
        print(f"Failed to fetch/parse XML: {e}")


if __name__ == "__main__":
    main()
