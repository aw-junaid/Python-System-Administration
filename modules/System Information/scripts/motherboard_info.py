#!/usr/bin/env python3
"""
motherboard_info.py
---------------------
Retrieves motherboard (baseboard) information: manufacturer,
product name, version, and serial number.

- On Linux: reads from /sys/class/dmi/id/ (serial number requires
  root privileges to read).
- On Windows: uses WMI via the 'wmi' package (optional dependency).

Usage:
    python3 motherboard_info.py
    sudo python3 motherboard_info.py     # on Linux, to see the serial number

Requires:
    pip install -r requirements.txt   (installs 'wmi' on Windows only;
    no extra packages needed on Linux)
"""

import platform
import sys

DMI_PATH = "/sys/class/dmi/id"

LINUX_BOARD_FIELDS = {
    "Manufacturer": "board_vendor",
    "Product name": "board_name",
    "Version": "board_version",
    "Serial number": "board_serial",
}


def read_dmi_file(filename):
    try:
        with open(f"{DMI_PATH}/{filename}", "r") as f:
            return f.read().strip()
    except PermissionError:
        return "Permission denied (try running with sudo)"
    except FileNotFoundError:
        return "Not available"


def get_linux_board_info():
    info = {}
    for label, filename in LINUX_BOARD_FIELDS.items():
        info[label] = read_dmi_file(filename)
    return info


def get_windows_board_info():
    try:
        import wmi
    except ImportError:
        print("[!] The 'wmi' package is required on Windows.")
        print("    Run: pip install -r requirements.txt")
        sys.exit(1)

    c = wmi.WMI()
    info = {}
    for board in c.Win32_BaseBoard():
        info["Manufacturer"] = board.Manufacturer
        info["Product name"] = board.Product
        info["Version"] = board.Version
        info["Serial number"] = board.SerialNumber
    return info


def main():
    print("=" * 50)
    print(" MOTHERBOARD INFORMATION")
    print("=" * 50)

    system = platform.system()

    if system == "Linux":
        info = get_linux_board_info()
    elif system == "Windows":
        info = get_windows_board_info()
    else:
        print(f"[!] This script does not support {system}.")
        print("    Supported: Linux, Windows.")
        sys.exit(1)

    for key, value in info.items():
        print(f"{key:<15}: {value}")

    print("=" * 50)


if __name__ == "__main__":
    main()
