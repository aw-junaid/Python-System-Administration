#!/usr/bin/env python3
"""
gpu_info.py
------------
Detects NVIDIA/AMD GPU presence and reports VRAM usage.

- NVIDIA: uses the 'nvidia-smi' command-line tool (ships with the
  NVIDIA driver; not pip-installable).
- AMD: uses the 'rocm-smi' command-line tool if available.
- Fallback: lists GPU-like devices via 'lspci' on Linux if neither
  vendor tool is found (no VRAM usage in this case).

Usage:
    python3 gpu_info.py

Requires:
    No third-party Python packages. Relies on 'nvidia-smi',
    'rocm-smi', or 'lspci' being installed on the system (these are
    OS/driver-level tools, not pip packages).
"""

import shutil
import subprocess


def run_command(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        return None


def check_nvidia():
    if not shutil.which("nvidia-smi"):
        return False

    output = run_command([
        "nvidia-smi",
        "--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu",
        "--format=csv,noheader,nounits",
    ])

    if not output:
        return False

    print("[*] NVIDIA GPU(s) detected:\n")
    for i, line in enumerate(output.splitlines()):
        parts = [p.strip() for p in line.split(",")]
        if len(parts) == 5:
            name, mem_total, mem_used, mem_free, util = parts
            print(f"GPU {i}: {name}")
            print(f"  Total VRAM   : {mem_total} MB")
            print(f"  Used VRAM    : {mem_used} MB")
            print(f"  Free VRAM    : {mem_free} MB")
            print(f"  GPU Utilization: {util}%\n")
    return True


def check_amd():
    if not shutil.which("rocm-smi"):
        return False

    output = run_command(["rocm-smi", "--showmeminfo", "vram"])
    if not output:
        return False

    print("[*] AMD GPU(s) detected (rocm-smi):\n")
    print(output)
    return True


def check_lspci_fallback():
    if not shutil.which("lspci"):
        print("[!] No NVIDIA/AMD tool found, and 'lspci' is unavailable.")
        print("    Cannot detect GPU on this system.")
        return

    output = run_command(["lspci"])
    if not output:
        print("[!] Could not query PCI devices.")
        return

    gpu_lines = [
        line for line in output.splitlines()
        if "VGA" in line or "3D controller" in line
    ]

    if gpu_lines:
        print("[*] GPU device(s) found via lspci (no vendor tool for VRAM usage):\n")
        for line in gpu_lines:
            print(f"  {line}")
    else:
        print("[!] No GPU devices found via lspci.")


def main():
    print("=" * 60)
    print(" GPU INFORMATION")
    print("=" * 60)

    found = check_nvidia()
    found = check_amd() or found

    if not found:
        check_lspci_fallback()

    print("=" * 60)


if __name__ == "__main__":
    main()
