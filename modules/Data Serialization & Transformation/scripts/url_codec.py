#!/usr/bin/env python3
"""
url_codec.py
---------------
Topic 353: URL Encode/Decode Data

Percent-encodes special characters for safe inclusion in URLs (query
strings, path segments) and decodes them back. Standard library only
(urllib.parse).

USAGE
    # Run built-in demo (no arguments needed)
    python3 url_codec.py

    # Encode a string
    python3 url_codec.py --mode encode --text "search term with spaces & symbols"

    # Decode a string
    python3 url_codec.py --mode decode --text "search%20term%20with%20spaces%20%26%20symbols"

    # Encode/decode a full query-string dict (JSON object of key/value pairs)
    python3 url_codec.py --mode encode-query --json '{"q": "python 3", "page": "2"}'

EXPECTED OUTPUT
    The encoded or decoded string, printed to the terminal.
"""
import argparse
import json
import sys
from urllib.parse import quote, unquote, urlencode, parse_qs

DEMO_TEXT = "search term with spaces & symbols?"


def main():
    parser = argparse.ArgumentParser(description="URL encode/decode data")
    parser.add_argument(
        "--mode",
        choices=["encode", "decode", "encode-query", "decode-query"],
        default="encode",
    )
    parser.add_argument("--text", help="Text to encode/decode")
    parser.add_argument("--json", help="JSON object for encode-query mode")
    args = parser.parse_args()

    if args.mode == "encode":
        text = args.text if args.text is not None else DEMO_TEXT
        print(quote(text))
    elif args.mode == "decode":
        text = args.text if args.text is not None else quote(DEMO_TEXT)
        print(unquote(text))
    elif args.mode == "encode-query":
        obj = json.loads(args.json) if args.json else {"q": "python 3", "page": "2"}
        print(urlencode(obj))
    elif args.mode == "decode-query":
        text = args.text if args.text is not None else "q=python+3&page=2"
        parsed = parse_qs(text)
        print(json.dumps({k: v[0] if len(v) == 1 else v for k, v in parsed.items()}, indent=2))


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(f"Original       : {DEMO_TEXT}")
        print(f"URL-encoded    : {quote(DEMO_TEXT)}")
        print(f"Decoded again  : {unquote(quote(DEMO_TEXT))}")
    else:
        main()
