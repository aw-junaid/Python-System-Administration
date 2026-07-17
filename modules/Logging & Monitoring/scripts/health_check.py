#!/usr/bin/env python3
"""
health_check.py
-------------------
A combined system health check script: CPU, RAM, disk, and key
services, all in one report. Exits with a non-zero status code if
any check fails a threshold - handy for cron jobs or CI health
gates. Requires `psutil`.

Usage:
    python3 health_check.py --cpu-threshold 85 --mem-threshold 80 \
        --disk-threshold 80 --disk-path / --services sshd,cron
"""

import argparse
import sys
import psutil


def run_health_check(cpu_threshold, mem_threshold, disk_threshold, disk_path, services):
    print("=" * 50)
    print("SYSTEM HEALTH CHECK")
    print("=" * 50)

    problems = []

    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_ok = cpu_percent < cpu_threshold
    print(f"CPU usage: {cpu_percent}% - {'OK' if cpu_ok else 'WARNING'}")
    if not cpu_ok:
        problems.append(f"CPU usage high: {cpu_percent}%")

    # Memory
    mem = psutil.virtual_memory()
    mem_ok = mem.percent < mem_threshold
    print(f"Memory usage: {mem.percent}% - {'OK' if mem_ok else 'WARNING'}")
    if not mem_ok:
        problems.append(f"Memory usage high: {mem.percent}%")

    # Disk
    disk = psutil.disk_usage(disk_path)
    disk_ok = disk.percent < disk_threshold
    print(f"Disk usage ({disk_path}): {disk.percent}% - {'OK' if disk_ok else 'WARNING'}")
    if not disk_ok:
        problems.append(f"Disk usage high: {disk.percent}%")

    # Services
    for service in services:
        running = any(
            proc.info["name"] and service.lower() in proc.info["name"].lower()
            for proc in psutil.process_iter(["name"])
        )
        print(f"Service '{service}': {'RUNNING' if running else 'NOT RUNNING'}")
        if not running:
            problems.append(f"Service down: {service}")

    print("=" * 50)
    if problems:
        print(f"HEALTH CHECK FAILED - {len(problems)} issue(s) found:")
        for p in problems:
            print(f"  - {p}")
        return False
    else:
        print("HEALTH CHECK PASSED - all systems normal")
        return True


def main():
    parser = argparse.ArgumentParser(description="Run a combined system health check")
    parser.add_argument("--cpu-threshold", type=float, default=85.0)
    parser.add_argument("--mem-threshold", type=float, default=80.0)
    parser.add_argument("--disk-threshold", type=float, default=80.0)
    parser.add_argument("--disk-path", default="/")
    parser.add_argument("--services", default="sshd", help="Comma-separated service names")
    args = parser.parse_args()

    services = [s.strip() for s in args.services.split(",")]

    healthy = run_health_check(
        args.cpu_threshold,
        args.mem_threshold,
        args.disk_threshold,
        args.disk_path,
        services,
    )

    sys.exit(0 if healthy else 1)


if __name__ == "__main__":
    main()
