#!/usr/bin/env python3
"""
sftp_automation.py

Purpose:
    Navigate a remote filesystem and transfer files over SFTP (SSH File
    Transfer Protocol) using `paramiko`. Unlike scp_transfer.py (single
    file, one direction per run), this script also supports listing
    remote directories and uploading/downloading entire directories
    (non-recursive, files only), making it useful for interactive-style
    remote filesystem tasks in an automated script.

    Requires: pip install paramiko  (see requirements.txt)

Usage:
    # List a remote directory
    python sftp_automation.py --host server.example.com --user deploy --key ~/.ssh/id_rsa \
        --action list --remote-path /var/www

    # Upload a whole local directory to a remote directory
    python sftp_automation.py --host server.example.com --user deploy --key ~/.ssh/id_rsa \
        --action upload-dir --local-path ./dist --remote-path /var/www/html

    # Download a whole remote directory to a local directory
    python sftp_automation.py --host server.example.com --user deploy --key ~/.ssh/id_rsa \
        --action download-dir --remote-path /var/log/app --local-path ./logs

    # Upload/download a single file
    python sftp_automation.py --host server.example.com --user deploy --key ~/.ssh/id_rsa \
        --action upload-file --local-path ./app.conf --remote-path /etc/app/app.conf

Expected output:
    - list: a directory listing (name, size, type file/dir, permissions).
    - upload-dir / download-dir: one line per file transferred, plus a
      summary of files transferred and total bytes.
    - upload-file / download-file: confirmation with file size and elapsed time.
    - Clear errors for missing paths, permission issues, or auth failures.
"""

import argparse
import getpass
import os
import stat
import sys
import time

try:
    import paramiko
except ImportError:
    print("[ERROR] Missing dependency 'paramiko'. Install it with: pip install paramiko", file=sys.stderr)
    sys.exit(1)


def human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"


def connect(args) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if args.key:
        client.connect(hostname=args.host, port=args.port, username=args.user,
                        key_filename=args.key, passphrase=args.password, timeout=args.timeout)
    else:
        client.connect(hostname=args.host, port=args.port, username=args.user,
                        password=args.password, timeout=args.timeout)
    return client


def do_list(sftp: paramiko.SFTPClient, remote_path: str):
    entries = sftp.listdir_attr(remote_path)
    print(f"\n{'TYPE':<6}{'SIZE':<12}{'PERMS':<8}NAME")
    for entry in sorted(entries, key=lambda e: e.filename):
        is_dir = stat.S_ISDIR(entry.st_mode)
        perms = stat.filemode(entry.st_mode)
        print(f"{'DIR' if is_dir else 'FILE':<6}{human_size(entry.st_size):<12}{perms:<8}{entry.filename}")
    print(f"\nTotal entries: {len(entries)}")


def do_upload_file(sftp: paramiko.SFTPClient, local_path: str, remote_path: str):
    if not os.path.isfile(local_path):
        print(f"[ERROR] Local file not found: {local_path}", file=sys.stderr)
        sys.exit(1)
    start = time.time()
    sftp.put(local_path, remote_path)
    size = os.path.getsize(local_path)
    print(f"[UPLOADED] {local_path} -> {remote_path} ({human_size(size)}, {time.time() - start:.2f}s)")


def do_download_file(sftp: paramiko.SFTPClient, remote_path: str, local_path: str):
    local_dir = os.path.dirname(os.path.abspath(local_path))
    if local_dir:
        os.makedirs(local_dir, exist_ok=True)
    start = time.time()
    sftp.get(remote_path, local_path)
    size = os.path.getsize(local_path)
    print(f"[DOWNLOADED] {remote_path} -> {local_path} ({human_size(size)}, {time.time() - start:.2f}s)")


