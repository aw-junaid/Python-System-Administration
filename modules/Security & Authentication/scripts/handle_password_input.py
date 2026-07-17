#!/usr/bin/env python3
"""
handle_password_input.py
------------------------------
Demonstrates and provides a reusable way to accept password input securely
(hidden from the terminal, not echoed to screen, not stored in shell history).

Usage:
    python handle_password_input.py

Example:
    python handle_password_input.py
    # Prompts: Enter password: (input is hidden as you type)
"""

import getpass
import sys


def get_secure_password(prompt: str = "Enter password: ") -> str:
    """Prompt the user for a password without echoing it to the terminal."""
    try:
        password = getpass.getpass(prompt)
    except (EOFError, KeyboardInterrupt):
        print("\nPassword input cancelled.")
        sys.exit(1)

    if not password:
        print("Error: password cannot be empty.")
        sys.exit(1)

    return password


def main():
    print("Secure password input demo.")
    print("Your input will NOT be shown on screen and is NOT saved anywhere.\n")

    password = get_secure_password("Enter your password: ")

    print(f"\nPassword received successfully ({len(password)} characters).")
    print("Note: this script does not store, log, or transmit the password anywhere.")


if __name__ == "__main__":
    main()
