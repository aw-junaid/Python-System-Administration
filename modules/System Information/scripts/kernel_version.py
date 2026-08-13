#!/usr/bin/env python3
"""
kernel_version.py
-------------------
Prints the exact kernel version, equivalent to `uname -r`, along
with the rest of the uname() tuple for context.

Usage:
    python3 kernel_version.py

Requires:
    No third-party packages. Uses only the Python standard library.
"""

import platform


def main():
    print("=" * 50)
    print(" KERNEL VERSION")
    print("=" * 50)

    uname = platform.uname()

    print(f"{'Kernel release (uname -r)':<28}: {uname.release}")
    print(f"{'Kernel version':<28}: {uname.version}")
    print(f"{'System name':<28}: {uname.system}")
    print(f"{'Node name':<28}: {uname.node}")
    print(f"{'Machine':<28}: {uname.machine}")
    print(f"{'Processor':<28}: {uname.processor or 'N/A'}")

    print("=" * 50)


if __name__ == "__main__":
    main()
