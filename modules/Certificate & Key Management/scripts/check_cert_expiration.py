#!/usr/bin/env python3
"""
check_cert_expiration.py - Check how many days remain until a certificate expires,
and exit with a non-zero code if it is within a warning threshold. Useful for
cron jobs / monitoring pipelines.

Usage:
    python3 check_cert_expiration.py --cert cert.pem --warn-days 30
    python3 check_cert_expiration.py --host example.com --port 443 --warn-days 14

Exit codes:
    0 - certificate is valid and outside the warning window
    1 - certificate expires within the warning window
    2 - certificate has already expired
    3 - error reading/fetching the certificate
"""
import argparse
import datetime
import socket
import ssl
import sys

from cryptography import x509


def get_cert_from_file(path):
    with open(path, "rb") as f:
        data = f.read()
    try:
        return x509.load_pem_x509_certificate(data)
    except ValueError:
        return x509.load_der_x509_certificate(data)


def get_cert_from_host(host, port, timeout=10):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with socket.create_connection((host, port), timeout=timeout) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as ssock:
            der = ssock.getpeercert(binary_form=True)
    return x509.load_der_x509_certificate(der)


def main():
    parser = argparse.ArgumentParser(description="Check certificate expiration.")
    parser.add_argument("--cert", help="Path to a local certificate file")
    parser.add_argument("--host", help="Remote host to check live TLS certificate")
    parser.add_argument("--port", type=int, default=443)
    parser.add_argument("--warn-days", type=int, default=30, help="Warn if expiry is within N days")
    args = parser.parse_args()

    if not args.cert and not args.host:
        print("[!] Provide either --cert or --host", file=sys.stderr)
        sys.exit(3)

    try:
        cert = get_cert_from_file(args.cert) if args.cert else get_cert_from_host(args.host, args.port)
        not_after = cert.not_valid_after_utc if hasattr(cert, "not_valid_after_utc") else cert.not_valid_after
        now = datetime.datetime.now(datetime.timezone.utc) if hasattr(cert, "not_valid_after_utc") \
            else datetime.datetime.utcnow()
        remaining = (not_after - now).days

        target = args.cert if args.cert else f"{args.host}:{args.port}"
        print(f"Target        : {target}")
        print(f"Expires On    : {not_after}")
        print(f"Days Remaining: {remaining}")

        if remaining < 0:
            print("[!] CERTIFICATE HAS EXPIRED")
            sys.exit(2)
        elif remaining <= args.warn_days:
            print(f"[!] WARNING: certificate expires within {args.warn_days} days")
            sys.exit(1)
        else:
            print("[+] Certificate is valid and not near expiry.")
            sys.exit(0)

    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
