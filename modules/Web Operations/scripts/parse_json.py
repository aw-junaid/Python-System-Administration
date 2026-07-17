#!/usr/bin/env python3
"""
parse_json.py
------------------
Fetches JSON from a URL (or reads a local JSON file) and demonstrates
parsing/navigating it: accessing keys, iterating lists, and handling
missing fields safely.

Usage:
    python3 parse_json.py --url https://jsonplaceholder.typicode.com/users
    python3 parse_json.py --file data.json
"""

import argparse
import json
import requests


def get_json_data(url=None, filepath=None):
    if url:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.json()
    elif filepath:
        with open(filepath, "r") as f:
            return json.load(f)
    else:
        raise ValueError("Either url or filepath must be provided")


def explore_json(data):
    print(f"Top-level type: {type(data).__name__}\n")

    if isinstance(data, list):
        print(f"List with {len(data)} item(s). Showing first item:")
        if data:
            print(json.dumps(data[0], indent=2)[:800])
            print(f"\nExample - safely accessing a field from item 0:")
            first = data[0]
            if isinstance(first, dict):
                # .get() avoids KeyError if the field doesn't exist
                print(f"  name/title: {first.get('name', first.get('title', 'N/A'))}")

    elif isinstance(data, dict):
        print("Top-level keys:", list(data.keys()))
        print("\nFull structure (first 800 chars):")
        print(json.dumps(data, indent=2)[:800])

    else:
        print("Value:", data)


def main():
    parser = argparse.ArgumentParser(description="Fetch and parse a JSON response")
    parser.add_argument("--url", help="URL returning JSON")
    parser.add_argument("--file", help="Local JSON file path")
    args = parser.parse_args()

    if not args.url and not args.file:
        print("Provide either --url or --file")
        return

    try:
        data = get_json_data(url=args.url, filepath=args.file)
        explore_json(data)
    except (requests.RequestException, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Failed to fetch/parse JSON: {e}")


if __name__ == "__main__":
    main()
