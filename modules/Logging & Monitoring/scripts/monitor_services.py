#!/usr/bin/env python3
"""
monitor_services.py
-----------------------
Checks whether specific processes/services (by name) are currently
running on the system. Useful for verifying that critical services
(e.g. nginx, mysql, sshd) haven't crashed. Requires `psutil`.

Usage:
    python3 monitor_services.py --services sshd,cron,nginx
"""

import argparse
import psutil


def is_running(process_name):
    for proc in psutil.process_iter(["name"]):
        try:
            if proc.info["name"] and process_name.lower() in proc.info["name"].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def check_services(service_list):
    print(f"Checking {len(service_list)} service(s)...\n")
    results = {}

    for service in service_list:
        running = is_running(service)
        results[service] = running
        status = "RUNNING" if running else "NOT RUNNING"
        symbol = "[OK]" if running else "[WARNING]"
        print(f"{symbol} {service}: {status}")

    down = [s for s, r in results.items() if not r]
    if down:
        print(f"\n{len(down)} service(s) are down: {', '.join(down)}")
    else:
        print("\nAll checked services are running.")

    return results


def main():
    parser = argparse.ArgumentParser(description="Check whether services/processes are running")
    parser.add_argument(
        "--services",
        default="sshd",
        help="Comma-separated list of process/service names to check",
    )
    args = parser.parse_args()

    service_list = [s.strip() for s in args.services.split(",")]
    check_services(service_list)


if __name__ == "__main__":
    main()
