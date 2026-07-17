#!/usr/bin/env python3
"""
ansible_integration.py
------------------------------
Runs Ansible playbooks and generates dynamic inventory files from Python,
wrapping the 'ansible-playbook' and 'ansible' CLI tools via subprocess.

Requires: Ansible installed (pip install ansible, or via your OS package manager).
Platform: Linux/macOS (Ansible does not run natively on Windows as a control node;
          use WSL on Windows).

Usage:
    python ansible_integration.py run-playbook <playbook.yml> [--inventory inventory.ini] [--extra-vars "key=value"]
    python ansible_integration.py generate-inventory <output_file> --hosts host1,host2,host3 [--group webservers]
    python ansible_integration.py ping <inventory.ini>

Example:
    python ansible_integration.py generate-inventory inventory.ini --hosts 10.0.0.1,10.0.0.2 --group webservers
    python ansible_integration.py ping inventory.ini
    python ansible_integration.py run-playbook deploy.yml --inventory inventory.ini
"""

import argparse
import shutil
import subprocess
import sys


def check_ansible_installed(command: str = "ansible-playbook"):
    if not shutil.which(command):
        print(f"Error: '{command}' not found on PATH.")
        print("Install Ansible with: pip install ansible  (or via your OS package manager)")
        sys.exit(1)


def generate_inventory(output_file: str, hosts: str, group: str) -> None:
    host_list = [h.strip() for h in hosts.split(",") if h.strip()]

    if not host_list:
        print("Error: no valid hosts provided.")
        sys.exit(1)

    lines = [f"[{group}]"]
    lines.extend(host_list)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Generated inventory file: {output_file}")
    print(f"Group '{group}' with {len(host_list)} host(s):")
    for h in host_list:
        print(f"  - {h}")


def run_playbook(playbook: str, inventory: str, extra_vars: str) -> None:
    check_ansible_installed("ansible-playbook")

    cmd = ["ansible-playbook", playbook]
    if inventory:
        cmd.extend(["-i", inventory])
    if extra_vars:
        cmd.extend(["--extra-vars", extra_vars])

    print(f"Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd)

    if result.returncode != 0:
        print(f"\nAnsible playbook exited with code {result.returncode}.")
        sys.exit(result.returncode)

    print("\nPlaybook run completed successfully.")


def ping_hosts(inventory: str) -> None:
    check_ansible_installed("ansible")

    cmd = ["ansible", "all", "-i", inventory, "-m", "ping"]
    print(f"Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd)

    if result.returncode != 0:
        print(f"\nSome hosts may be unreachable (exit code {result.returncode}).")
        sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser(description="Run Ansible playbooks and manage inventory from Python.")
    subparsers = parser.add_subparsers(dest="action", required=True)

    p = subparsers.add_parser("run-playbook", help="Run an Ansible playbook")
    p.add_argument("playbook", help="Path to the playbook YAML file")
    p.add_argument("--inventory", default=None, help="Path to an inventory file")
    p.add_argument("--extra-vars", default=None, help="Extra variables, e.g. 'key=value key2=value2'")

    p = subparsers.add_parser("generate-inventory", help="Generate a simple INI-style inventory file")
    p.add_argument("output_file", help="Path to write the inventory file")
    p.add_argument("--hosts", required=True, help="Comma-separated list of hostnames/IPs")
    p.add_argument("--group", default="all", help="Inventory group name (default: all)")

    p = subparsers.add_parser("ping", help="Ping all hosts in an inventory using the Ansible 'ping' module")
    p.add_argument("inventory", help="Path to the inventory file")

    args = parser.parse_args()

    if args.action == "run-playbook":
        run_playbook(args.playbook, args.inventory, args.extra_vars)
    elif args.action == "generate-inventory":
        generate_inventory(args.output_file, args.hosts, args.group)
    elif args.action == "ping":
        ping_hosts(args.inventory)


if __name__ == "__main__":
    main()
