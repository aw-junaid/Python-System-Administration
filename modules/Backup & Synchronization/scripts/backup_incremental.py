#!/usr/bin/env python3
"""
backup_incremental.py
========================
Back up only files that are new or changed since the last run (full or
incremental), tracked via a JSON manifest of path -> (mtime, size).

Usage
-----
    # First run acts as the baseline (backs up everything)
    python backup_incremental.py --source ./data --dest ./backups

    # Later runs only copy what changed since the manifest was last updated
    python backup_incremental.py --source ./data --dest ./backups
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime

MANIFEST_NAME = "manifest.json"


def create_sample_source(path: str) -> None:
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "report.txt"), "w", encoding="utf-8") as f:
        f.write("Quarterly report draft.\n")
    print(f"[info] No --source given, created a sample directory at: {path}")


def load_manifest(dest_dir: str) -> dict:
    path = os.path.join(dest_dir, MANIFEST_NAME)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_manifest(dest_dir: str, manifest: dict) -> None:
    path = os.path.join(dest_dir, MANIFEST_NAME)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def scan_source(source: str) -> dict:
    state = {}
    for root, _dirs, files in os.walk(source):
        for name in files:
            full = os.path.join(root, name)
            rel = os.path.relpath(full, source)
            st = os.stat(full)
            state[rel] = {"mtime": st.st_mtime, "size": st.st_size}
    return state


def run_incremental(source: str, dest_dir: str) -> None:
    if not os.path.isdir(source):
        print(f"[error] Source directory not found: {source}")
        sys.exit(1)

    os.makedirs(dest_dir, exist_ok=True)
    manifest = load_manifest(dest_dir)
    current_state = scan_source(source)

    changed = {
        rel: meta for rel, meta in current_state.items()
        if rel not in manifest or manifest[rel] != meta
    }

    if not changed:
        print("[info] No new or changed files since last backup — nothing to do.")
        return

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    inc_dir = os.path.join(dest_dir, f"incremental-{timestamp}")
    os.makedirs(inc_dir, exist_ok=True)

    for rel in changed:
        src_path = os.path.join(source, rel)
        dst_path = os.path.join(inc_dir, rel)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy2(src_path, dst_path)
        print(f"[copy] {rel}")

    manifest.update(changed)
    save_manifest(dest_dir, manifest)

    print(f"[success] Incremental backup written to: {inc_dir}")
    print(f"          {len(changed)} file(s) copied out of {len(current_state)} total tracked")


def main():
    parser = argparse.ArgumentParser(description="Back up only files changed since the last run.")
    parser.add_argument("--source", default=None)
    parser.add_argument("--dest", default="./backups")
    args = parser.parse_args()

    source = args.source
    if source is None:
        source = "sample_source"
        create_sample_source(source)

    run_incremental(source, args.dest)


if __name__ == "__main__":
    main()
