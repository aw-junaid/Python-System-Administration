#!/usr/bin/env python3
"""
get_process_info.py

Purpose:
    Retrieve detailed information about a specific process by PID:
    name, status, CPU%, memory usage, executable path, start time,
    and command line.

Usage:
    python get_process_info.py <PID>
    python get_process_info.py 1234

    If no PID is given, this script prints info about its own process
    as a safe demo.

Expected Output:
    PID:          1234
    Name:         python3
    Status:       running
    CPU%:         0.3
    Memory (MB):  25.4
    Executable:   /usr/bin/python3
    Started:      2026-07-16 10:00:00
    Command line: python3 script.py

Caution:
    - Some fields (like executable path or command line) may be
      unavailable or restricted depending on OS permissions, returning
      "N/A" instead of raising an error.
    - Process information is a live snapshot; values like CPU% and
      memory will change moment to moment.
"""

import os
import sys
import datetime

try:
    import psutil
except ImportError:
    print("Error: this script requires 'psutil'. Install with:")
    print("    pip install -r requirements.txt")
    sys.exit(1)


def print_process_info(pid: int) -> None:
    try:
        proc = psutil.Process(pid)
        with proc.oneshot():
            name = proc.name()
            status = proc.status()
            cpu = proc.cpu_percent(interval=0.3)
            mem_mb = proc.memory_info().rss / (1024 * 1024)
            try:
                exe = proc.exe()
            except (psutil.AccessDenied, psutil.ZombieProcess):
                exe = "N/A"
            started = datetime.datetime.fromtimestamp(
                proc.create_time()
            ).strftime("%Y-%m-%d %H:%M:%S")
            try:
                cmdline = " ".join(proc.cmdline()) or "N/A"
            except (psutil.AccessDenied, psutil.ZombieProcess):
                cmdline = "N/A"

        print(f"PID:          {pid}")
        print(f"Name:         {name}")
        print(f"Status:       {status}")
        print(f"CPU%:         {cpu}")
        print(f"Memory (MB):  {mem_mb:.1f}")
        print(f"Executable:   {exe}")
        print(f"Started:      {started}")
        print(f"Command line: {cmdline}")
    except psutil.NoSuchProcess:
        print(f"Error: no process found with PID {pid}.")
    except psutil.AccessDenied:
        print(f"Error: access denied reading info for PID {pid}.")


def main():
    if len(sys.argv) > 1:
        pid = int(sys.argv[1])
    else:
        pid = os.getpid()
        print("No PID given; showing info for this script's own process.\n")
    print_process_info(pid)


if __name__ == "__main__":
    main()
