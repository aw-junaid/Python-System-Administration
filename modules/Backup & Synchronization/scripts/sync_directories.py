#!/usr/bin/env python3
"""
sync_directories.py
======================
One-way, additive synchronization: copy new and modified files from
--source to --dest. Files that exist only in --dest are left alone.

Usage
-----
    python sync_directories.py --source ./project --dest ./staging
"""

import argparse
import hashlib
import os
import shutil
import sys


def create_sample_dirs(source: str, dest: str) -> None:
    os.makedirs(source, exist_ok=True)
    os.makedirs(dest, exist_ok=True)
    with open(os.path.join(source, "index.html"), "w", encoding="utf-8") as f:
        f.write("<html><body>Hello</body></html>\n")
    with open(os.path.join(dest, "old_notes.txt"), "w", encoding="utf-8") as f:
        f.write("This file only exists in dest and will NOT be deleted.\n")
    print(f"[info] No --source/--dest given, created sample dirs: {source}, {dest}")


def file_hash(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def needs_copy(src_path: str, dst_path: str, use_hash: bool) -> bool:
    if not os.path.exists(dst_path):
        return True
    src_stat, dst_stat = os.stat(src_path), os.stat(dst_path)
    if use_hash:
        return file_hash(src_path) != file_hash(dst_path)
    return src_stat.st_size != dst_stat.st_size or src_stat.st_mtime > dst_stat.st_mtime


def sync(source: str, dest: str, use_hash: bool, dry_run: bool) -> None:
    if not os.path.isdir(source):
        print(f"[error] Source directory not found: {source}")
        sys.exit(1)

    os.makedirs(dest, exist_ok=True)
    copied, skipped = 0, 0

    for root, _dirs, files in os.walk(source):
        rel_root = os.path.relpath(root, source)
        dst_root = os.path.join(dest, rel_root) if rel_root != "." else dest
        os.makedirs(dst_root, exist_ok=True)

        for name in files:
            src_path = os.path.join(root, name)
            dst_path = os.path.join(dst_root, name)

            if needs_copy(src_path, dst_path, use_hash):
                action = "[would copy]" if dry_run else "[copy]"
                print(f"{action} {os.path.relpath(src_path, source)}")
                if not dry_run:
                    shutil.copy2(src_path, dst_path)
                copied += 1
            else:
                skipped += 1

    verb = "would copy" if dry_run else "copied"
    print(f"[success] Sync complete: {copied} file(s) {verb}, {skipped} file(s) already up to date")


def main():
    parser = argparse.ArgumentParser(description="One-way additive directory synchronization.")
    parser.add_argument("--source", default=None)
    parser.add_argument("--dest", default=None)
    parser.add_argument("--hash", action="store_true", help="Compare file contents via SHA-256 instead of size/mtime")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be copied without copying")
    args = parser.parse_args()

    source, dest = args.source, args.dest
    if source is None or dest is None:
        source, dest = "sample_source", "sample_dest"
        create_sample_dirs(source, dest)

    sync(source, dest, args.hash, args.dry_run)


if __name__ == "__main__":
    main()
