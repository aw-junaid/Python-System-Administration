#!/usr/bin/env python3
"""
extract_tar_archives.py
-----------------------------
Extracts the contents of a TAR (or TAR.GZ) archive to a destination directory.

Usage:
    python extract_tar_archives.py <tar_file> [destination_dir]

Example:
    python extract_tar_archives.py backup.tar.gz
    python extract_tar_archives.py backup.tar ./extracted
"""

import argparse
import os
import sys
import tarfile


def extract_tar(tar_path: str, destination: str) -> None:
    if not os.path.isfile(tar_path):
        print(f"Error: '{tar_path}' does not exist.")
        sys.exit(1)

    if not tarfile.is_tarfile(tar_path):
        print(f"Error: '{tar_path}' is not a valid TAR archive.")
        sys.exit(1)

    os.makedirs(destination, exist_ok=True)

    try:
        with tarfile.open(tar_path, "r:*") as tar:
            tar.extractall(destination)
            file_count = len(tar.getnames())

        print(f"Extracted {file_count} item(s) from '{tar_path}' to '{destination}'")
    except (OSError, tarfile.TarError) as e:
        print(f"Error extracting archive: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Extract a TAR/TAR.GZ archive.")
    parser.add_argument("tar_file", help="TAR file to extract")
    parser.add_argument("destination", nargs="?", default=".", help="Destination directory (default: current directory)")
    args = parser.parse_args()

    extract_tar(args.tar_file, args.destination)


if __name__ == "__main__":
    main()
