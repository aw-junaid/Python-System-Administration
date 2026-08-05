#!/usr/bin/env python3
"""
monitor_processes.py

Purpose:
    List currently running processes with basic info: PID, name,
    CPU usage %, and memory usage %.

Usage:
    python monitor_processes.py
    python monitor_processes.py --filter python

Expected Output:
    A table like:
    PID     NAME                 CPU%     MEM%
    1234    python3              1.2      0.5
    5678    chrome               15.3     4.2
    ...

Caution:
    - Requires the third-party 'psutil' library (see requirements.txt).
    - CPU% on the first call may read as 0.0 for each process; this is
      normal for psutil, which needs a short interval between two
      samples to compute accurate CPU usage (this script handles that
      automatically with a brief warm-up).
    - Listing all system processes may include processes owned by other
      users, which you may not have permission to inspect fully.
"""

import sys
import time

try:
    import psutil
except ImportError:
    print("Error: this script requires 'psutil'. Install with:")
    print("    pip install -r requirements.txt")
    sys.exit(1)


def monitor(filter_name: str = None) -> None:
    # Warm-up call so cpu_percent readings are meaningful
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    time.sleep(0.5)

    print(f"{'PID':<8}{'NAME':<25}{'CPU%':<10}{'MEM%':<10}")
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            name = proc.info['name'] or "unknown"
            if filter_name and filter_name.lower() not in name.lower():
                continue
            cpu = proc.cpu_percent(interval=None)
            mem = proc.memory_percent()
            print(f"{proc.info['pid']:<8}{name:<25}{cpu:<10.1f}{mem:<10.2f}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue


def main():
    filter_name = None
    if "--filter" in sys.argv:
        idx = sys.argv.index("--filter")
        if idx + 1 < len(sys.argv):
            filter_name = sys.argv[idx + 1]
    monitor(filter_name)


if __name__ == "__main__":
    main()
