#!/usr/bin/env python3
"""
scp_transfer.py

Purpose:
    Securely copy files to/from a remote server over an SSH tunnel using
    SCP semantics, implemented with `paramiko`'s SCP-compatible transport
    (via `paramiko.SFTPClient`, which provides the same secure-copy
    result as the `scp` command). Supports both upload and download.

    Requires: pip install paramiko  (see requirements.txt)

Usage:
    # Upload a local file to a remote server
    python scp_transfer.py --host server.example.com --user deploy --key ~/.ssh/id_rsa \
        --direction upload --local ./app.tar.gz --remote /srv/releases/app.tar.gz

    # Download a remote file to your local machine
    python scp_transfer.py --host server.example.com --user deploy --key ~/.ssh/id_rsa \
        --direction download --remote /var/log/app.log --local ./app.log

    # Password auth instead of a key
    python scp_transfer.py --host 10.0.0.5 --user admin --password mypass \
        --direction upload --local ./config.yaml --remote /etc/app/config.yaml

Expected output:
    - Connection confirmation.
    - A live progress line showing bytes transferred / total bytes as
      the copy proceeds.
    - Final summary: direction, file paths, total size, elapsed time,
      and transfer speed.
    - Clear error and non-zero exit code on connection, auth, or
      file-not-found failures.
"""

import argparse
import getpass
import os
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


def make_progress_callback():
    start_time = time.time()
    last_print = [0.0]

    def callback(transferred: int, total: int):
        now = time.time()
        if now - last_print[0] > 0.5 or transferred == total:
            pct = (transferred / total * 100) if total else 0
            elapsed = now - start_time
            speed = transferred / elapsed if elapsed > 0 else 0
            print(f"\r  {human_size(transferred)} / {human_size(total)} ({pct:.1f}%) "
                  f"at {human_size(speed)}/s", end="", flush=True)
            last_print[0] = now

    return callback


def main():
    parser = argparse.ArgumentParser(description="Securely copy a file to/from a remote server over SSH (SCP-style).")
    parser.add_argument("--host", "-H", required=True, help="Remote hostname or IP.")
    parser.add_argument("--port", type=int, default=22, help="SSH port (default: 22).")
    parser.add_argument("--user", "-u", required=True, help="SSH username.")
    parser.add_argument("--password", "-p", default=None, help="SSH password (omit to be prompted if no --key given).")
    parser.add_argument("--key", "-k", default=None, help="Path to a private key file for key-based auth.")
    parser.add_argument("--direction", choices=["upload", "download"], required=True, help="Transfer direction.")
    parser.add_argument("--local", "-l", required=True, help="Local file path (source for upload, destination for download).")
    parser.add_argument("--remote", "-r", required=True, help="Remote file path (destination for upload, source for download).")
    parser.add_argument("--timeout", "-t", type=int, default=15, help="Connection timeout in seconds (default: 15).")
    args = parser.parse_args()

    password = args.password
    if password is None and not args.key:
        password = getpass.getpass("SSH password: ")

    if args.direction == "upload" and not os.path.isfile(args.local):
        print(f"[ERROR] Local file not found: {args.local}", file=sys.stderr)
        sys.exit(1)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print(f"Connecting to {args.host}:{args.port} as {args.user}...")
    try:
        if args.key:
            client.connect(hostname=args.host, port=args.port, username=args.user,
                            key_filename=args.key, passphrase=password, timeout=args.timeout)
        else:
            client.connect(hostname=args.host, port=args.port, username=args.user,
                            password=password, timeout=args.timeout)
    except (paramiko.AuthenticationException, paramiko.SSHException, OSError) as e:
        print(f"[ERROR] Could not connect: {e}", file=sys.stderr)
        sys.exit(1)

    sftp = client.open_sftp()
    start = time.time()

    try:
        if args.direction == "upload":
            print(f"Uploading {args.local} -> {args.host}:{args.remote}")
            sftp.put(args.local, args.remote, callback=make_progress_callback())
            size = os.path.getsize(args.local)
        else:
            print(f"Downloading {args.host}:{args.remote} -> {args.local}")
            local_dir = os.path.dirname(os.path.abspath(args.local))
            if local_dir:
                os.makedirs(local_dir, exist_ok=True)
            sftp.get(args.remote, args.local, callback=make_progress_callback())
            size = os.path.getsize(args.local)
    except FileNotFoundError as e:
        print(f"\n[ERROR] File not found: {e}", file=sys.stderr)
        sftp.close()
        client.close()
        sys.exit(1)
    except IOError as e:
        print(f"\n[ERROR] Transfer failed: {e}", file=sys.stderr)
        sftp.close()
        client.close()
        sys.exit(1)

    sftp.close()
    client.close()
    elapsed = time.time() - start

    print("\n\n=== Transfer Summary ===")
    print(f"Direction    : {args.direction}")
    print(f"Local path   : {args.local}")
    print(f"Remote path  : {args.remote}")
    print(f"Size         : {human_size(size)}")
    print(f"Elapsed time : {elapsed:.2f}s")
    print(f"Avg speed    : {human_size(size / elapsed) if elapsed > 0 else 'n/a'}/s")


if __name__ == "__main__":
    main()
