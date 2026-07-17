#!/usr/bin/env python3
"""
test_connectivity.py

Purpose:
    Test raw socket-level connectivity to specific host:port endpoints
    (Layer 4 / TCP). Distinct from ping_hosts.py (ICMP/L3) and
    scan_ports.py (broad port enumeration) -- this script is for
    checking a small, specific list of known endpoints you depend on,
    such as verifying a database, API, or mail server is reachable
    before/after a deployment or network change.

Usage:
    python test_connectivity.py --endpoint 8.8.8.8:53
    python test_connectivity.py --endpoint db.internal:5432 --endpoint api.example.com:443
    python test_connectivity.py --endpoint smtp.example.com:587 --timeout 5 --retries 3

Expected output:
    - For each endpoint: CONNECTED (with latency in ms) or FAILED
      (with the specific error, e.g. "Connection refused" or "timed out").
    - If --retries > 1, shows each attempt and reports success as soon
      as one attempt connects.
    - Final summary table + exit code 0 if all endpoints connected,
      1 if any failed (useful for readiness checks in CI/CD or cron).
"""

import argparse
import socket
import sys
import time


def parse_endpoint(endpoint: str):
    if ":" not in endpoint:
        raise ValueError(f"Endpoint must be in host:port format, got '{endpoint}'")
    host, port_str = endpoint.rsplit(":", 1)
    return host, int(port_str)


def test_endpoint(host: str, port: int, timeout: float, retries: int):
    last_error = None
    for attempt in range(1, retries + 1):
        start = time.time()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                sock.connect((host, port))
                latency_ms = (time.time() - start) * 1000
                return True, latency_ms, attempt, None
        except socket.timeout:
            last_error = "connection timed out"
        except ConnectionRefusedError:
            last_error = "connection refused"
        except socket.gaierror:
            last_error = "DNS resolution failed"
            break  # no point retrying an unresolvable host
        except OSError as e:
            last_error = str(e)
        if attempt < retries:
            time.sleep(1)
    return False, None, retries, last_error


def main():
    parser = argparse.ArgumentParser(description="Test TCP connectivity to specific host:port endpoints.")
    parser.add_argument("--endpoint", "-e", action="append", required=True,
                         help="Endpoint in host:port format, e.g. api.example.com:443. Can be given multiple times.")
    parser.add_argument("--timeout", "-t", type=float, default=3.0, help="Timeout per attempt in seconds (default: 3.0).")
    parser.add_argument("--retries", "-r", type=int, default=1, help="Number of attempts per endpoint (default: 1).")
    args = parser.parse_args()

    results = []
    for endpoint in args.endpoint:
        try:
            host, port = parse_endpoint(endpoint)
        except ValueError as e:
            print(f"[ERROR] {e}")
            results.append((endpoint, False, None, "invalid format"))
            continue

        print(f"\nTesting {endpoint} ...")
        success, latency_ms, attempts_used, error = test_endpoint(host, port, args.timeout, args.retries)
        if success:
            print(f"  -> CONNECTED after {attempts_used} attempt(s), {latency_ms:.1f} ms")
        else:
            print(f"  -> FAILED after {attempts_used} attempt(s): {error}")
        results.append((endpoint, success, latency_ms, error))

    print("\n=== Connectivity Summary ===")
    print(f"{'ENDPOINT':<30}{'STATUS':<12}{'DETAIL'}")
    for endpoint, success, latency_ms, error in results:
        status = "CONNECTED" if success else "FAILED"
        detail = f"{latency_ms:.1f} ms" if success else error
        print(f"{endpoint:<30}{status:<12}{detail}")

    sys.exit(1 if any(not success for _, success, _, _ in results) else 0)


if __name__ == "__main__":
    main()
