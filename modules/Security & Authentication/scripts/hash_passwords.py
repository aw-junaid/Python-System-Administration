#!/usr/bin/env python3
"""
hash_passwords.py
------------------------
Securely hashes a password using PBKDF2-HMAC-SHA256 with a random salt.
Outputs a self-contained string (salt + hash) that can be stored safely
and later checked with verify_password_hash.py.

NEVER store plain-text passwords. Always store only the hash.

Usage:
    python hash_passwords.py

Example:
    python hash_passwords.py
    # Enter password: (hidden input)
    # Output: pbkdf2_sha256$390000$<salt_hex>$<hash_hex>
"""

import base64
import getpass
import hashlib
import os
import sys

ITERATIONS = 390000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)

    salt_b64 = base64.b64encode(salt).decode("ascii")
    hash_b64 = base64.b64encode(derived).decode("ascii")

    return f"pbkdf2_sha256${ITERATIONS}${salt_b64}${hash_b64}"


def main():
    print("Secure password hashing (PBKDF2-HMAC-SHA256).\n")

    try:
        password = getpass.getpass("Enter password to hash: ")
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        sys.exit(1)

    if not password:
        print("Error: password cannot be empty.")
        sys.exit(1)

    hashed = hash_password(password)

    print("\nPassword hashed successfully.")
    print(f"Stored hash string:\n{hashed}")
    print("\nSave this entire string (e.g. in a database). It contains the algorithm,")
    print("iteration count, salt, and hash — everything needed to verify later,")
    print("but NOT the original password.")
    print("\nUse verify_password_hash.py with this string to check a password later.")


if __name__ == "__main__":
    main()
