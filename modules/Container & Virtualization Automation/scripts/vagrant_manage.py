#!/usr/bin/env python3
"""
vagrant_manage.py
Control Vagrant development environments programmatically: spin up,
provision, halt, or destroy Vagrant boxes.

USAGE
    python vagrant_manage.py up --dir ./my-vagrant-project
    python vagrant_manage.py status --dir ./my-vagrant-project
    python vagrant_manage.py provision --dir ./my-vagrant-project
    python vagrant_manage.py halt --dir ./my-vagrant-project
    python vagrant_manage.py destroy --dir ./my-vagrant-project --force

REQUIREMENTS
    - Vagrant installed and on PATH (https://www.vagrantup.com/downloads)
    - A hypervisor provider installed (VirtualBox, libvirt, etc.)
    - A Vagrantfile present in --dir
    - pip install -r requirements.txt   (installs python-vagrant)

EXPECTED OUTPUT
    up         -> Vagrant's own boot log, ending with "Environment is up."
    status     -> current machine status, e.g. "default: running"
    provision  -> provisioner output, ending with "Provisioning complete."
    halt       -> "Environment halted."
    destroy    -> "Environment destroyed."
"""

import argparse

import vagrant


def up(v, args):
    v.up(provision=args.provision)
    print("Environment is up.")


def status(v, args):
    for s in v.status():
        print(f"{s.name}: {s.state}")


def provision(v, args):
    v.provision()
    print("Provisioning complete.")


def halt(v, args):
    v.halt()
    print("Environment halted.")


def destroy(v, args):
    v.destroy()
    print("Environment destroyed.")


def main():
    parser = argparse.ArgumentParser(description="Manage Vagrant environments programmatically.")
    parser.add_argument("command", choices=["up", "status", "provision", "halt", "destroy"])
    parser.add_argument("--dir", required=True, help="Path to the directory containing the Vagrantfile")
    parser.add_argument("--provision", action="store_true", help="Run provisioners when bringing the machine up")
    parser.add_argument("--force", action="store_true", help="(kept for CLI familiarity; python-vagrant destroy is non-interactive)")
    args = parser.parse_args()

    v = vagrant.Vagrant(root=args.dir, quiet_stdout=False, quiet_stderr=False)

    dispatch = {
        "up": up,
        "status": status,
        "provision": provision,
        "halt": halt,
        "destroy": destroy,
    }
    dispatch[args.command](v, args)


if __name__ == "__main__":
    main()
