#!/usr/bin/env python3
"""
Topic: Parse Command-Line Options using argparse

Demonstrates defining named options, flags, and positional arguments using
Python's built-in argparse module.

Usage:
    python argparse_options.py --name Junaid --age 25 --verbose
    python argparse_options.py -h        (shows auto-generated help)

Expected Output:
    A greeting message built from the parsed arguments. With --verbose,
    extra debug details are printed too.
"""

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Example script demonstrating argparse for CLI options."
    )
    parser.add_argument("--name", type=str, default="World", help="Name to greet")
    parser.add_argument("--age", type=int, help="Your age (optional)")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    print(f"Hello, {args.name}!")

    if args.age is not None:
        print(f"You are {args.age} years old.")

    if args.verbose:
        print("[debug] Parsed arguments:", vars(args))


if __name__ == "__main__":
    main()
