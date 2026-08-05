#!/usr/bin/env python3
"""
send_signal_to_process.py

Purpose:
    Send a specific OS signal (e.g. SIGTERM, SIGKILL, SIGHUP, SIGINT)
    to a running process by PID.

Usage:
    python send_signal_to_process.py --pid 1234 --signal SIGTERM
    python send_signal_to_process.py --pid 1234 --signal SIGKILL

    If no arguments are given, this script launches a short-lived demo
    process and sends it SIGTERM as an example.

Expected Output:
    Sending SIGTERM to PID 1234...
    Signal sent successfully.

Caution:
    - SIGKILL (signal 9) cannot be caught or ignored by the target
      process -- it terminates immediately without any chance to clean
      up open files or save state. Prefer SIGTERM first, and only use
      SIGKILL if the process does not respond.
    - Sending signals to a process you don't own, or a system-critical
      process, can require elevated privileges and can destabilize
      your system -- verify the PID with monitor_processes.py or
      get_process_info.py first.
    - Available signals differ between Linux/macOS (POSIX signals) and
      Windows (which has a much more limited signal set). This script
      targets POSIX systems primarily.
"""

import signal
import subprocess
import sys
import time

# Common signal name -> signal object mapping
SIGNAL_MAP = {
    "SIGTERM": signal.SIGTERM,
    "SIGKILL": getattr(signal, "SIGKILL", signal.SIGTERM),  # SIGKILL not on Windows
    "SIGINT": signal.SIGINT,
    "SIGHUP": getattr(signal, "SIGHUP", signal.SIGTERM),    # SIGHUP not on Windows
}


def send_signal(pid: int, sig_name: str) -> None:
    sig = SIGNAL_MAP.get(sig_name.upper())
    if sig is None:
        print(f"Error: unknown signal '{sig_name}'. "
              f"Supported: {', '.join(SIGNAL_MAP.keys())}")
        return
    try:
        import os
        print(f"Sending {sig_name.upper()} to PID {pid}...")
        os.kill(pid, sig)
        print("Signal sent successfully.")
    except ProcessLookupError:
        print(f"Error: no process found with PID {pid}.")
    except PermissionError:
        print(f"Error: permission denied sending signal to PID {pid}.")


def parse_args():
    args = sys.argv[1:]
    pid = None
    sig_name = None
    i = 0
    while i < len(args):
        if args[i] == "--pid" and i + 1 < len(args):
            pid = int(args[i + 1]); i += 2
        elif args[i] == "--signal" and i + 1 < len(args):
            sig_name = args[i + 1]; i += 2
        else:
            i += 1
    return pid, sig_name


def main():
    pid, sig_name = parse_args()
    if pid is None or sig_name is None:
        print("No arguments given, running demo mode.")
        proc = subprocess.Popen("sleep 30", shell=True)
        print(f"Launched demo process PID: {proc.pid}")
        time.sleep(1)
        pid, sig_name = proc.pid, "SIGTERM"
    send_signal(pid, sig_name)


if __name__ == "__main__":
    main()
