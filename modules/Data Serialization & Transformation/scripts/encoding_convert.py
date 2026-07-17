#!/usr/bin/env python3
"""
encoding_convert.py
-----------------------
Topic 354: Convert Between Character Encodings

Transcodes text files between character encodings (e.g. UTF-8,
Latin-1/ISO-8859-1, ASCII, UTF-16) without data loss, as long as the
target encoding can represent every character in the source text.
Standard library only.

USAGE
    # Run built-in demo (no arguments needed)
    python3 encoding_convert.py

    # Convert a file from Latin-1 to UTF-8
    python3 encoding_convert.py --input legacy.txt --from-encoding latin-1 \\
        --to-encoding utf-8 --output modern.txt

EXPECTED OUTPUT
    Confirms the source/target encodings and byte counts, and writes
    the transcoded file if --output is given. If a character cannot
    be represented in the target encoding, a clear error is shown
    (use --errors replace or --errors ignore to override).
"""
import argparse
import sys
from pathlib import Path

DEMO_TEXT = "Café - naïve - 100% résumé"


def main():
    parser = argparse.ArgumentParser(description="Convert text between character encodings")
    parser.add_argument("--input", help="Path to a text file to convert")
    parser.add_argument("--output", help="Path to write the converted file")
    parser.add_argument("--from-encoding", default="utf-8", help="Source encoding (default: utf-8)")
    parser.add_argument("--to-encoding", default="latin-1", help="Target encoding (default: latin-1)")
    parser.add_argument(
        "--errors",
        default="strict",
        choices=["strict", "replace", "ignore"],
        help="How to handle characters that don't fit the target encoding",
    )
    args = parser.parse_args()

    if args.input:
        raw_bytes = Path(args.input).read_bytes()
        text = raw_bytes.decode(args.from_encoding)
    else:
        text = DEMO_TEXT

    try:
        converted = text.encode(args.to_encoding, errors=args.errors)
    except UnicodeEncodeError as exc:
        sys.exit(
            f"ERROR: cannot encode to {args.to_encoding}: {exc}\n"
            f"Try --errors replace or --errors ignore, or pick a target encoding "
            f"that supports all characters (e.g. utf-8)."
        )

    print(f"Text            : {text}")
    print(f"Source encoding : {args.from_encoding}")
    print(f"Target encoding : {args.to_encoding}")
    print(f"Converted bytes : {converted!r}")

    if args.output:
        Path(args.output).write_bytes(converted)
        print(f"[written to {args.output}]", file=sys.stderr)


if __name__ == "__main__":
    main()
