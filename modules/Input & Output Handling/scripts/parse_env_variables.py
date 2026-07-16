#!/usr/bin/env python3
"""
Topic: Parse Environment Variables

Reads configuration values from environment variables, with sensible
defaults when they are not set.

Usage:
    python parse_env_variables.py
    APP_NAME=MyApp DEBUG=true python parse_env_variables.py

Expected Output:
    Prints the resolved configuration values (from env vars or defaults).
"""

import os


def str_to_bool(value: str) -> bool:
    return value.strip().lower() in ("1", "true", "yes", "on")


def main() -> None:
    app_name = os.environ.get("APP_NAME", "DefaultApp")
    debug = str_to_bool(os.environ.get("DEBUG", "false"))
    max_workers = int(os.environ.get("MAX_WORKERS", "4"))

    print("Resolved configuration:")
    print(f"  APP_NAME    = {app_name}")
    print(f"  DEBUG       = {debug}")
    print(f"  MAX_WORKERS = {max_workers}")

    print("\nTip: set variables before running to override defaults, e.g.")
    print("  APP_NAME=MyApp DEBUG=true MAX_WORKERS=8 python parse_env_variables.py")


if __name__ == "__main__":
    main()
