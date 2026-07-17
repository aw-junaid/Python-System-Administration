#!/usr/bin/env python3
"""
encrypt_sensitive_data.py
-------------------------------
Encrypts a piece of text (or a file) using password-based Fernet
(AES) symmetric encryption, provided by the 'cryptography' library.

Requires: pip install cryptography

Usage:
    python encrypt_sensitive_data.py --text "my secret data" --password MyPass123
    python encrypt_sensitive_data.py --file secrets.txt --password MyPass123

Example:
    python encrypt_sensitive_data.py --text "database password: hunter2" --password Correct-Horse
"""

import argparse
import base64
import os
import sys

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError:
    print("Error: the 'cryptography' package is required.")
    print("Install it with: pip install -r requirements.txt")
    sys.exit(1)


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=390000)
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def encrypt_data(data: bytes, password: str) -> bytes:
    salt = os.urandom(16)
    key = derive_key(password, salt)
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    # Prepend the salt so decryption can regenerate the same key later.
    return base64.urlsafe_b64encode(salt) + b"." + encrypted


def main():
    parser = argparse.ArgumentParser(description="Encrypt text or a file using a password.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Text string to encrypt")
    group.add_argument("--file", help="Path to a file to encrypt")
    parser.add_argument("--password", required=True, help="Password used to derive the encryption key")
    parser.add_argument("--output", default=None, help="Output file path (default: <file>.enc, or prints for --text)")
    args = parser.parse_args()

    if args.text:
        encrypted = encrypt_data(args.text.encode("utf-8"), args.password)
        if args.output:
            with open(args.output, "wb") as f:
                f.write(encrypted)
            print(f"Encrypted text written to: {args.output}")
        else:
            print("Encrypted text (base64):\n")
            print(encrypted.decode("ascii"))
    else:
        if not os.path.isfile(args.file):
            print(f"Error: '{args.file}' does not exist.")
            sys.exit(1)

        with open(args.file, "rb") as f:
            data = f.read()

        encrypted = encrypt_data(data, args.password)
        output_path = args.output or (args.file + ".enc")

        with open(output_path, "wb") as f:
            f.write(encrypted)

        print(f"Encrypted: '{args.file}' -> '{output_path}'")

    print("\nKeep your password safe. It is required to decrypt this data and cannot be recovered.")


if __name__ == "__main__":
    main()
