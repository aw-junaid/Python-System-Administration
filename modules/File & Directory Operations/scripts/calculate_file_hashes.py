#!/usr/bin/env python3
"""
calculate_file_hashes.py
------------------------------
Calculates the hash (MD5, SHA1, or SHA256) of one or more files.

Usage:
    python calculate_file_hashes.py <file1> [file2 ...] [--algo sha256]

Example:
    python calculate_file_hashes.py document.pdf
    python calculate_file_hashes.py a.txt b.txt --algo md5
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


def calculate_file_hashes(file_paths, algorithm: str) -> None:
    for file_path in file_paths:
        if not os.path.isfile(file_path):
            print(f"Skipped (not found): {file_path}")
            continue

        try:
            digest = calculate_hash(file_path, algorithm)
            print(f"{algorithm.upper()}  {digest}  {file_path}")
        except (OSError, ValueError) as e:
            print(f"Error hashing '{file_path}': {e}")


def main():
    parser = argparse.ArgumentParser(description="Calculate file hashes (MD5/SHA1/SHA256).")
    parser.add_argument("files", nargs="+", help="File path(s) to hash")
    parser.add_argument(
        "--algo", default="sha256", choices=["md5", "sha1", "sha256"], help="Hash algorithm (default: sha256)"
    )
    args = parser.parse_args()

    calculate_file_hashes(args.files, args.algo)


if __name__ == "__main__":
    main()
