#!/usr/bin/env python3
"""
set_cpu_affinity.py

Purpose:
    View and set which CPU cores a given process is allowed to run on
    (its "CPU affinity").

Usage:
    python set_cpu_affinity.py --pid 1234 --cpus 0,1
    python set_cpu_affinity.py --pid 1234           (view current affinity only)

    If no arguments are given, this script shows the CPU affinity of
    its own process as a safe demo (view-only, no changes made).

Expected Output:
    Current CPU affinity for PID 1234: [0, 1, 2, 3]
    Setting CPU affinity to: [0, 1]
    New CPU affinity for PID 1234: [0, 1]

Caution:
    - Restricting a process to fewer CPU cores can reduce its
      performance; only do this if you have a specific reason (e.g.
      isolating a noisy process, testing, or NUMA tuning).
    - CPU affinity control is NOT supported on macOS via psutil; this
      script's set-affinity feature works on Linux and Windows.
    - Setting affinity on a process you don't own may require elevated
      privileges.
"""

import os
import sys

try:
    import psutil
except ImportError:
    print("Error: this script requires 'psutil'. Install with:")
    print("    pip install -r requirements.txt")
    sys.exit(1)


def show_affinity(pid: int):
    try:
        proc = psutil.Process(pid)
        affinity = proc.cpu_affinity()
        print(f"Current CPU affinity for PID {pid}: {affinity}")
        return affinity
    except psutil.NoSuchProcess:
        print(f"Error: no process found with PID {pid}.")
    except psutil.AccessDenied:
        print(f"Error: access denied reading affinity for PID {pid}.")
    except AttributeError:
        print("Error: cpu_affinity() is not supported on this OS (e.g. macOS).")
    return None


def set_affinity(pid: int, cpus: list):
    try:
        proc = psutil.Process(pid)
        print(f"Setting CPU affinity to: {cpus}")
        proc.cpu_affinity(cpus)
        print(f"New CPU affinity for PID {pid}: {proc.cpu_affinity()}")
    except psutil.NoSuchProcess:
        print(f"Error: no process found with PID {pid}.")
    except psutil.AccessDenied:
        print(f"Error: access denied setting affinity for PID {pid}.")
    except AttributeError:
        print("Error: cpu_affinity() is not supported on this OS (e.g. macOS).")
    except ValueError as e:
        print(f"Error: invalid CPU list - {e}")


def parse_args():
    args = sys.argv[1:]
    pid = None
    cpus = None
    i = 0
    while i < len(args):
        if args[i] == "--pid" and i + 1 < len(args):
            pid = int(args[i + 1]); i += 2
        elif args[i] == "--cpus" and i + 1 < len(args):
            cpus = [int(c) for c in args[i + 1].split(",")]; i += 2
        else:
            i += 1
    return pid, cpus


def main():
    pid, cpus = parse_args()
    if pid is None:
        pid = os.getpid()
        print("No --pid given; showing affinity for this script's own process.\n")

    show_affinity(pid)
    if cpus:
        set_affinity(pid, cpus)


if __name__ == "__main__":
    main()
