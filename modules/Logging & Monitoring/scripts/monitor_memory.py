#!/usr/bin/env python3
"""
monitor_memory.py
---------------------
Checks current RAM and swap usage and warns if usage exceeds a
threshold percentage. Requires the `psutil` library.

Usage:
    python3 monitor_memory.py --threshold 80
"""

import argparse
import psutil


def check_memory(threshold):
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    print(f"RAM usage: {mem.percent}%")
    print(f"  Total: {mem.total / (1024**3):.2f} GB")
    print(f"  Used:  {mem.used / (1024**3):.2f} GB")
    print(f"  Available: {mem.available / (1024**3):.2f} GB")
    print(f"Swap usage: {swap.percent}%")

    if mem.percent >= threshold:
        print(f"[WARNING] RAM usage ({mem.percent}%) exceeds threshold ({threshold}%)")
        return False
    else:
        print(f"[OK] RAM usage is within the {threshold}% threshold")
        return True


def main():
    parser = argparse.ArgumentParser(description="Monitor memory (RAM/swap) usage")
    parser.add_argument("--threshold", type=float, default=80.0, help="Warning threshold percent")
    args = parser.parse_args()

    check_memory(args.threshold)


if __name__ == "__main__":
    main()
