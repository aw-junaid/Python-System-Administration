#!/usr/bin/env python3
"""
verify_backup.py
===================
Compare a source directory against a backup directory using SHA-256
checksums and report any file that's missing, extra, or has drifted.

Usage
-----
    python verify_backup.py --source ./data --backup ./backups/full-20260713-020000
"""

import argparse
import hashlib
import os
import sys


def create_sample_dirs(source: str, backup: str) -> None:
    os.makedirs(source, exist_ok=True)
    os.makedirs(backup, exist_ok=True)
    with open(os.path.join(source, "a.txt"), "w", encoding="utf-8") as f:
        f.write("content A\n")
    with open(os.path.join(source, "b.txt"), "w", encoding="utf-8") as f:
        f.write("content B\n")
    with open(os.path.join(backup, "a.txt"), "w", encoding="utf-8") as f:
        f.write("content A\n")  # matches
    with open(os.path.join(backup, "b.txt"), "w", encoding="utf-8") as f:
        f.write("CORRUPTED\n")  # deliberately different, to demonstrate a mismatch
    print(f"[info] No --source/--backup given, created sample dirs (with one deliberate mismatch): "
          f"{source}, {backup}")


def file_hash(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build_hash_map(root: str) -> dict:
    result = {}
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root)
            result[rel] = file_hash(full)
    return result


def verify(source: str, backup: str) -> bool:
    if not os.path.isdir(source):
        print(f"[error] Source directory not found: {source}")
        sys.exit(1)
    if not os.path.isdir(backup):
        print(f"[error] Backup directory not found: {backup}")
        sys.exit(1)

    print("[info] Hashing source tree...")
    source_hashes = build_hash_map(source)
    print("[info] Hashing backup tree...")
    backup_hashes = build_hash_map(backup)

    missing = sorted(set(source_hashes) - set(backup_hashes))
    extra = sorted(set(backup_hashes) - set(source_hashes))
    mismatched = sorted(
        rel for rel in (set(source_hashes) & set(backup_hashes))
        if source_hashes[rel] != backup_hashes[rel]
    )

    for rel in missing:
        print(f"[MISSING]    {rel}  (in source, not in backup)")
    for rel in extra:
        print(f"[EXTRA]      {rel}  (in backup, not in source)")
    for rel in mismatched:
        print(f"[MISMATCH]   {rel}  (checksum differs)")

    ok = not (missing or mismatched)  # extras are reported but don't fail integrity on their own
    total = len(source_hashes)
    verified = total - len(missing) - len(mismatched)

    if ok and not extra:
        print(f"[success] Verified {verified}/{total} file(s) — backup matches source exactly.")
    elif ok:
        print(f"[success] Verified {verified}/{total} file(s) — all source files present and correct "
              f"({len(extra)} extra file(s) in backup, not necessarily a problem).")
    else:
        print(f"[FAILURE] {len(missing)} missing, {len(mismatched)} corrupted, out of {total} source file(s). "
              f"This backup should NOT be trusted for restore until resolved.")

    return ok


def main():
    parser = argparse.ArgumentParser(description="Verify a backup's integrity against its source via SHA-256.")
    parser.add_argument("--source", default=None)
    parser.add_argument("--backup", default=None)
    args = parser.parse_args()

    source, backup = args.source, args.backup
    if source is None or backup is None:
        source, backup = "sample_source", "sample_backup"
        create_sample_dirs(source, backup)

    ok = verify(source, backup)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
