#!/usr/bin/env python3
"""
execute_startup_script.py

Purpose:
    Demonstrate/execute a "startup script" pattern: run one or more
    setup commands in sequence when a system or application starts,
    stopping early if any command fails.

Usage:
    python execute_startup_script.py

    This runs a demo list of startup commands defined inside the script
    (edit the STARTUP_COMMANDS list below to customize for your use
    case, e.g. checking directories exist, setting env, etc.).

Expected Output:
    [Startup 1/3] echo Checking environment...
    STDOUT: Checking environment...
    [Startup 2/3] echo Creating temp directory...
    STDOUT: Creating temp directory...
    [Startup 3/3] echo Startup complete.
    STDOUT: Startup complete.
    All startup steps completed successfully.

Caution:
    - This script stops at the FIRST failing command (non-zero exit
      code) to avoid continuing in a broken state, similar to how a
      real startup/init script should behave.
    - This is a demonstration of the startup-script pattern in Python.
      To have your OS actually run this at boot, register it with your
      OS's own mechanism: systemd (Linux), Task Scheduler (Windows), or
      launchd (macOS) — see manage_system_services.py for a related
      example.
"""

import subprocess
import sys

# Edit this list to define your own startup sequence.
STARTUP_COMMANDS = [
    "echo Checking environment...",
    "echo Creating temp directory...",
    "echo Startup complete."
]


def run_startup_sequence(commands) -> bool:
    total = len(commands)
    for i, command in enumerate(commands, start=1):
        print(f"[Startup {i}/{total}] {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.stdout.strip():
            print("STDOUT:", result.stdout.strip())
        if result.stderr.strip():
            print("STDERR:", result.stderr.strip())
        if result.returncode != 0:
            print(f"Startup step {i} failed with exit code {result.returncode}. Stopping.")
            return False
    print("All startup steps completed successfully.")
    return True


def main():
    success = run_startup_sequence(STARTUP_COMMANDS)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
