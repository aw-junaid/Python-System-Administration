#!/usr/bin/env python3
"""
decrypt_sensitive_data.py
-------------------------------
Decrypts data that was encrypted with encrypt_sensitive_data.py,
using the same password.

Requires: pip install cryptography

Usage:
    python decrypt_sensitive_data.py --text "<encrypted_base64_string>" --password MyPass123
    python decrypt_sensitive_data.py --file secrets.txt.enc --password MyPass123

Example:
    python decrypt_sensitive_data.py --file secrets.txt.enc --password Correct-Horse
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


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=390000)
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def decrypt_data(payload: bytes, password: str) -> bytes:
    try:
        salt_b64, encrypted = payload.split(b".", 1)
        salt = base64.urlsafe_b64decode(salt_b64)
    except (ValueError, Exception):
        print("Error: encrypted data is not in the expected format.")
        sys.exit(1)

    key = derive_key(password, salt)
    fernet = Fernet(key)

    try:
        return fernet.decrypt(encrypted)
    except InvalidToken:
        print("Error: decryption failed. Wrong password or corrupted data.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Decrypt text or a file encrypted with encrypt_sensitive_data.py.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Encrypted text string (base64) to decrypt")
    group.add_argument("--file", help="Path to an encrypted file")
    parser.add_argument("--password", required=True, help="Password used to originally encrypt the data")
    parser.add_argument("--output", default=None, help="Output file path (default: prints text, or strips .enc for files)")
    args = parser.parse_args()

    if args.text:
        payload = args.text.encode("ascii")
        decrypted = decrypt_data(payload, args.password)

        if args.output:
            with open(args.output, "wb") as f:
                f.write(decrypted)
            print(f"Decrypted data written to: {args.output}")
        else:
            print("Decrypted text:\n")
            print(decrypted.decode("utf-8", errors="replace"))
    else:
        if not os.path.isfile(args.file):
            print(f"Error: '{args.file}' does not exist.")
            sys.exit(1)

        with open(args.file, "rb") as f:
            payload = f.read()

        decrypted = decrypt_data(payload, args.password)
        output_path = args.output or (args.file[:-4] if args.file.endswith(".enc") else args.file + ".decrypted")

        with open(output_path, "wb") as f:
            f.write(decrypted)

        print(f"Decrypted: '{args.file}' -> '{output_path}'")


if __name__ == "__main__":
    main()
