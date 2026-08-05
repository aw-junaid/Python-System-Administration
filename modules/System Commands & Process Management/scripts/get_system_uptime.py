#!/usr/bin/env python3
"""
get_system_uptime.py

Purpose:
    Calculate and print how long the system has been running since its
    last boot (uptime), in a human-readable format.

Usage:
    python get_system_uptime.py

Expected Output:
    System Boot Time: 2026-07-14 08:15:32
    Uptime: 2 day(s), 3 hour(s), 12 minute(s)

Caution:
    - Requires the third-party 'psutil' library (see requirements.txt).
    - This script only reads information; it makes no system changes.
    - In virtual machines or containers, boot time may reflect when the
      VM/container itself started, not the underlying physical host.
"""

import sys
import time
import datetime

try:
    import psutil
except ImportError:
    print("Error: this script requires 'psutil'. Install with:")
    print("    pip install -r requirements.txt")
    sys.exit(1)


def get_uptime() -> None:
    boot_timestamp = psutil.boot_time()
    boot_time = datetime.datetime.fromtimestamp(boot_timestamp)
    now = datetime.datetime.now()
    uptime_seconds = (now - boot_time).total_seconds()

    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)

    print(f"System Boot Time: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Uptime: {int(days)} day(s), {int(hours)} hour(s), {int(minutes)} minute(s)")


def main():
    get_uptime()


if __name__ == "__main__":
    main()
