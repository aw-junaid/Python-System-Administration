#!/usr/bin/env python3
"""
network_interfaces.py
----------------------
Prints network interface details: MAC addresses and IP
configuration (IPv4/IPv6) per NIC.

Usage:
    python3 network_interfaces.py

Requires:
    pip install -r requirements.txt   (psutil)
"""

import socket
import sys

try:
    import psutil
except ImportError:
    print("[!] psutil is not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


ADDR_FAMILY_NAMES = {
    socket.AF_INET: "IPv4",
    socket.AF_INET6: "IPv6",
}

# psutil.AF_LINK covers MAC addresses cross-platform
MAC_FAMILY = getattr(psutil, "AF_LINK", None)


def main():
    print("=" * 60)
    print(" NETWORK INTERFACES")
    print("=" * 60)

    all_addrs = psutil.net_if_addrs()
    all_stats = psutil.net_if_stats()

    if not all_addrs:
        print("No network interfaces found.")
        return

    for iface, addrs in all_addrs.items():
        print(f"\nInterface: {iface}")

        stats = all_stats.get(iface)
        if stats:
            state = "UP" if stats.isup else "DOWN"
            print(f"  Status     : {state}")
            print(f"  Speed      : {stats.speed} Mbps" if stats.speed else "  Speed      : N/A")
            print(f"  MTU        : {stats.mtu}")

        for addr in addrs:
            if MAC_FAMILY is not None and addr.family == MAC_FAMILY:
                print(f"  MAC Address: {addr.address}")
            elif addr.family in ADDR_FAMILY_NAMES:
                label = ADDR_FAMILY_NAMES[addr.family]
                print(f"  {label} Address: {addr.address}")
                if addr.netmask:
                    print(f"    Netmask   : {addr.netmask}")
                if addr.broadcast:
                    print(f"    Broadcast : {addr.broadcast}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
