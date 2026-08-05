#!/usr/bin/env python3
"""
get_hostname.py

Purpose:
    Retrieve and print the hostname of the current machine.

Usage:
    python get_hostname.py

Expected Output:
    Hostname: my-machine-name

Caution:
    - This script only reads information; it makes no system changes.
    - In containerized environments (Docker, etc.), the hostname
      returned is typically the container's ID or a name assigned by
      the container runtime, not your physical machine's name.
"""

import socket


def get_hostname() -> None:
    print(f"Hostname: {socket.gethostname()}")


def main():
    get_hostname()


if __name__ == "__main__":
    main()
