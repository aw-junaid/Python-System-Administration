#!/usr/bin/env python3
"""
msgpack_serialize.py
------------------------
Topic 351: Binary Serialization with MessagePack

Packs Python data into MessagePack -- a compact, cross-language
binary format that is typically smaller and faster to (de)serialize
than JSON. Requires the `msgpack` package (see requirements.txt).

USAGE
    python3 msgpack_serialize.py
    python3 msgpack_serialize.py --input data.json --output data.msgpack
    python3 msgpack_serialize.py --mode load --input data.msgpack

EXPECTED OUTPUT
    On pack: the packed byte size compared to the equivalent JSON
    size, and the file it was written to.
    On load: the object that was unpacked, printed with repr().
"""
import argparse
import json
import sys
from pathlib import Path

try:
    import msgpack
except ImportError:
    sys.exit(
        "ERROR: msgpack is not installed.\n"
        "Install dependencies first:  pip install -r requirements.txt"
    )

DEMO_DATA = {
    "id": 42,
    "name": "Acme Corp",
    "employees": [
        {"name": "Alice", "role": "Engineer", "salary": 95000},
        {"name": "Bob", "role": "Designer", "salary": 80000},
    ],
    "active": True,
}


def main():
    parser = argparse.ArgumentParser(description="Pack/unpack data with MessagePack")
    parser.add_argument("--mode", choices=["pack", "load"], default="pack")
    parser.add_argument("--input", help="For pack: JSON file. For load: .msgpack file")
    parser.add_argument("--output", default="data.msgpack", help="Path for the packed file")
    args = parser.parse_args()

    if args.mode == "pack":
        data = json.loads(Path(args.input).read_text(encoding="utf-8")) if args.input else DEMO_DATA
        packed = msgpack.packb(data, use_bin_type=True)
        Path(args.output).write_bytes(packed)

        json_size = len(json.dumps(data).encode("utf-8"))
        print(f"Packed {len(packed)} bytes -> {args.output}")
        print(f"Equivalent JSON size: {json_size} bytes")
        print(f"Space saved: {json_size - len(packed)} bytes ({(1 - len(packed) / json_size):.1%})")
    else:
        if not args.input:
            sys.exit("ERROR: --input is required for --mode load")
        packed = Path(args.input).read_bytes()
        obj = msgpack.unpackb(packed, raw=False)
        print(f"Unpacked object: {obj!r}")


if __name__ == "__main__":
    main()
