#!/usr/bin/env python3
"""
compress_logs.py
-------------------
Scans a directory for old log files (based on age in days) and
compresses them into .gz archives to save disk space, then removes
the original uncompressed file.

Usage:
    python3 compress_logs.py --dir logs --days 0
    (use --days 0 for demo purposes so it compresses everything immediately;
     in production use something like --days 7)

Arguments:
    --dir   Directory containing log files (default: logs)
    --days  Minimum age in days before a log file is compressed (default: 7)
"""

import argparse
import gzip
import os
import shutil
import time


def compress_file(path):
    gz_path = path + ".gz"
    with open(path, "rb") as f_in, gzip.open(gz_path, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    os.remove(path)
    return gz_path


def compress_old_logs(directory, min_age_days):
    if not os.path.isdir(directory):
        print(f"Directory not found: {directory}")
        return

    now = time.time()
    cutoff = now - (min_age_days * 86400)
    compressed_count = 0

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)

        # Skip directories and already-compressed files
        if not os.path.isfile(filepath) or filename.endswith(".gz"):
            continue
        if not filename.endswith(".log"):
            continue

        file_mtime = os.path.getmtime(filepath)
        if file_mtime <= cutoff:
            gz_path = compress_file(filepath)
            print(f"Compressed: {filepath} -> {gz_path}")
            compressed_count += 1

    print(f"\nDone. {compressed_count} file(s) compressed.")


def main():
    parser = argparse.ArgumentParser(description="Compress old log files into .gz archives")
    parser.add_argument("--dir", default="logs", help="Directory containing log files")
    parser.add_argument("--days", type=int, default=7, help="Minimum age in days")
    args = parser.parse_args()

    compress_old_logs(args.dir, args.days)


if __name__ == "__main__":
    main()
