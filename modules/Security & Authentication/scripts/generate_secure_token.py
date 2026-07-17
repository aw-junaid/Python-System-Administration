#!/usr/bin/env python3
"""
generate_secure_token.py
------------------------------
Generates cryptographically secure random tokens, useful for API keys,
session tokens, password-reset links, CSRF tokens, etc.

Usage:
    python generate_secure_token.py [--bytes 32] [--format hex|urlsafe|base64]

Example:
    python generate_secure_token.py
    python generate_secure_token.py --bytes 48 --format urlsafe
"""

import argparse
import secrets


def generate_token(num_bytes: int, fmt: str) -> str:
    if fmt == "hex":
        return secrets.token_hex(num_bytes)
    elif fmt == "urlsafe":
        return secrets.token_urlsafe(num_bytes)
    elif fmt == "base64":
        import base64
        return base64.b64encode(secrets.token_bytes(num_bytes)).decode("ascii")
    else:
        raise ValueError(f"Unknown format: {fmt}")


def main():
    parser = argparse.ArgumentParser(description="Generate a cryptographically secure random token.")
    parser.add_argument("--bytes", type=int, default=32, dest="num_bytes",
                         help="Number of random bytes to generate (default: 32)")
    parser.add_argument("--format", default="urlsafe", choices=["hex", "urlsafe", "base64"],
                         help="Output format (default: urlsafe)")
    args = parser.parse_args()

    token = generate_token(args.num_bytes, args.format)

    print(f"Generated a {args.num_bytes}-byte secure token ({args.format} format):\n")
    print(token)
    print("\nUse this for API keys, session IDs, or password-reset tokens.")
    print("This token is not stored anywhere — copy it now if you need it.")


if __name__ == "__main__":
    main()
