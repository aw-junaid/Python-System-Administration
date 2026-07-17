#!/usr/bin/env python3
"""
jq_query.py
--------------
Topic 347: Parse and Transform with jq-style Queries

Applies simplified jq-style path expressions to JSON data, entirely
in pure Python (no dependency on the `jq` C library, which can be
tricky to install on some systems). Supports:

    .a.b.c          -> nested field access
    .a.b[0]         -> array indexing
    .a.b[*]         -> collect a field across every array item
    .[]             -> iterate a top-level array

USAGE
    python3 jq_query.py
    python3 jq_query.py --input data.json --query ".employees[*].name"
    python3 jq_query.py --json '{"a":{"b":5}}' --query ".a.b"

EXPECTED OUTPUT
    The result of applying the query, printed as JSON.

NOTE
    This is a lightweight subset of real jq syntax, sufficient for
    common field-extraction and array-mapping tasks. It does not
    implement jq's full filter language (pipes, functions, etc).
"""
import argparse
import json
import re
import sys
from pathlib import Path

DEMO_DATA = {
    "company": "Acme Corp",
    "employees": [
        {"name": "Alice", "role": "Engineer", "salary": 95000},
        {"name": "Bob", "role": "Designer", "salary": 80000},
    ],
}

TOKEN_RE = re.compile(r"\.([A-Za-z0-9_]+)|\[(\*|\d+)\]|\.\[\]")


def tokenize(query: str):
    tokens = []
    pos = 0
    query = query.strip()
    while pos < len(query):
        m = TOKEN_RE.match(query, pos)
        if not m:
            sys.exit(f"ERROR: could not parse query near '{query[pos:]}'")
        if m.group(0) == ".[]":
            tokens.append(("wildcard_top", None))
        elif m.group(1) is not None:
            tokens.append(("field", m.group(1)))
        elif m.group(2) == "*":
            tokens.append(("wildcard", None))
        else:
            tokens.append(("index", int(m.group(2))))
        pos = m.end()
    return tokens


def apply_tokens(data, tokens):
    if not tokens:
        return data
    kind, val = tokens[0]
    rest = tokens[1:]

    if kind == "field":
        if isinstance(data, dict) and val in data:
            return apply_tokens(data[val], rest)
        return None
    if kind == "index":
        if isinstance(data, list) and 0 <= val < len(data):
            return apply_tokens(data[val], rest)
        return None
    if kind in ("wildcard", "wildcard_top"):
        if isinstance(data, list):
            return [apply_tokens(item, rest) for item in data]
        return None
    return None


def main():
    parser = argparse.ArgumentParser(description="Apply a jq-style query to JSON")
    parser.add_argument("--input", help="Path to a JSON file")
    parser.add_argument("--json", help="Raw JSON string")
    parser.add_argument(
        "--query",
        default=".employees[*].name",
        help='jq-style query, e.g. ".employees[*].name" (default shown)',
    )
    args = parser.parse_args()

    if args.json:
        data = json.loads(args.json)
    elif args.input:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    else:
        data = DEMO_DATA

    tokens = tokenize(args.query)
    result = apply_tokens(data, tokens)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
