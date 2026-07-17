#!/usr/bin/env python3
"""
check_outdated.py
--------------------
Programmatic inventory of stale (outdated) requirements using
`pip list --outdated --format=json`.

Usage:
    python check_outdated.py
    python check_outdated.py --json                # raw JSON output
    python check_outdated.py --save outdated.json   # also write results to a file
    python check_outdated.py --python /path/to/venv/bin/python

Exit codes:
    0 -> ran successfully (0 or more outdated packages found)
    1 -> failed to query pip
"""

import argparse
import json
import subprocess
import sys


def check_outdated(python_exe=sys.executable):
    cmd = [python_exe, "-m", "pip", "list", "--outdated", "--format=json"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print("[check] Could not query pip:")
        print(result.stderr.strip())
        sys.exit(1)
    try:
        return json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        print("[check] Unexpected pip output.")
        sys.exit(1)


def print_table(outdated):
    if not outdated:
        print("Everything is up to date.")
        return
    name_w = max(len(p["name"]) for p in outdated) + 2
    cur_w = max(len(p["version"]) for p in outdated) + 2
    print(f"{'PACKAGE'.ljust(name_w)}{'CURRENT'.ljust(cur_w)}{'LATEST'}")
    for p in outdated:
        print(f"{p['name'].ljust(name_w)}{p['version'].ljust(cur_w)}{p['latest_version']}")
    print(f"\n{len(outdated)} package(s) outdated.")


def main():
    parser = argparse.ArgumentParser(description="Inventory of outdated Python packages.")
    parser.add_argument("--json", action="store_true", help="Print raw JSON instead of a table")
    parser.add_argument("--save", metavar="FILE", help="Also write the JSON result to a file")
    parser.add_argument("--python", default=sys.executable, help="Path to target python interpreter")
    args = parser.parse_args()

    outdated = check_outdated(args.python)

    if args.json:
        print(json.dumps(outdated, indent=2))
    else:
        print_table(outdated)

    if args.save:
        with open(args.save, "w") as f:
            json.dump(outdated, f, indent=2)
        print(f"\nSaved to {args.save}")

    sys.exit(0)


if __name__ == "__main__":
    main()
