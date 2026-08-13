#!/usr/bin/env python3
"""
bios_info.py
------------
Retrieves BIOS information: vendor, version, release date, and
(where permitted) serial numbers.

- On Linux: reads from /sys/class/dmi/id/ (some fields, like the
  system serial number, require root privileges to read).
- On Windows: uses WMI via the 'wmi' package (optional dependency).

Usage:
    python3 bios_info.py
    sudo python3 bios_info.py     # on Linux, to see serial numbers

Requires:
    pip install -r requirements.txt   (installs 'wmi' on Windows only;
    no extra packages needed on Linux)
"""

import platform
import sys


DMI_PATH = "/sys/class/dmi/id"

LINUX_BIOS_FIELDS = {
    "Vendor": "bios_vendor",
    "Version": "bios_version",
    "Release date": "bios_date",
    "BIOS revision": "bios_release",
}


def read_dmi_file(filename):
    try:
        with open(f"{DMI_PATH}/{filename}", "r") as f:
            return f.read().strip()
    except PermissionError:
        return "Permission denied (try running with sudo)"
    except FileNotFoundError:
        return "Not available"


def get_linux_bios_info():
    info = {}
    for label, filename in LINUX_BIOS_FIELDS.items():
        info[label] = read_dmi_file(filename)
    return info


def get_windows_bios_info():
    try:
        import wmi
    except ImportError:
        print("[!] The 'wmi' package is required on Windows.")
        print("    Run: pip install -r requirements.txt")
        sys.exit(1)

    c = wmi.WMI()
    info = {}
    for bios in c.Win32_BIOS():
        info["Vendor"] = bios.Manufacturer
        info["Version"] = bios.Version
        info["Release date"] = bios.ReleaseDate
        info["Serial number"] = bios.SerialNumber
    return info


def main():
    print("=" * 50)
    print(" BIOS INFORMATION")
    print("=" * 50)

    system = platform.system()

    if system == "Linux":
        info = get_linux_bios_info()
    elif system == "Windows":
        info = get_windows_bios_info()
    else:
        print(f"[!] This script does not support {system}.")
        print("    Supported: Linux, Windows.")
        sys.exit(1)

    for key, value in info.items():
        print(f"{key:<15}: {value}")

    print("=" * 50)


if __name__ == "__main__":
    main()
