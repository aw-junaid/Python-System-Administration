#!/usr/bin/env python3
"""
Topic: Read from stdin with Timeout

Waits for user input on stdin, but gives up after a fixed timeout if
nothing is typed. Uses the 'select' module (Linux/Mac only).

Note:
    The 'select' based approach works on Unix-like systems (Linux/Mac).
    On Windows, stdin timeouts require a different approach (e.g. threading
    or the 'msvcrt' module) since 'select' does not support stdin there.

Usage:
    python read_stdin_timeout.py

Expected Output:
    Waits up to 5 seconds for you to type something and press Enter.
    If you type in time, it echoes your input. Otherwise it prints a
    timeout message.
"""

import sys
import select

TIMEOUT_SECONDS = 5


def main() -> None:
    print(f"You have {TIMEOUT_SECONDS} seconds to type something and press Enter...")

    if not hasattr(select, "select") or sys.platform.startswith("win"):
        print("select-based stdin timeout is not supported on this platform (Windows).")
        print("Falling back to a normal blocking input():")
        line = input("> ")
        print(f"You entered: {line}")
        return

    ready, _, _ = select.select([sys.stdin], [], [], TIMEOUT_SECONDS)

    if ready:
        line = sys.stdin.readline().strip()
        print(f"You entered: {line}")
    else:
        print("Timeout reached - no input received.")


if __name__ == "__main__":
    main()
