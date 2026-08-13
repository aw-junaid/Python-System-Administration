#### 13.3 Differential Backups: `backup_differential.py`

##### Use Case

A sysadmin wants faster, simpler restores than an incremental chain offers (see 13.2) without paying the full cost of nightly full backups (13.1). Differential backups solve this by always comparing against the *last full backup only* — each differential grows a little larger than the last, but a restore only ever needs two pieces: the full backup, and the most recent differential.

##### Prerequisites

No third-party packages required — standard library only (`json`, `shutil`, `os`).

```bash
python3 --version
```

OS scope: Linux, macOS, Windows.

##### Cautions

- Unlike 13.2, a differential run does **not** update its baseline — it always measures against the last *full* backup's manifest. If you never take a new full backup, differentials will keep growing indefinitely; take a fresh full backup periodically (e.g., weekly) and reset the baseline.
- This script assumes a full backup (with a `full-manifest.json` baseline) has already been created via `--action full` before any `--action diff` run.

##### Script

```python
#!/usr/bin/env python3
"""
backup_differential.py
=========================
Take a full backup that establishes a baseline manifest, then take
differential backups that always compare against that same baseline
(not against the previous differential).

Usage
-----
    # Establish the baseline (copies everything, records full-manifest.json)
    python backup_differential.py --action full --source ./data --dest ./backups

    # Each differential run copies everything changed since the FULL backup
    python backup_differential.py --action diff --source ./data --dest ./backups
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime

BASELINE_MANIFEST = "full-manifest.json"


def create_sample_source(path: str) -> None:
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "ledger.csv"), "w", encoding="utf-8") as f:
        f.write("date,amount\n2026-07-01,100\n")
    print(f"[info] No --source given, created a sample directory at: {path}")


def scan_source(source: str) -> dict:
    state = {}
    for root, _dirs, files in os.walk(source):
        for name in files:
            full = os.path.join(root, name)
            rel = os.path.relpath(full, source)
            st = os.stat(full)
            state[rel] = {"mtime": st.st_mtime, "size": st.st_size}
    return state


def run_full(source: str, dest_dir: str) -> None:
    if not os.path.isdir(source):
        print(f"[error] Source directory not found: {source}")
        sys.exit(1)

    os.makedirs(dest_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    full_dir = os.path.join(dest_dir, f"full-{timestamp}")
    state = scan_source(source)

    for rel in state:
        src_path = os.path.join(source, rel)
        dst_path = os.path.join(full_dir, rel)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy2(src_path, dst_path)

    with open(os.path.join(dest_dir, BASELINE_MANIFEST), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

    print(f"[success] Full backup written to: {full_dir}")
    print(f"          Baseline manifest recorded ({len(state)} file(s)) — future --action diff "
          f"runs compare against this until the next full backup.")


def run_diff(source: str, dest_dir: str) -> None:
    baseline_path = os.path.join(dest_dir, BASELINE_MANIFEST)
    if not os.path.exists(baseline_path):
        print(f"[error] No baseline found at {baseline_path}. Run --action full first.")
        sys.exit(1)

    with open(baseline_path, "r", encoding="utf-8") as f:
        baseline = json.load(f)

    current_state = scan_source(source)
    changed = {
        rel: meta for rel, meta in current_state.items()
        if rel not in baseline or baseline[rel] != meta
    }

    if not changed:
        print("[info] No changes since the last full backup — nothing to do.")
        return

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    diff_dir = os.path.join(dest_dir, f"differential-{timestamp}")

    for rel in changed:
        src_path = os.path.join(source, rel)
        dst_path = os.path.join(diff_dir, rel)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy2(src_path, dst_path)
        print(f"[copy] {rel}")

    print(f"[success] Differential backup written to: {diff_dir}")
    print(f"          {len(changed)} file(s) changed since the last full backup "
          f"(baseline: {len(baseline)} file(s))")


def main():
    parser = argparse.ArgumentParser(description="Full + differential backups against a fixed baseline.")
    parser.add_argument("--action", choices=["full", "diff"], default="full")
    parser.add_argument("--source", default=None)
    parser.add_argument("--dest", default="./backups")
    args = parser.parse_args()

    source = args.source
    if source is None:
        source = "sample_source"
        create_sample_source(source)

    if args.action == "full":
        run_full(source, args.dest)
    else:
        run_diff(source, args.dest)


if __name__ == "__main__":
    main()
```

##### How It Works and How to Run

`--action full` walks the source, copies every file into a timestamped `full-*` folder, and writes `full-manifest.json` — the fixed reference point. `--action diff` walks the source again and compares against that same `full-manifest.json` (never against a previous differential), copying anything that's new or changed into a fresh `differential-*` folder. Restoring means: extract the latest full backup, then overlay the most recent differential on top.

```bash
# Week 1: establish the baseline
python backup_differential.py --action full --source /data --dest /backups

# Every day after: differential against that same baseline
python backup_differential.py --action diff --source /data --dest /backups

# Following week: take a new full backup to reset growth
python backup_differential.py --action full --source /data --dest /backups
```

##### Sample Output

```
$ python backup_differential.py --action full --source ./data --dest ./backups
[success] Full backup written to: ./backups/full-20260713-020000
          Baseline manifest recorded (1 file(s)) — future --action diff runs
          compare against this until the next full backup.

$ python backup_differential.py --action diff --source ./data --dest ./backups
[copy] ledger.csv
[success] Differential backup written to: ./backups/differential-20260714-020000
          1 file(s) changed since the last full backup (baseline: 1 file(s))
```

##### Variations / Flags

- Add `--hash` for content-hash comparison instead of mtime/size, same rationale as 13.2.
- Add a `--report-only` flag to print what a diff *would* include without copying — useful for estimating tonight's backup size before running it.
- Schedule with cron: full backup weekly (`0 2 * * 0`), differential daily the other six days (`0 2 * * 1-6`) — both invoking this same script with different `--action` values.

##### Common Pitfalls

- **Forgetting to take a new full backup:** if `--action full` is never re-run, every differential keeps comparing against an ever-more-stale baseline and grows toward the size of a full backup anyway, defeating the purpose — schedule full backups on a fixed cadence (e.g., weekly).
- **Restore requires exactly two pieces, in order:** applying a differential without first restoring its corresponding full backup will leave the restore incomplete (only the *changed* files will be present) — always restore full, then differential, never differential alone.
- **Multiple full backups in the destination:** since `full-manifest.json` is a single file, taking a second full backup overwrites the baseline that old differentials were computed against — don't mix differentials from before and after a new full backup when restoring.
