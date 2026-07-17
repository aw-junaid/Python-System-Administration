#!/usr/bin/env python3
"""
ftp_upload.py

Purpose:
    Upload (deploy) local files to an FTP server -- e.g. pushing built
    web assets to shared hosting -- using Python's built-in `ftplib`.

Usage:
    python ftp_upload.py --host ftp.example.com --user myuser --password mypass \
        --local-path ./dist/index.html --remote-path /public_html/index.html

    # Upload every file in a local directory (non-recursive) into a remote dir
    python ftp_upload.py --host ftp.example.com --user myuser --password mypass \
        --local-dir ./dist --remote-dir /public_html

    # Use explicit FTPS (FTP over TLS)
    python ftp_upload.py --host ftp.example.com --user myuser --password mypass \
        --local-path ./dist/app.js --remote-path /public_html/app.js --tls

Expected output:
    - Connection/login confirmation.
    - Progress/confirmation per file uploaded.
    - Final summary: files uploaded, total bytes, elapsed time.
    - Non-zero exit code and clear error message on connection/auth/
      permission failures.

CAUTION:
    Plain FTP (without --tls) transmits credentials and data in clear
    text over the network. Prefer --tls (FTPS) or, better, use
    sftp_automation.py (SSH-based) whenever the server supports it.
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
        ftp.prot_p()
    return ftp


def ensure_remote_dir(ftp: ftplib.FTP, remote_dir: str):
    """Create remote directory (and parents) if they don't already exist."""
    parts = remote_dir.strip("/").split("/")
    path = ""
    for part in parts:
        if not part:
            continue
        path += "/" + part
        try:
            ftp.mkd(path)
        except ftplib.error_perm:
            pass  # already exists


def upload_single_file(ftp: ftplib.FTP, local_path: str, remote_path: str) -> int:
    size = os.path.getsize(local_path)
    with open(local_path, "rb") as f:
        ftp.storbinary(f"STOR {remote_path}", f)
    return size


def upload_directory(ftp: ftplib.FTP, local_dir: str, remote_dir: str) -> tuple:
    ensure_remote_dir(ftp, remote_dir)
    total_files = 0
    total_bytes = 0
    for name in sorted(os.listdir(local_dir)):
        local_path = os.path.join(local_dir, name)
        if not os.path.isfile(local_path):
            print(f"[SKIP] {name} (subdirectories not supported in non-recursive mode)")
            continue
        remote_path = remote_dir.rstrip("/") + "/" + name
        size = upload_single_file(ftp, local_path, remote_path)
        print(f"[UPLOADED] {local_path} -> {remote_path} ({human_size(size)})")
        total_files += 1
        total_bytes += size
    return total_files, total_bytes


def main():
    parser = argparse.ArgumentParser(description="Upload files to an FTP server via ftplib.")
    parser.add_argument("--host", required=True, help="FTP server hostname or IP.")
    parser.add_argument("--port", type=int, default=21, help="FTP port (default: 21).")
    parser.add_argument("--user", default=None, help="FTP username.")
    parser.add_argument("--password", default=None, help="FTP password.")
    parser.add_argument("--anonymous", action="store_true", help="Log in as anonymous (no credentials needed).")
    parser.add_argument("--tls", action="store_true", help="Use explicit FTPS (FTP over TLS).")
    parser.add_argument("--timeout", type=int, default=15, help="Connection timeout in seconds (default: 15).")
    parser.add_argument("--local-path", default=None, help="Single local file path to upload.")
    parser.add_argument("--remote-path", default=None, help="Remote path to upload the file to.")
    parser.add_argument("--local-dir", default=None, help="Local directory of files to upload (non-recursive).")
    parser.add_argument("--remote-dir", default=None, help="Remote directory to upload files into.")
    args = parser.parse_args()

    if not args.anonymous and (not args.user or not args.password):
        print("[ERROR] Provide --user and --password, or use --anonymous.", file=sys.stderr)
        sys.exit(1)

    if not ((args.local_path and args.remote_path) or (args.local_dir and args.remote_dir)):
        print("[ERROR] Provide either (--local-path and --remote-path) or (--local-dir and --remote-dir).", file=sys.stderr)
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
        if args.local_path:
            if not os.path.isfile(args.local_path):
                print(f"[ERROR] Local file not found: {args.local_path}", file=sys.stderr)
                ftp.quit()
                sys.exit(1)
            size = upload_single_file(ftp, args.local_path, args.remote_path)
            print(f"[UPLOADED] {args.local_path} -> {args.remote_path} ({human_size(size)})")
            total_files, total_bytes = 1, size
        else:
            total_files, total_bytes = upload_directory(ftp, args.local_dir, args.remote_dir)
    except ftplib.all_errors as e:
        print(f"[ERROR] Transfer failed: {e}", file=sys.stderr)
        ftp.quit()
        sys.exit(1)

    ftp.quit()
    elapsed = time.time() - start

    print("\n=== Upload Summary ===")
    print(f"Files uploaded : {total_files}")
    print(f"Total size     : {human_size(total_bytes)}")
    print(f"Elapsed time   : {elapsed:.2f}s")


if __name__ == "__main__":
    main()
