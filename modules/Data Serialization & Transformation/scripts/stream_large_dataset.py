#!/usr/bin/env python3
"""
stream_large_dataset.py
---------------------------
Topic 359: Stream Large Datasets Without Loading into Memory

Processes large JSON or CSV files incrementally (row-by-row /
item-by-item) instead of loading the whole file into RAM. JSON
streaming uses `ijson` (see requirements.txt); CSV streaming uses
the standard-library `csv` module, which is already iterator-based.

USAGE
    # Run built-in demo: generates a sample large-ish JSON array file
    # and a CSV file, then streams both while computing simple stats
    python3 stream_large_dataset.py

    # Stream a specific JSON file (must be a top-level JSON array)
    python3 stream_large_dataset.py --format json --input big.json

    # Stream a specific CSV file
    python3 stream_large_dataset.py --format csv --input big.csv

EXPECTED OUTPUT
    Progress is NOT buffered into memory as a whole list; the script
    prints a running count and a couple of aggregate stats (e.g. a
    numeric column's min/max/average) computed with O(1) extra
    memory as it streams, plus peak memory usage for the process.
"""
import argparse
import csv
import json
import sys
import tracemalloc
from pathlib import Path

try:
    import ijson
except ImportError:
    ijson = None


def generate_demo_files(json_path: Path, csv_path: Path, n=5000):
    # JSON: array of {"id": int, "value": float}
    with open(json_path, "w", encoding="utf-8") as f:
        f.write("[\n")
        for i in range(n):
            row = {"id": i, "value": round((i * 37) % 1000 / 3, 2)}
            sep = ",\n" if i < n - 1 else "\n"
            f.write(json.dumps(row) + sep)
        f.write("]\n")

    # CSV: id,value
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "value"])
        for i in range(n):
            writer.writerow([i, round((i * 37) % 1000 / 3, 2)])


def stream_json(path: Path):
    if ijson is None:
        sys.exit(
            "ERROR: ijson is not installed.\n"
            "Install dependencies first:  pip install -r requirements.txt"
        )
    count = 0
    total = 0.0
    vmin, vmax = None, None
    with open(path, "rb") as f:
        for item in ijson.items(f, "item"):
            count += 1
            v = item.get("value")
            if v is not None:
                total += v
                vmin = v if vmin is None else min(vmin, v)
                vmax = v if vmax is None else max(vmax, v)
    avg = total / count if count else 0
    return count, vmin, vmax, avg


def stream_csv(path: Path):
    count = 0
    total = 0.0
    vmin, vmax = None, None
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            count += 1
            v = float(row["value"])
            total += v
            vmin = v if vmin is None else min(vmin, v)
            vmax = v if vmax is None else max(vmax, v)
    avg = total / count if count else 0
    return count, vmin, vmax, avg


def main():
    parser = argparse.ArgumentParser(description="Stream large JSON/CSV files without loading them fully into memory")
    parser.add_argument("--format", choices=["json", "csv"], help="Which format to stream")
    parser.add_argument("--input", help="Path to the file to stream")
    args = parser.parse_args()

    tracemalloc.start()

    if args.format and args.input:
        path = Path(args.input)
        if args.format == "json":
            count, vmin, vmax, avg = stream_json(path)
        else:
            count, vmin, vmax, avg = stream_csv(path)
        label = f"{args.format.upper()} file: {path}"
    else:
        tmp_dir = Path("./_stream_demo")
        tmp_dir.mkdir(exist_ok=True)
        json_path = tmp_dir / "demo_large.json"
        csv_path = tmp_dir / "demo_large.csv"
        print("No --input given: generating demo files (5000 rows each)...")
        generate_demo_files(json_path, csv_path)

        print("\nStreaming CSV...")
        count, vmin, vmax, avg = stream_csv(csv_path)
        label = f"CSV file: {csv_path}"
        print(f"{label} -> rows={count}, min={vmin}, max={vmax}, avg={avg:.2f}")

        if ijson is not None:
            print("\nStreaming JSON...")
            count, vmin, vmax, avg = stream_json(json_path)
            label = f"JSON file: {json_path}"
        else:
            print("\n(skipping JSON streaming demo: ijson not installed)")
            current, peak = tracemalloc.get_traced_memory()
            print(f"\nPeak memory used during streaming: {peak / 1024:.1f} KB")
            return

    print(f"{label} -> rows={count}, min={vmin}, max={vmax}, avg={avg:.2f}")
    current, peak = tracemalloc.get_traced_memory()
    print(f"\nPeak memory used during streaming: {peak / 1024:.1f} KB")


if __name__ == "__main__":
    main()
