#!/usr/bin/env python3
"""
monitor_system_resources.py
---------------------------------
Displays live system resource usage: CPU, memory, disk, and network,
either once or continuously.

Requires: pip install psutil

Usage:
    python monitor_system_resources.py [--watch] [--interval 2]

Example:
    python monitor_system_resources.py
    python monitor_system_resources.py --watch --interval 5
"""

import argparse
import sys
import time
from datetime import datetime

try:
    import psutil
except ImportError:
    print("Error: the 'psutil' package is required.")
    print("Install it with: pip install -r requirements.txt")
    sys.exit(1)


def bytes_to_human(n: float) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def print_snapshot() -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    net = psutil.net_io_counters()

    print(f"[{timestamp}] System Resource Snapshot\n")

    print(f"CPU Usage:     {cpu_percent}%")
    print(f"CPU Per Core:  {cpu_per_core}")

    print(f"\nMemory:        {bytes_to_human(mem.used)} / {bytes_to_human(mem.total)} used ({mem.percent}%)")
    print(f"Swap:          {bytes_to_human(psutil.swap_memory().used)} / {bytes_to_human(psutil.swap_memory().total)} used")

    print(f"\nDisk (/):      {bytes_to_human(disk.used)} / {bytes_to_human(disk.total)} used ({disk.percent}%)")

    print(f"\nNetwork Sent:  {bytes_to_human(net.bytes_sent)}")
    print(f"Network Recv:  {bytes_to_human(net.bytes_recv)}")


def main():
    parser = argparse.ArgumentParser(description="Monitor system CPU, memory, disk, and network usage.")
    parser.add_argument("--watch", action="store_true", help="Continuously monitor instead of a single snapshot")
    parser.add_argument("--interval", type=int, default=2, help="Refresh interval in seconds when using --watch (default: 2)")
    args = parser.parse_args()

    if args.watch:
        print(f"Monitoring system resources every {args.interval} second(s). Press Ctrl+C to stop.\n")
        try:
            while True:
                print_snapshot()
                print("=" * 60)
                time.sleep(max(0, args.interval - 1))  # cpu_percent(interval=1) already waits 1s
        except KeyboardInterrupt:
            print("\nStopped monitoring.")
    else:
        print_snapshot()


if __name__ == "__main__":
    main()
