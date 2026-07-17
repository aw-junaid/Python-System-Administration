#!/usr/bin/env python3
"""
extract_cert_info.py - Parse a certificate file and print subject, issuer,
validity dates, serial number, and fingerprints.

Usage:
    python3 extract_cert_info.py --cert cert.pem
    python3 extract_cert_info.py --cert cert.der --form DER
    python3 extract_cert_info.py --cert cert.pem --json

Output:
    Human-readable summary printed to stdout (or JSON with --json).
"""
import argparse
import json
import sys

from cryptography import x509
from cryptography.hazmat.primitives import hashes


def load_cert(path, form):
    with open(path, "rb") as f:
        data = f.read()
    if form == "PEM":
        return x509.load_pem_x509_certificate(data)
    return x509.load_der_x509_certificate(data)


def cert_info(cert):
    not_before = cert.not_valid_before_utc if hasattr(cert, "not_valid_before_utc") else cert.not_valid_before
    not_after = cert.not_valid_after_utc if hasattr(cert, "not_valid_after_utc") else cert.not_valid_after
    return {
        "subject": cert.subject.rfc4514_string(),
        "issuer": cert.issuer.rfc4514_string(),
        "serial_number": str(cert.serial_number),
        "not_valid_before": not_before.isoformat(),
        "not_valid_after": not_after.isoformat(),
        "signature_algorithm": cert.signature_hash_algorithm.name
            if cert.signature_hash_algorithm else "unknown",
        "sha256_fingerprint": cert.fingerprint(hashes.SHA256()).hex(),
        "sha1_fingerprint": cert.fingerprint(hashes.SHA1()).hex(),
    }


def main():
    parser = argparse.ArgumentParser(description="Extract information from a certificate file.")
    parser.add_argument("--cert", required=True)
    parser.add_argument("--form", choices=["PEM", "DER"], default="PEM")
    parser.add_argument("--json", action="store_true", help="Print output as JSON")
    args = parser.parse_args()

    try:
        cert = load_cert(args.cert, args.form)
        info = cert_info(cert)

        if args.json:
            print(json.dumps(info, indent=2))
        else:
            print(f"Subject             : {info['subject']}")
            print(f"Issuer               : {info['issuer']}")
            print(f"Serial Number        : {info['serial_number']}")
            print(f"Valid From           : {info['not_valid_before']}")
            print(f"Valid Until          : {info['not_valid_after']}")
            print(f"Signature Algorithm  : {info['signature_algorithm']}")
            print(f"SHA256 Fingerprint   : {info['sha256_fingerprint']}")
            print(f"SHA1 Fingerprint     : {info['sha1_fingerprint']}")

    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
