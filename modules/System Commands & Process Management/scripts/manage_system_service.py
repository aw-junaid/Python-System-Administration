#!/usr/bin/env python3
"""
manage_system_service.py

Purpose:
    Start, stop, restart, or check the status of a system service,
    using the appropriate native tool for the current OS
    (systemctl on Linux, sc/net on Windows, launchctl on macOS - Linux
    is the primary supported target here via systemctl).

Usage:
    python manage_system_service.py status ssh
    python manage_system_service.py start ssh
    python manage_system_service.py stop ssh
    python manage_system_service.py restart ssh

    If no arguments are given, this script only prints usage help (it
    will NOT touch any real service without an explicit service name).

Expected Output:
    Running: systemctl status ssh
    <systemctl output describing the service state>

Caution:
    - THIS CAN AFFECT REAL SYSTEM SERVICES. Stopping or restarting the
      wrong service (e.g. your SSH daemon, display manager, or network
      manager) can disrupt your system or lock you out of a remote
      session. Double-check the service name before running start/
      stop/restart.
    - Managing services typically requires elevated privileges; on
      Linux/macOS you may need to run this script with sudo, e.g.:
          sudo python manage_system_service.py restart nginx
    - This script currently targets Linux's systemctl. On macOS/Windows
      you would need to adapt the underlying command (launchctl / sc).
"""

import platform
import subprocess
import sys


def manage_service(action: str, service_name: str) -> None:
    system = platform.system()
    if system == "Linux":
        command = f"systemctl {action} {service_name}"
    elif system == "Darwin":
        print("Note: macOS uses launchctl, which has a different syntax "
              "than systemctl. This demo will attempt a best-effort command.")
        command = f"sudo launchctl {action} {service_name}"
    elif system == "Windows":
        action_map = {"start": "start", "stop": "stop", "status": "query", "restart": "restart"}
        command = f"sc {action_map.get(action, action)} {service_name}"
    else:
        print(f"Unsupported OS: {system}")
        return

    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(result.stdout if result.stdout else "(no output)")
    if result.stderr.strip():
        print("STDERR:", result.stderr.strip())
    print(f"Exit Code: {result.returncode}")


def print_usage():
    print("Usage: python manage_system_service.py <start|stop|restart|status> <service_name>")
    print("Example: python manage_system_service.py status ssh")
    print("No service name was given, so nothing was executed.")


def main():
    if len(sys.argv) >= 3:
        action = sys.argv[1].lower()
        service_name = sys.argv[2]
        if action not in ("start", "stop", "restart", "status"):
            print(f"Unknown action '{action}'. Use start, stop, restart, or status.")
            return
        manage_service(action, service_name)
    else:
        print_usage()


if __name__ == "__main__":
    main()
