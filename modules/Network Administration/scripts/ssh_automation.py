#!/usr/bin/env python3
"""
ssh_automation.py

Purpose:
    Execute one or more shell commands on a remote Linux server over
    SSH, using the `paramiko` library. Useful for automating routine
    admin tasks (checking disk space, restarting a service, pulling
    logs) across one or many servers without manually opening a
    terminal session to each.

    Requires: pip install paramiko  (see requirements.txt)

Usage:
    # Password auth, single command
    python ssh_automation.py --host 10.0.0.5 --user admin --password mypass --command "df -h"

    # Key-based auth, multiple commands (run in order, same session)
    python ssh_automation.py --host server.example.com --user deploy --key ~/.ssh/id_rsa \
        --command "cd /srv/app && git pull" --command "sudo systemctl restart app"

    # Run the same command across multiple hosts
    python ssh_automation.py --host web1.example.com --host web2.example.com \
        --user admin --key ~/.ssh/id_rsa --command "uptime"

Expected output:
    - Per host: connection confirmation, then for each command its
      STDOUT, STDERR (if any), and exit status.
    - Final summary listing which hosts succeeded (all commands exit 0)
      vs failed, so you can spot problems across a fleet at a glance.
    - Non-zero script exit code if any command on any host failed.

CAUTION:
    Passing --password on the command line can leave it visible in your
    shell history / process list. Prefer --key (SSH key auth) or omit
    --password to be prompted securely.
"""

import argparse
import getpass
import sys

try:
    import paramiko
except ImportError:
    print("[ERROR] Missing dependency 'paramiko'. Install it with: pip install paramiko", file=sys.stderr)
    sys.exit(1)


def run_commands_on_host(host: str, port: int, user: str, password: str, key_path: str,
                          commands: list, timeout: int) -> bool:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print(f"\n=== Connecting to {host}:{port} as {user} ===")
    try:
        if key_path:
            # key_filename lets paramiko auto-detect the key type (RSA/Ed25519/ECDSA/etc.)
            client.connect(hostname=host, port=port, username=user, key_filename=key_path,
                            passphrase=password, timeout=timeout)
        else:
            client.connect(hostname=host, port=port, username=user, password=password, timeout=timeout)
    except (paramiko.AuthenticationException, paramiko.SSHException, OSError) as e:
        print(f"[ERROR] Could not connect to {host}: {e}", file=sys.stderr)
        return False

    all_ok = True
    for command in commands:
        print(f"\n$ {command}")
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        exit_status = stdout.channel.recv_exit_status()
        out = stdout.read().decode("utf-8", errors="ignore")
        err = stderr.read().decode("utf-8", errors="ignore")
        if out:
            print(out.rstrip())
        if err:
            print(f"[STDERR] {err.rstrip()}", file=sys.stderr)
        print(f"[exit status: {exit_status}]")
        if exit_status != 0:
            all_ok = False

    client.close()
    return all_ok


def main():
    parser = argparse.ArgumentParser(description="Execute remote commands on Linux servers via SSH (paramiko).")
    parser.add_argument("--host", "-H", action="append", required=True,
                         help="Remote hostname or IP. Can be given multiple times to run on several hosts.")
    parser.add_argument("--port", type=int, default=22, help="SSH port (default: 22).")
    parser.add_argument("--user", "-u", required=True, help="SSH username.")
    parser.add_argument("--password", "-p", default=None,
                         help="SSH password (or private key passphrase if --key is used). Omit to be prompted.")
    parser.add_argument("--key", "-k", default=None, help="Path to a private key file for key-based auth.")
    parser.add_argument("--command", "-c", action="append", required=True,
                         help="Command to run. Can be given multiple times; commands run in order.")
    parser.add_argument("--timeout", "-t", type=int, default=15, help="Connection/command timeout in seconds (default: 15).")
    args = parser.parse_args()

    password = args.password
    if password is None and not args.key:
        password = getpass.getpass("SSH password: ")

    results = {}
    for host in args.host:
        success = run_commands_on_host(host, args.port, args.user, password, args.key, args.command, args.timeout)
        results[host] = success

    print("\n=== SSH Automation Summary ===")
    for host, success in results.items():
        print(f"{host:<30}{'SUCCESS' if success else 'FAILED'}")

    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
