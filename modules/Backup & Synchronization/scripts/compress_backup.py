#!/usr/bin/env python3
"""
compress_backup.py
=====================
Compress a directory into a single .tar.gz or .zip archive, with a
configurable compression level.

Usage
-----
    python compress_backup.py --source ./backups/full-20260713-020000 \
        --output ./backups/full-20260713-020000.tar.gz --format tar.gz --level 9
"""

import argparse
import os
import sys
import tarfile
import zipfile


def create_sample_source(path: str) -> None:
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "data.txt"), "w", encoding="utf-8") as f:
        f.write("Sample backup content. " * 200 + "\n")
    print(f"[info] No --source given, created a sample directory at: {path}")


def compress_tar_gz(source: str, output: str, level: int) -> None:
    with tarfile.open(output, f"w:gz", compresslevel=level) as tar:
        tar.add(source, arcname=os.path.basename(source.rstrip("/")))


def compress_zip(source: str, output: str, level: int) -> None:
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=level) as zf:
        base = os.path.basename(source.rstrip("/"))
        for root, _dirs, files in os.walk(source):
            for name in files:
                full = os.path.join(root, name)
                arcname = os.path.join(base, os.path.relpath(full, source))
                zf.write(full, arcname)


def compress(source: str, output: str, fmt: str, level: int) -> None:
    if not os.path.isdir(source):
        print(f"[error] Source directory not found: {source}")
        sys.exit(1)

    uncompressed_size = sum(
        os.path.getsize(os.path.join(dp, f))
        for dp, _dn, filenames in os.walk(source)
        for f in filenames
    )

    print(f"[info] Compressing {source} ({uncompressed_size} bytes uncompressed) -> {output} "
          f"(format={fmt}, level={level})")

    if fmt == "tar.gz":
        compress_tar_gz(source, output, level)
    else:
        compress_zip(source, output, level)

    compressed_size = os.path.getsize(output)
    ratio = (1 - compressed_size / uncompressed_size) * 100 if uncompressed_size else 0
    print(f"[success] Archive written to: {output}")
    print(f"          {uncompressed_size} bytes -> {compressed_size} bytes ({ratio:.1f}% smaller)")


def main():
    parser = argparse.ArgumentParser(description="Compress a directory into a single tar.gz or zip archive.")
    parser.add_argument("--source", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--format", choices=["tar.gz", "zip"], default="tar.gz")
    parser.add_argument("--level", type=int, default=6, help="Compression level: 1 (fastest) to 9 (smallest)")
    args = parser.parse_args()

    source = args.source
    if source is None:
        source = "sample_source"
        create_sample_source(source)

    output = args.output or f"{source.rstrip('/')}.{args.format}"
    compress(source, output, args.format, args.level)


if __name__ == "__main__":
    main()
