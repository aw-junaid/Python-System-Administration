#!/usr/bin/env python3
"""
upgrade_packages.py
--------------------
Detect outdated packages (via `pip list --outdated --format=json`) and
batch-upgrade them via `pip install --upgrade`.

Usage:
    python upgrade_packages.py                # upgrade everything outdated
    python upgrade_packages.py requests numpy  # upgrade only these, if outdated
    python upgrade_packages.py --dry-run       # show what would be upgraded
    python upgrade_packages.py --python /path/to/venv/bin/python

Exit codes:
    0 -> success (including "nothing to upgrade")
    1 -> one or more upgrades failed
"""

import argparse
import json
import subprocess
import sys


def get_outdated(python_exe):
    cmd = [python_exe, "-m", "pip", "list", "--outdated", "--format=json"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print("[upgrade] Could not query outdated packages:")
        print(result.stderr.strip())
        sys.exit(1)
    try:
        return json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        print("[upgrade] Unexpected pip output, aborting.")
        sys.exit(1)


def upgrade(python_exe, names, dry_run=False):
    if not names:
        print("[upgrade] Nothing to upgrade.")
        return []

    failed = []
    for name in names:
        cmd = [python_exe, "-m", "pip", "install", "--upgrade", name]
        if dry_run:
            print(f"[dry-run] Would run: {' '.join(cmd)}")
            continue
        print(f"[upgrade] Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"[upgrade] OK: {name}")
        else:
            print(f"[upgrade] FAILED: {name}")
            print(result.stderr.strip()[-800:])
            failed.append(name)
    return failed


def main():
    parser = argparse.ArgumentParser(description="Batch-upgrade outdated Python packages.")
    parser.add_argument("packages", nargs="*", help="Optional subset of package names to consider")
    parser.add_argument("--dry-run", action="store_true", help="List what would be upgraded, do nothing")
    parser.add_argument("--python", default=sys.executable, help="Path to target python interpreter")
    args = parser.parse_args()

    outdated = get_outdated(args.python)
    outdated_names = {pkg["name"] for pkg in outdated}

    if args.packages:
        targets = [p for p in args.packages if p in outdated_names]
        skipped = [p for p in args.packages if p not in outdated_names]
        if skipped:
            print(f"[upgrade] Already up to date / not installed, skipping: {', '.join(skipped)}")
    else:
        targets = sorted(outdated_names)

    if not targets:
        print("[upgrade] Nothing outdated. All good.")
        sys.exit(0)

    print(f"[upgrade] {len(targets)} package(s) to upgrade: {', '.join(targets)}")
    failed = upgrade(args.python, targets, dry_run=args.dry_run)

    print("\n--- Summary ---")
    print(f"Attempted: {len(targets)}  Failed: {len(failed)}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
