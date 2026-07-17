#!/usr/bin/env python3
"""
generate_csv_report.py

Generates a simple tabular CSV data extract, ready to be opened in
Excel, Google Sheets, LibreOffice Calc, or any spreadsheet app. Uses
built-in sample data unless a JSON input file is supplied.

Usage:
    python generate_csv_report.py
    python generate_csv_report.py --input data.json --output report.csv

Expected output:
    A .csv file with a header row followed by data rows, comma
    separated, UTF-8 encoded, opens cleanly as a table in any
    spreadsheet application.
"""

import argparse
import csv
import json
import os
import sys


def load_sample_data():
    headers = ["Employee ID", "Name", "Department", "Salary", "Join Date"]
    rows = [
        ["E001", "Ahmed Khan", "Engineering", "95000", "2022-03-15"],
        ["E002", "Fatima Noor", "Marketing", "72000", "2021-11-01"],
        ["E003", "Usman Ali", "Engineering", "101000", "2020-06-23"],
        ["E004", "Hina Malik", "Finance", "88000", "2023-01-09"],
        ["E005", "Bilal Ahmed", "Sales", "67000", "2019-09-30"],
    ]
    return headers, rows


def load_json_data(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list) and data and isinstance(data[0], dict):
        headers = list(data[0].keys())
        rows = [[str(item.get(h, "")) for h in headers] for item in data]
        return headers, rows

    raise ValueError("JSON input must be a list of flat objects (list[dict]).")


def write_csv(headers, rows, output_path):
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Generate a CSV report from JSON data.")
    parser.add_argument("--input", "-i", help="Path to input JSON file (list of flat objects). If omitted, sample data is used.")
    parser.add_argument("--output", "-o", default="report.csv", help="Path to output CSV file (default: report.csv)")
    args = parser.parse_args()

    if args.input:
        if not os.path.isfile(args.input):
            print(f"Error: input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        headers, rows = load_json_data(args.input)
    else:
        headers, rows = load_sample_data()
        print("No --input provided, using built-in sample data.")

    write_csv(headers, rows, args.output)

    print(f"CSV report written to: {os.path.abspath(args.output)}")
    print(f"Rows written: {len(rows)}. Open it in Excel, Sheets, or any spreadsheet app.")


if __name__ == "__main__":
    main()
