#!/usr/bin/env python3
"""
remote_backup.py
===================
Ship a local backup directory off-site using rsync (over SSH to a
remote host) or rclone (to cloud storage), with a required dry-run
preview path.

Usage
-----
    # rsync to a remote server over SSH
    python remote_backup.py --tool rsync --source ./backups/ --dest user@remotehost:/backups/ --dry-run
    python remote_backup.py --tool rsync --source ./backups/ --dest user@remotehost:/backups/

    # rclone to a configured cloud remote (run `rclone config` first)
    python remote_backup.py --tool rclone --source ./backups/ --dest myremote:backups/ --dry-run
    python remote_backup.py --tool rclone --source ./backups/ --dest myremote:backups/
"""

import argparse
import shutil
import subprocess
import sys


def create_sample_source(path: str) -> None:
    import os
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "placeholder.txt"), "w", encoding="utf-8") as f:
        f.write("Sample local backup content for a remote_backup.py dry-run demo.\n")
    print(f"[info] No --source given, created a sample directory at: {path}")


def check_tool(tool: str) -> None:
    if shutil.which(tool) is None:
        print(f"[error] '{tool}' command not found on PATH. See the Prerequisites section for install instructions.")
        sys.exit(1)


def build_rsync_command(source: str, dest: str, dry_run: bool, extra_flags):
    cmd = ["rsync", "-avz", "--progress"]
    if dry_run:
        cmd.append("--dry-run")
    cmd.extend(extra_flags)
    cmd.extend([source, dest])
    return cmd


def build_rclone_command(source: str, dest: str, dry_run: bool, extra_flags):
    cmd = ["rclone", "sync", source, dest, "--progress"]
    if dry_run:
        cmd.append("--dry-run")
    cmd.extend(extra_flags)
    return cmd


def run_transfer(tool: str, source: str, dest: str, dry_run: bool, extra_flags) -> None:
    check_tool(tool)

    if tool == "rsync":
        cmd = build_rsync_command(source, dest, dry_run, extra_flags)
    else:
        cmd = build_rclone_command(source, dest, dry_run, extra_flags)

    print(f"[info] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, text=True)

    if result.returncode != 0:
        print(f"[error] {tool} exited with code {result.returncode} — transfer may be incomplete.")
        sys.exit(result.returncode)

    mode = "Dry-run preview" if dry_run else "Transfer"
    print(f"[success] {mode} completed via {tool}: {source} -> {dest}")


def main():
    parser = argparse.ArgumentParser(description="Ship a local backup off-site via rsync (SSH) or rclone (cloud).")
    parser.add_argument("--tool", choices=["rsync", "rclone"], default="rsync")
    parser.add_argument("--source", default=None, help="Local source path (trailing slash matters for rsync)")
    parser.add_argument("--dest", default=None, help="Remote destination, e.g. user@host:/path/ or remote:bucket/path/")
    parser.add_argument("--dry-run", action="store_true", help="Preview the transfer without copying any data")
    parser.add_argument("--extra-flags", nargs="*", default=[], help="Additional flags passed through to rsync/rclone")
    args = parser.parse_args()

    source, dest = args.source, args.dest
    if source is None:
        source = "sample_source/"
        create_sample_source("sample_source")
    if dest is None:
        print("[error] --dest is required (e.g. user@remotehost:/backups/ or myremote:backups/)")
        sys.exit(1)

    run_transfer(args.tool, source, dest, args.dry_run, args.extra_flags)


if __name__ == "__main__":
    main()
