#!/usr/bin/env python3
"""
launch_background_process.py

Purpose:
    Launch a command as a background process (non-blocking) and
    immediately return control to the script, printing the new PID.

Usage:
    python launch_background_process.py "sleep 30"
    python launch_background_process.py "ping -c 10 127.0.0.1"

    If no command is given, a safe built-in demo runs (a 5-second sleep).

Expected Output:
    Started background process with PID: <number>
    (the parent script exits immediately without waiting)

Caution:
    - The background process keeps running even after this script exits.
      Use monitor_processes.py or kill_process.py (from this same folder)
      to check on or stop it later, using the printed PID.
    - On Windows, backgrounding behaves differently; this script targets
      Linux/macOS (POSIX) behavior primarily but will still launch the
      process non-blocking on Windows via Popen.
"""

import subprocess
import sys


def launch_background(command: str) -> int:
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print(f"Started background process with PID: {process.pid}")
    print("The parent script is not waiting for it to finish.")
    return process.pid


def main():
    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
    else:
        command = "sleep 5"
    launch_background(command)


if __name__ == "__main__":
    main()
