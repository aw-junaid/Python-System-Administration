#!/usr/bin/env python3
"""
pickle_serialize.py
-----------------------
Topic 350: Binary Serialization with Pickle

Serializes complex Python objects (including custom classes,
datetimes, sets, tuples -- things plain JSON cannot represent) into
binary .pkl format, and demonstrates loading them back.

!! SECURITY WARNING !!
    pickle.load() can execute arbitrary code if the data comes from
    an untrusted or unauthenticated source. NEVER unpickle data you
    did not create yourself or that arrived over an insecure channel.
    This script is safe because it only loads files it just wrote.

USAGE
    # Run built-in demo: serializes sample data to demo.pkl then
    # reads it back and prints it
    python3 pickle_serialize.py

    # Serialize your own file: pass a .py file that defines DATA
    python3 pickle_serialize.py --mode dump --input mydata.py --output out.pkl

    # Load an existing pickle file (only do this for files you trust!)
    python3 pickle_serialize.py --mode load --input out.pkl

EXPECTED OUTPUT
    On dump: confirmation that N bytes were written to the .pkl file.
    On load: repr() of the deserialized Python object.
"""
import argparse
import importlib.util
import pickle
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class Event:
    name: str
    when: datetime
    tags: set


def build_demo_data():
    return {
        "event": Event("Launch", datetime(2026, 7, 17, 10, 0), {"prod", "release"}),
        "coordinates": (33.6844, 73.0479),  # tuple, not representable in JSON as-is
        "counts": {1, 2, 3, 3, 2},  # a set
    }


def load_input_module(path: str):
    spec = importlib.util.spec_from_file_location("user_input", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "DATA"):
        sys.exit(f"ERROR: {path} must define a top-level variable named DATA")
    return module.DATA


def main():
    parser = argparse.ArgumentParser(description="Serialize/deserialize Python objects with pickle")
    parser.add_argument("--mode", choices=["dump", "load", "roundtrip"], default="roundtrip")
    parser.add_argument("--input", help="For dump: .py file with DATA. For load: .pkl file")
    parser.add_argument("--output", default="demo.pkl", help="Path for the .pkl file (dump mode)")
    args = parser.parse_args()

    if args.mode in ("dump", "roundtrip"):
        data = load_input_module(args.input) if (args.input and args.mode == "dump") else build_demo_data()
        with open(args.output, "wb") as f:
            pickle.dump(data, f)
        size = Path(args.output).stat().st_size
        print(f"Serialized object -> {args.output} ({size} bytes)")
        print(f"Original object: {data!r}")

    if args.mode == "load":
        with open(args.input, "rb") as f:
            obj = pickle.load(f)
        print(f"Deserialized object: {obj!r}")

    if args.mode == "roundtrip":
        with open(args.output, "rb") as f:
            obj = pickle.load(f)
        print(f"\nRound-tripped object (loaded back): {obj!r}")


if __name__ == "__main__":
    main()
