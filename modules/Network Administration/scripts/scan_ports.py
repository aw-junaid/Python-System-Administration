#!/usr/bin/env python3
"""
scan_ports.py

Purpose:
    Enumerate open TCP ports on a host using a TCP "connect" scan
    (completes the full TCP handshake on each port, then closes the
    connection). This is a legitimate, low-privilege scanning technique
    -- it does not require raw sockets/root and does not attempt to
    exploit anything; it simply reports which ports accept connections.

    ONLY scan hosts and networks you own or have explicit written
    permission to test. Scanning systems without authorization may be
    illegal in your jurisdiction and can violate the target's
    acceptable-use policy.

Usage:
    python scan_ports.py --host 192.168.1.10 --ports 1-1024
    python scan_ports.py --host example.com --ports 22,80,443,3306
    python scan_ports.py --host 10.0.0.5 --ports 1-65535 --workers 200 --timeout 0.5

Expected output:
    - A line per OPEN port found, with the port number and the common
      service name for well-known ports (e.g. 22 -> ssh) when recognized.
    - A final summary: number of ports scanned, number open, and elapsed time.
    - If no ports are open (or host is unreachable/filtered), a message
      saying no open ports were found.
"""

import argparse
import concurrent.futures
import socket
import time


COMMON_PORTS = {
    21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns",
    80: "http", 110: "pop3", 143: "imap", 443: "https", 445: "smb",
    3306: "mysql", 3389: "rdp", 5432: "postgresql", 6379: "redis",
    8080: "http-alt", 27017: "mongodb",
}


def parse_ports(port_spec: str) -> list:
    ports = set()
    for part in port_spec.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            ports.update(range(int(start), int(end) + 1))
        elif part:
            ports.add(int(part))
    return sorted(ports)


def scan_one_port(host: str, port: int, timeout: float):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            return port, result == 0
    except socket.gaierror:
        return port, None  # DNS resolution failure, handled by caller
    except OSError:
        return port, False


def main():
    parser = argparse.ArgumentParser(description="TCP connect scan to enumerate open ports on a host.")
    parser.add_argument("--host", "-H", required=True, help="Target hostname or IP address.")
    parser.add_argument("--ports", "-p", default="1-1024",
                         help="Ports to scan: comma list, ranges, or both, e.g. '22,80,443' or '1-1024' (default: 1-1024).")
    parser.add_argument("--timeout", "-t", type=float, default=1.0, help="Per-port connect timeout in seconds (default: 1.0).")
    parser.add_argument("--workers", "-w", type=int, default=100, help="Number of concurrent worker threads (default: 100).")
    args = parser.parse_args()

    try:
        resolved_ip = socket.gethostbyname(args.host)
    except socket.gaierror:
        print(f"[ERROR] Could not resolve host: {args.host}")
        return

    ports = parse_ports(args.ports)
    print(f"Scanning {args.host} ({resolved_ip}) — {len(ports)} port(s), timeout={args.timeout}s, workers={args.workers}\n")

    start = time.time()
    open_ports = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(scan_one_port, resolved_ip, port, args.timeout): port for port in ports}
        for future in concurrent.futures.as_completed(futures):
            port, is_open = future.result()
            if is_open:
                service = COMMON_PORTS.get(port, "unknown")
                print(f"[OPEN] {port}/tcp ({service})")
                open_ports.append(port)

    elapsed = time.time() - start
    open_ports.sort()

    print("\n=== Scan Summary ===")
    print(f"Host          : {args.host} ({resolved_ip})")
    print(f"Ports scanned : {len(ports)}")
    print(f"Open ports    : {len(open_ports)} -> {open_ports if open_ports else 'none found'}")
    print(f"Elapsed time  : {elapsed:.2f}s")


if __name__ == "__main__":
    main()
