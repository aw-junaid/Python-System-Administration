#!/usr/bin/env python3
"""
detect_resource_exhaustion.py
-----------------------------------
Continuously monitors CPU, memory, and disk usage and alerts (prints a
warning) when any of them crosses a configurable threshold — helping you
catch resource exhaustion before it causes an outage.

Requires: pip install psutil

Usage:
    python detect_resource_exhaustion.py [--cpu 90] [--memory 90] [--disk 90] [--interval 5]

Example:
    python detect_resource_exhaustion.py
    python detect_resource_exhaustion.py --cpu 80 --memory 85 --disk 95 --interval 10
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


def check_thresholds(cpu_limit: float, memory_limit: float, disk_limit: float) -> list:
    alerts = []

    cpu_percent = psutil.cpu_percent(interval=1)
    if cpu_percent >= cpu_limit:
        alerts.append(f"CPU usage is {cpu_percent}% (threshold: {cpu_limit}%)")

    mem = psutil.virtual_memory()
    if mem.percent >= memory_limit:
        alerts.append(f"Memory usage is {mem.percent}% (threshold: {memory_limit}%)")

    disk = psutil.disk_usage("/")
    if disk.percent >= disk_limit:
        alerts.append(f"Disk usage is {disk.percent}% (threshold: {disk_limit}%)")

    return alerts


def main():
    parser = argparse.ArgumentParser(description="Detect resource exhaustion (CPU, memory, disk) and alert.")
    parser.add_argument("--cpu", type=float, default=90, help="CPU usage percent threshold (default: 90)")
    parser.add_argument("--memory", type=float, default=90, help="Memory usage percent threshold (default: 90)")
    parser.add_argument("--disk", type=float, default=90, help="Disk usage percent threshold (default: 90)")
    parser.add_argument("--interval", type=int, default=5, help="Check interval in seconds (default: 5)")
    parser.add_argument("--once", action="store_true", help="Check once instead of continuously monitoring")
    args = parser.parse_args()

    if args.once:
        alerts = check_thresholds(args.cpu, args.memory, args.disk)
        if alerts:
            print("RESOURCE EXHAUSTION DETECTED:")
            for a in alerts:
                print(f"  - {a}")
            sys.exit(1)
        else:
            print("All resources are within normal thresholds.")
        return

    print(f"Monitoring for resource exhaustion every {args.interval} second(s).")
    print(f"Thresholds -> CPU: {args.cpu}%, Memory: {args.memory}%, Disk: {args.disk}%")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            alerts = check_thresholds(args.cpu, args.memory, args.disk)

            if alerts:
                print(f"[{timestamp}] ALERT — resource exhaustion detected:")
                for a in alerts:
                    print(f"  - {a}")
            else:
                print(f"[{timestamp}] OK — all resources within thresholds.")

            time.sleep(max(0, args.interval - 1))
    except KeyboardInterrupt:
        print("\nStopped monitoring.")


if __name__ == "__main__":
    main()
