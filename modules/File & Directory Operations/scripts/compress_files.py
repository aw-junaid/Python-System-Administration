#!/usr/bin/env python3
"""
compress_files.py
-----------------------
Compresses one or more files/folders into a ZIP archive.

Usage:
    python compress_files.py <output_zip> <source1> [source2 ...]

Example:
    python compress_files.py backup.zip file1.txt file2.txt
    python compress_files.py project.zip my_project_folder
"""

import argparse
import os
import sys
import zipfile


def compress_files(output_zip: str, sources) -> None:
    if not output_zip.lower().endswith(".zip"):
        output_zip += ".zip"

    try:
        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for src in sources:
                if not os.path.exists(src):
                    print(f"Skipped (not found): {src}")
                    continue

                if os.path.isfile(src):
                    zf.write(src, arcname=os.path.basename(src))
                    print(f"Added file: {src}")
                elif os.path.isdir(src):
                    for root, _, files in os.walk(src):
                        for f in files:
                            full_path = os.path.join(root, f)
                            arcname = os.path.relpath(full_path, os.path.dirname(src))
                            zf.write(full_path, arcname=arcname)
                    print(f"Added directory: {src}")

        print(f"\nArchive created: {output_zip}")
    except OSError as e:
        print(f"Error creating archive: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Compress files/folders into a ZIP archive.")
    parser.add_argument("output_zip", help="Output ZIP file path")
    parser.add_argument("sources", nargs="+", help="File(s)/folder(s) to compress")
    args = parser.parse_args()

    compress_files(args.output_zip, args.sources)


if __name__ == "__main__":
    main()