def do_upload_dir(sftp: paramiko.SFTPClient, local_dir: str, remote_dir: str):
    if not os.path.isdir(local_dir):
        print(f"[ERROR] Local directory not found: {local_dir}", file=sys.stderr)
        sys.exit(1)
    try:
        sftp.stat(remote_dir)
    except FileNotFoundError:
        sftp.mkdir(remote_dir)

    total_files = 0
    total_bytes = 0
    for name in sorted(os.listdir(local_dir)):
        local_path = os.path.join(local_dir, name)
        if not os.path.isfile(local_path):
            print(f"[SKIP] {name} (subdirectories not supported in non-recursive mode)")
            continue
        remote_path = remote_dir.rstrip("/") + "/" + name
        sftp.put(local_path, remote_path)
        size = os.path.getsize(local_path)
        print(f"[UPLOADED] {name} -> {remote_path} ({human_size(size)})")
        total_files += 1
        total_bytes += size
    print(f"\nFiles uploaded: {total_files}, total size: {human_size(total_bytes)}")


def do_download_dir(sftp: paramiko.SFTPClient, remote_dir: str, local_dir: str):
    os.makedirs(local_dir, exist_ok=True)
    entries = sftp.listdir_attr(remote_dir)
    total_files = 0
    total_bytes = 0
    for entry in entries:
        if stat.S_ISDIR(entry.st_mode):
            print(f"[SKIP] {entry.filename} (subdirectories not supported in non-recursive mode)")
            continue
        remote_path = remote_dir.rstrip("/") + "/" + entry.filename
        local_path = os.path.join(local_dir, entry.filename)
        sftp.get(remote_path, local_path)
        print(f"[DOWNLOADED] {entry.filename} -> {local_path} ({human_size(entry.st_size)})")
        total_files += 1
        total_bytes += entry.st_size
    print(f"\nFiles downloaded: {total_files}, total size: {human_size(total_bytes)}")


def main():
    parser = argparse.ArgumentParser(description="Browse and transfer files on a remote server via SFTP (paramiko).")
    parser.add_argument("--host", "-H", required=True, help="Remote hostname or IP.")
    parser.add_argument("--port", type=int, default=22, help="SSH port (default: 22).")
    parser.add_argument("--user", "-u", required=True, help="SSH username.")
    parser.add_argument("--password", "-p", default=None, help="SSH password (omit to be prompted if no --key given).")
    parser.add_argument("--key", "-k", default=None, help="Path to a private key file for key-based auth.")
    parser.add_argument("--timeout", "-t", type=int, default=15, help="Connection timeout in seconds (default: 15).")
    parser.add_argument("--action", required=True,
                         choices=["list", "upload-file", "download-file", "upload-dir", "download-dir"],
                         help="Operation to perform.")
    parser.add_argument("--local-path", default=None, help="Local file or directory path.")
    parser.add_argument("--remote-path", required=True, help="Remote file or directory path.")
    args = parser.parse_args()

    password = args.password
    if password is None and not args.key:
        password = getpass.getpass("SSH password: ")
    args.password = password

    print(f"Connecting to {args.host}:{args.port} as {args.user}...")
    try:
        client = connect(args)
    except (paramiko.AuthenticationException, paramiko.SSHException, OSError) as e:
        print(f"[ERROR] Could not connect: {e}", file=sys.stderr)
        sys.exit(1)

    sftp = client.open_sftp()
    print("Connected.\n")

    try:
        if args.action == "list":
            do_list(sftp, args.remote_path)
        elif args.action == "upload-file":
            do_upload_file(sftp, args.local_path, args.remote_path)
        elif args.action == "download-file":
            do_download_file(sftp, args.remote_path, args.local_path)
        elif args.action == "upload-dir":
            do_upload_dir(sftp, args.local_path, args.remote_path)
        elif args.action == "download-dir":
            do_download_dir(sftp, args.remote_path, args.local_path)
    except IOError as e:
        print(f"[ERROR] Operation failed: {e}", file=sys.stderr)
        sftp.close()
        client.close()
        sys.exit(1)

    sftp.close()
    client.close()


if __name__ == "__main__":
    main()
