#!/usr/bin/env python3
"""
cpu_info.py
-----------
Prints CPU information: physical cores, logical threads, and current
frequency (per-core where available).

Usage:
    python3 cpu_info.py

Requires:
    pip install -r requirements.txt   (psutil)
"""

import platform
import sys

try:
    import psutil
except ImportError:
    print("[!] psutil is not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


def get_cpu_info():
    info = {}

    info["Processor"] = platform.processor() or "Unknown"
    info["Architecture"] = platform.machine()
    info["Physical cores"] = psutil.cpu_count(logical=False)
    info["Logical threads"] = psutil.cpu_count(logical=True)

    freq = psutil.cpu_freq()
    if freq:
        info["Current frequency (MHz)"] = round(freq.current, 2)
        info["Min frequency (MHz)"] = round(freq.min, 2) if freq.min else "N/A"
        info["Max frequency (MHz)"] = round(freq.max, 2) if freq.max else "N/A"
    else:
        info["Current frequency (MHz)"] = "Not available on this system"

    info["Overall CPU usage (%)"] = psutil.cpu_percent(interval=0.5)

    return info


def print_per_core_usage():
    print("\nPer-core usage (%):")
    usages = psutil.cpu_percent(interval=0.5, percpu=True)
    for i, usage in enumerate(usages):
        print(f"  Core {i}: {usage}%")


def main():
    print("=" * 50)
    print(" CPU INFORMATION")
    print("=" * 50)

    info = get_cpu_info()
    for key, value in info.items():
        print(f"{key:<28}: {value}")

    print_per_core_usage()
    print("=" * 50)


if __name__ == "__main__":
    main()
