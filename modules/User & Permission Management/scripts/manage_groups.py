#!/usr/bin/env python3
"""
manage_groups.py
-----------------------
Adds or deletes system groups, and adds/removes users from groups.
Wraps 'groupadd', 'groupdel', 'usermod -aG', and 'gpasswd -d' on Linux.

Platform: Linux only.
Requires: root/sudo.

Usage:
    python manage_groups.py create <group_name>
    python manage_groups.py delete <group_name>
    python manage_groups.py add-user <username> <group_name>
    python manage_groups.py remove-user <username> <group_name>
    python manage_groups.py list [--user <username>]

Example:
    sudo python3 manage_groups.py create developers
    sudo python3 manage_groups.py add-user johndoe developers
    sudo python3 manage_groups.py remove-user johndoe developers
    sudo python3 manage_groups.py delete developers
    python3 manage_groups.py list --user johndoe
"""

import argparse
import grp
import os
import platform
import subprocess
import sys


def check_root():
    if os.geteuid() != 0:
        print("Error: this script must be run as root (use sudo) for create/delete/add-user/remove-user.")
        sys.exit(1)


def create_group(group_name: str) -> None:
    check_root()
    result = subprocess.run(["groupadd", group_name], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"Group '{group_name}' created successfully.")
    else:
        print("Error creating group:")
        print(result.stderr.strip())
        sys.exit(1)


def delete_group(group_name: str) -> None:
    check_root()
    result = subprocess.run(["groupdel", group_name], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"Group '{group_name}' deleted successfully.")
    else:
        print("Error deleting group:")
        print(result.stderr.strip())
        sys.exit(1)


def add_user_to_group(username: str, group_name: str) -> None:
    check_root()
    result = subprocess.run(["usermod", "-aG", group_name, username], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"User '{username}' added to group '{group_name}'.")
    else:
        print("Error adding user to group:")
        print(result.stderr.strip())
        sys.exit(1)


def remove_user_from_group(username: str, group_name: str) -> None:
    check_root()
    result = subprocess.run(["gpasswd", "-d", username, group_name], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"User '{username}' removed from group '{group_name}'.")
    else:
        print("Error removing user from group:")
        print(result.stderr.strip())
        sys.exit(1)


def list_groups(username: str = None) -> None:
    if username:
        try:
            result = subprocess.run(["id", "-Gn", username], capture_output=True, text=True, check=True)
            groups = result.stdout.strip().split()
            print(f"Groups for user '{username}':")
            for g in groups:
                print(f"  - {g}")
        except subprocess.CalledProcessError:
            print(f"Error: user '{username}' not found.")
            sys.exit(1)
    else:
        print("All system groups:\n")
        for g in sorted(grp.getgrall(), key=lambda x: x.gr_name):
            members = ", ".join(g.gr_mem) if g.gr_mem else "(no members)"
            print(f"{g.gr_name} (gid={g.gr_gid}): {members}")


def main():
    if platform.system() != "Linux":
        print("Error: this script only supports Linux.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Manage system groups and group memberships.")
    subparsers = parser.add_subparsers(dest="action", required=True)

    create_parser = subparsers.add_parser("create", help="Create a new group")
    create_parser.add_argument("group_name", help="Name of the group to create")

    delete_parser = subparsers.add_parser("delete", help="Delete a group")
    delete_parser.add_argument("group_name", help="Name of the group to delete")

    add_parser = subparsers.add_parser("add-user", help="Add a user to a group")
    add_parser.add_argument("username", help="User to add")
    add_parser.add_argument("group_name", help="Group to add the user to")

    remove_parser = subparsers.add_parser("remove-user", help="Remove a user from a group")
    remove_parser.add_argument("username", help="User to remove")
    remove_parser.add_argument("group_name", help="Group to remove the user from")

    list_parser = subparsers.add_parser("list", help="List all groups, or groups for a specific user")
    list_parser.add_argument("--user", default=None, help="Show groups for this user only")

    args = parser.parse_args()

    if args.action == "create":
        create_group(args.group_name)
    elif args.action == "delete":
        delete_group(args.group_name)
    elif args.action == "add-user":
        add_user_to_group(args.username, args.group_name)
    elif args.action == "remove-user":
        remove_user_from_group(args.username, args.group_name)
    elif args.action == "list":
        list_groups(args.user)


if __name__ == "__main__":
    main()
