#!/usr/bin/env python3
"""
vm_clone.py
Duplicate an entire libvirt VM instance, including its disks and settings,
for rapid environment replication. Wraps the battle-tested `virt-clone`
utility so disk copying and MAC address regeneration are handled correctly.

USAGE
    python vm_clone.py --original test-vm --clone test-vm-copy
    python vm_clone.py --original test-vm --clone test-vm-copy \
        --new-disk-path /var/lib/libvirt/images/test-vm-copy.qcow2

REQUIREMENTS
    - A working libvirt/KVM hypervisor host (Linux only)
    - virt-clone (part of virtinst) installed:
        sudo apt install virtinst
    - Sufficient disk space to hold a full copy of the source VM's disk(s)
    - pip install -r requirements.txt

EXPECTED OUTPUT
    virt-clone's own progress output while it copies the disk image(s),
    followed by:
        Clone complete: 'test-vm-copy' cloned from 'test-vm'

CAUTION
    The source VM should be shut off before cloning to avoid copying a disk
    that is still being written to.
"""

import argparse
import subprocess
import sys


def clone_vm(args):
    cmd = ["virt-clone", "--original", args.original, "--name", args.clone]
    if args.new_disk_path:
        cmd += ["--file", args.new_disk_path]
    else:
        cmd += ["--auto-clone"]

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        print(f"Clone failed with exit code {result.returncode}")
        sys.exit(result.returncode)

    print(f"Clone complete: '{args.clone}' cloned from '{args.original}'")


def main():
    parser = argparse.ArgumentParser(description="Clone a libvirt VM using virt-clone.")
    parser.add_argument("--original", required=True, help="Name of the source VM")
    parser.add_argument("--clone", required=True, help="Name for the new cloned VM")
    parser.add_argument("--new-disk-path", help="Explicit path for the cloned disk (optional; auto-generated if omitted)")
    args = parser.parse_args()
    clone_vm(args)


if __name__ == "__main__":
    main()
