#!/usr/bin/env python3
"""
merge_csv.py
============
Concatenate multiple CSV files with the same column structure into a
single CSV file (vertical merge / "stacking" rows).

Usage
-----
    python merge_csv.py --inputs jan.csv feb.csv mar.csv --output merged.csv

If --inputs is omitted, three small sample CSV files are created in
the current directory and then merged, so the script works out of the
box.

Expected output
----------------
A single CSV file (--output) containing the header from the first
file followed by the data rows of every input file, in order. The
script verifies all input files share the same header and warns if
they don't.

Requirements
------------
No third-party packages required (uses the built-in csv module).
"""

import argparse
import csv
import os


def create_sample_csvs():
    files = {
        "jan.csv": "Date,Product,Units\n2026-01-05,Widget,10\n2026-01-18,Gadget,4\n",
        "feb.csv": "Date,Product,Units\n2026-02-02,Widget,7\n2026-02-21,Gizmo,12\n",
        "mar.csv": "Date,Product,Units\n2026-03-11,Gadget,9\n2026-03-29,Widget,15\n",
    }
    for name, content in files.items():
        with open(name, "w", encoding="utf-8") as f:
            f.write(content)
    print(f"[info] No --inputs given, created sample files: {list(files.keys())}")
    return list(files.keys())


def merge_csv(inputs, output: str) -> None:
    header = None
    total_rows = 0

    with open(output, "w", newline="", encoding="utf-8") as out_f:
        writer = csv.writer(out_f)

        for path in inputs:
            if not os.path.exists(path):
                print(f"[warning] Skipping missing file: {path}")
                continue

            with open(path, newline="", encoding="utf-8") as in_f:
                reader = csv.reader(in_f)
                try:
                    file_header = next(reader)
                except StopIteration:
                    print(f"[warning] Skipping empty file: {path}")
                    continue

                if header is None:
                    header = file_header
                    writer.writerow(header)
                elif file_header != header:
                    print(f"[warning] Header mismatch in {path}: {file_header} != {header} (rows appended anyway)")

                for row in reader:
                    writer.writerow(row)
                    total_rows += 1

    print(f"[success] Merged {len(inputs)} file(s) into: {output}")
    print(f"          Header: {header}")
    print(f"          Total data rows written: {total_rows}")


def main():
    parser = argparse.ArgumentParser(description="Merge multiple homogeneous CSV files vertically.")
    parser.add_argument("--inputs", nargs="*", default=None, help="Paths to CSV files to merge, in order")
    parser.add_argument("--output", default="merged.csv", help="Path for the merged output CSV")
    args = parser.parse_args()

    inputs = args.inputs
    if not inputs:
        inputs = create_sample_csvs()

    merge_csv(inputs, args.output)


if __name__ == "__main__":
    main()
