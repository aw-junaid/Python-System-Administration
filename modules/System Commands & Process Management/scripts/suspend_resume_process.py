#!/usr/bin/env python3
"""
suspend_resume_process.py

Purpose:
    Suspend (pause) a running process and later resume it, by PID.

Usage:
    python suspend_resume_process.py --suspend <PID>
    python suspend_resume_process.py --resume <PID>

    If no arguments are given, a safe built-in demo runs: it launches a
    dummy process, suspends it, waits, then resumes it.

Expected Output:
    Process <PID> suspended.
    ... (later) ...
    Process <PID> resumed.

Caution:
    - A suspended process stops using CPU but stays in memory; it does
      NOT save its state to disk or release resources like open network
      connections, which may time out while suspended.
    - Suspend/resume signals (SIGSTOP/SIGCONT) are POSIX (Linux/macOS)
      concepts. On Windows, psutil emulates this via a different
      mechanism; behavior may vary by process type.
    - Do not suspend critical system processes; this can hang your
      session or make the system unresponsive.
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


def suspend(pid: int) -> None:
    try:
        proc = psutil.Process(pid)
        proc.suspend()
        print(f"Process {pid} suspended.")
    except psutil.NoSuchProcess:
        print(f"Error: no process found with PID {pid}.")
    except psutil.AccessDenied:
        print(f"Error: access denied suspending PID {pid}.")


def resume(pid: int) -> None:
    try:
        proc = psutil.Process(pid)
        proc.resume()
        print(f"Process {pid} resumed.")
    except psutil.NoSuchProcess:
        print(f"Error: no process found with PID {pid}.")
    except psutil.AccessDenied:
        print(f"Error: access denied resuming PID {pid}.")


def main():
    args = sys.argv[1:]

    if "--suspend" in args:
        idx = args.index("--suspend")
        pid = int(args[idx + 1])
        suspend(pid)
    elif "--resume" in args:
        idx = args.index("--resume")
        pid = int(args[idx + 1])
        resume(pid)
    else:
        # Demo mode
        print("No arguments given, running demo mode.")
        proc = subprocess.Popen("sleep 30", shell=True)
        print(f"Launched demo process PID: {proc.pid}")
        time.sleep(1)
        suspend(proc.pid)
        time.sleep(2)
        resume(proc.pid)
        proc.terminate()


if __name__ == "__main__":
    main()
