#!/usr/bin/env python3
"""
generate_csr.py - Generate a private key and a Certificate Signing Request (CSR)
to submit to a Certificate Authority (public or internal).

Usage:
    python3 generate_csr.py --cn www.example.com --org "Example Inc" \
        --country US --state California --locality "San Francisco" \
        --san www.example.com --san example.com \
        --out-csr request.csr --out-key request.key

Output:
    - PEM private key file
    - PEM CSR file, ready to send to a CA
"""
import argparse
import sys

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


def generate_csr(cn, org, country, state, locality, sans, key_size, out_csr, out_key):
    key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)

    name_attrs = [x509.NameAttribute(NameOID.COMMON_NAME, cn)]
    if org:
        name_attrs.append(x509.NameAttribute(NameOID.ORGANIZATION_NAME, org))
    if country:
        name_attrs.append(x509.NameAttribute(NameOID.COUNTRY_NAME, country))
    if state:
        name_attrs.append(x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state))
    if locality:
        name_attrs.append(x509.NameAttribute(NameOID.LOCALITY_NAME, locality))

    builder = x509.CertificateSigningRequestBuilder().subject_name(x509.Name(name_attrs))

    san_list = sans or [cn]
    builder = builder.add_extension(
        x509.SubjectAlternativeName([x509.DNSName(d) for d in san_list]),
        critical=False,
    )

    csr = builder.sign(key, hashes.SHA256())

    with open(out_key, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    with open(out_csr, "wb") as f:
        f.write(csr.public_bytes(serialization.Encoding.PEM))

    print(f"[+] Private key written to: {out_key}")
    print(f"[+] CSR written to: {out_csr}")
    print("[*] Submit the CSR file to your Certificate Authority.")


def main():
    parser = argparse.ArgumentParser(description="Generate a private key and CSR.")
    parser.add_argument("--cn", required=True)
    parser.add_argument("--org", default=None)
    parser.add_argument("--country", default=None)
    parser.add_argument("--state", default=None)
    parser.add_argument("--locality", default=None)
    parser.add_argument("--san", action="append", help="Additional SAN entries, repeatable")
    parser.add_argument("--keysize", type=int, default=2048, choices=[2048, 3072, 4096])
    parser.add_argument("--out-csr", default="request.csr")
    parser.add_argument("--out-key", default="request.key")
    args = parser.parse_args()

    try:
        generate_csr(args.cn, args.org, args.country, args.state, args.locality,
                     args.san, args.keysize, args.out_csr, args.out_key)
    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
