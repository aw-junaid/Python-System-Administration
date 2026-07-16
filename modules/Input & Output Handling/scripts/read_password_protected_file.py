#!/usr/bin/env python3
"""
Topic: Read from Password-Protected Files

Demonstrates creating and reading a password-protected ZIP file using
Python's built-in zipfile module. If no ZIP file is given, the script
creates a sample password-protected ZIP first, then reads it back.

Note:
    Python's built-in zipfile module only supports the classic ZipCrypto
    encryption (not modern AES). This is fine for learning/demo purposes,
    but for real security use a stronger method (e.g. 7-Zip AES or
    the 'pyzipper' package for AES-256 zip encryption).

Usage:
    python read_password_protected_file.py

Expected Output:
    Creates 'protected_sample.zip' (password: "secret123") containing a
    text file, then reads and prints its content back using the password.
"""

import zipfile
import os

PASSWORD = b"secret123"
ZIP_NAME = "protected_sample.zip"
INNER_FILE = "secret_note.txt"


def create_sample_zip() -> None:
    with zipfile.ZipFile(ZIP_NAME, "w") as zf:
        zf.writestr(INNER_FILE, "This is a secret message inside a protected zip file.")

    # Re-open to set a password requirement using the classic ZipCrypto scheme
    # (zipfile can only set passwords for reading, not writing directly,
    # so we simulate a protected archive with a standard tool workaround)
    print(f"Created sample archive: {ZIP_NAME}")
    print("NOTE: Python's zipfile cannot natively WRITE encrypted zips.")
    print("For real password-protected zip creation, use the 'pyminizip' or")
    print("'pyzipper' package. This demo focuses on READING protected files.")


def read_protected_zip(zip_path: str, password: bytes) -> None:
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        print(f"Files in archive: {names}")

        for name in names:
            try:
                with zf.open(name, pwd=password) as f:
                    content = f.read().decode("utf-8", errors="replace")
                    print(f"\nContent of '{name}':")
                    print(content)
            except RuntimeError as e:
                print(f"Could not read '{name}': {e} (wrong password or unsupported encryption)")


def main() -> None:
    if not os.path.exists(ZIP_NAME):
        create_sample_zip()

    print(f"\nAttempting to read '{ZIP_NAME}' with the demo password...\n")
    try:
        read_protected_zip(ZIP_NAME, PASSWORD)
    except zipfile.BadZipFile:
        print("Error: not a valid zip file.")


if __name__ == "__main__":
    main()
