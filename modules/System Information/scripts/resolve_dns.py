#!/usr/bin/env python3
"""
resolve_dns.py

Purpose:
    Look up DNS records (A, AAAA, MX, TXT, NS, CNAME, SOA) for a domain
    using the `dnspython` library, which queries DNS servers directly
    (more reliable and flexible than relying only on the OS resolver).

    Requires: pip install dnspython  (see requirements.txt)

Usage:
    python resolve_dns.py --domain example.com --type A
    python resolve_dns.py --domain example.com --type MX
    python resolve_dns.py --domain example.com --type TXT
    python resolve_dns.py --domain example.com --type A --type MX --type TXT
    python resolve_dns.py --domain example.com --type A --resolver 1.1.1.1

Expected output:
    - For each requested record type: every matching record found,
      printed one per line, with its TTL.
    - If a record type doesn't exist for the domain (NXDOMAIN / NoAnswer),
      a clear message is shown instead of a crash.
    - A summary line showing total records found across all types queried.
"""

import argparse
import sys

try:
    import dns.resolver
except ImportError:
    print("[ERROR] Missing dependency 'dnspython'. Install it with: pip install dnspython", file=sys.stderr)
    sys.exit(1)


def query_records(domain: str, record_type: str, resolver: "dns.resolver.Resolver"):
    try:
        answers = resolver.resolve(domain, record_type)
        return [(str(rdata), answers.rrset.ttl) for rdata in answers]
    except dns.resolver.NXDOMAIN:
        print(f"[{record_type}] Domain does not exist: {domain}")
        return []
    except dns.resolver.NoAnswer:
        print(f"[{record_type}] No {record_type} records found for {domain}")
        return []
    except dns.exception.Timeout:
        print(f"[{record_type}] Query timed out")
        return []
    except Exception as e:
        print(f"[{record_type}] Error: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(description="Resolve DNS records (A, AAAA, MX, TXT, NS, CNAME, SOA) for a domain.")
    parser.add_argument("--domain", "-d", required=True, help="Domain name to query, e.g. example.com")
    parser.add_argument("--type", "-t", action="append", default=None,
                         choices=["A", "AAAA", "MX", "TXT", "NS", "CNAME", "SOA"],
                         help="Record type to query. Can be given multiple times (default: A, MX, TXT, NS).")
    parser.add_argument("--resolver", "-r", default=None,
                         help="Optional custom DNS resolver IP to query directly (e.g. 1.1.1.1 or 8.8.8.8).")
    args = parser.parse_args()

    record_types = args.type or ["A", "MX", "TXT", "NS"]

    resolver = dns.resolver.Resolver()
    if args.resolver:
        resolver.nameservers = [args.resolver]

    total_found = 0
    for record_type in record_types:
        print(f"\n=== {record_type} records for {args.domain} ===")
        records = query_records(args.domain, record_type, resolver)
        for value, ttl in records:
            print(f"  {value}  (TTL: {ttl}s)")
        total_found += len(records)

    print(f"\n=== Summary ===")
    print(f"Domain          : {args.domain}")
    print(f"Record types    : {', '.join(record_types)}")
    print(f"Resolver used   : {args.resolver or 'system default'}")
    print(f"Total records   : {total_found}")


if __name__ == "__main__":
    main()
