#!/usr/bin/env python3
"""
daemonize_process.py

Purpose:
    Demonstrate turning the current script into a background "daemon"
    process on POSIX systems (Linux/macOS) using the classic double-fork
    technique, detaching it from the controlling terminal.

Usage:
    python daemonize_process.py

    This will daemonize itself, then (as the daemon) write a line to
    /tmp/daemonize_process_demo.log every 2 seconds, 5 times, then exit.

Expected Output:
    (Immediately in your terminal:)
    Daemonizing... check /tmp/daemonize_process_demo.log for output.
    (your shell prompt returns right away)

    (Contents of /tmp/daemonize_process_demo.log after a few seconds:)
    Daemon started, PID <number>
    Tick 1
    Tick 2
    Tick 3
    Tick 4
    Tick 5
    Daemon exiting.

Caution:
    - THIS SCRIPT IS POSIX-ONLY (Linux/macOS). It uses os.fork(), which
      does not exist on Windows; running it there will raise an
      AttributeError.
    - Daemonizing detaches the process from your terminal completely;
      you cannot Ctrl+C it. To stop it early, find its PID (printed
      inside the log file) and use kill_process.py from this same
      folder.
    - This is a minimal educational example. Production-grade daemons
      typically also redirect stdin/stdout/stderr to /dev/null or log
      files and set a proper working directory/umask, which this
      script does in simplified form.
"""

import os
import sys
import time

LOG_FILE = "/tmp/daemonize_process_demo.log"


def daemonize():
    if sys.platform.startswith("win"):
        print("Error: daemonize_process.py requires a POSIX OS (Linux/macOS). "
              "os.fork() is not available on Windows.")
        sys.exit(1)

    # First fork
    pid = os.fork()
    if pid > 0:
        # Parent process exits, letting the child continue detached
        print(f"Daemonizing... check {LOG_FILE} for output.")
        sys.exit(0)

    os.setsid()  # start a new session, detaching from controlling terminal

    # Second fork (prevents daemon from acquiring a controlling terminal again)
    pid = os.fork()
    if pid > 0:
        sys.exit(0)

    # Now running as the daemon process
    with open(LOG_FILE, "a") as f:
        f.write(f"Daemon started, PID {os.getpid()}\n")
        f.flush()
        for i in range(1, 6):
            time.sleep(2)
            f.write(f"Tick {i}\n")
            f.flush()
        f.write("Daemon exiting.\n")

    os._exit(0)


def main():
    daemonize()


if __name__ == "__main__":
    main()
