#!/usr/bin/env python3
"""
os_version.py
--------------
Prints the operating system release name and build number.

Usage:
    python3 os_version.py

Requires:
    pip install -r requirements.txt   (uses 'distro' on Linux for
    accurate distribution name/version; falls back to the standard
    library if 'distro' is not installed)
"""

import platform


def get_linux_release_info():
    try:
        import distro
        return {
            "Distribution": distro.name(pretty=True),
            "Version": distro.version(),
            "Codename": distro.codename() or "N/A",
        }
    except ImportError:
        # Fallback: parse /etc/os-release manually
        info = {}
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        info[k] = v.strip('"')
            return {
                "Distribution": info.get("PRETTY_NAME", "Unknown"),
                "Version": info.get("VERSION_ID", "Unknown"),
                "Codename": info.get("VERSION_CODENAME", "N/A"),
            }
        except FileNotFoundError:
            return {"Distribution": "Unknown", "Version": "Unknown", "Codename": "N/A"}


def main():
    print("=" * 50)
    print(" OPERATING SYSTEM VERSION")
    print("=" * 50)

    system = platform.system()
    print(f"{'System':<15}: {system}")
    print(f"{'Release':<15}: {platform.release()}")
    print(f"{'Version/Build':<15}: {platform.version()}")
    print(f"{'Machine':<15}: {platform.machine()}")

    if system == "Linux":
        info = get_linux_release_info()
        print("\nDistribution details:")
        for key, value in info.items():
            print(f"  {key:<13}: {value}")

    print("=" * 50)


if __name__ == "__main__":
    main()
