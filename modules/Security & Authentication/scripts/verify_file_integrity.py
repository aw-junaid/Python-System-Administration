#!/usr/bin/env python3
"""
verify_file_integrity.py
------------------------------
Verifies that a file matches an expected checksum (hash), to confirm
it has not been corrupted or tampered with.

Usage:
    python verify_file_integrity.py <file_path> <expected_hash> [--algo sha256]

Example:
    python verify_file_integrity.py installer.exe a1b2c3...  --algo sha256
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


def verify_integrity(file_path: str, expected_hash: str, algorithm: str) -> None:
    if not os.path.isfile(file_path):
        print(f"Error: '{file_path}' does not exist.")
        sys.exit(1)

    actual_hash = calculate_hash(file_path, algorithm)
    expected_hash = expected_hash.strip().lower()
    actual_hash_lower = actual_hash.lower()

    print(f"File:          {file_path}")
    print(f"Algorithm:     {algorithm.upper()}")
    print(f"Expected hash: {expected_hash}")
    print(f"Actual hash:   {actual_hash_lower}")

    if actual_hash_lower == expected_hash:
        print("\nResult: MATCH — file integrity verified.")
    else:
        print("\nResult: MISMATCH — file may be corrupted or tampered with!")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Verify file integrity against an expected checksum.")
    parser.add_argument("file_path", help="Path to the file to verify")
    parser.add_argument("expected_hash", help="The expected checksum/hash value")
    parser.add_argument("--algo", default="sha256", choices=["md5", "sha1", "sha256", "sha512"],
                         help="Hash algorithm (default: sha256)")
    args = parser.parse_args()

    verify_integrity(args.file_path, args.expected_hash, args.algo)


if __name__ == "__main__":
    main()
