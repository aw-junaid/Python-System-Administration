#!/usr/bin/env python3
"""
monitor_cpu.py
------------------
Checks current CPU usage and warns if it exceeds a threshold
percentage. Requires the `psutil` library.

Usage:
    python3 monitor_cpu.py --threshold 85 --interval 1
"""

import argparse
import psutil


def check_cpu(threshold, interval):
    percent = psutil.cpu_percent(interval=interval)
    per_core = psutil.cpu_percent(interval=0.5, percpu=True)

    print(f"Overall CPU usage: {percent}%")
    print(f"Per-core usage: {per_core}")

    if percent >= threshold:
        print(f"[WARNING] CPU usage ({percent}%) exceeds threshold ({threshold}%)")
        return False
    else:
        print(f"[OK] CPU usage is within the {threshold}% threshold")
        return True


def main():
    parser = argparse.ArgumentParser(description="Monitor CPU usage")
    parser.add_argument("--threshold", type=float, default=85.0, help="Warning threshold percent")
    parser.add_argument("--interval", type=float, default=1.0, help="Sampling interval in seconds")
    args = parser.parse_args()

    check_cpu(args.threshold, args.interval)


if __name__ == "__main__":
    main()
