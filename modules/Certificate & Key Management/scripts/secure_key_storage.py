#!/usr/bin/env python3
"""
secure_key_storage.py - Store and retrieve private keys securely, either in a
local encrypted keystore (password-derived Fernet key) or in a HashiCorp
Vault instance (if the `hvac` library and a running Vault server are
available).

Usage:
    # Local encrypted keystore
    python3 secure_key_storage.py store --backend local --keystore store.enc \
        --key-file id_rsa --password mypassword --name my-server-key

    python3 secure_key_storage.py retrieve --backend local --keystore store.enc \
        --password mypassword --name my-server-key --out id_rsa_recovered

    # HashiCorp Vault (requires VAULT_ADDR / VAULT_TOKEN env vars or --vault-* flags)
    python3 secure_key_storage.py store --backend vault --name my-server-key \
        --key-file id_rsa --vault-addr https://vault.internal:8200 --vault-token s.xxxx

    python3 secure_key_storage.py retrieve --backend vault --name my-server-key \
        --vault-addr https://vault.internal:8200 --vault-token s.xxxx --out id_rsa_recovered

Output:
    - local backend: a single encrypted file (store.enc) holding one or more named keys
    - vault backend: secrets written under the `secret/` KV path in Vault

NOTE: The static salt below is for demonstration only. In production, generate
a random per-keystore salt, store it alongside (not inside) the encrypted
file, and load it at runtime instead of hardcoding it in source.
"""
import argparse
import base64
import json
import os
import sys

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SALT = b"cert-key-mgmt-static-salt-change-me"
ITERATIONS = 390000


def derive_fernet_key(password):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=SALT, iterations=ITERATIONS)
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def load_store(path, password):
    fkey = derive_fernet_key(password)
    fernet = Fernet(fkey)
    if not os.path.exists(path):
        return fernet, {}
    with open(path, "rb") as f:
        token = f.read()
    data = json.loads(fernet.decrypt(token).decode())
    return fernet, data


def save_store(path, fernet, data):
    token = fernet.encrypt(json.dumps(data).encode())
    with open(path, "wb") as f:
        f.write(token)
    os.chmod(path, 0o600)


def store_local(args):
    with open(args.key_file, "r") as f:
        key_contents = f.read()
    fernet, data = load_store(args.keystore, args.password)
    data[args.name] = key_contents
    save_store(args.keystore, fernet, data)
    print(f"[+] Stored '{args.name}' in {args.keystore}")


def retrieve_local(args):
    fernet, data = load_store(args.keystore, args.password)
    if args.name not in data:
        print(f"[!] No entry named '{args.name}' found.", file=sys.stderr)
        sys.exit(1)
    with open(args.out, "w") as f:
        f.write(data[args.name])
    os.chmod(args.out, 0o600)
    print(f"[+] Retrieved '{args.name}' -> {args.out}")


def get_vault_client(args):
    import hvac
    addr = args.vault_addr or os.environ.get("VAULT_ADDR")
    token = args.vault_token or os.environ.get("VAULT_TOKEN")
    if not addr or not token:
        print("[!] Vault address/token required (via flags or VAULT_ADDR/VAULT_TOKEN).", file=sys.stderr)
        sys.exit(1)
    client = hvac.Client(url=addr, token=token)
    if not client.is_authenticated():
        print("[!] Vault authentication failed.", file=sys.stderr)
        sys.exit(1)
    return client


def store_vault(args):
    with open(args.key_file, "r") as f:
        key_contents = f.read()
    client = get_vault_client(args)
    client.secrets.kv.v2.create_or_update_secret(
        path=args.name, secret={"private_key": key_contents}
    )
    print(f"[+] Stored '{args.name}' in Vault under secret/{args.name}")


def retrieve_vault(args):
    client = get_vault_client(args)
    secret = client.secrets.kv.v2.read_secret_version(path=args.name)
    key_contents = secret["data"]["data"]["private_key"]
    with open(args.out, "w") as f:
        f.write(key_contents)
    os.chmod(args.out, 0o600)
    print(f"[+] Retrieved '{args.name}' from Vault -> {args.out}")


def main():
    parser = argparse.ArgumentParser(description="Securely store/retrieve private keys.")
    sub = parser.add_subparsers(dest="action", required=True)

    for action in ("store", "retrieve"):
        p = sub.add_parser(action)
        p.add_argument("--backend", choices=["local", "vault"], required=True)
        p.add_argument("--name", required=True, help="Logical name/path for the key")
        p.add_argument("--keystore", default="store.enc", help="Local keystore file (local backend)")
        p.add_argument("--password", default=None, help="Password for local keystore encryption")
        p.add_argument("--key-file", default=None, help="Private key file to store (store action)")
        p.add_argument("--out", default=None, help="Output path to write retrieved key (retrieve action)")
        p.add_argument("--vault-addr", default=None)
        p.add_argument("--vault-token", default=None)

    args = parser.parse_args()

    try:
        if args.backend == "local" and not args.password:
            print("[!] --password is required for the local backend.", file=sys.stderr)
            sys.exit(1)

        if args.action == "store":
            if not args.key_file:
                print("[!] --key-file is required for store.", file=sys.stderr)
                sys.exit(1)
            store_local(args) if args.backend == "local" else store_vault(args)
        else:
            if not args.out:
                print("[!] --out is required for retrieve.", file=sys.stderr)
                sys.exit(1)
            retrieve_local(args) if args.backend == "local" else retrieve_vault(args)

    except ImportError:
        print("[!] The 'hvac' package is required for the vault backend. "
              "Install it with: pip install hvac", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
