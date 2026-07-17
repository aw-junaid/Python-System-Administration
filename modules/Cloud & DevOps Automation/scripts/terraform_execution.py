#!/usr/bin/env python3
"""
terraform_execution.py
------------------------------
Generates a simple Terraform (.tf) configuration file from Python, and
wraps 'terraform init/plan/apply/destroy' commands via subprocess so you
can drive Terraform from a Python automation pipeline.

Requires: the 'terraform' CLI installed and available on PATH.
          (Download from https://developer.hashicorp.com/terraform/downloads)

Usage:
    python terraform_execution.py generate <output_dir> --provider aws --region us-east-1
    python terraform_execution.py init <directory>
    python terraform_execution.py plan <directory>
    python terraform_execution.py apply <directory> [--auto-approve]
    python terraform_execution.py destroy <directory> [--auto-approve]

Example:
    python terraform_execution.py generate ./infra --provider aws --region us-east-1
    python terraform_execution.py init ./infra
    python terraform_execution.py plan ./infra
    python terraform_execution.py apply ./infra --auto-approve
    python terraform_execution.py destroy ./infra --auto-approve
"""

import argparse
import os
import shutil
import subprocess
import sys

AWS_TEMPLATE = """\
terraform {{
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = "{region}"
}}

# Example resource — edit as needed before running 'apply'.
# resource "aws_instance" "example" {{
#   ami           = "ami-0abcdef1234567890"
#   instance_type = "t2.micro"
# }}
"""

AZURE_TEMPLATE = """\
terraform {{
  required_providers {{
    azurerm = {{
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }}
  }}
}}

provider "azurerm" {{
  features {{}}
}}

# Example resource — edit as needed before running 'apply'.
# resource "azurerm_resource_group" "example" {{
#   name     = "example-resources"
#   location = "{region}"
# }}
"""

GCP_TEMPLATE = """\
terraform {{
  required_providers {{
    google = {{
      source  = "hashicorp/google"
      version = "~> 5.0"
    }}
  }}
}}

provider "google" {{
  project = "your-project-id"
  region  = "{region}"
}}

# Example resource — edit as needed before running 'apply'.
# resource "google_compute_instance" "example" {{
#   name         = "example-instance"
#   machine_type = "e2-medium"
#   zone         = "{region}-a"
# }}
"""

TEMPLATES = {"aws": AWS_TEMPLATE, "azure": AZURE_TEMPLATE, "gcp": GCP_TEMPLATE}


def check_terraform_installed():
    if not shutil.which("terraform"):
        print("Error: 'terraform' CLI not found on PATH.")
        print("Install it from: https://developer.hashicorp.com/terraform/downloads")
        sys.exit(1)


def generate_config(output_dir: str, provider: str, region: str) -> None:
    if provider not in TEMPLATES:
        print(f"Error: unsupported provider '{provider}'. Choose from: {', '.join(TEMPLATES.keys())}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "main.tf")

    if os.path.exists(output_path):
        print(f"Error: '{output_path}' already exists. Choose a different directory or remove it first.")
        sys.exit(1)

    content = TEMPLATES[provider].format(region=region)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Generated Terraform config: {output_path}")
    print(f"Provider: {provider}, Region: {region}")
    print("Edit this file to add real resources, then run 'init', 'plan', and 'apply'.")


def run_terraform(subcommand: list, directory: str) -> None:
    check_terraform_installed()

    if not os.path.isdir(directory):
        print(f"Error: directory '{directory}' does not exist.")
        sys.exit(1)

    cmd = ["terraform"] + subcommand
    print(f"Running: {' '.join(cmd)} (in {directory})\n")

    result = subprocess.run(cmd, cwd=directory)

    if result.returncode != 0:
        print(f"\nTerraform command exited with code {result.returncode}.")
        sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser(description="Generate Terraform configs and run terraform commands.")
    subparsers = parser.add_subparsers(dest="action", required=True)

    p = subparsers.add_parser("generate", help="Generate a starter main.tf file")
    p.add_argument("output_dir", help="Directory to write main.tf into")
    p.add_argument("--provider", required=True, choices=["aws", "azure", "gcp"], help="Cloud provider")
    p.add_argument("--region", default="us-east-1", help="Region (default: us-east-1)")

    p = subparsers.add_parser("init", help="Run 'terraform init'")
    p.add_argument("directory", help="Terraform working directory")

    p = subparsers.add_parser("plan", help="Run 'terraform plan'")
    p.add_argument("directory", help="Terraform working directory")

    p = subparsers.add_parser("apply", help="Run 'terraform apply'")
    p.add_argument("directory", help="Terraform working directory")
    p.add_argument("--auto-approve", action="store_true", help="Skip interactive approval")

    p = subparsers.add_parser("destroy", help="Run 'terraform destroy'")
    p.add_argument("directory", help="Terraform working directory")
    p.add_argument("--auto-approve", action="store_true", help="Skip interactive approval")

    args = parser.parse_args()

    if args.action == "generate":
        generate_config(args.output_dir, args.provider, args.region)
    elif args.action == "init":
        run_terraform(["init"], args.directory)
    elif args.action == "plan":
        run_terraform(["plan"], args.directory)
    elif args.action == "apply":
        cmd = ["apply"]
        if args.auto_approve:
            cmd.append("-auto-approve")
        run_terraform(cmd, args.directory)
    elif args.action == "destroy":
        cmd = ["destroy"]
        if args.auto_approve:
            cmd.append("-auto-approve")
        run_terraform(cmd, args.directory)


if __name__ == "__main__":
    main()
