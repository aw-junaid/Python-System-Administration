#!/usr/bin/env python3
"""
decrypt_files.py
----------------------
Decrypts a file that was encrypted with encrypt_files.py, using the same password.

Requires: pip install cryptography

Usage:
    python decrypt_files.py <encrypted_file> <password>

Example:
    python decrypt_files.py secret.txt.enc MyStrongPassword123
"""

import argparse
import base64
import os
import sys

try:
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError:
    print("Error: the 'cryptography' package is required.")
    print("Install it with: pip install -r requirements.txt")
    sys.exit(1)


SALT = b"file_encryption_salt_v1"  # Must match the salt used in encrypt_files.py


def derive_key(password: str) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SALT,
        iterations=390000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def decrypt_file(file_path: str, password: str) -> None:
    if not os.path.isfile(file_path):
        print(f"Error: '{file_path}' does not exist.")
        sys.exit(1)

    key = derive_key(password)
    fernet = Fernet(key)

    with open(file_path, "rb") as f:
        encrypted_data = f.read()

    try:
        decrypted_data = fernet.decrypt(encrypted_data)
    except InvalidToken:
        print("Error: decryption failed. Wrong password or corrupted file.")
        sys.exit(1)

    if file_path.endswith(".enc"):
        output_path = file_path[:-4]
    else:
        output_path = file_path + ".decrypted"

    with open(output_path, "wb") as f:
        f.write(decrypted_data)

    print(f"Decrypted: '{file_path}' -> '{output_path}'")


def main():
    parser = argparse.ArgumentParser(description="Decrypt a file encrypted with encrypt_files.py.")
    parser.add_argument("file_path", help="Encrypted file (.enc)")
    parser.add_argument("password", help="Password used to originally encrypt the file")
    args = parser.parse_args()

    decrypt_file(args.file_path, args.password)


if __name__ == "__main__":
    main()
