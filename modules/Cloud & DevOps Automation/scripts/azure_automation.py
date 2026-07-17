#!/usr/bin/env python3
"""
azure_automation.py
--------------------------
Manages basic Azure Virtual Machines and Blob Storage using the Azure SDK
for Python.

Requires: pip install azure-identity azure-mgmt-compute azure-mgmt-storage azure-storage-blob
Requires: Azure credentials configured (via 'az login' for local dev, or
          environment variables for a service principal:
          AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET).

Usage:
    python azure_automation.py vm-list <subscription_id> <resource_group>
    python azure_automation.py vm-start <subscription_id> <resource_group> <vm_name>
    python azure_automation.py vm-stop <subscription_id> <resource_group> <vm_name>
    python azure_automation.py blob-list-containers <storage_account_url>
    python azure_automation.py blob-upload <storage_account_url> <container> <local_file> [--blob-name name]

Example:
    python azure_automation.py vm-list 00000000-0000-0000-0000-000000000000 my-resource-group
    python azure_automation.py blob-upload https://myaccount.blob.core.windows.net mycontainer ./report.pdf
"""

import argparse
import os
import sys

try:
    from azure.identity import DefaultAzureCredential
    from azure.mgmt.compute import ComputeManagementClient
    from azure.storage.blob import BlobServiceClient
    from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
except ImportError:
    print("Error: required Azure packages are missing.")
    print("Install them with: pip install -r requirements.txt")
    sys.exit(1)


def handle_azure_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ClientAuthenticationError:
            print("Error: Azure authentication failed.")
            print("Run 'az login' or set AZURE_CLIENT_ID / AZURE_TENANT_ID / AZURE_CLIENT_SECRET.")
            sys.exit(1)
        except HttpResponseError as e:
            print(f"Azure API error: {e.message}")
            sys.exit(1)
    return wrapper


@handle_azure_errors
def vm_list(subscription_id: str, resource_group: str) -> None:
    credential = DefaultAzureCredential()
    compute_client = ComputeManagementClient(credential, subscription_id)

    vms = list(compute_client.virtual_machines.list(resource_group))

    if not vms:
        print(f"No VMs found in resource group '{resource_group}'.")
        return

    print(f"VMs in '{resource_group}' ({len(vms)}):\n")
    for vm in vms:
        instance_view = compute_client.virtual_machines.instance_view(resource_group, vm.name)
        statuses = [s.display_status for s in instance_view.statuses]
        power_state = next((s for s in statuses if s.startswith("VM")), "Unknown")
        print(f"{vm.name:<30} Size: {vm.hardware_profile.vm_size:<20} State: {power_state}")


@handle_azure_errors
def vm_start(subscription_id: str, resource_group: str, vm_name: str) -> None:
    credential = DefaultAzureCredential()
    compute_client = ComputeManagementClient(credential, subscription_id)

    print(f"Starting VM '{vm_name}'...")
    poller = compute_client.virtual_machines.begin_start(resource_group, vm_name)
    poller.result()
    print(f"VM '{vm_name}' started successfully.")


@handle_azure_errors
def vm_stop(subscription_id: str, resource_group: str, vm_name: str) -> None:
    credential = DefaultAzureCredential()
    compute_client = ComputeManagementClient(credential, subscription_id)

    print(f"Stopping (deallocating) VM '{vm_name}'...")
    poller = compute_client.virtual_machines.begin_deallocate(resource_group, vm_name)
    poller.result()
    print(f"VM '{vm_name}' stopped successfully.")


@handle_azure_errors
def blob_list_containers(storage_account_url: str) -> None:
    credential = DefaultAzureCredential()
    blob_service = BlobServiceClient(account_url=storage_account_url, credential=credential)

    containers = list(blob_service.list_containers())

    if not containers:
        print("No containers found in this storage account.")
        return

    print(f"Containers ({len(containers)}):\n")
    for c in containers:
        print(f"{c.name}  (last modified: {c.last_modified})")


@handle_azure_errors
def blob_upload(storage_account_url: str, container: str, local_file: str, blob_name: str) -> None:
    if not os.path.isfile(local_file):
        print(f"Error: local file '{local_file}' does not exist.")
        sys.exit(1)

    credential = DefaultAzureCredential()
    blob_service = BlobServiceClient(account_url=storage_account_url, credential=credential)

    target_blob_name = blob_name or os.path.basename(local_file)
    blob_client = blob_service.get_blob_client(container=container, blob=target_blob_name)

    print(f"Uploading '{local_file}' to container '{container}' as '{target_blob_name}'...")
    with open(local_file, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    print("Upload complete.")


def main():
    parser = argparse.ArgumentParser(description="Manage Azure VMs and Blob Storage.")
    subparsers = parser.add_subparsers(dest="action", required=True)

    p = subparsers.add_parser("vm-list", help="List VMs in a resource group")
    p.add_argument("subscription_id", help="Azure subscription ID")
    p.add_argument("resource_group", help="Resource group name")

    p = subparsers.add_parser("vm-start", help="Start a VM")
    p.add_argument("subscription_id", help="Azure subscription ID")
    p.add_argument("resource_group", help="Resource group name")
    p.add_argument("vm_name", help="Name of the VM to start")

    p = subparsers.add_parser("vm-stop", help="Stop (deallocate) a VM")
    p.add_argument("subscription_id", help="Azure subscription ID")
    p.add_argument("resource_group", help="Resource group name")
    p.add_argument("vm_name", help="Name of the VM to stop")

    p = subparsers.add_parser("blob-list-containers", help="List blob containers in a storage account")
    p.add_argument("storage_account_url", help="e.g. https://myaccount.blob.core.windows.net")

    p = subparsers.add_parser("blob-upload", help="Upload a file to Azure Blob Storage")
    p.add_argument("storage_account_url", help="e.g. https://myaccount.blob.core.windows.net")
    p.add_argument("container", help="Container name")
    p.add_argument("local_file", help="Path to the local file to upload")
    p.add_argument("--blob-name", default=None, help="Destination blob name (default: same filename)")

    args = parser.parse_args()

    if args.action == "vm-list":
        vm_list(args.subscription_id, args.resource_group)
    elif args.action == "vm-start":
        vm_start(args.subscription_id, args.resource_group, args.vm_name)
    elif args.action == "vm-stop":
        vm_stop(args.subscription_id, args.resource_group, args.vm_name)
    elif args.action == "blob-list-containers":
        blob_list_containers(args.storage_account_url)
    elif args.action == "blob-upload":
        blob_upload(args.storage_account_url, args.container, args.local_file, args.blob_name)


if __name__ == "__main__":
    main()
