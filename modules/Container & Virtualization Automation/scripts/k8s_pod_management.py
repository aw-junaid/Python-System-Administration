#!/usr/bin/env python3
"""
k8s_pod_management.py
Create, monitor, and terminate pods within a Kubernetes cluster using the
official Kubernetes Python client.

USAGE
    python k8s_pod_management.py create --name test-pod --image nginx:latest --namespace default
    python k8s_pod_management.py list --namespace default
    python k8s_pod_management.py status --name test-pod --namespace default
    python k8s_pod_management.py delete --name test-pod --namespace default

REQUIREMENTS
    - A reachable Kubernetes cluster and a valid kubeconfig
      (default location: ~/.kube/config, or set KUBECONFIG)
    - Sufficient RBAC permissions to create/list/delete pods in the namespace
    - pip install -r requirements.txt   (installs the `kubernetes` package)

EXPECTED OUTPUT
    create -> "Pod 'test-pod' created in namespace 'default'."
    list   -> table of pod names, phases and node assignments
    status -> "Pod 'test-pod' phase: Running"
    delete -> "Pod 'test-pod' deleted from namespace 'default'."
"""

import argparse

from kubernetes import client, config
from kubernetes.client.rest import ApiException


def load_client():
    config.load_kube_config()
    return client.CoreV1Api()


def create_pod(args):
    v1 = load_client()
    pod = client.V1Pod(
        metadata=client.V1ObjectMeta(name=args.name),
        spec=client.V1PodSpec(
            containers=[client.V1Container(name=args.name, image=args.image)]
        ),
    )
    try:
        v1.create_namespaced_pod(namespace=args.namespace, body=pod)
        print(f"Pod '{args.name}' created in namespace '{args.namespace}'.")
    except ApiException as e:
        print(f"Failed to create pod: {e}")


def list_pods(args):
    v1 = load_client()
    pods = v1.list_namespaced_pod(namespace=args.namespace)
    if not pods.items:
        print(f"No pods found in namespace '{args.namespace}'.")
        return
    print(f"{'NAME':30} {'PHASE':12} {'NODE'}")
    for p in pods.items:
        node = p.spec.node_name or "-"
        print(f"{p.metadata.name:30} {p.status.phase:12} {node}")


def pod_status(args):
    v1 = load_client()
    try:
        pod = v1.read_namespaced_pod_status(name=args.name, namespace=args.namespace)
        print(f"Pod '{args.name}' phase: {pod.status.phase}")
    except ApiException as e:
        print(f"Failed to read pod status: {e}")


def delete_pod(args):
    v1 = load_client()
    try:
        v1.delete_namespaced_pod(name=args.name, namespace=args.namespace)
        print(f"Pod '{args.name}' deleted from namespace '{args.namespace}'.")
    except ApiException as e:
        print(f"Failed to delete pod: {e}")


def main():
    parser = argparse.ArgumentParser(description="Manage Kubernetes pods programmatically.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create")
    p_create.add_argument("--name", required=True)
    p_create.add_argument("--image", required=True)
    p_create.add_argument("--namespace", default="default")
    p_create.set_defaults(func=create_pod)

    p_list = sub.add_parser("list")
    p_list.add_argument("--namespace", default="default")
    p_list.set_defaults(func=list_pods)

    p_status = sub.add_parser("status")
    p_status.add_argument("--name", required=True)
    p_status.add_argument("--namespace", default="default")
    p_status.set_defaults(func=pod_status)

    p_delete = sub.add_parser("delete")
    p_delete.add_argument("--name", required=True)
    p_delete.add_argument("--namespace", default="default")
    p_delete.set_defaults(func=delete_pod)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
