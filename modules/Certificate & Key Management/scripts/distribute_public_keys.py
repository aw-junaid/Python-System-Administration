#!/usr/bin/env python3
"""
distribute_public_keys.py - Publish a public key (SSH, GPG, or certificate)
to a shared distribution point: a local trusted directory, an HTTP(S)
endpoint, or (for GPG keys) a public keyserver.

Usage:
    # Copy a public key into a shared/trusted directory
    python3 distribute_public_keys.py local --file id_ed25519.pub \
        --dest-dir /shared/trusted_keys/

    # Upload a public key to an internal HTTP endpoint
    python3 distribute_public_keys.py http --file cert.pem \
        --url https://keys.internal.example.com/upload --name web-server-cert

    # Publish a GPG public key to a public keyserver
    python3 distribute_public_keys.py gpg-keyserver --fingerprint ABCD1234EF \
        --keyserver hkps://keys.openpgp.org

Output:
    Confirmation message describing where the key was published.
"""
import argparse
import hashlib
import os
import shutil
import sys

import requests


def dist_local(args):
    os.makedirs(args.dest_dir, exist_ok=True)
    dest_path = os.path.join(args.dest_dir, os.path.basename(args.file))
    shutil.copy2(args.file, dest_path)
    with open(args.file, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    print(f"[+] Key copied to: {dest_path}")
    print(f"[+] SHA256 (verify out-of-band before trusting): {digest}")


def dist_http(args):
    with open(args.file, "rb") as f:
        files = {"file": (args.name or os.path.basename(args.file), f)}
        response = requests.post(args.url, files=files, timeout=30)
    response.raise_for_status()
    print(f"[+] Uploaded to {args.url} (HTTP {response.status_code})")


def dist_gpg_keyserver(args):
    import gnupg
    gpg = gnupg.GPG()
    result = gpg.send_keys(args.keyserver, args.fingerprint)
    print(f"[+] Sent key {args.fingerprint} to {args.keyserver}")
    print(f"[*] Result: {getattr(result, 'stderr', result)}")


def main():
    parser = argparse.ArgumentParser(description="Distribute public keys/certificates securely.")
    sub = parser.add_subparsers(dest="mode", required=True)

    p_local = sub.add_parser("local", help="Copy to a local/shared trusted directory")
    p_local.add_argument("--file", required=True)
    p_local.add_argument("--dest-dir", required=True)
    p_local.set_defaults(func=dist_local)

    p_http = sub.add_parser("http", help="Upload to an HTTP(S) endpoint")
    p_http.add_argument("--file", required=True)
    p_http.add_argument("--url", required=True)
    p_http.add_argument("--name", default=None)
    p_http.set_defaults(func=dist_http)

    p_gpg = sub.add_parser("gpg-keyserver", help="Publish a GPG key to a public keyserver")
    p_gpg.add_argument("--fingerprint", required=True)
    p_gpg.add_argument("--keyserver", default="hkps://keys.openpgp.org")
    p_gpg.set_defaults(func=dist_gpg_keyserver)

    args = parser.parse_args()

    try:
        args.func(args)
    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
