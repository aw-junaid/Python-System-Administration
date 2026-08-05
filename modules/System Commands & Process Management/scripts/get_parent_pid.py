#!/usr/bin/env python3
"""
get_parent_pid.py

Purpose:
    Retrieve the Parent Process ID (PPID) of a given process, or of
    this script itself if no PID is given.

Usage:
    python get_parent_pid.py <PID>
    python get_parent_pid.py 1234

    If no PID is given, this script prints its own PID and PPID as a
    safe demo.

Expected Output:
    PID:          1234
    Parent PID:   1000
    Parent Name:  bash

Caution:
    - This script only reads information; it makes no system changes.
    - If the parent process has already exited (an "orphaned" child
      process), the parent PID may show as 1 (Linux, adopted by init/
      systemd) or may raise an error depending on OS/timing.
"""

import os
import sys

try:
    import psutil
except ImportError:
    print("Error: this script requires 'psutil'. Install with:")
    print("    pip install -r requirements.txt")
    sys.exit(1)


def get_parent_pid(pid: int) -> None:
    try:
        proc = psutil.Process(pid)
        ppid = proc.ppid()
        print(f"PID:          {pid}")
        print(f"Parent PID:   {ppid}")
        try:
            parent_name = psutil.Process(ppid).name()
            print(f"Parent Name:  {parent_name}")
        except psutil.NoSuchProcess:
            print("Parent Name:  (parent process no longer exists)")
    except psutil.NoSuchProcess:
        print(f"Error: no process found with PID {pid}.")
    except psutil.AccessDenied:
        print(f"Error: access denied reading PID {pid}.")


def main():
    if len(sys.argv) > 1:
        pid = int(sys.argv[1])
    else:
        pid = os.getpid()
        print("No PID given; showing info for this script's own process.\n")
    get_parent_pid(pid)


if __name__ == "__main__":
    main()
