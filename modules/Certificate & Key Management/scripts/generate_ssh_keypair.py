#!/usr/bin/env python3
"""
generate_ssh_keypair.py - Generate RSA, ECDSA, or Ed25519 SSH key pairs.

Usage:
    python3 generate_ssh_keypair.py --type ed25519 --out-private id_ed25519 \
        --out-public id_ed25519.pub --comment "user@host"

    python3 generate_ssh_keypair.py --type rsa --bits 4096 --out-private id_rsa \
        --out-public id_rsa.pub --passphrase mypassphrase

Output:
    - OpenSSH-formatted private key file (chmod 600 recommended)
    - OpenSSH public key file (id_*.pub), ready for authorized_keys
"""
import argparse
import os
import sys

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, ec, rsa


def generate_key(key_type, bits, curve):
    if key_type == "rsa":
        return rsa.generate_private_key(public_exponent=65537, key_size=bits)
    elif key_type == "ecdsa":
        curve_map = {"256": ec.SECP256R1(), "384": ec.SECP384R1(), "521": ec.SECP521R1()}
        return ec.generate_private_key(curve_map[curve])
    elif key_type == "ed25519":
        return ed25519.Ed25519PrivateKey.generate()
    raise ValueError(f"Unsupported key type: {key_type}")


def main():
    parser = argparse.ArgumentParser(description="Generate an SSH key pair.")
    parser.add_argument("--type", choices=["rsa", "ecdsa", "ed25519"], default="ed25519")
    parser.add_argument("--bits", type=int, default=4096, help="Key size for RSA (2048/3072/4096)")
    parser.add_argument("--curve", choices=["256", "384", "521"], default="256", help="Curve for ECDSA")
    parser.add_argument("--comment", default="", help="Comment appended to the public key")
    parser.add_argument("--passphrase", default=None, help="Optional passphrase to encrypt the private key")
    parser.add_argument("--out-private", default="id_key", help="Output private key path")
    parser.add_argument("--out-public", default="id_key.pub", help="Output public key path")
    args = parser.parse_args()

    try:
        key = generate_key(args.type, args.bits, args.curve)

        encryption = (
            serialization.BestAvailableEncryption(args.passphrase.encode())
            if args.passphrase else serialization.NoEncryption()
        )

        private_bytes = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.OpenSSH,
            encryption_algorithm=encryption,
        )
        public_bytes = key.public_key().public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH,
        )

        with open(args.out_private, "wb") as f:
            f.write(private_bytes)
        os.chmod(args.out_private, 0o600)

        with open(args.out_public, "wb") as f:
            f.write(public_bytes)
            if args.comment:
                f.write(f" {args.comment}".encode())
            f.write(b"\n")

        print(f"[+] Private key written to: {args.out_private} (permissions set to 600)")
        print(f"[+] Public key written to: {args.out_public}")

    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
