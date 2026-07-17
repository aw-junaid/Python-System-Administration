#!/usr/bin/env python3
"""
build_internal_pki.py - Build a two-tier internal PKI: a self-signed Root CA
and an Intermediate CA signed by the Root, ready to issue leaf certificates
for enterprise/internal infrastructure (use sign_certificate.py with the
intermediate to issue end-entity certs).

Usage:
    python3 build_internal_pki.py --org "My Company" --country US \
        --root-cn "My Company Root CA" --intermediate-cn "My Company Intermediate CA" \
        --root-days 7300 --intermediate-days 3650 --out-dir pki/

Output (under --out-dir):
    root_ca.key, root_ca.pem                 - Root CA private key + self-signed cert
    intermediate_ca.key, intermediate_ca.pem  - Intermediate CA key + cert (signed by root)
    chain.pem                                 - Intermediate + Root chain, for distribution
"""
import argparse
import datetime
import os
import sys

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


def build_name(cn, org, country):
    return x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, country),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, org),
        x509.NameAttribute(NameOID.COMMON_NAME, cn),
    ])


def make_ca_cert(subject_name, issuer_name, public_key, signing_key, days, path_length):
    now = datetime.datetime.utcnow()
    builder = (
        x509.CertificateBuilder()
        .subject_name(subject_name)
        .issuer_name(issuer_name)
        .public_key(public_key)
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=days))
        .add_extension(x509.BasicConstraints(ca=True, path_length=path_length), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True, content_commitment=False, key_encipherment=False,
                data_encipherment=False, key_agreement=False, key_cert_sign=True,
                crl_sign=True, encipher_only=False, decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(public_key), critical=False
        )
    )
    return builder.sign(signing_key, hashes.SHA256())


def main():
    parser = argparse.ArgumentParser(description="Build a two-tier internal PKI (Root + Intermediate CA).")
    parser.add_argument("--org", default="Internal Org")
    parser.add_argument("--country", default="US")
    parser.add_argument("--root-cn", default="Internal Root CA")
    parser.add_argument("--intermediate-cn", default="Internal Intermediate CA")
    parser.add_argument("--root-days", type=int, default=7300, help="Root CA validity (default ~20y)")
    parser.add_argument("--intermediate-days", type=int, default=3650, help="Intermediate validity (~10y)")
    parser.add_argument("--keysize", type=int, default=4096, choices=[2048, 3072, 4096])
    parser.add_argument("--out-dir", default="pki")
    args = parser.parse_args()

    try:
        os.makedirs(args.out_dir, exist_ok=True)

        print("[*] Generating Root CA key and self-signed certificate ...")
        root_key = rsa.generate_private_key(public_exponent=65537, key_size=args.keysize)
        root_name = build_name(args.root_cn, args.org, args.country)
        root_cert = make_ca_cert(root_name, root_name, root_key.public_key(), root_key,
                                  args.root_days, path_length=1)

        print("[*] Generating Intermediate CA key and certificate signed by Root ...")
        inter_key = rsa.generate_private_key(public_exponent=65537, key_size=args.keysize)
        inter_name = build_name(args.intermediate_cn, args.org, args.country)
        inter_cert = make_ca_cert(inter_name, root_name, inter_key.public_key(), root_key,
                                   args.intermediate_days, path_length=0)

        root_key_path = os.path.join(args.out_dir, "root_ca.key")
        root_cert_path = os.path.join(args.out_dir, "root_ca.pem")
        inter_key_path = os.path.join(args.out_dir, "intermediate_ca.key")
        inter_cert_path = os.path.join(args.out_dir, "intermediate_ca.pem")
        chain_path = os.path.join(args.out_dir, "chain.pem")

        with open(root_key_path, "wb") as f:
            f.write(root_key.private_bytes(
                serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption(),
            ))
        with open(root_cert_path, "wb") as f:
            f.write(root_cert.public_bytes(serialization.Encoding.PEM))
        with open(inter_key_path, "wb") as f:
            f.write(inter_key.private_bytes(
                serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption(),
            ))
        with open(inter_cert_path, "wb") as f:
            f.write(inter_cert.public_bytes(serialization.Encoding.PEM))
        with open(chain_path, "wb") as f:
            f.write(inter_cert.public_bytes(serialization.Encoding.PEM))
            f.write(root_cert.public_bytes(serialization.Encoding.PEM))

        for p in (root_key_path, inter_key_path):
            os.chmod(p, 0o600)

        print(f"[+] Root CA key/cert     : {root_key_path}, {root_cert_path}")
        print(f"[+] Intermediate key/cert: {inter_key_path}, {inter_cert_path}")
        print(f"[+] Full chain           : {chain_path}")
        print("[*] Use sign_certificate.py with intermediate_ca.pem/.key to issue leaf certificates.")
        print("[!] Protect root_ca.key offline; it should rarely, if ever, be used directly.")

    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
