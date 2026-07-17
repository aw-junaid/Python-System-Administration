#!/usr/bin/env python3
"""
backup_config.py

Purpose:
    Create a timestamped backup copy of a configuration file, so you
    have a safe restore point before modifying it.

Usage:
    python3 backup_config.py <path_to_config_file>
    python3 backup_config.py <path_to_config_file> --backup-dir backups

    If no path is given, this script creates a small demo config file
    and backs it up as an example.

Expected Output:
    Backed up 'config.json' to 'config.json.20260717_101530.bak'

Caution:
    - By default, backups are placed alongside the original file (same
      directory) with a timestamp suffix. Use --backup-dir to store
      them elsewhere instead.
    - This script does NOT delete old backups automatically; running it
      repeatedly will accumulate one backup file per run. Clean up old
      backups periodically if disk space matters.
    - This script only copies files; it never modifies the original.
"""

import datetime
import os
import shutil
import sys

DEMO_FILE = "demo_config_to_backup.json"
DEMO_CONTENT = '{\n  "server": {"host": "127.0.0.1", "port": 8080}\n}\n'


def backup_file(path: str, backup_dir: str = None) -> None:
    if not os.path.isfile(path):
        print(f"Error: file not found: {path}")
        return

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(path)
    backup_name = f"{filename}.{timestamp}.bak"

    if backup_dir:
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, backup_name)
    else:
        backup_path = os.path.join(os.path.dirname(path) or ".", backup_name)

    shutil.copy2(path, backup_path)
    print(f"Backed up '{path}' to '{backup_path}'")


def parse_args():
    args = sys.argv[1:]
    path = None
    backup_dir = None
    positional = []
    i = 0
    while i < len(args):
        if args[i] == "--backup-dir" and i + 1 < len(args):
            backup_dir = args[i + 1]; i += 2
        else:
            positional.append(args[i]); i += 1
    if positional:
        path = positional[0]
    return path, backup_dir


def main():
    path, backup_dir = parse_args()

    if not path:
        print("No file path given, creating and backing up a demo config file.\n")
        if not os.path.isfile(DEMO_FILE):
            with open(DEMO_FILE, "w", encoding="utf-8") as f:
                f.write(DEMO_CONTENT)
        path = DEMO_FILE

    backup_file(path, backup_dir)


if __name__ == "__main__":
    main()
