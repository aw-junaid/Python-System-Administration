#!/usr/bin/env python3
"""
k8s_deploy.py
Apply a Kubernetes Deployment manifest and roll out updates to applications
running on a cluster, using the official Kubernetes Python client.

USAGE
    python k8s_deploy.py apply --file deployment.yaml --namespace default
    python k8s_deploy.py rollout-status --name my-app --namespace default
    python k8s_deploy.py scale --name my-app --replicas 5 --namespace default
    python k8s_deploy.py delete --name my-app --namespace default

REQUIREMENTS
    - A reachable Kubernetes cluster and a valid kubeconfig
    - A Deployment manifest YAML file (apiVersion: apps/v1, kind: Deployment)
    - pip install -r requirements.txt   (installs kubernetes + PyYAML)

EXPECTED OUTPUT
    apply           -> "Deployment 'my-app' created." or "... updated."
    rollout-status  -> "Deployment 'my-app': 3/3 replicas ready."
    scale           -> "Deployment 'my-app' scaled to 5 replicas."
    delete          -> "Deployment 'my-app' deleted from namespace 'default'."
"""

import argparse

import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException


def load_apps_client():
    config.load_kube_config()
    return client.AppsV1Api()


def apply_deployment(args):
    apps_v1 = load_apps_client()
    with open(args.file) as f:
        manifest = yaml.safe_load(f)

    name = manifest["metadata"]["name"]
    namespace = args.namespace
    try:
        apps_v1.read_namespaced_deployment(name=name, namespace=namespace)
        apps_v1.replace_namespaced_deployment(name=name, namespace=namespace, body=manifest)
        print(f"Deployment '{name}' updated.")
    except ApiException as e:
        if e.status == 404:
            apps_v1.create_namespaced_deployment(namespace=namespace, body=manifest)
            print(f"Deployment '{name}' created.")
        else:
            print(f"Failed to apply deployment: {e}")


def rollout_status(args):
    apps_v1 = load_apps_client()
    try:
        dep = apps_v1.read_namespaced_deployment_status(name=args.name, namespace=args.namespace)
        ready = dep.status.ready_replicas or 0
        desired = dep.spec.replicas
        print(f"Deployment '{args.name}': {ready}/{desired} replicas ready.")
    except ApiException as e:
        print(f"Failed to read rollout status: {e}")


def scale(args):
    apps_v1 = load_apps_client()
    body = {"spec": {"replicas": args.replicas}}
    try:
        apps_v1.patch_namespaced_deployment_scale(name=args.name, namespace=args.namespace, body=body)
        print(f"Deployment '{args.name}' scaled to {args.replicas} replicas.")
    except ApiException as e:
        print(f"Failed to scale deployment: {e}")


def delete_deployment(args):
    apps_v1 = load_apps_client()
    try:
        apps_v1.delete_namespaced_deployment(name=args.name, namespace=args.namespace)
        print(f"Deployment '{args.name}' deleted from namespace '{args.namespace}'.")
    except ApiException as e:
        print(f"Failed to delete deployment: {e}")


def main():
    parser = argparse.ArgumentParser(description="Deploy and manage Kubernetes Deployments programmatically.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_apply = sub.add_parser("apply")
    p_apply.add_argument("--file", required=True, help="Path to a Deployment manifest YAML file")
    p_apply.add_argument("--namespace", default="default")
    p_apply.set_defaults(func=apply_deployment)

    p_status = sub.add_parser("rollout-status")
    p_status.add_argument("--name", required=True)
    p_status.add_argument("--namespace", default="default")
    p_status.set_defaults(func=rollout_status)

    p_scale = sub.add_parser("scale")
    p_scale.add_argument("--name", required=True)
    p_scale.add_argument("--replicas", type=int, required=True)
    p_scale.add_argument("--namespace", default="default")
    p_scale.set_defaults(func=scale)

    p_delete = sub.add_parser("delete")
    p_delete.add_argument("--name", required=True)
    p_delete.add_argument("--namespace", default="default")
    p_delete.set_defaults(func=delete_deployment)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
