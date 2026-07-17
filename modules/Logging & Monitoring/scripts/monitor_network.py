#!/usr/bin/env python3
"""
monitor_network.py
----------------------
Monitors network traffic (bytes sent/received) over a sampling
interval and reports throughput. Requires the `psutil` library.

Usage:
    python3 monitor_network.py --interval 2
"""

import argparse
import time
import psutil


def monitor(interval):
    old = psutil.net_io_counters()
    print(f"Sampling network traffic over {interval} second(s)...")
    time.sleep(interval)
    new = psutil.net_io_counters()

    sent_bytes = new.bytes_sent - old.bytes_sent
    recv_bytes = new.bytes_recv - old.bytes_recv

    sent_rate = sent_bytes / interval / 1024  # KB/s
    recv_rate = recv_bytes / interval / 1024  # KB/s

    print(f"Upload:   {sent_rate:.2f} KB/s ({sent_bytes} bytes total)")
    print(f"Download: {recv_rate:.2f} KB/s ({recv_bytes} bytes total)")

    # Per-interface stats
    print("\nPer-interface status:")
    stats = psutil.net_if_stats()
    for iface, info in stats.items():
        status = "UP" if info.isup else "DOWN"
        print(f"  {iface}: {status}, speed={info.speed}Mbps")


def main():
    parser = argparse.ArgumentParser(description="Monitor network throughput")
    parser.add_argument("--interval", type=float, default=2.0, help="Sampling interval in seconds")
    args = parser.parse_args()

    monitor(args.interval)


if __name__ == "__main__":
    main()
