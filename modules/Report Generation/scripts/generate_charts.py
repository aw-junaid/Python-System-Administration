#!/usr/bin/env python3
"""
generate_charts.py

Generates bar, line, and pie chart images from CSV data using
Matplotlib. Requires 'matplotlib'.

Usage:
    python generate_charts.py
    python generate_charts.py --input data.csv --outdir charts --label-col Category --value-col Value

Expected output:
    Three PNG image files written to the output directory:
    bar_chart.png, line_chart.png, pie_chart.png — each a standalone
    image you can open, embed in documents, or attach to an email.
"""

import argparse
import csv
import os
import sys

try:
    import matplotlib
    matplotlib.use("Agg")  # headless / no display needed
    import matplotlib.pyplot as plt
except ImportError:
    print("Missing dependency 'matplotlib'. Install it with: pip install matplotlib", file=sys.stderr)
    sys.exit(1)


def load_sample_data():
    labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    values = [120, 150, 90, 200, 175, 210]
    return labels, values


def load_csv_data(path, label_col, value_col):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        raise ValueError("CSV file is empty.")

    if label_col not in rows[0] or value_col not in rows[0]:
        raise ValueError(
            f"Columns not found. Available columns: {list(rows[0].keys())}. "
            f"Use --label-col and --value-col to select them."
        )

    labels = [row[label_col] for row in rows]
    values = [float(row[value_col]) for row in rows]
    return labels, values


def make_bar_chart(labels, values, output_path, title):
    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values, color="#2563eb")
    plt.title(title)
    plt.ylabel("Value")
    plt.xticks(rotation=30, ha="right")
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height, f"{height:g}",
                  ha="center", va="bottom", fontsize=8)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def make_line_chart(labels, values, output_path, title):
    plt.figure(figsize=(8, 5))
    plt.plot(labels, values, marker="o", color="#16a34a", linewidth=2)
    plt.title(title)
    plt.ylabel("Value")
    plt.xticks(rotation=30, ha="right")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def make_pie_chart(labels, values, output_path, title):
    plt.figure(figsize=(7, 7))
    plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=90,
            colors=plt.cm.Pastel1.colors)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Generate bar, line, and pie charts from CSV data.")
    parser.add_argument("--input", "-i", help="Path to input CSV file. If omitted, sample data is used.")
    parser.add_argument("--outdir", "-d", default="charts", help="Output directory for chart images (default: charts)")
    parser.add_argument("--label-col", default=None, help="CSV column to use as labels (required if --input is given)")
    parser.add_argument("--value-col", default=None, help="CSV column to use as numeric values (required if --input is given)")
    parser.add_argument("--title", "-t", default="Monthly Values", help="Base chart title")
    args = parser.parse_args()

    if args.input:
        if not os.path.isfile(args.input):
            print(f"Error: input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        if not args.label_col or not args.value_col:
            print("Error: --label-col and --value-col are required when using --input.", file=sys.stderr)
            sys.exit(1)
        labels, values = load_csv_data(args.input, args.label_col, args.value_col)
    else:
        labels, values = load_sample_data()
        print("No --input provided, using built-in sample data.")

    os.makedirs(args.outdir, exist_ok=True)

    bar_path = os.path.join(args.outdir, "bar_chart.png")
    line_path = os.path.join(args.outdir, "line_chart.png")
    pie_path = os.path.join(args.outdir, "pie_chart.png")

    make_bar_chart(labels, values, bar_path, f"{args.title} — Bar")
    make_line_chart(labels, values, line_path, f"{args.title} — Line")
    make_pie_chart(labels, values, pie_path, f"{args.title} — Distribution")

    print(f"Charts written to: {os.path.abspath(args.outdir)}")
    print(f"  - {bar_path}\n  - {line_path}\n  - {pie_path}")


if __name__ == "__main__":
    main()
