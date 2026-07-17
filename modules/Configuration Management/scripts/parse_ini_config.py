#!/usr/bin/env python3
"""
parse_ini_config.py

Purpose:
    Parse an INI-format configuration file (sections with key=value
    pairs) using Python's built-in configparser module, and print its
    structure.

Usage:
    python3 parse_ini_config.py <path_to_file.ini>

    If no path is given, this script creates and parses a demo
    demo_config.ini file in the current directory.

Expected Output:
    Sections found: ['server', 'database']

    [server]
      host = 127.0.0.1
      port = 8080

    [database]
      name = mydb
      user = admin

Caution:
    - This script only reads/parses the file; it makes no changes.
    - configparser treats all values as strings by default (e.g. "8080"
      stays a string) — convert types yourself if you need integers or
      booleans (see validate_config_values.py in this folder for an
      example of type validation).
    - Duplicate section names or malformed syntax will raise a
      configparser error; this script catches and reports that clearly
      instead of crashing with a raw traceback.
"""

import configparser
import os
import sys

DEMO_FILE = "demo_config.ini"
DEMO_CONTENT = (
    "[server]\n"
    "host = 127.0.0.1\n"
    "port = 8080\n"
    "\n"
    "[database]\n"
    "name = mydb\n"
    "user = admin\n"
)


def parse_ini(path: str) -> None:
    if not os.path.isfile(path):
        print(f"Error: file not found: {path}")
        return

    parser = configparser.ConfigParser()
    try:
        parser.read(path, encoding="utf-8")
    except configparser.Error as e:
        print(f"Error parsing INI file: {e}")
        return

    print(f"Sections found: {parser.sections()}\n")
    for section in parser.sections():
        print(f"[{section}]")
        for key, value in parser.items(section):
            print(f"  {key} = {value}")
        print()


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        print("No file path given, creating and parsing a demo INI file.\n")
        if not os.path.isfile(DEMO_FILE):
            with open(DEMO_FILE, "w", encoding="utf-8") as f:
                f.write(DEMO_CONTENT)
        path = DEMO_FILE
    parse_ini(path)


if __name__ == "__main__":
    main()
