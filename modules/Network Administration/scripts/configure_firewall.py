#!/usr/bin/env python3
"""
configure_firewall.py

Purpose:
    Manage basic firewall rules (allow/block a port, list current rules)
    on the local machine, using the native firewall tool for the
    detected OS:
      - Linux  -> iptables (via subprocess)
      - Windows -> netsh advfirewall (via subprocess)

    This script does not reimplement firewall logic -- it builds and
    runs the same commands you would type yourself, so you can always
    see exactly what will be executed before it runs.

Usage (Linux, requires sudo/root):
    sudo python3 configure_firewall.py --action allow --port 22 --protocol tcp
    sudo python3 configure_firewall.py --action block --port 8080 --protocol tcp
    sudo python3 configure_firewall.py --action list
    sudo python3 configure_firewall.py --action remove --port 8080 --protocol tcp --direction block

Usage (Windows, requires Administrator terminal):
    python configure_firewall.py --action allow --port 3389 --protocol tcp
    python configure_firewall.py --action block --port 445 --protocol tcp
    python configure_firewall.py --action list

Expected output:
    - Prints the exact underlying command being run (iptables/netsh)
      before executing it, for transparency.
    - allow/block/remove: confirms whether the rule command succeeded,
      showing the tool's own output/error text.
    - list: prints the current rule set as reported by iptables/netsh.
    - Non-zero exit code if the underlying command fails (e.g. not run
      with sufficient privileges) or the platform is unsupported.

CAUTION:
    - Modifying firewall rules can lock you out of a remote machine
      (e.g. blocking port 22/3389 you're connected through). Double-
      check --port and --protocol before running, especially with
      --action block on a machine you're remotely connected to.
    - Requires root/sudo on Linux and an Administrator/elevated
      terminal on Windows -- the underlying tools enforce this, this
      script does not escalate privileges for you.
    - Rules on Linux made directly via iptables are typically NOT
      persisted across reboots unless you also save them with your
      distro's mechanism (e.g. `iptables-save`, `netfilter-persistent`).
"""

import argparse
import platform
import subprocess
import sys


def run_command(cmd: list):
    print(f"[RUNNING] {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        print(f"[ERROR] Command not found: {cmd[0]}. Is the firewall tool installed and on PATH?", file=sys.stderr)
        sys.exit(1)

    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)

    return result.returncode


def linux_allow_block(action: str, port: int, protocol: str):
    chain_action = "ACCEPT" if action == "allow" else "DROP"
    cmd = ["iptables", "-A", "INPUT", "-p", protocol, "--dport", str(port), "-j", chain_action]
    return run_command(cmd)


def linux_remove(direction: str, port: int, protocol: str):
    chain_action = "ACCEPT" if direction == "allow" else "DROP"
    cmd = ["iptables", "-D", "INPUT", "-p", protocol, "--dport", str(port), "-j", chain_action]
    return run_command(cmd)


def linux_list():
    return run_command(["iptables", "-L", "INPUT", "-n", "-v", "--line-numbers"])


def windows_allow_block(action: str, port: int, protocol: str):
    rule_name = f"{'Allow' if action == 'allow' else 'Block'}_Port_{port}_{protocol.upper()}"
    net_action = "allow" if action == "allow" else "block"
    cmd = [
        "netsh", "advfirewall", "firewall", "add", "rule",
        f"name={rule_name}", "dir=in", f"action={net_action}",
        f"protocol={protocol.upper()}", f"localport={port}",
    ]
    return run_command(cmd)


def windows_remove(direction: str, port: int, protocol: str):
    rule_name = f"{'Allow' if direction == 'allow' else 'Block'}_Port_{port}_{protocol.upper()}"
    cmd = ["netsh", "advfirewall", "firewall", "delete", "rule", f"name={rule_name}"]
    return run_command(cmd)


def windows_list():
    return run_command(["netsh", "advfirewall", "firewall", "show", "rule", "name=all"])


def main():
    parser = argparse.ArgumentParser(description="Manage basic firewall rules via iptables (Linux) or netsh (Windows).")
    parser.add_argument("--action", required=True, choices=["allow", "block", "remove", "list"],
                         help="allow/block: add a rule. remove: delete a previously added allow/block rule. list: show current rules.")
    parser.add_argument("--port", "-p", type=int, default=None, help="Port number (required for allow/block/remove).")
    parser.add_argument("--protocol", default="tcp", choices=["tcp", "udp"], help="Protocol (default: tcp).")
    parser.add_argument("--direction", choices=["allow", "block"], default=None,
                         help="For --action remove: which previously added rule type to remove (allow or block).")
    args = parser.parse_args()

    system = platform.system().lower()
    if system not in ("linux", "windows"):
        print(f"[ERROR] Unsupported platform: {system}. This script supports Linux (iptables) and Windows (netsh) only.",
              file=sys.stderr)
        sys.exit(1)

    if args.action in ("allow", "block", "remove") and args.port is None:
        print("[ERROR] --port is required for allow/block/remove actions.", file=sys.stderr)
        sys.exit(1)

    if args.action == "remove" and args.direction is None:
        print("[ERROR] --direction (allow or block) is required for --action remove, "
              "to identify which rule to delete.", file=sys.stderr)
        sys.exit(1)

    print(f"Platform detected: {system}\n")

    if args.action == "list":
        rc = linux_list() if system == "linux" else windows_list()
    elif args.action in ("allow", "block"):
        rc = (linux_allow_block(args.action, args.port, args.protocol) if system == "linux"
              else windows_allow_block(args.action, args.port, args.protocol))
    else:  # remove
        rc = (linux_remove(args.direction, args.port, args.protocol) if system == "linux"
              else windows_remove(args.direction, args.port, args.protocol))

    print(f"\n=== Result ===")
    print(f"Action  : {args.action}")
    print(f"Status  : {'SUCCESS' if rc == 0 else 'FAILED'}")
    print("(If FAILED, confirm you are running with root/sudo (Linux) or an elevated/Administrator terminal (Windows).)")

    sys.exit(rc)


if __name__ == "__main__":
    main()
