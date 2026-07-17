#!/usr/bin/env python3
"""
split_csv.py
============
Split a CSV file either by a fixed number of rows per chunk, or by the
distinct values found in a chosen column (e.g. one output file per
"Region").

Usage
-----
    # Split by row count (200 data rows per file)
    python split_csv.py --file data.csv --by rows --rows-per-file 200

    # Split by column value (one file per unique value in "Region")
    python split_csv.py --file data.csv --by column --column Region

If --file is omitted, a sample CSV is generated so the script can run
immediately (split by column "Region" by default).

Expected output
----------------
Multiple CSV files written to --output-dir (default: "split_output"):
    - Row-based split: <original_name>_part1.csv, _part2.csv, ...
    - Column-based split: <original_name>_<value>.csv for each unique value

Each output file includes the original header row.

Requirements
------------
No third-party packages required (uses the built-in csv module).
"""

import argparse
import csv
import os


def create_sample_csv(path: str) -> None:
    content = (
        "Region,Rep,Sales\n"
        "North,Ali Raza,4200\n"
        "South,Mehak Sohail,7800\n"
        "North,Bilal Ahmed,3100\n"
        "East,Usman Tariq,2500\n"
        "South,Sara Malik,6600\n"
        "East,Noor Fatima,4100\n"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[info] No --file given, created a sample CSV at: {path}")


def split_by_rows(path: str, rows_per_file: int, output_dir: str) -> None:
    base = os.path.splitext(os.path.basename(path))[0]
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)

        part = 1
        buffer = []
        files_written = []

        def flush(buf, part_num):
            out_path = os.path.join(output_dir, f"{base}_part{part_num}.csv")
            with open(out_path, "w", newline="", encoding="utf-8") as out_f:
                writer = csv.writer(out_f)
                writer.writerow(header)
                writer.writerows(buf)
            files_written.append(out_path)

        for row in reader:
            buffer.append(row)
            if len(buffer) >= rows_per_file:
                flush(buffer, part)
                part += 1
                buffer = []

        if buffer:
            flush(buffer, part)

    print(f"[success] Split by rows ({rows_per_file}/file) -> {len(files_written)} file(s):")
    for fp in files_written:
        print(f"          {fp}")


def split_by_column(path: str, column: str, output_dir: str) -> None:
    base = os.path.splitext(os.path.basename(path))[0]
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if column not in (reader.fieldnames or []):
            print(f"[error] Column '{column}' not found. Available columns: {reader.fieldnames}")
            return

        buckets = {}
        for row in reader:
            key = row[column]
            buckets.setdefault(key, []).append(row)

        files_written = []
        for value, rows in buckets.items():
            safe_value = "".join(c if c.isalnum() else "_" for c in str(value))
            out_path = os.path.join(output_dir, f"{base}_{safe_value}.csv")
            with open(out_path, "w", newline="", encoding="utf-8") as out_f:
                writer = csv.DictWriter(out_f, fieldnames=reader.fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            files_written.append(out_path)

    print(f"[success] Split by column '{column}' -> {len(files_written)} file(s):")
    for fp in files_written:
        print(f"          {fp}")


def main():
    parser = argparse.ArgumentParser(description="Split a CSV file by row count or by column value.")
    parser.add_argument("--file", default=None, help="Path to the CSV file to split")
    parser.add_argument("--by", choices=["rows", "column"], default="column", help="Split strategy")
    parser.add_argument("--rows-per-file", type=int, default=2, help="Rows per output file when --by rows")
    parser.add_argument("--column", default="Region", help="Column name to split by when --by column")
    parser.add_argument("--output-dir", default="split_output", help="Directory to write split files into")
    args = parser.parse_args()

    path = args.file
    if path is None:
        path = "sample.csv"
        create_sample_csv(path)

    os.makedirs(args.output_dir, exist_ok=True)

    if args.by == "rows":
        split_by_rows(path, args.rows_per_file, args.output_dir)
    else:
        split_by_column(path, args.column, args.output_dir)


if __name__ == "__main__":
    main()
