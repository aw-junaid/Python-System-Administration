#!/usr/bin/env python3
"""
mirror_folders.py
====================
Exact one-way mirror: --dest ends up containing exactly what --source
contains — new/changed files are copied, and anything in --dest that
is not in --source is deleted.

Usage
-----
    python mirror_folders.py --source ./release --dest /var/www/html --dry-run
    python mirror_folders.py --source ./release --dest /var/www/html
"""

import argparse
import os
import shutil
import sys


def create_sample_dirs(source: str, dest: str) -> None:
    os.makedirs(source, exist_ok=True)
    os.makedirs(dest, exist_ok=True)
    with open(os.path.join(source, "app.js"), "w", encoding="utf-8") as f:
        f.write("console.log('hello');\n")
    with open(os.path.join(dest, "old_app.js"), "w", encoding="utf-8") as f:
        f.write("// stale file, not in source — will be removed by mirror\n")
    print(f"[info] No --source/--dest given, created sample dirs: {source}, {dest}")


def needs_copy(src_path: str, dst_path: str) -> bool:
    if not os.path.exists(dst_path):
        return True
    s, d = os.stat(src_path), os.stat(dst_path)
    return s.st_size != d.st_size or s.st_mtime > d.st_mtime


def mirror(source: str, dest: str, dry_run: bool) -> None:
    if not os.path.isdir(source):
        print(f"[error] Source directory not found: {source}")
        sys.exit(1)

    os.makedirs(dest, exist_ok=True)

    source_rel_files = set()
    copied = 0

    # Pass 1: copy new/changed files, tracking every relative path seen in source
    for root, _dirs, files in os.walk(source):
        rel_root = os.path.relpath(root, source)
        dst_root = os.path.join(dest, rel_root) if rel_root != "." else dest
        if not dry_run:
            os.makedirs(dst_root, exist_ok=True)

        for name in files:
            src_path = os.path.join(root, name)
            dst_path = os.path.join(dst_root, name)
            rel_path = os.path.normpath(os.path.join(rel_root, name)) if rel_root != "." else name
            source_rel_files.add(rel_path)

            if needs_copy(src_path, dst_path):
                action = "[would copy]" if dry_run else "[copy]"
                print(f"{action} {rel_path}")
                if not dry_run:
                    shutil.copy2(src_path, dst_path)
                copied += 1

    # Pass 2: remove anything in dest that isn't in source
    removed = 0
    for root, dirs, files in os.walk(dest, topdown=False):
        rel_root = os.path.relpath(root, dest)
        for name in files:
            rel_path = os.path.normpath(os.path.join(rel_root, name)) if rel_root != "." else name
            if rel_path not in source_rel_files:
                action = "[would delete]" if dry_run else "[delete]"
                print(f"{action} {rel_path}")
                if not dry_run:
                    os.remove(os.path.join(root, name))
                removed += 1
        # remove now-empty directories (except dest itself)
        if not dry_run and root != dest and not os.listdir(root):
            os.rmdir(root)

    verb_c, verb_d = ("would copy", "would delete") if dry_run else ("copied", "deleted")
    print(f"[success] Mirror complete: {copied} file(s) {verb_c}, {removed} file(s) {verb_d}")


def main():
    parser = argparse.ArgumentParser(description="Exact one-way directory mirror (copies + deletions).")
    parser.add_argument("--source", default=None)
    parser.add_argument("--dest", default=None)
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without changing anything")
    args = parser.parse_args()

    source, dest = args.source, args.dest
    if source is None or dest is None:
        source, dest = "sample_source", "sample_dest"
        create_sample_dirs(source, dest)

    mirror(source, dest, args.dry_run)


if __name__ == "__main__":
    main()
