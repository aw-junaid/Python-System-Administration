#!/usr/bin/env python3
"""
serverless_deploy.py
---------------------------
Packages a Python function directory into a ZIP file and deploys it as an
AWS Lambda function (via boto3) or prepares it for Azure Functions
deployment (via the Azure Functions Core Tools CLI).

Requires:
    AWS:   pip install boto3           (+ AWS credentials configured)
    Azure: Azure Functions Core Tools installed (npm install -g azure-functions-core-tools@4)
           and an Azure CLI login ('az login').

Usage:
    python serverless_deploy.py package <source_dir> <output_zip>
    python serverless_deploy.py aws-deploy <function_name> <zip_path> <role_arn> [--runtime python3.12] [--handler handler.lambda_handler] [--region us-east-1]
    python serverless_deploy.py aws-update <function_name> <zip_path> [--region us-east-1]
    python serverless_deploy.py azure-deploy <function_app_name> <source_dir>

Example:
    python serverless_deploy.py package ./my_function ./my_function.zip
    python serverless_deploy.py aws-deploy my-function ./my_function.zip arn:aws:iam::123456789012:role/lambda-role
    python serverless_deploy.py aws-update my-function ./my_function.zip
    python serverless_deploy.py azure-deploy my-function-app ./my_function
"""

import argparse
import os
import shutil
import subprocess
import sys
import zipfile


def package_function(source_dir: str, output_zip: str) -> None:
    if not os.path.isdir(source_dir):
        print(f"Error: source directory '{source_dir}' does not exist.")
        sys.exit(1)

    if not output_zip.lower().endswith(".zip"):
        output_zip += ".zip"

    print(f"Packaging '{source_dir}' into '{output_zip}'...")

    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", "venv", ".venv")]
            for f in files:
                if f.endswith(".pyc"):
                    continue
                full_path = os.path.join(root, f)
                arcname = os.path.relpath(full_path, source_dir)
                zf.write(full_path, arcname=arcname)

    size_kb = os.path.getsize(output_zip) / 1024
    print(f"Package created: {output_zip} ({size_kb:.1f} KB)")


def aws_deploy(function_name: str, zip_path: str, role_arn: str, runtime: str, handler: str, region: str) -> None:
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
    except ImportError:
        print("Error: the 'boto3' package is required for AWS deployment.")
        print("Install it with: pip install -r requirements.txt")
        sys.exit(1)

    if not os.path.isfile(zip_path):
        print(f"Error: zip file '{zip_path}' does not exist. Run 'package' first.")
        sys.exit(1)

    with open(zip_path, "rb") as f:
        zip_bytes = f.read()

    client = boto3.client("lambda", region_name=region)

    print(f"Creating Lambda function '{function_name}'...")
    try:
        response = client.create_function(
            FunctionName=function_name,
            Runtime=runtime,
            Role=role_arn,
            Handler=handler,
            Code={"ZipFile": zip_bytes},
            Publish=True,
        )
        print(f"Function '{function_name}' created successfully.")
        print(f"ARN: {response['FunctionArn']}")
    except NoCredentialsError:
        print("Error: no AWS credentials found. Run 'aws configure' first.")
        sys.exit(1)
    except ClientError as e:
        print(f"Error creating function: {e.response['Error']['Message']}")
        sys.exit(1)


def aws_update(function_name: str, zip_path: str, region: str) -> None:
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
    except ImportError:
        print("Error: the 'boto3' package is required for AWS deployment.")
        print("Install it with: pip install -r requirements.txt")
        sys.exit(1)

    if not os.path.isfile(zip_path):
        print(f"Error: zip file '{zip_path}' does not exist. Run 'package' first.")
        sys.exit(1)

    with open(zip_path, "rb") as f:
        zip_bytes = f.read()

    client = boto3.client("lambda", region_name=region)

    print(f"Updating Lambda function '{function_name}' code...")
    try:
        response = client.update_function_code(FunctionName=function_name, ZipFile=zip_bytes, Publish=True)
        print(f"Function '{function_name}' updated successfully.")
        print(f"New version: {response['Version']}")
    except NoCredentialsError:
        print("Error: no AWS credentials found. Run 'aws configure' first.")
        sys.exit(1)
    except ClientError as e:
        print(f"Error updating function: {e.response['Error']['Message']}")
        sys.exit(1)


def azure_deploy(function_app_name: str, source_dir: str) -> None:
    if not shutil.which("func"):
        print("Error: Azure Functions Core Tools ('func') not found on PATH.")
        print("Install it with: npm install -g azure-functions-core-tools@4")
        sys.exit(1)

    if not os.path.isdir(source_dir):
        print(f"Error: source directory '{source_dir}' does not exist.")
        sys.exit(1)

    cmd = ["func", "azure", "functionapp", "publish", function_app_name]
    print(f"Running: {' '.join(cmd)} (in {source_dir})\n")
    print("Note: requires 'az login' to already be authenticated.\n")

    result = subprocess.run(cmd, cwd=source_dir)

    if result.returncode != 0:
        print(f"\nDeployment exited with code {result.returncode}.")
        sys.exit(result.returncode)

    print(f"\nFunction app '{function_app_name}' deployed successfully.")


def main():
    parser = argparse.ArgumentParser(description="Package and deploy serverless functions (AWS Lambda / Azure Functions).")
    subparsers = parser.add_subparsers(dest="action", required=True)

    p = subparsers.add_parser("package", help="Package a function directory into a ZIP file")
    p.add_argument("source_dir", help="Directory containing the function code")
    p.add_argument("output_zip", help="Path for the output ZIP file")

    p = subparsers.add_parser("aws-deploy", help="Create a new AWS Lambda function")
    p.add_argument("function_name", help="Name for the Lambda function")
    p.add_argument("zip_path", help="Path to the packaged ZIP file")
    p.add_argument("role_arn", help="IAM role ARN with Lambda execution permissions")
    p.add_argument("--runtime", default="python3.12", help="Lambda runtime (default: python3.12)")
    p.add_argument("--handler", default="handler.lambda_handler", help="Handler entrypoint (default: handler.lambda_handler)")
    p.add_argument("--region", default="us-east-1", help="AWS region (default: us-east-1)")

    p = subparsers.add_parser("aws-update", help="Update code for an existing AWS Lambda function")
    p.add_argument("function_name", help="Name of the existing Lambda function")
    p.add_argument("zip_path", help="Path to the packaged ZIP file")
    p.add_argument("--region", default="us-east-1", help="AWS region (default: us-east-1)")

    p = subparsers.add_parser("azure-deploy", help="Deploy to an existing Azure Function App")
    p.add_argument("function_app_name", help="Name of the Azure Function App")
    p.add_argument("source_dir", help="Directory containing the function code")

    args = parser.parse_args()

    if args.action == "package":
        package_function(args.source_dir, args.output_zip)
    elif args.action == "aws-deploy":
        aws_deploy(args.function_name, args.zip_path, args.role_arn, args.runtime, args.handler, args.region)
    elif args.action == "aws-update":
        aws_update(args.function_name, args.zip_path, args.region)
    elif args.action == "azure-deploy":
        azure_deploy(args.function_app_name, args.source_dir)


if __name__ == "__main__":
    main()
