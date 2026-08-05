#!/usr/bin/env python3
"""
run_with_prompts.py

Purpose:
    Run an external command WHILE allowing it to interact with the user
    (i.e. the command's prompts appear on screen and wait for real input).

Usage:
    python run_with_prompts.py "some_interactive_command"

    If no command is given, a safe built-in demo runs that asks the
    user to type something and confirm.

Expected Output:
    You will see any prompts printed live, and the program will pause
    until you respond via the keyboard.

Caution:
    - Because this script does not capture output, you interact with the
      child process directly. Only run commands you trust, since you are
      giving them full access to your terminal's input/output.
    - This is intentionally different from run_without_prompts.py, which
      suppresses interaction. Use this script when you WANT to be asked
      before an action proceeds (e.g. confirming a deletion).
"""

import subprocess
import sys


def run_with_prompt_demo() -> None:
    name = input("Demo prompt - what is your name? ")
    confirm = input(f"Proceed as '{name}'? (y/n): ").strip().lower()
    if confirm == "y":
        print(f"Confirmed. Hello, {name}!")
    else:
        print("Cancelled by user.")


def run_external_with_prompt(command: str) -> None:
    print(f"Running interactively: {command}\n")
    # No capture_output here - lets the child process use the real
    # terminal stdin/stdout/stderr directly for live prompts.
    result = subprocess.run(command, shell=True)
    print(f"\nExit Code: {result.returncode}")


def main():
    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
        run_external_with_prompt(command)
    else:
        run_with_prompt_demo()


if __name__ == "__main__":
    main()
