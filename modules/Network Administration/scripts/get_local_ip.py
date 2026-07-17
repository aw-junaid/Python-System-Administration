#!/usr/bin/env python3
"""
get_local_ip.py

Purpose:
    Identify the machine's private LAN IP address(es) -- the address(es)
    assigned to this machine on its local network(s), as opposed to the
    public-facing IP (see get_public_ip.py). Uses only the Python
    standard library.

Usage:
    python get_local_ip.py
    python get_local_ip.py --all-interfaces

Expected output:
    - Default mode: the single IP address this machine would use to
      reach the internet (determined via a UDP socket "trick" that
      doesn't actually send any packets), plus the hostname.
    - --all-interfaces mode: every IP address associated with every
      network interface/hostname alias on the machine (useful on
      multi-homed servers).
"""

import argparse
import socket


def get_primary_local_ip() -> str:
    """
    Determine the local IP that would be used to reach the outside world.
    This opens a UDP socket to a public IP (no data is actually sent,
    UDP 'connect' just selects the outbound route/interface) and reads
    back the local address the OS chose.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except OSError:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def get_all_local_ips() -> list:
    hostname = socket.gethostname()
    try:
        addr_info = socket.getaddrinfo(hostname, None)
        ips = sorted({info[4][0] for info in addr_info})
    except socket.gaierror:
        ips = []
    return ips


def main():
    parser = argparse.ArgumentParser(description="Identify this machine's private LAN IP address(es).")
    parser.add_argument("--all-interfaces", "-a", action="store_true",
                         help="List all local IP addresses across all interfaces/aliases, not just the primary one.")
    args = parser.parse_args()

    hostname = socket.gethostname()
    print(f"Hostname: {hostname}")

    if args.all_interfaces:
        ips = get_all_local_ips()
        print(f"\nAll local IP addresses found ({len(ips)}):")
        for ip in ips:
            print(f"  {ip}")
        if not ips:
            print("  (none found -- try running without --all-interfaces for the primary IP)")
    else:
        primary_ip = get_primary_local_ip()
        print(f"Primary local IP (used for outbound traffic): {primary_ip}")


if __name__ == "__main__":
    main()
