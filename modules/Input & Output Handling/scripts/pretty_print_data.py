#!/usr/bin/env python3
"""
Topic: Pretty-Print Structured Data

Compares Python's built-in pprint module against normal print() for
nested data structures (dicts/lists), and shows pretty JSON output too.

Usage:
    python pretty_print_data.py

Expected Output:
    The same nested data structure printed three ways: plain print(),
    pprint.pprint(), and json.dumps(indent=2).
"""

import json
from pprint import pprint


def main() -> None:
    data = {
        "name": "Junaid",
        "role": "Python Developer",
        "skills": ["automation", "scripting", "linux", "networking"],
        "projects": [
            {"title": "System Admin Toolkit", "stars": 42},
            {"title": "CLI Utilities", "stars": 17},
        ],
        "active": True,
    }

    print("--- Using plain print() ---")
    print(data)

    print("\n--- Using pprint.pprint() ---")
    pprint(data)

    print("\n--- Using json.dumps(indent=2) ---")
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
