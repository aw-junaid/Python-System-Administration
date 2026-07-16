#!/usr/bin/env python3
"""
Topic: Write to Standard Output (stdout)

Shows different ways of writing to standard output: print(), sys.stdout.write(),
and flushing output manually.

Usage:
    python write_stdout.py

Expected Output:
    Several lines demonstrating different stdout writing techniques.
"""

import sys
import time


def main() -> None:
    print("Using print():", "this is the simplest way to write to stdout.")

    sys.stdout.write("Using sys.stdout.write(): this also writes to stdout.\n")

    print("Writing without newline...", end="")
    sys.stdout.flush()
    time.sleep(0.5)
    print(" done (flushed manually before continuing).")

    for i in range(3):
        print(f"Streaming value: {i}", flush=True)
        time.sleep(0.2)


if __name__ == "__main__":
    main()
