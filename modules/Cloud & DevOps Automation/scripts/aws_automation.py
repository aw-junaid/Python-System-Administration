#!/usr/bin/env python3
"""
aws_automation.py
------------------------
Manages basic AWS EC2, S3, and IAM resources using boto3, the official
AWS SDK for Python.

Requires: pip install boto3
Requires: AWS credentials configured (via 'aws configure', environment
          variables AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY, or an IAM role).

Usage:
    python aws_automation.py ec2-list [--region us-east-1]
    python aws_automation.py ec2-start <instance_id> [--region us-east-1]
    python aws_automation.py ec2-stop <instance_id> [--region us-east-1]
    python aws_automation.py s3-list-buckets
    python aws_automation.py s3-list-objects <bucket_name>
    python aws_automation.py s3-upload <bucket_name> <local_file> [--key remote_key]
    python aws_automation.py iam-list-users

Example:
    python aws_automation.py ec2-list --region us-east-1
    python aws_automation.py s3-upload my-bucket ./report.pdf --key reports/report.pdf
"""

import argparse
import os
import sys

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError
except ImportError:
    print("Error: the 'boto3' package is required.")
    print("Install it with: pip install -r requirements.txt")
    sys.exit(1)


def handle_aws_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NoCredentialsError:
            print("Error: no AWS credentials found.")
            print("Configure them with 'aws configure' or set AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY.")
            sys.exit(1)
        except EndpointConnectionError as e:
            print(f"Error: could not connect to AWS endpoint: {e}")
            sys.exit(1)
        except ClientError as e:
            print(f"AWS API error: {e.response['Error']['Code']} - {e.response['Error']['Message']}")
            sys.exit(1)
    return wrapper


@handle_aws_errors
def ec2_list(region: str) -> None:
    ec2 = boto3.client("ec2", region_name=region)
    response = ec2.describe_instances()

    instances = []
    for reservation in response["Reservations"]:
        instances.extend(reservation["Instances"])

    if not instances:
        print(f"No EC2 instances found in region '{region}'.")
        return

    print(f"EC2 instances in '{region}' ({len(instances)}):\n")
    for inst in instances:
        name = next((t["Value"] for t in inst.get("Tags", []) if t["Key"] == "Name"), "(no name)")
        print(f"ID: {inst['InstanceId']}  State: {inst['State']['Name']:<10}  Type: {inst['InstanceType']:<12}  Name: {name}")


@handle_aws_errors
def ec2_start(instance_id: str, region: str) -> None:
    ec2 = boto3.client("ec2", region_name=region)
    ec2.start_instances(InstanceIds=[instance_id])
    print(f"Start request sent for instance '{instance_id}'. Check ec2-list for status.")


@handle_aws_errors
def ec2_stop(instance_id: str, region: str) -> None:
    ec2 = boto3.client("ec2", region_name=region)
    ec2.stop_instances(InstanceIds=[instance_id])
    print(f"Stop request sent for instance '{instance_id}'. Check ec2-list for status.")


@handle_aws_errors
def s3_list_buckets() -> None:
    s3 = boto3.client("s3")
    response = s3.list_buckets()
    buckets = response["Buckets"]

    if not buckets:
        print("No S3 buckets found.")
        return

    print(f"S3 buckets ({len(buckets)}):\n")
    for b in buckets:
        print(f"{b['Name']}  (created: {b['CreationDate']})")


@handle_aws_errors
def s3_list_objects(bucket_name: str) -> None:
    s3 = boto3.client("s3")
    response = s3.list_objects_v2(Bucket=bucket_name)
    objects = response.get("Contents", [])

    if not objects:
        print(f"Bucket '{bucket_name}' is empty or does not exist.")
        return

    print(f"Objects in '{bucket_name}' ({len(objects)}):\n")
    for obj in objects:
        size_kb = obj["Size"] / 1024
        print(f"{obj['Key']:<50} {size_kb:>10.1f} KB  {obj['LastModified']}")


@handle_aws_errors
def s3_upload(bucket_name: str, local_file: str, key: str) -> None:
    if not os.path.isfile(local_file):
        print(f"Error: local file '{local_file}' does not exist.")
        sys.exit(1)

    s3 = boto3.client("s3")
    remote_key = key or os.path.basename(local_file)

    print(f"Uploading '{local_file}' to 's3://{bucket_name}/{remote_key}'...")
    s3.upload_file(local_file, bucket_name, remote_key)
    print("Upload complete.")


@handle_aws_errors
def iam_list_users() -> None:
    iam = boto3.client("iam")
    response = iam.list_users()
    users = response["Users"]

    if not users:
        print("No IAM users found.")
        return

    print(f"IAM users ({len(users)}):\n")
    for u in users:
        print(f"{u['UserName']:<30} created: {u['CreateDate']}")


def main():
    parser = argparse.ArgumentParser(description="Manage AWS EC2, S3, and IAM resources via boto3.")
    subparsers = parser.add_subparsers(dest="action", required=True)

    p = subparsers.add_parser("ec2-list", help="List EC2 instances")
    p.add_argument("--region", default="us-east-1", help="AWS region (default: us-east-1)")

    p = subparsers.add_parser("ec2-start", help="Start an EC2 instance")
    p.add_argument("instance_id", help="EC2 instance ID")
    p.add_argument("--region", default="us-east-1", help="AWS region (default: us-east-1)")

    p = subparsers.add_parser("ec2-stop", help="Stop an EC2 instance")
    p.add_argument("instance_id", help="EC2 instance ID")
    p.add_argument("--region", default="us-east-1", help="AWS region (default: us-east-1)")

    subparsers.add_parser("s3-list-buckets", help="List all S3 buckets")

    p = subparsers.add_parser("s3-list-objects", help="List objects in an S3 bucket")
    p.add_argument("bucket_name", help="Name of the S3 bucket")

    p = subparsers.add_parser("s3-upload", help="Upload a local file to S3")
    p.add_argument("bucket_name", help="Destination S3 bucket")
    p.add_argument("local_file", help="Path to the local file to upload")
    p.add_argument("--key", default=None, help="Destination key/path in the bucket (default: same filename)")

    subparsers.add_parser("iam-list-users", help="List all IAM users")

    args = parser.parse_args()

    if args.action == "ec2-list":
        ec2_list(args.region)
    elif args.action == "ec2-start":
        ec2_start(args.instance_id, args.region)
    elif args.action == "ec2-stop":
        ec2_stop(args.instance_id, args.region)
    elif args.action == "s3-list-buckets":
        s3_list_buckets()
    elif args.action == "s3-list-objects":
        s3_list_objects(args.bucket_name)
    elif args.action == "s3-upload":
        s3_upload(args.bucket_name, args.local_file, args.key)
    elif args.action == "iam-list-users":
        iam_list_users()


if __name__ == "__main__":
    main()
