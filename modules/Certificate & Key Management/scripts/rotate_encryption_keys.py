#!/usr/bin/env python3
"""
rotate_encryption_keys.py - Rotate a symmetric encryption key (Fernet/AES),
re-encrypting existing data with a freshly generated key and archiving the
old key for a defined grace period. Useful for periodic key-rotation policies
on encrypted data at rest.

Usage:
    # Generate the very first key
    python3 rotate_encryption_keys.py init --keystore keys/

    # Rotate: generates a new key, re-encrypts files, archives the old key
    python3 rotate_encryption_keys.py rotate --keystore keys/ --data-dir encrypted_data/

Output:
    - keys/current.key                   the active key
    - keys/archive/<timestamp>.key        previous key(s), retained for recovery
    - Files in --data-dir re-encrypted under the new key
"""
import argparse
import datetime
import os
import sys

from cryptography.fernet import Fernet


def init_keystore(keystore_dir):
    os.makedirs(keystore_dir, exist_ok=True)
    os.makedirs(os.path.join(keystore_dir, "archive"), exist_ok=True)
    key_path = os.path.join(keystore_dir, "current.key")
    if os.path.exists(key_path):
        print(f"[!] {key_path} already exists. Refusing to overwrite.", file=sys.stderr)
        sys.exit(1)
    key = Fernet.generate_key()
    with open(key_path, "wb") as f:
        f.write(key)
    os.chmod(key_path, 0o600)
    print(f"[+] New key store initialized: {key_path}")


def rotate(keystore_dir, data_dir):
    current_path = os.path.join(keystore_dir, "current.key")
    if not os.path.exists(current_path):
        print("[!] No current key found. Run `init` first.", file=sys.stderr)
        sys.exit(1)

    with open(current_path, "rb") as f:
        old_key = f.read()
    old_fernet = Fernet(old_key)

    new_key = Fernet.generate_key()
    new_fernet = Fernet(new_key)

    # Re-encrypt data files under the new key, if a data directory was given
    if data_dir and os.path.isdir(data_dir):
        for name in os.listdir(data_dir):
            path = os.path.join(data_dir, name)
            if not os.path.isfile(path):
                continue
            with open(path, "rb") as f:
                token = f.read()
            try:
                plaintext = old_fernet.decrypt(token)
            except Exception:
                print(f"[!] Skipping {name}: could not decrypt with current key.", file=sys.stderr)
                continue
            new_token = new_fernet.encrypt(plaintext)
            with open(path, "wb") as f:
                f.write(new_token)
            print(f"[+] Re-encrypted: {path}")

    # Archive the old key, then promote the new key
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    archive_path = os.path.join(keystore_dir, "archive", f"{timestamp}.key")
    with open(archive_path, "wb") as f:
        f.write(old_key)
    os.chmod(archive_path, 0o600)

    with open(current_path, "wb") as f:
        f.write(new_key)
    os.chmod(current_path, 0o600)

    print(f"[+] Old key archived to: {archive_path}")
    print(f"[+] New active key written to: {current_path}")


def main():
    parser = argparse.ArgumentParser(description="Rotate symmetric encryption keys.")
    sub = parser.add_subparsers(dest="action", required=True)

    p_init = sub.add_parser("init", help="Initialize a new key store")
    p_init.add_argument("--keystore", required=True)

    p_rot = sub.add_parser("rotate", help="Rotate the active key")
    p_rot.add_argument("--keystore", required=True)
    p_rot.add_argument("--data-dir", default=None, help="Directory of Fernet-encrypted files to re-encrypt")

    args = parser.parse_args()

    try:
        if args.action == "init":
            init_keystore(args.keystore)
        else:
            rotate(args.keystore, args.data_dir)
    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
