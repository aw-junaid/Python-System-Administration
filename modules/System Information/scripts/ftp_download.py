#!/usr/bin/env python3
"""
ftp_download.py

Purpose:
    Retrieve (download) files from a legacy FTP server using Python's
    built-in `ftplib` -- no external dependencies required.

Usage:
    python ftp_download.py --host ftp.example.com --user myuser --password mypass \
        --remote-path /pub/data.zip --local-path ./data.zip

    # Anonymous FTP
    python ftp_download.py --host ftp.example.com --anonymous \
        --remote-path /pub/readme.txt --local-path ./readme.txt

    # Download an entire remote directory (non-recursive, files only)
    python ftp_download.py --host ftp.example.com --user myuser --password mypass \
        --remote-dir /pub/reports --local-dir ./reports

    # Use explicit FTPS (FTP over TLS) instead of plain FTP
    python ftp_download.py --host ftp.example.com --user myuser --password mypass \
        --remote-path /pub/data.zip --local-path ./data.zip --tls

Expected output:
    - Connection/login confirmation.
    - Progress messages as bytes are received.
    - Final summary: file(s) downloaded, total bytes, elapsed time.
    - Non-zero exit code and clear error message on connection/auth/
      file-not-found failures.

CAUTION:
    Plain FTP (without --tls) transmits credentials and data in clear
    text. Prefer --tls (FTPS) or, better, use sftp_automation.py (SSH-based)
    whenever the server supports it.
"""

import argparse
import ftplib
import os
import sys
import time


def human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"


def connect(args) -> ftplib.FTP:
    ftp_cls = ftplib.FTP_TLS if args.tls else ftplib.FTP
    ftp = ftp_cls()
    ftp.connect(args.host, args.port, timeout=args.timeout)
    if args.anonymous:
        ftp.login()
    else:
        ftp.login(args.user, args.password)
    if args.tls:
        ftp.prot_p()  # secure the data connection too
    return ftp


def download_single_file(ftp: ftplib.FTP, remote_path: str, local_path: str) -> int:
    os.makedirs(os.path.dirname(os.path.abspath(local_path)) or ".", exist_ok=True)
    downloaded = [0]

    def callback(chunk):
        downloaded[0] += len(chunk)
        f.write(chunk)

    with open(local_path, "wb") as f:
        ftp.retrbinary(f"RETR {remote_path}", callback)
    return downloaded[0]


def download_directory(ftp: ftplib.FTP, remote_dir: str, local_dir: str) -> tuple:
    os.makedirs(local_dir, exist_ok=True)
    ftp.cwd(remote_dir)
    entries = ftp.nlst()
    total_files = 0
    total_bytes = 0
    for entry in entries:
        local_path = os.path.join(local_dir, os.path.basename(entry))
        try:
            size = download_single_file(ftp, entry, local_path)
            print(f"[DOWNLOADED] {entry} -> {local_path} ({human_size(size)})")
            total_files += 1
            total_bytes += size
        except ftplib.error_perm:
            print(f"[SKIP] {entry} (likely a subdirectory, not supported in non-recursive mode)")
    return total_files, total_bytes


def main():
    parser = argparse.ArgumentParser(description="Download files from an FTP server via ftplib.")
    parser.add_argument("--host", required=True, help="FTP server hostname or IP.")
    parser.add_argument("--port", type=int, default=21, help="FTP port (default: 21).")
    parser.add_argument("--user", default=None, help="FTP username.")
    parser.add_argument("--password", default=None, help="FTP password.")
    parser.add_argument("--anonymous", action="store_true", help="Log in as anonymous (no credentials needed).")
    parser.add_argument("--tls", action="store_true", help="Use explicit FTPS (FTP over TLS).")
    parser.add_argument("--timeout", type=int, default=15, help="Connection timeout in seconds (default: 15).")
    parser.add_argument("--remote-path", default=None, help="Single remote file path to download.")
    parser.add_argument("--local-path", default=None, help="Local path to save the downloaded file.")
    parser.add_argument("--remote-dir", default=None, help="Remote directory to download files from (non-recursive).")
    parser.add_argument("--local-dir", default=None, help="Local directory to save downloaded files.")
    args = parser.parse_args()

    if not args.anonymous and (not args.user or not args.password):
        print("[ERROR] Provide --user and --password, or use --anonymous.", file=sys.stderr)
        sys.exit(1)

    if not ((args.remote_path and args.local_path) or (args.remote_dir and args.local_dir)):
        print("[ERROR] Provide either (--remote-path and --local-path) or (--remote-dir and --local-dir).", file=sys.stderr)
        sys.exit(1)

    start = time.time()
    try:
        print(f"Connecting to {args.host}:{args.port} ({'FTPS' if args.tls else 'FTP'})...")
        ftp = connect(args)
        print("Connected and logged in.\n")
    except (ftplib.all_errors, OSError) as e:
        print(f"[ERROR] Could not connect/login: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.remote_path:
            size = download_single_file(ftp, args.remote_path, args.local_path)
            print(f"[DOWNLOADED] {args.remote_path} -> {args.local_path} ({human_size(size)})")
            total_files, total_bytes = 1, size
        else:
            total_files, total_bytes = download_directory(ftp, args.remote_dir, args.local_dir)
    except ftplib.all_errors as e:
        print(f"[ERROR] Transfer failed: {e}", file=sys.stderr)
        ftp.quit()
        sys.exit(1)

    ftp.quit()
    elapsed = time.time() - start

    print("\n=== Download Summary ===")
    print(f"Files downloaded: {total_files}")
    print(f"Total size      : {human_size(total_bytes)}")
    print(f"Elapsed time    : {elapsed:.2f}s")


if __name__ == "__main__":
    main()
