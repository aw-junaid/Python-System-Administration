#!/usr/bin/env python3
"""
helm_deploy.py
Package and deploy applications to Kubernetes using Helm charts, managed
and driven from Python (a thin, scriptable wrapper around the `helm` CLI).

USAGE
    python helm_deploy.py install --release my-release --chart ./mychart --namespace default
    python helm_deploy.py upgrade --release my-release --chart ./mychart --set image.tag=1.2.0
    python helm_deploy.py list --namespace default
    python helm_deploy.py uninstall --release my-release --namespace default

REQUIREMENTS
    - Helm 3 installed and on PATH (https://helm.sh/docs/intro/install/)
    - A reachable Kubernetes cluster and a valid kubeconfig
    - A Helm chart directory or packaged .tgz chart
    - pip install -r requirements.txt   (no extra Python packages strictly
      required beyond the standard library, but PyYAML is included for
      parsing --set-file/values files if you extend this script)

EXPECTED OUTPUT
    install    -> Helm's own install summary, ending with "Release 'my-release' installed."
    upgrade    -> Helm's own upgrade summary, ending with "Release 'my-release' upgraded."
    list       -> table of releases (name, namespace, status, chart, app version)
    uninstall  -> "Release 'my-release' uninstalled."
"""

import argparse
import subprocess
import sys


def run_helm(args_list):
    print(f"Running: helm {' '.join(args_list)}")
    result = subprocess.run(["helm"] + args_list, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
    return result.returncode


def install(args):
    cmd = ["install", args.release, args.chart, "--namespace", args.namespace, "--create-namespace"]
    for kv in args.set or []:
        cmd += ["--set", kv]
    rc = run_helm(cmd)
    if rc == 0:
        print(f"Release '{args.release}' installed.")
    else:
        sys.exit(rc)


def upgrade(args):
    cmd = ["upgrade", args.release, args.chart, "--namespace", args.namespace]
    if args.install:
        cmd.append("--install")
    for kv in args.set or []:
        cmd += ["--set", kv]
    rc = run_helm(cmd)
    if rc == 0:
        print(f"Release '{args.release}' upgraded.")
    else:
        sys.exit(rc)


def list_releases(args):
    cmd = ["list", "--namespace", args.namespace]
    run_helm(cmd)


def uninstall(args):
    cmd = ["uninstall", args.release, "--namespace", args.namespace]
    rc = run_helm(cmd)
    if rc == 0:
        print(f"Release '{args.release}' uninstalled.")
    else:
        sys.exit(rc)


def main():
    parser = argparse.ArgumentParser(description="Deploy applications to Kubernetes via Helm.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_install = sub.add_parser("install")
    p_install.add_argument("--release", required=True)
    p_install.add_argument("--chart", required=True, help="Chart directory or .tgz path")
    p_install.add_argument("--namespace", default="default")
    p_install.add_argument("--set", action="append", help="key=value, repeatable")
    p_install.set_defaults(func=install)

    p_upgrade = sub.add_parser("upgrade")
    p_upgrade.add_argument("--release", required=True)
    p_upgrade.add_argument("--chart", required=True)
    p_upgrade.add_argument("--namespace", default="default")
    p_upgrade.add_argument("--install", action="store_true", help="Install the release if it does not exist")
    p_upgrade.add_argument("--set", action="append", help="key=value, repeatable")
    p_upgrade.set_defaults(func=upgrade)

    p_list = sub.add_parser("list")
    p_list.add_argument("--namespace", default="default")
    p_list.set_defaults(func=list_releases)

    p_uninstall = sub.add_parser("uninstall")
    p_uninstall.add_argument("--release", required=True)
    p_uninstall.add_argument("--namespace", default="default")
    p_uninstall.set_defaults(func=uninstall)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
