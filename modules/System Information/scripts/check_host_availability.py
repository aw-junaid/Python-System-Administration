#!/usr/bin/env python3
"""
check_host_availability.py

Purpose:
    Combined health check for a host: performs an ICMP ping AND a TCP
    probe against one or more specific ports. Useful because some hosts
    block ICMP entirely but are still reachable on the service ports you
    actually care about (e.g. a web server that blocks ping but serves
    on port 443).

Usage:
    python check_host_availability.py --host example.com --port 80 --port 443
    python check_host_availability.py --host 10.0.0.5 --port 22 --no-ping

Expected output:
    - Ping result: REACHABLE / UNREACHABLE / SKIPPED (if --no-ping).
    - For each port checked: OPEN or CLOSED/FILTERED with response time.
    - An overall verdict: "UP" if ping succeeds OR at least one port is
      open; "DOWN" if ping fails AND all checked ports are closed.
    - Exit code 0 if verdict is UP, 1 if DOWN (useful for monitoring scripts).
"""

import argparse
import platform
import socket
import subprocess
import sys
import time


def ping_once(host: str, timeout: int) -> bool:
    system = platform.system().lower()
    if system == "windows":
        cmd = ["ping", "-n", "1", "-w", str(timeout * 1000), host]
    else:
        cmd = ["ping", "-c", "1", "-W", str(timeout), host]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 3)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_port(host: str, port: int, timeout: float):
    start = time.time()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            elapsed_ms = (time.time() - start) * 1000
            return result == 0, elapsed_ms
    except OSError:
        return False, (time.time() - start) * 1000


def main():
    parser = argparse.ArgumentParser(description="Combined ping + TCP port health check for a host.")
    parser.add_argument("--host", "-H", required=True, help="Hostname or IP to check.")
    parser.add_argument("--port", "-p", action="append", type=int, default=[],
                         help="TCP port to probe. Can be given multiple times.")
    parser.add_argument("--timeout", "-t", type=float, default=2.0, help="Timeout in seconds (default: 2.0).")
    parser.add_argument("--no-ping", action="store_true", help="Skip the ICMP ping check.")
    args = parser.parse_args()

    print(f"=== Checking availability of {args.host} ===\n")

    ping_ok = None
    if not args.no_ping:
        ping_ok = ping_once(args.host, int(args.timeout))
        print(f"[PING] {'REACHABLE' if ping_ok else 'UNREACHABLE'}")
    else:
        print("[PING] SKIPPED (--no-ping)")

    port_results = []
    for port in args.port:
        is_open, elapsed_ms = check_port(args.host, port, args.timeout)
        status = "OPEN" if is_open else "CLOSED/FILTERED"
        print(f"[PORT {port}] {status} ({elapsed_ms:.1f} ms)")
        port_results.append((port, is_open))

    any_port_open = any(is_open for _, is_open in port_results)
    overall_up = bool(ping_ok) or any_port_open

    print("\n=== Verdict ===")
    print(f"Host        : {args.host}")
    print(f"Ping        : {'n/a' if ping_ok is None else ('OK' if ping_ok else 'FAIL')}")
    print(f"Open ports  : {[p for p, ok in port_results if ok] or 'none'}")
    print(f"Overall     : {'UP' if overall_up else 'DOWN'}")

    sys.exit(0 if overall_up else 1)


if __name__ == "__main__":
    main()
