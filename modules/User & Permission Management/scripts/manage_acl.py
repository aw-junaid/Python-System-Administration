#!/usr/bin/env python3
"""
manage_acl.py
--------------------
Sets, views, and removes POSIX Access Control Lists (ACLs) on a file or
directory — fine-grained permissions beyond the basic owner/group/other
Unix model (e.g. "give this specific user read+write, without changing
the file's normal owner"). Wraps the 'setfacl' and 'getfacl' command-line
tools, which must be installed on the system (part of the 'acl' package
on most Linux distributions).

Platform: Linux only (POSIX ACLs). Not applicable to Windows or macOS
          in this form.
Requires: the 'acl' package installed at the OS level (setfacl/getfacl),
          and root/sudo for changing ACLs on files you don't own.

Usage:
    python manage_acl.py view <path>
    python manage_acl.py set <path> --entity user:USERNAME:PERMS
    python manage_acl.py set <path> --entity group:GROUPNAME:PERMS
    python manage_acl.py remove <path> --entity user:USERNAME
    python manage_acl.py remove-all <path>

Example:
    python3 manage_acl.py view myfile.txt
    sudo python3 manage_acl.py set myfile.txt --entity user:johndoe:rw-
    sudo python3 manage_acl.py set /shared/project --entity group:developers:rwx --recursive
    sudo python3 manage_acl.py remove myfile.txt --entity user:johndoe
    sudo python3 manage_acl.py remove-all myfile.txt
"""

import argparse
import platform
import shutil
import subprocess
import sys


def check_tools_available():
    if platform.system() != "Linux":
        print("Error: POSIX ACLs (setfacl/getfacl) are only supported on Linux.")
        sys.exit(1)

    if not shutil.which("setfacl") or not shutil.which("getfacl"):
        print("Error: 'setfacl'/'getfacl' not found on this system.")
        print("Install the ACL tools first, e.g.:")
        print("  Debian/Ubuntu: sudo apt install acl")
        print("  RHEL/CentOS:   sudo yum install acl")
        sys.exit(1)


def view_acl(path: str) -> None:
    result = subprocess.run(["getfacl", path], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"ACL entries for '{path}':\n")
        print(result.stdout)
    else:
        print("Error reading ACL:")
        print(result.stderr.strip())
        sys.exit(1)


def set_acl(path: str, entity: str, recursive: bool) -> None:
    cmd = ["setfacl"]
    if recursive:
        cmd.append("-R")
    cmd.extend(["-m", entity, path])

    print(f"Setting ACL entry '{entity}' on '{path}'...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("ACL entry set successfully.")
        view_acl(path)
    else:
        print("Error setting ACL (may require sudo):")
        print(result.stderr.strip())
        sys.exit(1)


def remove_acl(path: str, entity: str) -> None:
    # For removal, entity is like "user:johndoe" (without the permission part)
    cmd = ["setfacl", "-x", entity, path]

    print(f"Removing ACL entry '{entity}' from '{path}'...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("ACL entry removed successfully.")
        view_acl(path)
    else:
        print("Error removing ACL entry (may require sudo):")
        print(result.stderr.strip())
        sys.exit(1)


def remove_all_acl(path: str) -> None:
    result = subprocess.run(["setfacl", "-b", path], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"All extended ACL entries removed from '{path}' (basic permissions unaffected).")
    else:
        print("Error removing all ACL entries (may require sudo):")
        print(result.stderr.strip())
        sys.exit(1)


def main():
    check_tools_available()

    parser = argparse.ArgumentParser(
        description="Manage POSIX Access Control Lists (ACLs) on a file or directory.",
        epilog="Entity format: user:NAME:PERMS or group:NAME:PERMS, e.g. user:johndoe:rw-",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)

    view_parser = subparsers.add_parser("view", help="View ACL entries for a path")
    view_parser.add_argument("path", help="File or directory to inspect")

    set_parser = subparsers.add_parser("set", help="Set (add/update) an ACL entry")
    set_parser.add_argument("path", help="File or directory to modify")
    set_parser.add_argument("--entity", required=True,
                             help="ACL entry, e.g. 'user:johndoe:rw-' or 'group:developers:rwx'")
    set_parser.add_argument("--recursive", action="store_true", help="Apply recursively (directories only)")

    remove_parser = subparsers.add_parser("remove", help="Remove a specific ACL entry")
    remove_parser.add_argument("path", help="File or directory to modify")
    remove_parser.add_argument("--entity", required=True, help="Entity to remove, e.g. 'user:johndoe'")

    remove_all_parser = subparsers.add_parser("remove-all", help="Remove ALL extended ACL entries from a path")
    remove_all_parser.add_argument("path", help="File or directory to modify")

    args = parser.parse_args()

    if args.action == "view":
        view_acl(args.path)
    elif args.action == "set":
        set_acl(args.path, args.entity, args.recursive)
    elif args.action == "remove":
        remove_acl(args.path, args.entity)
    elif args.action == "remove-all":
        remove_all_acl(args.path)


if __name__ == "__main__":
    main()
