#!/usr/bin/env python3
"""
idempotent_automation.py

Demonstrates designing automation that is IDEMPOTENT — safe to run
over and over with the same end result, instead of failing or
duplicating work on the second run. Covers three common patterns:
"ensure directory exists", "ensure a config line is present exactly
once", and "only do work if the output is missing/outdated" using a
checksum/state file.

Usage:
    python idempotent_automation.py
    python idempotent_automation.py   # run it again — notice no errors,
                                        # no duplicate lines, no repeated work

Expected output:
    Running the script prints what it changed on the FIRST run
    (directory created, config line added, file processed). Running it
    again immediately afterward prints that everything was already in
    the desired state, and it made NO changes the second time — proving
    the automation is idempotent. Creates a small workspace at
    ./idempotent_demo/.
"""

import hashlib
import json
import os


WORKSPACE = "idempotent_demo"
CONFIG_FILE = os.path.join(WORKSPACE, "app.conf")
STATE_FILE = os.path.join(WORKSPACE, ".state.json")
DATA_FILE = os.path.join(WORKSPACE, "input.txt")
PROCESSED_FILE = os.path.join(WORKSPACE, "processed.txt")

DESIRED_CONFIG_LINE = "feature_flag_enabled=true"


def ensure_directory(path: str) -> bool:
    """Create a directory only if it doesn't already exist. Returns True if it made a change."""
    if os.path.isdir(path):
        return False
    os.makedirs(path, exist_ok=True)
    return True


def ensure_line_in_file(path: str, line: str) -> bool:
    """
    Ensure a specific line exists in a file EXACTLY once. Safe to call
    repeatedly — it will not duplicate the line on subsequent runs.
    """
    existing_lines = []
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            existing_lines = [l.rstrip("\n") for l in f]

    if line in existing_lines:
        return False  # already present, nothing to do

    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    return True


def file_checksum(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_state() -> dict:
    if os.path.isfile(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def process_if_changed(input_path: str, output_path: str) -> bool:
    """
    Only re-process input_path if its checksum has changed since the
    last successful run (tracked in a small state file). This avoids
    redoing expensive work when nothing actually changed.
    """
    state = load_state()
    current_checksum = file_checksum(input_path)

    if state.get("input_checksum") == current_checksum and os.path.isfile(output_path):
        return False  # nothing changed, output already up to date

    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content.upper())  # stand-in for "expensive processing"

    state["input_checksum"] = current_checksum
    save_state(state)
    return True


def main():
    print("Idempotent Automation Demo")
    print("=" * 40)

    changed = []

    if ensure_directory(WORKSPACE):
        changed.append(f"created directory '{WORKSPACE}/'")

    if ensure_line_in_file(CONFIG_FILE, DESIRED_CONFIG_LINE):
        changed.append(f"added config line to '{CONFIG_FILE}'")

    if not os.path.isfile(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            f.write("hello idempotent world\n")
        changed.append(f"created sample input file '{DATA_FILE}'")

    if process_if_changed(DATA_FILE, PROCESSED_FILE):
        changed.append(f"processed '{DATA_FILE}' -> '{PROCESSED_FILE}'")

    if changed:
        print("Changes made this run:")
        for c in changed:
            print(f"  - {c}")
    else:
        print("No changes needed — system was already in the desired state.")
        print("(This is the goal: running this script again is always safe.)")

    print()
    print(f"Workspace: {os.path.abspath(WORKSPACE)}")
    print("Run this script again to see idempotency in action — it should report no changes.")


if __name__ == "__main__":
    main()
