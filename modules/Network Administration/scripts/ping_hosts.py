#!/usr/bin/env python3
"""
ping_hosts.py

Purpose:
    Verify Layer-3 (network layer) connectivity to one or more hosts by
    sending ICMP echo requests (the same mechanism as the OS `ping`
    command). This script wraps the system `ping` utility via subprocess
    rather than crafting raw ICMP packets, so it works without root
    privileges on most systems.

Usage:
    python ping_hosts.py --host 8.8.8.8
    python ping_hosts.py --host google.com --host 1.1.1.1 --count 4
    python ping_hosts.py --host 192.168.1.1 --timeout 2

Expected output:
    - For each host: whether it is REACHABLE or UNREACHABLE, plus the
      average round-trip time (ms) parsed from the ping output when
      available.
    - A final summary table listing every host and its status.
    - Exit code 0 if ALL hosts responded, 1 if any host failed to
      respond (useful for scripting/monitoring/cron jobs).

Notes:
    - Requires the `ping` command to be available on the system
      (present by default on Windows, Linux, and macOS).
    - Some hosts/firewalls block ICMP; a host may be reachable via
      TCP even if it does not respond to ping (see check_host_availability.py).
"""

import argparse
import platform
import re
import subprocess
import sys


def ping_host(host: str, count: int, timeout: int):
    system = platform.system().lower()
    if system == "windows":
        cmd = ["ping", "-n", str(count), "-w", str(timeout * 1000), host]
    else:
        cmd = ["ping", "-c", str(count), "-W", str(timeout), host]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout * count + 5)
    except subprocess.TimeoutExpired:
        return False, None, "ping command timed out"
    except FileNotFoundError:
        return False, None, "ping command not found on this system"

    output = result.stdout
    reachable = result.returncode == 0

    avg_ms = None
    # Linux/macOS: "min/avg/max/mdev = 0.020/0.025/0.030/0.005 ms"
    match = re.search(r"=\s*[\d.]+/([\d.]+)/[\d.]+", output)
    if match:
        avg_ms = float(match.group(1))
    else:
        # Windows: "Average = 25ms"
        match = re.search(r"Average = (\d+)ms", output)
        if match:
            avg_ms = float(match.group(1))

    return reachable, avg_ms, output


def main():
    parser = argparse.ArgumentParser(description="Ping one or more hosts to verify L3 connectivity.")
    parser.add_argument("--host", "-H", action="append", required=True,
                         help="Hostname or IP to ping. Can be given multiple times.")
    parser.add_argument("--count", "-c", type=int, default=4, help="Number of echo requests to send (default: 4).")
    parser.add_argument("--timeout", "-t", type=int, default=2, help="Timeout in seconds per request (default: 2).")
    args = parser.parse_args()

    results = []
    for host in args.host:
        print(f"\nPinging {host} ({args.count} packets)...")
        reachable, avg_ms, output = ping_host(host, args.count, args.timeout)
        status = "REACHABLE" if reachable else "UNREACHABLE"
        rtt_str = f"{avg_ms:.2f} ms avg" if avg_ms is not None else "n/a"
        print(f"  -> {status} ({rtt_str})")
        results.append((host, status, rtt_str))

    print("\n=== Ping Summary ===")
    print(f"{'HOST':<30}{'STATUS':<15}{'AVG RTT'}")
    for host, status, rtt_str in results:
        print(f"{host:<30}{status:<15}{rtt_str}")

    any_failed = any(status == "UNREACHABLE" for _, status, _ in results)
    sys.exit(1 if any_failed else 0)


if __name__ == "__main__":
    main()
