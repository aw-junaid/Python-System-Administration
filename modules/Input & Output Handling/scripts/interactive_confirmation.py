#!/usr/bin/env python3
"""
Topic: Interactive Confirmation Prompts

Asks the user a yes/no question and only proceeds if they confirm.
Keeps prompting until a valid answer (y/n) is given.

Usage:
    python interactive_confirmation.py

Expected Output:
    A yes/no prompt. Answering "y" prints a success message; answering
    "n" cancels the action.
"""

def confirm(prompt: str = "Are you sure you want to continue?") -> bool:
    while True:
        answer = input(f"{prompt} [y/n]: ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please answer with 'y' or 'n'.")


def main() -> None:
    print("This script simulates a destructive action (e.g. deleting a file).")

    if confirm("Delete 'important_file.txt'?"):
        print("Action confirmed: file would be deleted now.")
    else:
        print("Action cancelled by user.")


if __name__ == "__main__":
    main()
