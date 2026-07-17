#!/usr/bin/env python3
"""
generate_checksums.py
---------------------------
Generates checksums (hashes) for one or more files, and optionally
writes them to a checksum file (e.g. SHA256SUMS) for later verification.

Usage:
    python generate_checksums.py <file1> [file2 ...] [--algo sha256] [--output SHA256SUMS.txt]

Example:
    python generate_checksums.py installer.exe
    python generate_checksums.py *.iso --algo sha512 --output checksums.txt
"""

import argparse
import hashlib
import os
import sys


def calculate_hash(file_path: str, algorithm: str) -> str:
    hasher = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def generate_checksums(file_paths, algorithm: str, output: str = None) -> None:
    results = []

    for file_path in file_paths:
        if not os.path.isfile(file_path):
            print(f"Skipped (not found): {file_path}")
            continue

        digest = calculate_hash(file_path, algorithm)
        results.append((digest, file_path))
        print(f"{digest}  {file_path}")

    if output and results:
        with open(output, "w", encoding="utf-8") as f:
            for digest, path in results:
                f.write(f"{digest}  {path}\n")
        print(f"\nChecksums written to: {output}")
        print(f"Verify later with: sha256sum -c {output}  (or use verify_file_integrity.py per file)")


def main():
    parser = argparse.ArgumentParser(description="Generate checksums for one or more files.")
    parser.add_argument("files", nargs="+", help="File path(s) to checksum")
    parser.add_argument("--algo", default="sha256", choices=["md5", "sha1", "sha256", "sha512"],
                         help="Hash algorithm (default: sha256)")
    parser.add_argument("--output", default=None, help="Optional output file to save checksums")
    args = parser.parse_args()

    generate_checksums(args.files, args.algo, args.output)


if __name__ == "__main__":
    main()
