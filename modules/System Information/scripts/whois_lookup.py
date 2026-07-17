#!/usr/bin/env python3
"""
whois_lookup.py

Purpose:
    Query WHOIS data for a domain to retrieve registration and expiration
    information (registrar, creation date, expiration date, name servers,
    registrant organization when publicly available). Implemented using
    only the Python standard library -- it speaks the WHOIS protocol
    (RFC 3912) directly over a raw TCP socket to port 43, starting at
    IANA's root WHOIS server and following the referral to the
    registry-specific server. No extra package required.

Usage:
    python whois_lookup.py --domain example.com
    python whois_lookup.py --domain example.com --raw

Expected output:
    - Parsed summary: Registrar, Creation Date, Expiration Date,
      Updated Date, Name Servers, Domain Status (when present in the
      response -- field availability varies by TLD/registrar).
    - With --raw, prints the complete, unmodified WHOIS response text
      instead of the parsed summary (useful when parsing misses a field
      you need).
    - If the TLD's WHOIS server can't be determined or doesn't respond,
      prints a clear error message.
"""

import argparse
import re
import socket
import sys

IANA_WHOIS = "whois.iana.org"
WHOIS_PORT = 43
TIMEOUT = 10


def query_whois_server(server: str, query: str) -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(TIMEOUT)
        sock.connect((server, WHOIS_PORT))
        sock.sendall((query + "\r\n").encode("utf-8"))
        response = b""
        while True:
            try:
                chunk = sock.recv(4096)
            except socket.timeout:
                break
            if not chunk:
                break
            response += chunk
    return response.decode("utf-8", errors="ignore")


def find_referral_server(iana_response: str):
    match = re.search(r"refer:\s*(\S+)", iana_response, re.IGNORECASE)
    return match.group(1) if match else None


def parse_field(text: str, *labels) -> str:
    for label in labels:
        match = re.search(rf"{label}:\s*(.+)", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return "Not found"


def parse_all(text: str, *labels) -> list:
    results = []
    for label in labels:
        for match in re.finditer(rf"{label}:\s*(.+)", text, re.IGNORECASE):
            value = match.group(1).strip()
            if value not in results:
                results.append(value)
    return results


def main():
    parser = argparse.ArgumentParser(description="Query WHOIS registration data for a domain.")
    parser.add_argument("--domain", "-d", required=True, help="Domain name to look up, e.g. example.com")
    parser.add_argument("--raw", action="store_true", help="Print the raw WHOIS response instead of a parsed summary.")
    args = parser.parse_args()

    domain = args.domain.strip().lower()

    try:
        print(f"Querying {IANA_WHOIS} for referral...")
        iana_response = query_whois_server(IANA_WHOIS, domain)
    except (socket.timeout, socket.error) as e:
        print(f"[ERROR] Could not reach {IANA_WHOIS}: {e}", file=sys.stderr)
        sys.exit(1)

    referral_server = find_referral_server(iana_response)
    if not referral_server:
        print("[ERROR] Could not determine the registry WHOIS server for this domain/TLD.", file=sys.stderr)
        print("Raw IANA response was:\n" + iana_response)
        sys.exit(1)

    try:
        print(f"Querying {referral_server} for domain details...\n")
        whois_response = query_whois_server(referral_server, domain)
    except (socket.timeout, socket.error) as e:
        print(f"[ERROR] Could not reach {referral_server}: {e}", file=sys.stderr)
        sys.exit(1)

    if args.raw:
        print(whois_response)
        return

    print(f"=== WHOIS Summary: {domain} ===")
    print(f"Registrar        : {parse_field(whois_response, 'Registrar', 'registrar organization')}")
    print(f"Creation Date    : {parse_field(whois_response, 'Creation Date', 'created')}")
    print(f"Expiration Date  : {parse_field(whois_response, 'Registry Expiry Date', 'Expiration Date', 'expires')}")
    print(f"Updated Date     : {parse_field(whois_response, 'Updated Date', 'changed')}")
    print(f"Domain Status    : {', '.join(parse_all(whois_response, 'Domain Status')) or 'Not found'}")
    print(f"Name Servers     : {', '.join(parse_all(whois_response, 'Name Server')) or 'Not found'}")
    print("\n(Tip: use --raw to see the complete, unparsed WHOIS response.)")


if __name__ == "__main__":
    main()
