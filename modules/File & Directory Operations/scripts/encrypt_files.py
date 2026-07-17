#!/usr/bin/env python3
"""
encrypt_files.py
----------------------
Encrypts a file using a password, with the Fernet symmetric encryption
scheme (AES-based, provided by the 'cryptography' library).

Produces a .enc file. Use decrypt_files.py with the SAME password to reverse it.

Requires: pip install cryptography

Usage:
    python encrypt_files.py <file_path> <password>

Example:
    python encrypt_files.py secret.txt MyStrongPassword123
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


SALT = b"file_encryption_salt_v1"  # Fixed salt for reproducible key derivation from a password


def derive_key(password: str) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SALT,
        iterations=390000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def encrypt_file(file_path: str, password: str) -> None:
    if not os.path.isfile(file_path):
        print(f"Error: '{file_path}' does not exist.")
        sys.exit(1)

    key = derive_key(password)
    fernet = Fernet(key)

    with open(file_path, "rb") as f:
        data = f.read()

    encrypted_data = fernet.encrypt(data)
    output_path = file_path + ".enc"

    with open(output_path, "wb") as f:
        f.write(encrypted_data)

    print(f"Encrypted: '{file_path}' -> '{output_path}'")
    print("Keep your password safe — it is required to decrypt this file.")


def main():
    parser = argparse.ArgumentParser(description="Encrypt a file using a password.")
    parser.add_argument("file_path", help="File to encrypt")
    parser.add_argument("password", help="Password used to encrypt the file")
    args = parser.parse_args()

    encrypt_file(args.file_path, args.password)


if __name__ == "__main__":
    main()
