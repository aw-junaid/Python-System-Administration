#!/usr/bin/env python3
"""
manage_api_keys.py
------------------------
A simple local API key manager: add, list, get, and remove named API keys,
stored encrypted (password-protected) in a local JSON file.

Requires: pip install cryptography

Usage:
    python manage_api_keys.py add <name> <key_value> --password MyPass123
    python manage_api_keys.py list --password MyPass123
    python manage_api_keys.py get <name> --password MyPass123
    python manage_api_keys.py remove <name> --password MyPass123

Example:
    python manage_api_keys.py add openai sk-abc123... --password MyVaultPass
    python manage_api_keys.py list --password MyVaultPass
    python manage_api_keys.py get openai --password MyVaultPass
    python manage_api_keys.py remove openai --password MyVaultPass

Storage file: api_keys.vault (created in the current directory, encrypted)
"""

import argparse
import base64
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

VAULT_FILE = "api_keys.vault"
SALT_FILE = "api_keys.salt"


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
        print("Error: incorrect password or corrupted vault file.")
        sys.exit(1)

    return json.loads(decrypted.decode("utf-8"))


def save_vault(fernet: Fernet, data: dict) -> None:
    encrypted = fernet.encrypt(json.dumps(data).encode("utf-8"))
    with open(VAULT_FILE, "wb") as f:
        f.write(encrypted)
    os.chmod(VAULT_FILE, 0o600)


def main():
    parser = argparse.ArgumentParser(description="Manage API keys in a local encrypted vault.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add or update an API key")
    add_parser.add_argument("name", help="Name/label for the key (e.g. 'openai')")
    add_parser.add_argument("value", help="The actual API key value")
    add_parser.add_argument("--password", required=True, help="Vault password")

    list_parser = subparsers.add_parser("list", help="List stored key names (not values)")
    list_parser.add_argument("--password", required=True, help="Vault password")

    get_parser = subparsers.add_parser("get", help="Retrieve a stored API key value")
    get_parser.add_argument("name", help="Name/label of the key to retrieve")
    get_parser.add_argument("--password", required=True, help="Vault password")

    remove_parser = subparsers.add_parser("remove", help="Remove a stored API key")
    remove_parser.add_argument("name", help="Name/label of the key to remove")
    remove_parser.add_argument("--password", required=True, help="Vault password")

    args = parser.parse_args()

    salt = get_or_create_salt()
    key = derive_key(args.password, salt)
    fernet = Fernet(key)

    vault = load_vault(fernet)

    if args.command == "add":
        vault[args.name] = args.value
        save_vault(fernet, vault)
        print(f"API key '{args.name}' saved to vault ({VAULT_FILE}).")

    elif args.command == "list":
        if not vault:
            print("Vault is empty.")
        else:
            print(f"Stored API key names ({len(vault)}):")
            for name in vault:
                print(f"  - {name}")

    elif args.command == "get":
        if args.name not in vault:
            print(f"Error: no key named '{args.name}' found.")
            sys.exit(1)
        print(f"{args.name}: {vault[args.name]}")

    elif args.command == "remove":
        if args.name not in vault:
            print(f"Error: no key named '{args.name}' found.")
            sys.exit(1)
        del vault[args.name]
        save_vault(fernet, vault)
        print(f"API key '{args.name}' removed.")


if __name__ == "__main__":
    main()
