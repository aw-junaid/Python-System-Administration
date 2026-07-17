#!/usr/bin/env python3
"""
generate_json_report.py

Generates a structured, hierarchical JSON report — the kind typically
consumed by APIs, dashboards, or other automated systems. Reads from
CSV or uses built-in sample data, and nests records under metadata.

Usage:
    python generate_json_report.py
    python generate_json_report.py --input data.csv --output report.json --title "My Report"

Expected output:
    A .json file with a top-level "report" object containing "metadata"
    (title, generated_at, record_count) and a "data" array of objects,
    one per row, keyed by the CSV column headers. Valid, pretty-printed
    JSON that any API or script can parse with json.load().
"""

import argparse
import csv
import datetime
import json
import os
import sys


def load_sample_data():
    headers = ["host", "cpu_percent", "memory_percent", "uptime_days", "status"]
    rows = [
        ["web-01", 42, 63, 120, "healthy"],
        ["web-02", 88, 77, 45, "degraded"],
        ["db-01", 35, 81, 300, "healthy"],
        ["cache-01", 12, 22, 12, "healthy"],
    ]
    return headers, rows


def load_csv_data(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if not rows:
        raise ValueError("CSV file is empty.")
    return rows[0], rows[1:]


def coerce(value):
    """Try to coerce a CSV string into int/float, else leave as string."""
    try:
        if "." in value:
            return float(value)
        return int(value)
    except (ValueError, TypeError):
        return value


def build_report(headers, rows, title):
    generated_at = datetime.datetime.now().isoformat()

    data = []
    for row in rows:
        record = {headers[i]: coerce(row[i]) for i in range(len(headers))}
        data.append(record)

    return {
        "report": {
            "metadata": {
                "title": title,
                "generated_at": generated_at,
                "record_count": len(data),
                "fields": headers,
            },
            "data": data,
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Generate a structured JSON report from CSV data.")
    parser.add_argument("--input", "-i", help="Path to input CSV file. If omitted, sample data is used.")
    parser.add_argument("--output", "-o", default="report.json", help="Path to output JSON file (default: report.json)")
    parser.add_argument("--title", "-t", default="Infrastructure Health Report", help="Report title")
    args = parser.parse_args()

    if args.input:
        if not os.path.isfile(args.input):
            print(f"Error: input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        headers, rows = load_csv_data(args.input)
    else:
        headers, rows = load_sample_data()
        print("No --input provided, using built-in sample data.")

    report = build_report(headers, rows, args.title)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"JSON report written to: {os.path.abspath(args.output)}")
    print(f"Records: {report['report']['metadata']['record_count']}. Valid for use with json.load() or any API.")


if __name__ == "__main__":
    main()
