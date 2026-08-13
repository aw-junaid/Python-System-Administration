#!/usr/bin/env python3
"""
memory_info.py
--------------
Prints RAM statistics: total, available, used (and swap details).

Usage:
    python3 memory_info.py

Requires:
    pip install -r requirements.txt   (psutil)
"""

import sys

try:
    import psutil
except ImportError:
    print("[!] psutil is not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


def bytes_to_gb(value):
    return round(value / (1024 ** 3), 2)


def main():
    print("=" * 50)
    print(" MEMORY INFORMATION")
    print("=" * 50)

    vm = psutil.virtual_memory()
    print(f"{'Total RAM (GB)':<28}: {bytes_to_gb(vm.total)}")
    print(f"{'Available RAM (GB)':<28}: {bytes_to_gb(vm.available)}")
    print(f"{'Used RAM (GB)':<28}: {bytes_to_gb(vm.used)}")
    print(f"{'Free RAM (GB)':<28}: {bytes_to_gb(vm.free)}")
    print(f"{'RAM usage (%)':<28}: {vm.percent}")

    swap = psutil.swap_memory()
    print("\nSwap:")
    print(f"{'  Total swap (GB)':<28}: {bytes_to_gb(swap.total)}")
    print(f"{'  Used swap (GB)':<28}: {bytes_to_gb(swap.used)}")
    print(f"{'  Free swap (GB)':<28}: {bytes_to_gb(swap.free)}")
    print(f"{'  Swap usage (%)':<28}: {swap.percent}")

    print("=" * 50)


if __name__ == "__main__":
    main()
