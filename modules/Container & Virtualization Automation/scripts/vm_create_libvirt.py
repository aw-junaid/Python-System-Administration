#!/usr/bin/env python3
"""
vm_create_libvirt.py
Provision a complete virtual machine (CPU, RAM, disk) through the libvirt
hypervisor API. Works with KVM/QEMU on Linux.

USAGE
    python vm_create_libvirt.py --name test-vm --vcpus 2 --memory-mb 2048 \
        --disk-path /var/lib/libvirt/images/test-vm.qcow2 --disk-size-gb 20 \
        --iso /var/lib/libvirt/images/ubuntu-22.04.iso

REQUIREMENTS
    - A working libvirt/KVM hypervisor host (Linux only). Install with:
        sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients virtinst
    - System libvirt development headers for the Python bindings:
        sudo apt install libvirt-dev
    - The user running this script should be in the 'libvirt' group,
      or you run it with sudo
    - pip install -r requirements.txt   (installs libvirt-python)
    - qemu-img available on PATH (used to create the disk image)

EXPECTED OUTPUT
    A raw disk image is created at --disk-path, the VM is defined and started,
    and the script prints:
        Disk image created: /var/lib/libvirt/images/test-vm.qcow2 (20G)
        Domain 'test-vm' defined and started (state=running)

CAUTION
    This script talks directly to your hypervisor and will create real disk
    images and VM definitions on the host. Double-check --disk-path and
    available disk space before running.
"""

import argparse
import subprocess
import sys

import libvirt

DOMAIN_XML_TEMPLATE = """
<domain type='kvm'>
  <name>{name}</name>
  <memory unit='MiB'>{memory_mb}</memory>
  <vcpu>{vcpus}</vcpu>
  <os>
    <type arch='x86_64'>hvm</type>
    <boot dev='cdrom'/>
    <boot dev='hd'/>
  </os>
  <features><acpi/><apic/></features>
  <devices>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2'/>
      <source file='{disk_path}'/>
      <target dev='vda' bus='virtio'/>
    </disk>
    {cdrom_xml}
    <interface type='network'>
      <source network='default'/>
      <model type='virtio'/>
    </interface>
    <graphics type='vnc' port='-1' autoport='yes'/>
    <console type='pty'/>
  </devices>
</domain>
"""

CDROM_XML_TEMPLATE = """
    <disk type='file' device='cdrom'>
      <driver name='qemu' type='raw'/>
      <source file='{iso_path}'/>
      <target dev='sda' bus='sata'/>
      <readonly/>
    </disk>
"""


def create_disk(disk_path, size_gb):
    subprocess.run(
        ["qemu-img", "create", "-f", "qcow2", disk_path, f"{size_gb}G"],
        check=True,
    )
    print(f"Disk image created: {disk_path} ({size_gb}G)")


def create_vm(args):
    create_disk(args.disk_path, args.disk_size_gb)

    cdrom_xml = CDROM_XML_TEMPLATE.format(iso_path=args.iso) if args.iso else ""
    domain_xml = DOMAIN_XML_TEMPLATE.format(
        name=args.name,
        memory_mb=args.memory_mb,
        vcpus=args.vcpus,
        disk_path=args.disk_path,
        cdrom_xml=cdrom_xml,
    )

    conn = libvirt.open(args.connect)
    if conn is None:
        print(f"Failed to open connection to {args.connect}")
        sys.exit(1)

    try:
        domain = conn.defineXML(domain_xml)
        domain.create()
        state, _ = domain.state()
        state_name = {1: "running", 3: "paused", 5: "shutoff"}.get(state, str(state))
        print(f"Domain '{args.name}' defined and started (state={state_name})")
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Create a VM via libvirt.")
    parser.add_argument("--name", required=True)
    parser.add_argument("--vcpus", type=int, default=2)
    parser.add_argument("--memory-mb", type=int, default=2048)
    parser.add_argument("--disk-path", required=True)
    parser.add_argument("--disk-size-gb", type=int, default=20)
    parser.add_argument("--iso", help="Path to installer ISO (optional)")
    parser.add_argument("--connect", default="qemu:///system", help="libvirt connection URI")
    args = parser.parse_args()
    create_vm(args)


if __name__ == "__main__":
    main()
