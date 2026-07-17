#!/usr/bin/env python3
"""
validate_certificate.py
-----------------------------
Validates and inspects an X.509 certificate (.pem or .crt file):
checks expiry, subject, issuer, and validity dates.

Requires: pip install cryptography

Usage:
    python validate_certificate.py <certificate_path>

Example:
    python validate_certificate.py server.pem
    python validate_certificate.py /etc/ssl/certs/example.crt
"""

import argparse
import os
import sys
from datetime import datetime, timezone

try:
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
except ImportError:
    print("Error: the 'cryptography' package is required.")
    print("Install it with: pip install -r requirements.txt")
    sys.exit(1)


def load_certificate(path: str):
    with open(path, "rb") as f:
        data = f.read()

    try:
        return x509.load_pem_x509_certificate(data, default_backend())
    except ValueError:
        pass

    try:
        return x509.load_der_x509_certificate(data, default_backend())
    except ValueError:
        print("Error: could not parse certificate as PEM or DER format.")
        sys.exit(1)


def validate_certificate(path: str) -> None:
    if not os.path.isfile(path):
        print(f"Error: '{path}' does not exist.")
        sys.exit(1)

    cert = load_certificate(path)

    now = datetime.now(timezone.utc)
    not_before = cert.not_valid_before_utc
    not_after = cert.not_valid_after_utc

    print(f"Certificate: {path}\n")
    print(f"Subject:        {cert.subject.rfc4514_string()}")
    print(f"Issuer:         {cert.issuer.rfc4514_string()}")
    print(f"Serial Number:  {cert.serial_number}")
    print(f"Valid From:     {not_before}")
    print(f"Valid Until:    {not_after}")
    print(f"Signature Algo: {cert.signature_algorithm_oid._name}")

    if now < not_before:
        print("\nStatus: NOT YET VALID (starts in the future)")
    elif now > not_after:
        days_expired = (now - not_after).days
        print(f"\nStatus: EXPIRED ({days_expired} day(s) ago)")
    else:
        days_remaining = (not_after - now).days
        print(f"\nStatus: VALID ({days_remaining} day(s) remaining)")
        if days_remaining <= 30:
            print("Warning: this certificate will expire soon.")


def main():
    parser = argparse.ArgumentParser(description="Validate and inspect an X.509 certificate.")
    parser.add_argument("certificate_path", help="Path to the certificate file (.pem or .crt)")
    args = parser.parse_args()

    validate_certificate(args.certificate_path)


if __name__ == "__main__":
    main()
