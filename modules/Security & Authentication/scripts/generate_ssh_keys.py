#!/usr/bin/env python3
"""
generate_ssh_keys.py
--------------------------
Generates a new SSH key pair (RSA or Ed25519) using the 'cryptography' library
and saves the private/public keys to disk in standard OpenSSH format.

Requires: pip install cryptography

Usage:
    python generate_ssh_keys.py <output_basename> [--type rsa|ed25519] [--bits 4096]

Example:
    python generate_ssh_keys.py my_key
    python generate_ssh_keys.py my_key --type ed25519
    # Produces: my_key (private) and my_key.pub (public)
"""

import argparse
import os
import stat
import sys

try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, ed25519
except ImportError:
    print("Error: the 'cryptography' package is required.")
    print("Install it with: pip install -r requirements.txt")
    sys.exit(1)


def generate_rsa_key(bits: int):
    return rsa.generate_private_key(public_exponent=65537, key_size=bits)


def generate_ed25519_key():
    return ed25519.Ed25519PrivateKey.generate()


def save_key_pair(private_key, output_basename: str) -> None:
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH,
    )

    private_path = output_basename
    public_path = output_basename + ".pub"

    if os.path.exists(private_path) or os.path.exists(public_path):
        print(f"Error: '{private_path}' or '{public_path}' already exists. Choose a different name.")
        sys.exit(1)

    with open(private_path, "wb") as f:
        f.write(private_bytes)
    os.chmod(private_path, stat.S_IRUSR | stat.S_IWUSR)  # chmod 600

    with open(public_path, "wb") as f:
        f.write(public_bytes + b"\n")

    print(f"Private key saved to: {private_path} (permissions set to 600)")
    print(f"Public key saved to:  {public_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate an SSH key pair.")
    parser.add_argument("output_basename", help="Base filename for the key pair (e.g. 'my_key')")
    parser.add_argument("--type", choices=["rsa", "ed25519"], default="ed25519",
                         help="Key type (default: ed25519, recommended)")
    parser.add_argument("--bits", type=int, default=4096, help="Key size in bits for RSA only (default: 4096)")
    args = parser.parse_args()

    print(f"Generating a {args.type.upper()} SSH key pair...")

    if args.type == "rsa":
        private_key = generate_rsa_key(args.bits)
    else:
        private_key = generate_ed25519_key()

    save_key_pair(private_key, args.output_basename)

    print("\nDone. Add the .pub file's content to a server's ~/.ssh/authorized_keys")
    print("to allow login using the private key. Never share the private key file.")


if __name__ == "__main__":
    main()
