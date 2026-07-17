#!/usr/bin/env python3
"""
restore_config.py

Purpose:
    Restore a configuration file from a previously created backup (see
    backup_config.py), overwriting the current version with the backed
    up one.

Usage:
    python3 restore_config.py <path_to_backup_file> <path_to_restore_to>

    If no arguments are given, this script runs an end-to-end demo:
    it creates a config, backs it up, modifies the original, then
    restores it from the backup so you can see the original content
    return.

Expected Output:
    Restored 'config.json.20260717_101530.bak' -> 'config.json'

Caution:
    - THIS OVERWRITES the destination file without prompting. Make sure
      you are restoring to the correct path.
    - This script does not validate that the backup file is a
      well-formed config in your expected format before restoring it —
      it performs a plain file copy. Verify the backup's contents
      first if you're unsure (see read_config_file.py).
    - If the destination file doesn't exist yet, it will simply be
      created from the backup.
"""

import os
import shutil
import sys

DEMO_ORIGINAL = "demo_config_to_restore.json"
DEMO_CONTENT_ORIGINAL = '{\n  "server": {"host": "127.0.0.1", "port": 8080}\n}\n'
DEMO_CONTENT_MODIFIED = '{\n  "server": {"host": "0.0.0.0", "port": 9999}\n}\n'


def restore_file(backup_path: str, restore_to: str) -> None:
    if not os.path.isfile(backup_path):
        print(f"Error: backup file not found: {backup_path}")
        return
    shutil.copy2(backup_path, restore_to)
    print(f"Restored '{backup_path}' -> '{restore_to}'")


def run_demo():
    import datetime
    print("No arguments given, running a full backup+restore demo.\n")

    # 1. Create an "original" config
    with open(DEMO_ORIGINAL, "w", encoding="utf-8") as f:
        f.write(DEMO_CONTENT_ORIGINAL)
    print(f"1. Created original config: {DEMO_ORIGINAL}")

    # 2. Back it up
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{DEMO_ORIGINAL}.{timestamp}.bak"
    shutil.copy2(DEMO_ORIGINAL, backup_path)
    print(f"2. Backed up to: {backup_path}")

    # 3. Simulate a bad change to the original
    with open(DEMO_ORIGINAL, "w", encoding="utf-8") as f:
        f.write(DEMO_CONTENT_MODIFIED)
    print(f"3. Modified original (simulating an unwanted change).")

    # 4. Restore from the backup
    restore_file(backup_path, DEMO_ORIGINAL)

    with open(DEMO_ORIGINAL, "r", encoding="utf-8") as f:
        print("\nFinal restored content:")
        print(f.read())


def main():
    args = sys.argv[1:]
    if len(args) >= 2:
        restore_file(args[0], args[1])
    else:
        run_demo()


if __name__ == "__main__":
    main()
