#!/usr/bin/env python3
"""
detect_os.py

Purpose:
    Detect and print details about the current operating system:
    name, release, version, machine architecture, and Python version.

Usage:
    python detect_os.py

Expected Output:
    OS Name:        Linux
    OS Release:     5.15.0-91-generic
    OS Version:     #101-Ubuntu SMP ...
    Machine Arch:   x86_64
    Python Version: 3.11.4

Caution:
    - This script only reads system information; it makes no changes,
      so it is always safe to run.
    - Output format varies significantly between Linux, macOS, and
      Windows; don't assume the same fields exist identically on every
      platform if you build automation on top of this.
"""

import platform
import sys


def detect_os() -> None:
    print(f"OS Name:        {platform.system()}")
    print(f"OS Release:     {platform.release()}")
    print(f"OS Version:     {platform.version()}")
    print(f"Machine Arch:   {platform.machine()}")
    print(f"Python Version: {platform.python_version()}")


def main():
    detect_os()


if __name__ == "__main__":
    main()
