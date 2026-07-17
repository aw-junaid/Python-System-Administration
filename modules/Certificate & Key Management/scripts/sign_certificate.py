#!/usr/bin/env python3
"""
sign_certificate.py - Act as an internal Certificate Authority: sign a CSR
with a CA private key/certificate and issue a signed certificate.

Usage:
    python3 sign_certificate.py --csr request.csr --ca-cert ca.pem \
        --ca-key ca.key --days 365 --out signed_cert.pem

Requires: an existing CA certificate & key (see build_internal_pki.py to create one).

Output:
    - PEM certificate signed by the supplied CA
"""
import argparse
import datetime
import sys

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization


def load_ca_key(path, password):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(), password=password.encode() if password else None
        )


def sign_csr(csr_path, ca_cert_path, ca_key_path, ca_key_password, days, out_path):
    with open(csr_path, "rb") as f:
        csr = x509.load_pem_x509_csr(f.read())

    if not csr.is_signature_valid:
        raise ValueError("CSR signature is invalid; refusing to sign.")

    with open(ca_cert_path, "rb") as f:
        ca_cert = x509.load_pem_x509_certificate(f.read())

    ca_key = load_ca_key(ca_key_path, ca_key_password)

    now = datetime.datetime.utcnow()
    builder = (
        x509.CertificateBuilder()
        .subject_name(csr.subject)
        .issuer_name(ca_cert.subject)
        .public_key(csr.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=days))
    )

    for ext in csr.extensions:
        builder = builder.add_extension(ext.value, critical=ext.critical)

    builder = builder.add_extension(
        x509.BasicConstraints(ca=False, path_length=None), critical=True
    )

    cert = builder.sign(ca_key, hashes.SHA256())

    with open(out_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print(f"[+] Signed certificate written to: {out_path}")
    print(f"[+] Subject: {csr.subject}")
    print(f"[+] Issuer: {ca_cert.subject}")
    print(f"[+] Valid until: {now + datetime.timedelta(days=days)}")


def main():
    parser = argparse.ArgumentParser(description="Sign a CSR using an internal CA.")
    parser.add_argument("--csr", required=True, help="Path to CSR file to sign")
    parser.add_argument("--ca-cert", required=True, help="Path to CA certificate")
    parser.add_argument("--ca-key", required=True, help="Path to CA private key")
    parser.add_argument("--ca-key-password", default=None, help="Password for CA key, if encrypted")
    parser.add_argument("--days", type=int, default=365, help="Validity period in days")
    parser.add_argument("--out", default="signed_cert.pem", help="Output signed certificate file")
    args = parser.parse_args()

    try:
        sign_csr(args.csr, args.ca_cert, args.ca_key, args.ca_key_password, args.days, args.out)
    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
