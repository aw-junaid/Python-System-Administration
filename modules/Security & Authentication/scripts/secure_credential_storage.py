#!/usr/bin/env python3
"""
secure_credential_storage.py
----------------------------------
Stores and retrieves username/password credentials in a local, encrypted
JSON vault, protected by a master password. Useful as a minimal personal
credential manager or as a building block for automation scripts.

Requires: pip install cryptography

Usage:
    python secure_credential_storage.py add <service> <username> --password <master_password>
    python secure_credential_storage.py get <service> --password <master_password>
    python secure_credential_storage.py list --password <master_password>
    python secure_credential_storage.py remove <service> --password <master_password>

Example:
    python secure_credential_storage.py add gmail myuser@gmail.com --password MyMasterPass
    # (You will be prompted to enter the credential's password securely)
    python secure_credential_storage.py get gmail --password MyMasterPass
    python secure_credential_storage.py list --password MyMasterPass

Storage file: credentials.vault (created in the current directory, encrypted)
"""

import argparse
import base64
import getpass
import json
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

VAULT_FILE = "credentials.vault"
SALT_FILE = "credentials.salt"


def get_or_create_salt() -> bytes:
    if os.path.exists(SALT_FILE):
        with open(SALT_FILE, "rb") as f:
            return f.read()
    salt = os.urandom(16)
    with open(SALT_FILE, "wb") as f:
        f.write(salt)
    return salt


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=390000)
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def load_vault(fernet: Fernet) -> dict:
    if not os.path.exists(VAULT_FILE):
        return {}

    with open(VAULT_FILE, "rb") as f:
        encrypted = f.read()

    if not encrypted:
        return {}

    try:
        decrypted = fernet.decrypt(encrypted)
    except InvalidToken:
        print("Error: incorrect master password or corrupted vault file.")
        sys.exit(1)

    return json.loads(decrypted.decode("utf-8"))


def save_vault(fernet: Fernet, data: dict) -> None:
    encrypted = fernet.encrypt(json.dumps(data).encode("utf-8"))
    with open(VAULT_FILE, "wb") as f:
        f.write(encrypted)
    os.chmod(VAULT_FILE, 0o600)


def main():
    parser = argparse.ArgumentParser(description="Store and retrieve credentials in a local encrypted vault.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add or update a credential")
    add_parser.add_argument("service", help="Service name/label (e.g. 'gmail')")
    add_parser.add_argument("username", help="Username for this service")
    add_parser.add_argument("--password", required=True, help="Master vault password")

    get_parser = subparsers.add_parser("get", help="Retrieve a stored credential")
    get_parser.add_argument("service", help="Service name/label to retrieve")
    get_parser.add_argument("--password", required=True, help="Master vault password")

    list_parser = subparsers.add_parser("list", help="List stored service names")
    list_parser.add_argument("--password", required=True, help="Master vault password")

    remove_parser = subparsers.add_parser("remove", help="Remove a stored credential")
    remove_parser.add_argument("service", help="Service name/label to remove")
    remove_parser.add_argument("--password", required=True, help="Master vault password")

    args = parser.parse_args()

    salt = get_or_create_salt()
    master_key = derive_key(args.password, salt)
    fernet = Fernet(master_key)

    vault = load_vault(fernet)

    if args.command == "add":
        try:
            credential_password = getpass.getpass(f"Enter password for '{args.username}' on '{args.service}': ")
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            sys.exit(1)

        vault[args.service] = {"username": args.username, "password": credential_password}
        save_vault(fernet, vault)
        print(f"\nCredential for '{args.service}' saved to vault ({VAULT_FILE}).")

    elif args.command == "get":
        if args.service not in vault:
            print(f"Error: no credential found for '{args.service}'.")
            sys.exit(1)
        entry = vault[args.service]
        print(f"Service:  {args.service}")
        print(f"Username: {entry['username']}")
        print(f"Password: {entry['password']}")

    elif args.command == "list":
        if not vault:
            print("Vault is empty.")
        else:
            print(f"Stored credentials ({len(vault)}):")
            for service, entry in vault.items():
                print(f"  - {service} (username: {entry['username']})")

    elif args.command == "remove":
        if args.service not in vault:
            print(f"Error: no credential found for '{args.service}'.")
            sys.exit(1)
        del vault[args.service]
        save_vault(fernet, vault)
        print(f"Credential for '{args.service}' removed.")


if __name__ == "__main__":
    main()
