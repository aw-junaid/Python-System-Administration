#!/usr/bin/env python3
"""
backup_create.py
==================
Create a full, timestamped, compressed backup of a directory tree.

Usage
-----
    python backup_create.py --source /etc/myapp --dest /var/backups

If --source is omitted, a small sample directory is created and backed
up so you can see the full flow immediately.
"""

import argparse
import fnmatch
import os
import sys
import tarfile
from datetime import datetime


def create_sample_source(path: str) -> None:
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "config.yaml"), "w", encoding="utf-8") as f:
        f.write("app_name: demo\nversion: 1.0\n")
    with open(os.path.join(path, "notes.txt"), "w", encoding="utf-8") as f:
        f.write("Sample file for backup_create.py demo run.\n")
    print(f"[info] No --source given, created a sample directory at: {path}")


def should_exclude(rel_path: str, patterns) -> bool:
    return any(fnmatch.fnmatch(rel_path, pat) for pat in patterns)


def create_backup(source: str, dest_dir: str, name: str, exclude_patterns) -> str:
    if not os.path.isdir(source):
        print(f"[error] Source directory not found: {source}")
        sys.exit(1)

    os.makedirs(dest_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    archive_name = f"{name}-{timestamp}.tar.gz"
    archive_path = os.path.join(dest_dir, archive_name)

    file_count = 0
    total_bytes = 0

    def filter_fn(tarinfo):
        nonlocal file_count, total_bytes
        rel = tarinfo.name
        if should_exclude(rel, exclude_patterns):
            print(f"[skip] {rel}")
            return None
        if tarinfo.isfile():
            file_count += 1
            total_bytes += tarinfo.size
        return tarinfo

    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(source, arcname=os.path.basename(source.rstrip("/")), filter=filter_fn)

    size = os.path.getsize(archive_path)
    print(f"[success] Backup written to: {archive_path}")
    print(f"          Files archived: {file_count}, uncompressed: {total_bytes} bytes, "
          f"compressed: {size} bytes")
    return archive_path


def main():
    parser = argparse.ArgumentParser(description="Create a full timestamped tar.gz backup of a directory.")
    parser.add_argument("--source", default=None, help="Directory to back up")
    parser.add_argument("--dest", default="./backups", help="Directory to write the archive into")
    parser.add_argument("--name", default="backup", help="Base name for the archive file")
    parser.add_argument("--exclude", nargs="*", default=[".git", "__pycache__", "*.pyc", "node_modules"],
                         help="Glob patterns (relative paths) to exclude from the backup")
    args = parser.parse_args()

    source = args.source
    if source is None:
        source = "sample_source"
        create_sample_source(source)

    create_backup(source, args.dest, args.name, args.exclude)


if __name__ == "__main__":
    main()
