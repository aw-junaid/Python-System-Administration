#!/usr/bin/env python3
"""
vm_snapshot.py
Capture, list, and restore point-in-time snapshots of a libvirt VM, useful
for testing and rollback scenarios.

USAGE
    python vm_snapshot.py create --domain test-vm --name before-update
    python vm_snapshot.py list --domain test-vm
    python vm_snapshot.py revert --domain test-vm --name before-update
    python vm_snapshot.py delete --domain test-vm --name before-update

REQUIREMENTS
    - A working libvirt/KVM hypervisor host (Linux only)
    - System libvirt development headers:
        sudo apt install libvirt-dev
    - pip install -r requirements.txt   (installs libvirt-python)
    - The target domain must already exist (see vm_create_libvirt.py)

EXPECTED OUTPUT
    create  -> "Snapshot 'before-update' created for domain 'test-vm'."
    list    -> a list of snapshot names for the domain
    revert  -> "Domain 'test-vm' reverted to snapshot 'before-update'."
    delete  -> "Snapshot 'before-update' deleted."

CAUTION
    Internal (default) snapshots are stored inside the qcow2 disk file itself
    and require the VM's disk to use the qcow2 format.
"""

import argparse
import sys

import libvirt

SNAPSHOT_XML_TEMPLATE = """
<domainsnapshot>
  <name>{name}</name>
  <description>Snapshot created by vm_snapshot.py</description>
</domainsnapshot>
"""


def get_domain(conn, name):
    try:
        return conn.lookupByName(name)
    except libvirt.libvirtError:
        print(f"Domain '{name}' not found.")
        sys.exit(1)


def create_snapshot(conn, args):
    domain = get_domain(conn, args.domain)
    xml = SNAPSHOT_XML_TEMPLATE.format(name=args.name)
    domain.snapshotCreateXML(xml, 0)
    print(f"Snapshot '{args.name}' created for domain '{args.domain}'.")


def list_snapshots(conn, args):
    domain = get_domain(conn, args.domain)
    names = domain.snapshotListNames()
    if not names:
        print(f"No snapshots found for domain '{args.domain}'.")
        return
    for n in names:
        print(n)


def revert_snapshot(conn, args):
    domain = get_domain(conn, args.domain)
    snapshot = domain.snapshotLookupByName(args.name, 0)
    domain.revertToSnapshot(snapshot, 0)
    print(f"Domain '{args.domain}' reverted to snapshot '{args.name}'.")


def delete_snapshot(conn, args):
    domain = get_domain(conn, args.domain)
    snapshot = domain.snapshotLookupByName(args.name, 0)
    snapshot.delete(0)
    print(f"Snapshot '{args.name}' deleted.")


def main():
    parser = argparse.ArgumentParser(description="Manage libvirt VM snapshots.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create")
    p_create.add_argument("--domain", required=True)
    p_create.add_argument("--name", required=True)
    p_create.set_defaults(func=create_snapshot)

    p_list = sub.add_parser("list")
    p_list.add_argument("--domain", required=True)
    p_list.set_defaults(func=list_snapshots)

    p_revert = sub.add_parser("revert")
    p_revert.add_argument("--domain", required=True)
    p_revert.add_argument("--name", required=True)
    p_revert.set_defaults(func=revert_snapshot)

    p_delete = sub.add_parser("delete")
    p_delete.add_argument("--domain", required=True)
    p_delete.add_argument("--name", required=True)
    p_delete.set_defaults(func=delete_snapshot)

    parser.add_argument("--connect", default="qemu:///system", help="libvirt connection URI")
    args = parser.parse_args()

    conn = libvirt.open(args.connect)
    if conn is None:
        print(f"Failed to open connection to {args.connect}")
        sys.exit(1)
    try:
        args.func(conn, args)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
