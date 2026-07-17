#!/usr/bin/env python3
"""
generate_inline_graph.py

Renders a dynamic ASCII/ANSI line graph directly in the terminal —
no browser, no file needed. Uses 'asciichartpy' if it is installed
for a smooth multi-row plot; otherwise falls back to a built-in
plain-ASCII bar renderer using only the standard library.

Usage:
    python generate_inline_graph.py
    python generate_inline_graph.py --input data.csv --value-col cpu_percent --color

Expected output:
    A line/bar graph made of text characters printed straight to
    your terminal, with axis labels and (optionally) ANSI colors.
    No files are created; the graph is only for terminal viewing.
"""

import argparse
import csv
import os
import sys

try:
    import asciichartpy
    HAS_ASCIICHART = True
except ImportError:
    HAS_ASCIICHART = False


ANSI_GREEN = "\033[92m"
ANSI_RESET = "\033[0m"


def load_sample_data():
    return [10, 25, 18, 40, 55, 48, 60, 72, 65, 80, 90, 75]


def load_csv_data(path, value_col):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        raise ValueError("CSV file is empty.")
    if value_col not in rows[0]:
        raise ValueError(f"Column '{value_col}' not found. Available: {list(rows[0].keys())}")
    return [float(row[value_col]) for row in rows]


def render_with_asciichart(values, use_color, height):
    config = {"height": height}
    if use_color:
        config["colors"] = [asciichartpy.green]
    return asciichartpy.plot(values, config)


def render_fallback_bars(values, use_color, height):
    """Plain-ASCII horizontal bar fallback, stdlib only."""
    max_val = max(values) if values else 1
    lines = []
    for i, v in enumerate(values):
        bar_len = int((v / max_val) * height * 4) if max_val else 0
        bar = "#" * max(bar_len, 1)
        if use_color:
            bar = f"{ANSI_GREEN}{bar}{ANSI_RESET}"
        lines.append(f"{i:>3} | {bar} {v:g}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Render an ASCII/ANSI graph directly in the terminal.")
    parser.add_argument("--input", "-i", help="Path to input CSV file. If omitted, sample data is used.")
    parser.add_argument("--value-col", default=None, help="CSV column with numeric values (required if --input is given)")
    parser.add_argument("--height", type=int, default=12, help="Graph height in terminal rows (default: 12)")
    parser.add_argument("--color", action="store_true", help="Enable ANSI color output")
    args = parser.parse_args()

    if args.input:
        if not os.path.isfile(args.input):
            print(f"Error: input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        if not args.value_col:
            print("Error: --value-col is required when using --input.", file=sys.stderr)
            sys.exit(1)
        values = load_csv_data(args.input, args.value_col)
    else:
        values = load_sample_data()
        print("No --input provided, using built-in sample data.\n")

    print("Terminal Graph Report")
    print("=" * 40)

    if HAS_ASCIICHART:
        print(render_with_asciichart(values, args.color, args.height))
    else:
        print("(Tip: install 'asciichartpy' for a smoother line-plot: pip install asciichartpy)")
        print(render_fallback_bars(values, args.color, args.height))

    print("=" * 40)
    print(f"Data points: {len(values)}  |  Min: {min(values):g}  Max: {max(values):g}  Avg: {sum(values)/len(values):.2f}")


if __name__ == "__main__":
    main()
