#!/usr/bin/env python3
"""
encrypt_backup.py
====================
Encrypt (and decrypt) a backup file using a password-derived key, via
Fernet symmetric encryption (AES-128-CBC + HMAC) from the `cryptography`
library.

Usage
-----
    # Encrypt (prompts for a password if not given via --password or DB_BACKUP_PASSWORD)
    python encrypt_backup.py --action encrypt --input backup.tar.gz --output backup.tar.gz.enc

    # Decrypt
    python encrypt_backup.py --action decrypt --input backup.tar.gz.enc --output backup.tar.gz

Requirements
------------
    pip install cryptography
"""

import argparse
import base64
import getpass
import os
import sys

try:
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError:
    print("[error] 'cryptography' is not installed. Run: pip install cryptography")
    sys.exit(1)

SALT_SIZE = 16
PBKDF2_ITERATIONS = 390_000


def create_sample_input(path: str) -> None:
    with open(path, "wb") as f:
        f.write(b"Sample backup archive contents, standing in for a real .tar.gz file.\n")
    print(f"[info] No --input given, created a sample file at: {path}")


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=PBKDF2_ITERATIONS)
    return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))


def get_password(cli_password: str) -> str:
    if cli_password:
        return cli_password
    env_password = os.environ.get("DB_BACKUP_PASSWORD")
    if env_password:
        return env_password
    return getpass.getpass("Backup encryption password: ")


def encrypt_file(input_path: str, output_path: str, password: str) -> None:
    if not os.path.exists(input_path):
        print(f"[error] Input file not found: {input_path}")
        sys.exit(1)

    salt = os.urandom(SALT_SIZE)
    key = derive_key(password, salt)
    fernet = Fernet(key)

    with open(input_path, "rb") as f:
        plaintext = f.read()
    ciphertext = fernet.encrypt(plaintext)

    with open(output_path, "wb") as f:
        f.write(salt)  # store the salt alongside the ciphertext; it's not secret
        f.write(ciphertext)

    print(f"[success] Encrypted '{input_path}' -> '{output_path}' "
          f"({os.path.getsize(input_path)} -> {os.path.getsize(output_path)} bytes)")


def decrypt_file(input_path: str, output_path: str, password: str) -> None:
    if not os.path.exists(input_path):
        print(f"[error] Input file not found: {input_path}")
        sys.exit(1)

    with open(input_path, "rb") as f:
        salt = f.read(SALT_SIZE)
        ciphertext = f.read()

    key = derive_key(password, salt)
    fernet = Fernet(key)

    try:
        plaintext = fernet.decrypt(ciphertext)
    except InvalidToken:
        print("[error] Decryption failed — wrong password, or the file is corrupted/tampered with.")
        sys.exit(1)

    with open(output_path, "wb") as f:
        f.write(plaintext)

    print(f"[success] Decrypted '{input_path}' -> '{output_path}' ({len(plaintext)} bytes)")


def main():
    parser = argparse.ArgumentParser(description="Encrypt or decrypt a backup file with a password.")
    parser.add_argument("--action", choices=["encrypt", "decrypt"], default="encrypt")
    parser.add_argument("--input", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--password", default=None,
                         help="Password (prefer DB_BACKUP_PASSWORD env var or the interactive prompt instead)")
    args = parser.parse_args()

    input_path = args.input
    if input_path is None:
        input_path = "sample_backup.tar.gz"
        create_sample_input(input_path)

    password = get_password(args.password)

    if args.action == "encrypt":
        output_path = args.output or f"{input_path}.enc"
        encrypt_file(input_path, output_path, password)
    else:
        output_path = args.output or input_path.removesuffix(".enc")
        decrypt_file(input_path, output_path, password)


if __name__ == "__main__":
    main()
