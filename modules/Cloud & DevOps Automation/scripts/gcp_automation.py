#!/usr/bin/env python3
"""
gcp_automation.py
-----------------------
Manages basic Google Cloud Compute Engine instances and Cloud Storage
buckets using the Google Cloud client libraries for Python.

Requires: pip install google-cloud-compute google-cloud-storage
Requires: GCP credentials configured (via 'gcloud auth application-default login'
          for local dev, or a service account JSON key referenced by the
          GOOGLE_APPLICATION_CREDENTIALS environment variable).

Usage:
    python gcp_automation.py compute-list <project_id> <zone>
    python gcp_automation.py compute-start <project_id> <zone> <instance_name>
    python gcp_automation.py compute-stop <project_id> <zone> <instance_name>
    python gcp_automation.py storage-list-buckets <project_id>
    python gcp_automation.py storage-upload <bucket_name> <local_file> [--blob-name name]

Example:
    python gcp_automation.py compute-list my-project us-central1-a
    python gcp_automation.py storage-upload my-bucket ./report.pdf
"""

import argparse
import os
import sys

try:
    from google.cloud import compute_v1
    from google.cloud import storage
    from google.api_core.exceptions import GoogleAPICallError, NotFound, Forbidden
    from google.auth.exceptions import DefaultCredentialsError
except ImportError:
    print("Error: required Google Cloud packages are missing.")
    print("Install them with: pip install -r requirements.txt")
    sys.exit(1)


def handle_gcp_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DefaultCredentialsError:
            print("Error: no Google Cloud credentials found.")
            print("Run 'gcloud auth application-default login' or set GOOGLE_APPLICATION_CREDENTIALS.")
            sys.exit(1)
        except NotFound as e:
            print(f"Error: resource not found: {e.message}")
            sys.exit(1)
        except Forbidden as e:
            print(f"Error: permission denied: {e.message}")
            sys.exit(1)
        except GoogleAPICallError as e:
            print(f"GCP API error: {e.message}")
            sys.exit(1)
    return wrapper


@handle_gcp_errors
def compute_list(project_id: str, zone: str) -> None:
    client = compute_v1.InstancesClient()
    instances = client.list(project=project_id, zone=zone)

    instance_list = list(instances)
    if not instance_list:
        print(f"No instances found in zone '{zone}' for project '{project_id}'.")
        return

    print(f"Compute instances in '{project_id}/{zone}' ({len(instance_list)}):\n")
    for inst in instance_list:
        machine_type = inst.machine_type.split("/")[-1]
        print(f"{inst.name:<30} Status: {inst.status:<10} Type: {machine_type}")


@handle_gcp_errors
def compute_start(project_id: str, zone: str, instance_name: str) -> None:
    client = compute_v1.InstancesClient()
    print(f"Starting instance '{instance_name}'...")
    operation = client.start(project=project_id, zone=zone, instance=instance_name)
    operation.result()
    print(f"Instance '{instance_name}' started successfully.")


@handle_gcp_errors
def compute_stop(project_id: str, zone: str, instance_name: str) -> None:
    client = compute_v1.InstancesClient()
    print(f"Stopping instance '{instance_name}'...")
    operation = client.stop(project=project_id, zone=zone, instance=instance_name)
    operation.result()
    print(f"Instance '{instance_name}' stopped successfully.")


@handle_gcp_errors
def storage_list_buckets(project_id: str) -> None:
    client = storage.Client(project=project_id)
    buckets = list(client.list_buckets())

    if not buckets:
        print(f"No storage buckets found for project '{project_id}'.")
        return

    print(f"Storage buckets in '{project_id}' ({len(buckets)}):\n")
    for b in buckets:
        print(f"{b.name}  (location: {b.location}, created: {b.time_created})")


@handle_gcp_errors
def storage_upload(bucket_name: str, local_file: str, blob_name: str) -> None:
    if not os.path.isfile(local_file):
        print(f"Error: local file '{local_file}' does not exist.")
        sys.exit(1)

    client = storage.Client()
    bucket = client.bucket(bucket_name)

    target_blob_name = blob_name or os.path.basename(local_file)
    blob = bucket.blob(target_blob_name)

    print(f"Uploading '{local_file}' to 'gs://{bucket_name}/{target_blob_name}'...")
    blob.upload_from_filename(local_file)
    print("Upload complete.")


def main():
    parser = argparse.ArgumentParser(description="Manage GCP Compute Engine and Cloud Storage.")
    subparsers = parser.add_subparsers(dest="action", required=True)

    p = subparsers.add_parser("compute-list", help="List Compute Engine instances in a zone")
    p.add_argument("project_id", help="GCP project ID")
    p.add_argument("zone", help="e.g. us-central1-a")

    p = subparsers.add_parser("compute-start", help="Start a Compute Engine instance")
    p.add_argument("project_id", help="GCP project ID")
    p.add_argument("zone", help="e.g. us-central1-a")
    p.add_argument("instance_name", help="Name of the instance to start")

    p = subparsers.add_parser("compute-stop", help="Stop a Compute Engine instance")
    p.add_argument("project_id", help="GCP project ID")
    p.add_argument("zone", help="e.g. us-central1-a")
    p.add_argument("instance_name", help="Name of the instance to stop")

    p = subparsers.add_parser("storage-list-buckets", help="List Cloud Storage buckets")
    p.add_argument("project_id", help="GCP project ID")

    p = subparsers.add_parser("storage-upload", help="Upload a file to Cloud Storage")
    p.add_argument("bucket_name", help="Destination bucket name")
    p.add_argument("local_file", help="Path to the local file to upload")
    p.add_argument("--blob-name", default=None, help="Destination blob name (default: same filename)")

    args = parser.parse_args()

    if args.action == "compute-list":
        compute_list(args.project_id, args.zone)
    elif args.action == "compute-start":
        compute_start(args.project_id, args.zone, args.instance_name)
    elif args.action == "compute-stop":
        compute_stop(args.project_id, args.zone, args.instance_name)
    elif args.action == "storage-list-buckets":
        storage_list_buckets(args.project_id)
    elif args.action == "storage-upload":
        storage_upload(args.bucket_name, args.local_file, args.blob_name)


if __name__ == "__main__":
    main()
