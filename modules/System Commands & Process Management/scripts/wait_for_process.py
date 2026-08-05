#!/usr/bin/env python3
"""
wait_for_process.py

Purpose:
    Wait (block) until a specified process finishes, then report how
    long it ran and its exit status if available.

Usage:
    python wait_for_process.py --pid 1234
    python wait_for_process.py --pid 1234 --timeout 30

    If no PID is given, this script launches a short demo process
    itself and waits for it to complete.

Expected Output:
    Waiting for PID 1234 to finish...
    Process 1234 finished after 4.2 seconds.

Caution:
    - If you pass the PID of a process NOT started by this script
      (e.g. a process from another shell), this script can only detect
      that it disappeared -- it cannot retrieve that process's original
      exit code (this is an OS limitation for non-child processes).
    - Without --timeout, this script will wait indefinitely for a
      long-running or hung process; consider setting a --timeout for
      unattended scripts.
"""

import subprocess
import sys
import time

try:
    import psutil
except ImportError:
    print("Error: this script requires 'psutil'. Install with:")
    print("    pip install -r requirements.txt")
    sys.exit(1)


def wait_for_pid(pid: int, timeout: float = None) -> None:
    try:
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        print(f"Error: no process found with PID {pid}.")
        return

    print(f"Waiting for PID {pid} to finish...")
    start = time.time()
    try:
        exit_code = proc.wait(timeout=timeout)
        elapsed = time.time() - start
        print(f"Process {pid} finished after {elapsed:.1f} seconds. "
              f"Exit status: {exit_code}")
    except psutil.TimeoutExpired:
        print(f"Timed out after {timeout} seconds; process {pid} is still running.")


def parse_args():
    args = sys.argv[1:]
    pid = None
    timeout = None
    i = 0
    while i < len(args):
        if args[i] == "--pid" and i + 1 < len(args):
            pid = int(args[i + 1]); i += 2
        elif args[i] == "--timeout" and i + 1 < len(args):
            timeout = float(args[i + 1]); i += 2
        else:
            i += 1
    return pid, timeout


def main():
    pid, timeout = parse_args()
    if pid is None:
        print("No --pid given, running demo mode: launching a short-lived process.")
        proc = subprocess.Popen("sleep 3", shell=True)
        pid = proc.pid
    wait_for_pid(pid, timeout)


if __name__ == "__main__":
    main()
