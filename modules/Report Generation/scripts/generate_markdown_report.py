#!/usr/bin/env python3
"""
generate_markdown_report.py

Generates a clean Markdown (.md) report suitable for documentation
repositories, wikis, or GitHub README-style output. Reads from CSV
or uses built-in sample data.

Usage:
    python generate_markdown_report.py
    python generate_markdown_report.py --input data.csv --output report.md --title "My Report"

Expected output:
    A .md file containing a title, a generation timestamp, a short
    summary section, and a clean Markdown pipe-table. Renders correctly
    on GitHub, GitLab, and any standard Markdown viewer.
"""

import argparse
import csv
import datetime
import os
import sys


def load_sample_data():
    headers = ["Task", "Owner", "Priority", "Status"]
    rows = [
        ["Set up CI pipeline", "Ayesha", "High", "Done"],
        ["Write unit tests", "Bilal", "Medium", "In Progress"],
        ["Deploy to staging", "Ayesha", "High", "Pending"],
        ["Update documentation", "Sara", "Low", "Pending"],
    ]
    return headers, rows


def load_csv_data(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if not rows:
        raise ValueError("CSV file is empty.")
    return rows[0], rows[1:]


def escape_md(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def build_markdown(headers, rows, title):
    generated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"_Generated on {generated_at}_")
    lines.append("")
    lines.append(f"**Total records:** {len(rows)}")
    lines.append("")
    lines.append("## Report Data")
    lines.append("")

    lines.append("| " + " | ".join(escape_md(h) for h in headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        lines.append("| " + " | ".join(escape_md(c) for c in row) + " |")

    lines.append("")
    lines.append("---")
    lines.append("*This report was generated automatically by `generate_markdown_report.py`.*")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate a Markdown report from CSV data.")
    parser.add_argument("--input", "-i", help="Path to input CSV file. If omitted, sample data is used.")
    parser.add_argument("--output", "-o", default="report.md", help="Path to output Markdown file (default: report.md)")
    parser.add_argument("--title", "-t", default="Project Status Report", help="Report title")
    args = parser.parse_args()

    if args.input:
        if not os.path.isfile(args.input):
            print(f"Error: input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        headers, rows = load_csv_data(args.input)
    else:
        headers, rows = load_sample_data()
        print("No --input provided, using built-in sample data.")

    md_content = build_markdown(headers, rows, args.title)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"Markdown report written to: {os.path.abspath(args.output)}")
    print("Open it in any Markdown viewer, or view it directly on GitHub/GitLab.")


if __name__ == "__main__":
    main()
