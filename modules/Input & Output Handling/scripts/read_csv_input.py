#!/usr/bin/env python3
"""
Topic: Read CSV Input

Reads and parses a CSV file (creating a sample one if none is given) using
Python's built-in csv module, printing rows as dictionaries.

Usage:
    python read_csv_input.py [path_to_file.csv]

Expected Output:
    Each row of the CSV printed as a dictionary, plus a total row count.
"""

import csv
import sys
import os


def main() -> None:
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "sample_data.csv"
        if not os.path.exists(file_path):
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["name", "age", "role"])
                writer.writerow(["Junaid", "25", "Developer"])
                writer.writerow(["Sara", "30", "Sysadmin"])
        print(f"No file given, using generated sample: {file_path}\n")

    if not os.path.isfile(file_path):
        print(f"Error: file not found -> {file_path}", file=sys.stderr)
        sys.exit(1)

    with open(file_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for i, row in enumerate(rows, start=1):
        print(f"Row {i}: {dict(row)}")

    print(f"\nTotal rows: {len(rows)}")


if __name__ == "__main__":
    main()
