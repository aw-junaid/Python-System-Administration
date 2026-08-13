#!/usr/bin/env python3
"""
installed_software.py
-----------------------
Queries the local package database to list installed software.

- Debian/Ubuntu systems: queries dpkg
- RHEL/Fedora/CentOS systems: queries rpm
- Falls back gracefully with a clear message if neither is present
  (e.g. on Windows or macOS, where this script does not apply).

Usage:
    python3 installed_software.py
    python3 installed_software.py --limit 50   # show only first 50 packages

Requires:
    No third-party packages. Uses only the Python standard library.
    Relies on the 'dpkg' or 'rpm' command-line tools being present
    on the host system (they are part of the OS, not pip-installable).
"""

import argparse
import shutil
import subprocess
import sys


def run_command(cmd):
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"[!] Command failed: {' '.join(cmd)}")
        print(e.stderr)
        return ""


def list_dpkg_packages(limit=None):
    print("[*] Detected dpkg (Debian/Ubuntu based system)\n")
    output = run_command(["dpkg-query", "-W", "-f=${Package} ${Version}\n"])
    lines = output.strip().splitlines()
    if limit:
        lines = lines[:limit]
    for line in lines:
        print(line)
    print(f"\nTotal packages shown: {len(lines)}")


def list_rpm_packages(limit=None):
    print("[*] Detected rpm (RHEL/Fedora/CentOS based system)\n")
    output = run_command(["rpm", "-qa", "--qf", "%{NAME} %{VERSION}-%{RELEASE}\n"])
    lines = output.strip().splitlines()
    if limit:
        lines = lines[:limit]
    for line in lines:
        print(line)
    print(f"\nTotal packages shown: {len(lines)}")


def main():
    parser = argparse.ArgumentParser(description="List installed software packages.")
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Limit the number of packages displayed"
    )
    args = parser.parse_args()

    print("=" * 60)
    print(" INSTALLED SOFTWARE")
    print("=" * 60)

    if shutil.which("dpkg-query"):
        list_dpkg_packages(args.limit)
    elif shutil.which("rpm"):
        list_rpm_packages(args.limit)
    else:
        print("[!] Neither dpkg nor rpm was found on this system.")
        print("    This script only supports Linux distributions that use")
        print("    dpkg (Debian/Ubuntu) or rpm (RHEL/Fedora/CentOS).")
        sys.exit(1)

    print("=" * 60)


if __name__ == "__main__":
    main()
