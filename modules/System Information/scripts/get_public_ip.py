#!/usr/bin/env python3
"""
get_public_ip.py

Purpose:
    Determine your network's public (NAT gateway) IP address -- the IP
    address your network shows to the outside internet -- by querying
    an external "what is my IP" API service over HTTPS. Uses only the
    Python standard library (urllib), no extra packages required.

Usage:
    python get_public_ip.py
    python get_public_ip.py --provider ifconfig.me
    python get_public_ip.py --ipv6

Expected output:
    - Your public IPv4 (or IPv6 with --ipv6) address, printed plainly.
    - The provider/service used to determine it.
    - If the request fails (no internet access, provider down), a clear
      error message and a suggestion to try a different --provider.

Notes:
    - This requires outbound internet access on port 443 (HTTPS).
    - Multiple providers are supported as fallbacks in case one is
      unreachable or rate-limits you.
"""

import argparse
import sys
import urllib.error
import urllib.request

PROVIDERS_V4 = {
    "ipify": "https://api.ipify.org",
    "icanhazip": "https://ipv4.icanhazip.com",
    "ifconfig.me": "https://ifconfig.me/ip",
}

PROVIDERS_V6 = {
    "ipify": "https://api6.ipify.org",
    "icanhazip": "https://ipv6.icanhazip.com",
}


def fetch_ip(url: str, timeout: int = 8) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "get_public_ip.py/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8").strip()


def main():
    parser = argparse.ArgumentParser(description="Retrieve your network's public IP address.")
    parser.add_argument("--provider", "-p", default=None,
                         help="Specific provider to use: ipify, icanhazip, or ifconfig.me (default: try all in order).")
    parser.add_argument("--ipv6", action="store_true", help="Look up your public IPv6 address instead of IPv4.")
    args = parser.parse_args()

    providers = PROVIDERS_V6 if args.ipv6 else PROVIDERS_V4

    if args.provider:
        if args.provider not in providers:
            print(f"[ERROR] Unknown provider '{args.provider}'. Choices: {', '.join(providers)}", file=sys.stderr)
            sys.exit(1)
        providers = {args.provider: providers[args.provider]}

    for name, url in providers.items():
        try:
            ip = fetch_ip(url)
            print(f"Public {'IPv6' if args.ipv6 else 'IPv4'} address: {ip}")
            print(f"(via {name}: {url})")
            return
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"[WARN] Provider '{name}' failed: {e}", file=sys.stderr)
            continue

    print("[ERROR] All providers failed. Check your internet connection or try a different --provider.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
