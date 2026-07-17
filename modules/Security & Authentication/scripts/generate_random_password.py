#!/usr/bin/env python3
"""
generate_random_password.py
---------------------------------
Generates one or more cryptographically secure random passwords using
Python's 'secrets' module.

Usage:
    python generate_random_password.py [--length 16] [--count 1] [--no-symbols]

Example:
    python generate_random_password.py
    python generate_random_password.py --length 20 --count 5
    python generate_random_password.py --length 12 --no-symbols
"""

import argparse
import secrets
import string
import sys


def generate_password(length: int, use_symbols: bool) -> str:
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*()-_=+[]{}?"

    alphabet = lowercase + uppercase + digits
    if use_symbols:
        alphabet += symbols

    if length < 4:
        print("Error: length must be at least 4 to guarantee character variety.")
        sys.exit(1)

    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(length))

        has_lower = any(c in lowercase for c in password)
        has_upper = any(c in uppercase for c in password)
        has_digit = any(c in digits for c in password)
        has_symbol = any(c in symbols for c in password) if use_symbols else True

        if has_lower and has_upper and has_digit and has_symbol:
            return password


def main():
    parser = argparse.ArgumentParser(description="Generate cryptographically secure random passwords.")
    parser.add_argument("--length", type=int, default=16, help="Password length (default: 16)")
    parser.add_argument("--count", type=int, default=1, help="Number of passwords to generate (default: 1)")
    parser.add_argument("--no-symbols", action="store_true", help="Exclude special symbols from the password")
    args = parser.parse_args()

    print(f"Generating {args.count} password(s) of length {args.length}:\n")

    for i in range(1, args.count + 1):
        password = generate_password(args.length, use_symbols=not args.no_symbols)
        print(f"{i}. {password}")

    print("\nStore these somewhere safe (e.g. a password manager). They are not saved by this script.")


if __name__ == "__main__":
    main()
