#!/usr/bin/env python3
"""
base64_codec.py
-------------------
Topic 352: Base64 Encode/Decode Data

Encodes binary/text data as ASCII-safe Base64 text (for embedding in
JSON, URLs, or text protocols), and decodes it back to the original
bytes. Standard library only (base64 module).

USAGE
    # Run built-in demo (encode then decode a sample string)
    python3 base64_codec.py

    # Encode a file (any binary file works, e.g. an image)
    python3 base64_codec.py --mode encode --input photo.png --output photo.b64

    # Decode a Base64 file back to binary
    python3 base64_codec.py --mode decode --input photo.b64 --output photo_copy.png

    # Encode/decode raw text directly
    python3 base64_codec.py --mode encode --text "hello world"
    python3 base64_codec.py --mode decode --text "aGVsbG8gd29ybGQ="

EXPECTED OUTPUT
    encode: the Base64 text (and/or an output file).
    decode: the recovered bytes, shown as text if valid UTF-8,
    otherwise a byte count.
"""
import argparse
import base64
import sys
from pathlib import Path

DEMO_TEXT = "Data Serialization & Transformation with Python 🚀"


def main():
    parser = argparse.ArgumentParser(description="Base64 encode/decode data")
    parser.add_argument("--mode", choices=["encode", "decode"], default="encode")
    parser.add_argument("--input", help="Path to a file to read")
    parser.add_argument("--text", help="Raw text to encode/decode instead of a file")
    parser.add_argument("--output", help="Path to write the result")
    args = parser.parse_args()

    demo_mode = args.text is None and args.input is None

    if args.text is not None:
        raw = args.text.encode("utf-8")
    elif args.input:
        raw = Path(args.input).read_bytes()
    else:
        raw = DEMO_TEXT.encode("utf-8")

    if demo_mode:
        encoded = base64.b64encode(raw).decode("ascii")
        print(f"Original: {DEMO_TEXT}")
        print(f"Encoded : {encoded}")
        print(f"Decoded : {base64.b64decode(encoded).decode('utf-8')}")
        return

    if args.mode == "encode":
        result = base64.b64encode(raw)
        print(result.decode("ascii"))
        if args.output:
            Path(args.output).write_bytes(result)
            print(f"[written to {args.output}]", file=sys.stderr)
    else:
        try:
            result = base64.b64decode(raw)
        except Exception as exc:
            sys.exit(f"ERROR: invalid Base64 input: {exc}")
        try:
            print(result.decode("utf-8"))
        except UnicodeDecodeError:
            print(f"[decoded {len(result)} bytes of binary data]")
        if args.output:
            Path(args.output).write_bytes(result)
            print(f"[written to {args.output}]", file=sys.stderr)


if __name__ == "__main__":
    main()
