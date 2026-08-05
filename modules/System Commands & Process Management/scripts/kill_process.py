#!/usr/bin/env python3
"""
kill_process.py

Purpose:
    Terminate (kill) a running process by its PID.

Usage:
    python kill_process.py <PID>
    python kill_process.py 1234

    If no PID is given, the script lists a few current processes so you
    can pick a valid PID to try (nothing is killed in this demo mode).

Expected Output:
    Success: "Process <PID> terminated successfully."
    Failure: an error message explaining why (not found, access denied).

Caution:
    - THIS IS DESTRUCTIVE. Killing the wrong PID can crash applications,
      corrupt in-progress work, or destabilize your system if you kill
      a critical system process.
    - Double check the PID with monitor_processes.py (in this same
      folder) before running this script for real.
    - Killing processes owned by another user or root may require
      elevated privileges (e.g. running with sudo on Linux/macOS).
"""

import sys

try:
    import psutil
except ImportError:
    print("Error: this script requires 'psutil'. Install with:")
    print("    pip install -r requirements.txt")
    sys.exit(1)


def kill_process(pid: int) -> None:
    try:
        proc = psutil.Process(pid)
        name = proc.name()
        proc.terminate()
        proc.wait(timeout=5)
        print(f"Process {pid} ({name}) terminated successfully.")
    except psutil.NoSuchProcess:
        print(f"Error: no process found with PID {pid}.")
    except psutil.AccessDenied:
        print(f"Error: access denied when trying to kill PID {pid}. "
              f"Try running with elevated privileges.")
    except psutil.TimeoutExpired:
        print(f"Warning: process {pid} did not terminate in time; "
              f"it may need to be force-killed.")


def list_sample_processes(limit: int = 10) -> None:
    print("No PID given. Here are some currently running processes:\n")
    print(f"{'PID':<8}{'NAME'}")
    count = 0
    for proc in psutil.process_iter(['pid', 'name']):
        print(f"{proc.info['pid']:<8}{proc.info['name']}")
        count += 1
        if count >= limit:
            break
    print("\nRun again as: python kill_process.py <PID>")


def main():
    if len(sys.argv) > 1:
        try:
            pid = int(sys.argv[1])
        except ValueError:
            print("Error: PID must be an integer.")
            sys.exit(1)
        kill_process(pid)
    else:
        list_sample_processes()


if __name__ == "__main__":
    main()
