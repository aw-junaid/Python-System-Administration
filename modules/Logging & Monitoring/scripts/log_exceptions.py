#!/usr/bin/env python3
"""
log_exceptions.py
-------------------
Demonstrates how to properly log exceptions (with full traceback) using
the logging module instead of just printing them.

Usage:
    python3 log_exceptions.py
"""

import logging
import os

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "exceptions.log")

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=LOG_FILE,
    filemode="a",
)

logger = logging.getLogger("exceptions_demo")


def risky_division(a, b):
    return a / b


def parse_int(value):
    return int(value)


def main():
    # Example 1: logger.exception() automatically includes the traceback
    try:
        risky_division(10, 0)
    except ZeroDivisionError:
        logger.exception("Division failed")

    # Example 2: logger.error() with exc_info=True does the same thing
    try:
        parse_int("not_a_number")
    except ValueError as e:
        logger.error("Failed to parse integer: %s", e, exc_info=True)

    print(f"Exceptions logged with traceback to: {LOG_FILE}")


if __name__ == "__main__":
    main()
