#!/usr/bin/env python3
"""
verify_password_hash.py
-----------------------------
Verifies a password against a hash string produced by hash_passwords.py
(format: pbkdf2_sha256$iterations$salt_b64$hash_b64).

Usage:
    python verify_password_hash.py "<stored_hash_string>"

Example:
    python verify_password_hash.py "pbkdf2_sha256$390000$abc123...$def456..."
    # Enter password: (hidden input)
    # Output: Password is VALID / Password is INVALID
"""

import argparse
import base64
import getpass
import hashlib
import hmac
import sys


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations_str, salt_b64, hash_b64 = stored_hash.split("$")
    except ValueError:
        print("Error: stored hash string is not in the expected format.")
        print("Expected format: pbkdf2_sha256$iterations$salt_b64$hash_b64")
        sys.exit(1)

    if algorithm != "pbkdf2_sha256":
        print(f"Error: unsupported algorithm '{algorithm}'.")
        sys.exit(1)

    iterations = int(iterations_str)
    salt = base64.b64decode(salt_b64)
    expected_hash = base64.b64decode(hash_b64)

    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)

    return hmac.compare_digest(derived, expected_hash)


def main():
    parser = argparse.ArgumentParser(description="Verify a password against a stored PBKDF2 hash.")
    parser.add_argument("stored_hash", help="The stored hash string (from hash_passwords.py)")
    args = parser.parse_args()

    try:
        password = getpass.getpass("Enter password to verify: ")
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        sys.exit(1)

    is_valid = verify_password(password, args.stored_hash)

    if is_valid:
        print("\nResult: Password is VALID.")
    else:
        print("\nResult: Password is INVALID.")
        sys.exit(1)


if __name__ == "__main__":
    main()
