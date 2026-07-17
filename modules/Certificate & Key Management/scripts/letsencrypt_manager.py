#!/usr/bin/env python3
"""
letsencrypt_manager.py - Thin automation wrapper around the `certbot` CLI to
obtain and renew free, trusted TLS certificates via the ACME protocol.

IMPORTANT: This script does not implement the ACME protocol itself. It
requires certbot to be installed separately (https://certbot.eff.org) and
simply orchestrates it. It must be run with sufficient privileges to bind
port 80/443 (standalone mode) or to write to your webroot.

Usage:
    # Obtain a new certificate using the standalone plugin (port 80 must be free)
    python3 letsencrypt_manager.py obtain --domain example.com --email admin@example.com \
        --method standalone

    # Obtain using webroot plugin
    python3 letsencrypt_manager.py obtain --domain example.com --email admin@example.com \
        --method webroot --webroot-path /var/www/html

    # Renew all certificates due for renewal
    python3 letsencrypt_manager.py renew

    # Dry run (test without hitting real rate limits)
    python3 letsencrypt_manager.py obtain --domain example.com --email admin@example.com \
        --method standalone --dry-run

Output:
    Certificates are stored by certbot under /etc/letsencrypt/live/<domain>/
    This script prints certbot's output and the resulting exit code.
"""
import argparse
import shutil
import subprocess
import sys


def ensure_certbot_installed():
    if shutil.which("certbot") is None:
        print(
            "[!] certbot is not installed or not on PATH.\n"
            "    Install it first, e.g.:\n"
            "      Ubuntu/Debian : sudo apt install certbot\n"
            "      macOS (brew)  : brew install certbot\n"
            "    See https://certbot.eff.org for OS-specific instructions.",
            file=sys.stderr,
        )
        sys.exit(1)


def obtain(args):
    cmd = ["certbot", "certonly", "--non-interactive", "--agree-tos",
           "--email", args.email, "-d", args.domain]

    if args.method == "standalone":
        cmd += ["--standalone"]
    elif args.method == "webroot":
        if not args.webroot_path:
            print("[!] --webroot-path is required for the webroot method", file=sys.stderr)
            sys.exit(1)
        cmd += ["--webroot", "-w", args.webroot_path]
    elif args.method == "dns":
        print("[*] DNS-01 challenges require a provider-specific certbot plugin "
              "(e.g. certbot-dns-cloudflare). Install it and re-run certbot manually "
              "or extend this script with the relevant --dns-* flags.")
        sys.exit(1)

    if args.dry_run:
        cmd += ["--dry-run"]

    print(f"[*] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def renew(args):
    cmd = ["certbot", "renew", "--non-interactive"]
    if args.dry_run:
        cmd += ["--dry-run"]
    print(f"[*] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def main():
    ensure_certbot_installed()

    parser = argparse.ArgumentParser(description="Automate Let's Encrypt certificates via certbot.")
    sub = parser.add_subparsers(dest="action", required=True)

    p_obtain = sub.add_parser("obtain", help="Obtain a new certificate")
    p_obtain.add_argument("--domain", required=True)
    p_obtain.add_argument("--email", required=True)
    p_obtain.add_argument("--method", choices=["standalone", "webroot", "dns"], default="standalone")
    p_obtain.add_argument("--webroot-path", default=None)
    p_obtain.add_argument("--dry-run", action="store_true")
    p_obtain.set_defaults(func=obtain)

    p_renew = sub.add_parser("renew", help="Renew all due certificates")
    p_renew.add_argument("--dry-run", action="store_true")
    p_renew.set_defaults(func=renew)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
