#!/usr/bin/env python3
"""
create_tar_archives.py
----------------------------
Creates a TAR archive (optionally gzip-compressed) from one or more files/folders.

Usage:
    python create_tar_archives.py <output_tar> <source1> [source2 ...] [--gzip]

Example:
    python create_tar_archives.py backup.tar file1.txt folder1
    python create_tar_archives.py backup.tar.gz file1.txt folder1 --gzip
"""

import argparse
import os
import sys
import tarfile


def create_tar(output_tar: str, sources, use_gzip: bool) -> None:
    mode = "w:gz" if use_gzip else "w"

    if use_gzip and not (output_tar.endswith(".tar.gz") or output_tar.endswith(".tgz")):
        output_tar += ".tar.gz"
    elif not use_gzip and not output_tar.endswith(".tar"):
        output_tar += ".tar"

    try:
        with tarfile.open(output_tar, mode) as tar:
            for src in sources:
                if not os.path.exists(src):
                    print(f"Skipped (not found): {src}")
                    continue
                tar.add(src, arcname=os.path.basename(src))
                print(f"Added: {src}")

        print(f"\nArchive created: {output_tar}")
    except (OSError, tarfile.TarError) as e:
        print(f"Error creating TAR archive: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Create a TAR archive.")
    parser.add_argument("output_tar", help="Output TAR file path")
    parser.add_argument("sources", nargs="+", help="File(s)/folder(s) to archive")
    parser.add_argument("--gzip", action="store_true", help="Compress the archive with gzip (.tar.gz)")
    args = parser.parse_args()

    create_tar(args.output_tar, args.sources, args.gzip)


if __name__ == "__main__":
    main()
