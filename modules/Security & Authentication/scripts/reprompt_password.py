#!/usr/bin/env python3
"""
reprompt_password.py
--------------------------
Prompts for a password and reprompts if it doesn't meet requirements,
or asks the user to confirm it by typing it twice (like a signup form).

Usage:
    python reprompt_password.py [--confirm] [--min-length 8] [--max-attempts 3]

Example:
    python reprompt_password.py
    python reprompt_password.py --confirm --min-length 10
"""

import argparse
import getpass
import sys


def is_valid(password: str, min_length: int) -> tuple[bool, str]:
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters long."
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter."
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit."
    return True, ""


def prompt_password(min_length: int, max_attempts: int, confirm: bool) -> str:
    for attempt in range(1, max_attempts + 1):
        password = getpass.getpass("Enter password: ")
        valid, reason = is_valid(password, min_length)

        if not valid:
            print(f"Invalid password: {reason}")
            print(f"Attempt {attempt}/{max_attempts}\n")
            continue

        if confirm:
            confirm_password = getpass.getpass("Confirm password: ")
            if password != confirm_password:
                print("Passwords do not match. Please try again.\n")
                continue

        return password

    print("\nMaximum attempts reached. Exiting.")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Prompt for a password with validation and reprompting.")
    parser.add_argument("--confirm", action="store_true", help="Ask the user to re-type the password to confirm")
    parser.add_argument("--min-length", type=int, default=8, help="Minimum required password length (default: 8)")
    parser.add_argument("--max-attempts", type=int, default=3, help="Maximum number of attempts (default: 3)")
    args = parser.parse_args()

    password = prompt_password(args.min_length, args.max_attempts, args.confirm)
    print(f"\nPassword accepted ({len(password)} characters). Not stored or displayed.")


if __name__ == "__main__":
    main()
