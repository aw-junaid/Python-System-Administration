#!/usr/bin/env python3
"""
read_ssh_keys.py
----------------------
Reads and displays information about an SSH key file (public or private):
key type, bit size/curve, and fingerprint. Does not print private key material.

Requires: pip install cryptography

Usage:
    python read_ssh_keys.py <key_path>

Example:
    python read_ssh_keys.py ~/.ssh/id_ed25519
    python read_ssh_keys.py ~/.ssh/id_ed25519.pub
"""

import argparse
import base64
import hashlib
import os
import sys

try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, ed25519
except ImportError:
    print("Error: the 'cryptography' package is required.")
    print("Install it with: pip install -r requirements.txt")
    sys.exit(1)


def fingerprint_from_public_bytes(public_openssh_bytes: bytes) -> str:
    # OpenSSH public key format: "<type> <base64-data> [comment]"
    parts = public_openssh_bytes.decode().strip().split()
    if len(parts) < 2:
        return "unavailable"
    key_data = base64.b64decode(parts[1])
    digest = hashlib.sha256(key_data).digest()
    return "SHA256:" + base64.b64encode(digest).decode().rstrip("=")


def read_key(path: str) -> None:
    if not os.path.isfile(path):
        print(f"Error: '{path}' does not exist.")
        sys.exit(1)

    with open(path, "rb") as f:
        data = f.read()

    is_public = path.endswith(".pub") or data.startswith((b"ssh-", b"ecdsa-"))

    print(f"Reading key: {path}\n")

    if is_public:
        try:
            public_key = serialization.load_ssh_public_key(data)
        except ValueError as e:
            print(f"Error: could not parse public key: {e}")
            sys.exit(1)

        fingerprint = fingerprint_from_public_bytes(data)
        print("Key kind:     PUBLIC")
        print(f"Fingerprint:  {fingerprint}")

    else:
        password = None
        try:
            private_key = serialization.load_ssh_private_key(data, password=password)
        except TypeError:
            print("This private key is password-protected. Reading encrypted keys is not supported by this script.")
            sys.exit(1)
        except ValueError as e:
            print(f"Error: could not parse private key: {e}")
            sys.exit(1)

        print("Key kind:     PRIVATE (contents not displayed)")

        if isinstance(private_key, rsa.RSAPrivateKey):
            print("Key type:     RSA")
            print(f"Key size:     {private_key.key_size} bits")
        elif isinstance(private_key, ed25519.Ed25519PrivateKey):
            print("Key type:     Ed25519")
        else:
            print(f"Key type:     {type(private_key).__name__}")

        public_bytes = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH,
        )
        fingerprint = fingerprint_from_public_bytes(public_bytes)
        print(f"Fingerprint:  {fingerprint}")

    print("\nNote: private key material is never printed by this script.")


def main():
    parser = argparse.ArgumentParser(description="Read and display info about an SSH key file.")
    parser.add_argument("key_path", help="Path to a public (.pub) or private SSH key file")
    args = parser.parse_args()

    read_key(args.key_path)


if __name__ == "__main__":
    main()
