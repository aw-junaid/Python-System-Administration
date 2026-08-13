#!/usr/bin/env python3
"""
backup_rotation.py
=====================
Apply a grandfather-father-son style retention policy to a directory
of dated backups: keep the N most recent daily backups, plus one
backup per week for --keep-weekly weeks, plus one per month for
--keep-monthly months. Everything else is deleted.

Usage
-----
    python backup_rotation.py --backup-dir ./backups \
        --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --dry-run
"""

import argparse
import os
import re
import shutil
import sys
from datetime import datetime

# Matches names like "full-20260713-020000", "backup-20260713-020000.tar.gz",
# "incremental-20260713-020000", "differential-20260713-020000"
TIMESTAMP_RE = re.compile(r"(\d{8})-(\d{6})")


def create_sample_backups(backup_dir: str) -> None:
    os.makedirs(backup_dir, exist_ok=True)
    from datetime import timedelta
    now = datetime.now()
    # Simulate 40 days of nightly backups
    for i in range(40):
        ts = (now - timedelta(days=i)).strftime("%Y%m%d-%H%M%S")
        name = f"backup-{ts}.tar.gz"
        with open(os.path.join(backup_dir, name), "w", encoding="utf-8") as f:
            f.write("sample backup placeholder\n")
    print(f"[info] No --backup-dir contents found, created 40 days of sample backups in: {backup_dir}")


def parse_timestamp(name: str):
    m = TIMESTAMP_RE.search(name)
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
    except ValueError:
        return None


def classify_retention(backups, keep_daily, keep_weekly, keep_monthly):
    """Return the set of filenames to KEEP."""
    backups_sorted = sorted(backups.items(), key=lambda kv: kv[1], reverse=True)  # newest first
    keep = set()

    # Keep the N most recent, unconditionally (daily tier)
    for name, _ts in backups_sorted[:keep_daily]:
        keep.add(name)

    # Weekly tier: for each of the last keep_weekly weeks, keep the newest backup in that week
    remaining = [(n, t) for n, t in backups_sorted if n not in keep]
    seen_weeks = {}
    for name, ts in remaining:
        week_key = ts.strftime("%Y-W%U")
        if week_key not in seen_weeks and len(seen_weeks) < keep_weekly:
            seen_weeks[week_key] = name
            keep.add(name)

    # Monthly tier: for each of the last keep_monthly months, keep the newest backup in that month
    remaining = [(n, t) for n, t in backups_sorted if n not in keep]
    seen_months = {}
    for name, ts in remaining:
        month_key = ts.strftime("%Y-%m")
        if month_key not in seen_months and len(seen_months) < keep_monthly:
            seen_months[month_key] = name
            keep.add(name)

    return keep


def rotate(backup_dir: str, keep_daily: int, keep_weekly: int, keep_monthly: int, dry_run: bool) -> None:
    if not os.path.isdir(backup_dir):
        print(f"[error] Backup directory not found: {backup_dir}")
        sys.exit(1)

    entries = os.listdir(backup_dir)
    backups, unrecognized = {}, []
    for name in entries:
        ts = parse_timestamp(name)
        if ts:
            backups[name] = ts
        else:
            unrecognized.append(name)

    if not backups:
        print("[info] No timestamped backups found — nothing to rotate.")
        return

    keep = classify_retention(backups, keep_daily, keep_weekly, keep_monthly)
    to_delete = sorted(set(backups) - keep)

    for name in unrecognized:
        print(f"[skip] {name}  (doesn't match the expected timestamp pattern — left untouched)")

    for name in sorted(keep):
        print(f"[keep] {name}")

    for name in to_delete:
        action = "[would delete]" if dry_run else "[delete]"
        print(f"{action} {name}")
        if not dry_run:
            full_path = os.path.join(backup_dir, name)
            if os.path.isdir(full_path):
                shutil.rmtree(full_path)
            else:
                os.remove(full_path)

    verb = "would delete" if dry_run else "deleted"
    print(f"[success] Retention applied: {len(keep)} kept, {len(to_delete)} {verb}, "
          f"{len(unrecognized)} unrecognized (left alone)")


def main():
    parser = argparse.ArgumentParser(description="Apply daily/weekly/monthly retention to a backup directory.")
    parser.add_argument("--backup-dir", default=None)
    parser.add_argument("--keep-daily", type=int, default=7)
    parser.add_argument("--keep-weekly", type=int, default=4)
    parser.add_argument("--keep-monthly", type=int, default=6)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    backup_dir = args.backup_dir
    if backup_dir is None:
        backup_dir = "sample_backups"
        create_sample_backups(backup_dir)

    rotate(backup_dir, args.keep_daily, args.keep_weekly, args.keep_monthly, args.dry_run)


if __name__ == "__main__":
    main()
