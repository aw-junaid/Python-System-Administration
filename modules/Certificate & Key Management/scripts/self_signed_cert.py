#!/usr/bin/env python3
"""
self_signed_cert.py - Generate a self-signed X.509 certificate and private key.
For internal testing / development only - browsers and OSes will not trust it.

Usage:
    python3 self_signed_cert.py --cn example.local --days 365 --keysize 2048 \
        --out-cert cert.pem --out-key key.pem

Output:
    - PEM encoded private key file
    - PEM encoded self-signed certificate file
"""
import argparse
import datetime
import sys

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


def generate_self_signed_cert(common_name, organization, country, days, key_size,
                               out_cert, out_key, key_password=None):
    print(f"[*] Generating {key_size}-bit RSA private key ...")
    key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, country),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])

    now = datetime.datetime.utcnow()
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=days))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName(common_name)]),
            critical=False,
        )
        .add_extension(
            x509.BasicConstraints(ca=False, path_length=None), critical=True
        )
        .sign(key, hashes.SHA256())
    )

    encryption = (
        serialization.BestAvailableEncryption(key_password.encode())
        if key_password else serialization.NoEncryption()
    )

    with open(out_key, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=encryption,
        ))

    with open(out_cert, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print(f"[+] Private key written to: {out_key}")
    print(f"[+] Certificate written to: {out_cert}")
    print(f"[+] Valid from {now} to {now + datetime.timedelta(days=days)}")


def main():
    parser = argparse.ArgumentParser(description="Generate a self-signed X.509 certificate.")
    parser.add_argument("--cn", required=True, help="Common Name (e.g. example.local)")
    parser.add_argument("--org", default="Internal Testing", help="Organization name")
    parser.add_argument("--country", default="US", help="2-letter country code")
    parser.add_argument("--days", type=int, default=365, help="Validity period in days")
    parser.add_argument("--keysize", type=int, default=2048, choices=[2048, 3072, 4096])
    parser.add_argument("--out-cert", default="cert.pem", help="Output certificate file")
    parser.add_argument("--out-key", default="key.pem", help="Output private key file")
    parser.add_argument("--key-password", default=None, help="Optional password to encrypt private key")
    args = parser.parse_args()

    try:
        generate_self_signed_cert(
            args.cn, args.org, args.country, args.days,
            args.keysize, args.out_cert, args.out_key, args.key_password
        )
    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
