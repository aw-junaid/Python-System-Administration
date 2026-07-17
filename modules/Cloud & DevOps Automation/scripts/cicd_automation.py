#!/usr/bin/env python3
"""
cicd_automation.py
-------------------------
Orchestrates a simple CI/CD pipeline locally: runs a sequence of named
stages (e.g. lint, test, build, deploy), each a shell command, defined in
a YAML config file. Stops on first failure by default, reports pass/fail
per stage, and can optionally continue past failures.

Requires: pip install pyyaml

Usage:
    python cicd_automation.py run <pipeline.yml> [--continue-on-error]
    python cicd_automation.py generate <output_file>

Example pipeline.yml:
    stages:
      - name: lint
        command: "flake8 ."
      - name: test
        command: "pytest"
      - name: build
        command: "python setup.py build"
      - name: deploy
        command: "./deploy.sh"

Usage:
    python cicd_automation.py generate pipeline.yml
    python cicd_automation.py run pipeline.yml
"""

import argparse
import shlex
import subprocess
import sys
import time
from datetime import datetime

try:
    import yaml
except ImportError:
    print("Error: the 'pyyaml' package is required.")
    print("Install it with: pip install -r requirements.txt")
    sys.exit(1)

EXAMPLE_PIPELINE = """\
# Example CI/CD pipeline definition.
# Each stage runs as a separate shell command, in order.
stages:
  - name: lint
    command: "echo Running lint checks..."
  - name: test
    command: "echo Running tests..."
  - name: build
    command: "echo Building project..."
  - name: deploy
    command: "echo Deploying application..."
"""


def generate_pipeline(output_file: str) -> None:
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(EXAMPLE_PIPELINE)

    print(f"Generated example pipeline: {output_file}")
    print("Edit the 'command' for each stage, then run:")
    print(f"  python cicd_automation.py run {output_file}")


def load_pipeline(path: str) -> list:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: pipeline file '{path}' not found.")
        sys.exit(1)

    stages = data.get("stages") if data else None
    if not stages:
        print(f"Error: '{path}' has no 'stages' defined.")
        sys.exit(1)

    return stages


def run_pipeline(pipeline_file: str, continue_on_error: bool) -> None:
    stages = load_pipeline(pipeline_file)

    print(f"Running pipeline '{pipeline_file}' ({len(stages)} stage(s))\n")
    print("=" * 60)

    results = []
    overall_success = True

    for i, stage in enumerate(stages, start=1):
        name = stage.get("name", f"stage-{i}")
        command = stage.get("command")

        if not command:
            print(f"[{i}/{len(stages)}] Skipping '{name}': no command defined.")
            results.append((name, "skipped", 0))
            continue

        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{i}/{len(stages)}] [{timestamp}] Stage: {name}")
        print(f"Command: {command}\n")

        start = time.time()
        result = subprocess.run(shlex.split(command))
        duration = time.time() - start

        if result.returncode == 0:
            print(f"\nStage '{name}' PASSED ({duration:.1f}s)")
            results.append((name, "passed", duration))
        else:
            print(f"\nStage '{name}' FAILED (exit code {result.returncode}, {duration:.1f}s)")
            results.append((name, "failed", duration))
            overall_success = False

            if not continue_on_error:
                print("\nStopping pipeline (use --continue-on-error to run remaining stages anyway).")
                break

        print("=" * 60)

    print("\nPipeline Summary:\n")
    for name, status, duration in results:
        symbol = {"passed": "PASS", "failed": "FAIL", "skipped": "SKIP"}[status]
        print(f"  [{symbol}] {name:<20} ({duration:.1f}s)")

    if overall_success:
        print("\nPipeline completed successfully.")
    else:
        print("\nPipeline completed with failures.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Run a simple local CI/CD pipeline defined in YAML.")
    subparsers = parser.add_subparsers(dest="action", required=True)

    p = subparsers.add_parser("run", help="Run a pipeline")
    p.add_argument("pipeline_file", help="Path to the pipeline YAML file")
    p.add_argument("--continue-on-error", action="store_true", help="Keep running remaining stages after a failure")

    p = subparsers.add_parser("generate", help="Generate an example pipeline YAML file")
    p.add_argument("output_file", help="Path to write the example pipeline to")

    args = parser.parse_args()

    if args.action == "run":
        run_pipeline(args.pipeline_file, args.continue_on_error)
    elif args.action == "generate":
        generate_pipeline(args.output_file)


if __name__ == "__main__":
    main()
