#!/usr/bin/env python3
"""
kubernetes_automation.py
-------------------------------
Dynamically creates, lists, and deletes Kubernetes pods and deployments
using the official 'kubernetes' Python client.

Requires: pip install kubernetes
Requires: a working kubeconfig (typically ~/.kube/config, set up via your
          cloud provider's CLI, minikube, kind, or similar).

Usage:
    python kubernetes_automation.py list-pods [--namespace default]
    python kubernetes_automation.py create-pod <pod_name> <image> [--namespace default] [--port 80]
    python kubernetes_automation.py delete-pod <pod_name> [--namespace default]
    python kubernetes_automation.py list-deployments [--namespace default]
    python kubernetes_automation.py create-deployment <name> <image> [--replicas 3] [--namespace default] [--port 80]
    python kubernetes_automation.py delete-deployment <name> [--namespace default]
    python kubernetes_automation.py scale-deployment <name> <replicas> [--namespace default]

Example:
    python kubernetes_automation.py list-pods
    python kubernetes_automation.py create-deployment web-app nginx:latest --replicas 3 --port 80
    python kubernetes_automation.py scale-deployment web-app 5
    python kubernetes_automation.py delete-deployment web-app
"""

import argparse
import sys

try:
    from kubernetes import client, config
    from kubernetes.client.rest import ApiException
except ImportError:
    print("Error: the 'kubernetes' package is required.")
    print("Install it with: pip install -r requirements.txt")
    sys.exit(1)


def load_kube_config():
    try:
        config.load_kube_config()
    except Exception:
        try:
            config.load_incluster_config()
        except Exception:
            print("Error: could not load a Kubernetes configuration.")
            print("Make sure you have a valid ~/.kube/config, or are running inside a cluster.")
            sys.exit(1)


def list_pods(namespace: str) -> None:
    load_kube_config()
    v1 = client.CoreV1Api()

    try:
        pods = v1.list_namespaced_pod(namespace)
    except ApiException as e:
        print(f"Error listing pods: {e.reason}")
        sys.exit(1)

    if not pods.items:
        print(f"No pods found in namespace '{namespace}'.")
        return

    print(f"Pods in namespace '{namespace}' ({len(pods.items)}):\n")
    for pod in pods.items:
        print(f"{pod.metadata.name:<30} Status: {pod.status.phase:<12} Node: {pod.spec.node_name}")


def create_pod(pod_name: str, image: str, namespace: str, port: int) -> None:
    load_kube_config()
    v1 = client.CoreV1Api()

    container = client.V1Container(
        name=pod_name,
        image=image,
        ports=[client.V1ContainerPort(container_port=port)] if port else None,
    )
    pod_spec = client.V1PodSpec(containers=[container])
    pod = client.V1Pod(
        metadata=client.V1ObjectMeta(name=pod_name),
        spec=pod_spec,
    )

    try:
        v1.create_namespaced_pod(namespace, pod)
        print(f"Pod '{pod_name}' created in namespace '{namespace}'.")
    except ApiException as e:
        print(f"Error creating pod: {e.reason}")
        sys.exit(1)


def delete_pod(pod_name: str, namespace: str) -> None:
    load_kube_config()
    v1 = client.CoreV1Api()

    try:
        v1.delete_namespaced_pod(pod_name, namespace)
        print(f"Pod '{pod_name}' deleted from namespace '{namespace}'.")
    except ApiException as e:
        print(f"Error deleting pod: {e.reason}")
        sys.exit(1)


def list_deployments(namespace: str) -> None:
    load_kube_config()
    apps_v1 = client.AppsV1Api()

    try:
        deployments = apps_v1.list_namespaced_deployment(namespace)
    except ApiException as e:
        print(f"Error listing deployments: {e.reason}")
        sys.exit(1)

    if not deployments.items:
        print(f"No deployments found in namespace '{namespace}'.")
        return

    print(f"Deployments in namespace '{namespace}' ({len(deployments.items)}):\n")
    for d in deployments.items:
        ready = d.status.ready_replicas or 0
        desired = d.spec.replicas
        print(f"{d.metadata.name:<30} Ready: {ready}/{desired}")


def create_deployment(name: str, image: str, replicas: int, namespace: str, port: int) -> None:
    load_kube_config()
    apps_v1 = client.AppsV1Api()

    container = client.V1Container(
        name=name,
        image=image,
        ports=[client.V1ContainerPort(container_port=port)] if port else None,
    )
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": name}),
        spec=client.V1PodSpec(containers=[container]),
    )
    spec = client.V1DeploymentSpec(
        replicas=replicas,
        selector=client.V1LabelSelector(match_labels={"app": name}),
        template=template,
    )
    deployment = client.V1Deployment(
        metadata=client.V1ObjectMeta(name=name),
        spec=spec,
    )

    try:
        apps_v1.create_namespaced_deployment(namespace, deployment)
        print(f"Deployment '{name}' created in namespace '{namespace}' with {replicas} replica(s).")
    except ApiException as e:
        print(f"Error creating deployment: {e.reason}")
        sys.exit(1)


def delete_deployment(name: str, namespace: str) -> None:
    load_kube_config()
    apps_v1 = client.AppsV1Api()

    try:
        apps_v1.delete_namespaced_deployment(name, namespace)
        print(f"Deployment '{name}' deleted from namespace '{namespace}'.")
    except ApiException as e:
        print(f"Error deleting deployment: {e.reason}")
        sys.exit(1)


def scale_deployment(name: str, replicas: int, namespace: str) -> None:
    load_kube_config()
    apps_v1 = client.AppsV1Api()

    body = {"spec": {"replicas": replicas}}

    try:
        apps_v1.patch_namespaced_deployment_scale(name, namespace, body)
        print(f"Deployment '{name}' scaled to {replicas} replica(s).")
    except ApiException as e:
        print(f"Error scaling deployment: {e.reason}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Manage Kubernetes pods and deployments.")
    subparsers = parser.add_subparsers(dest="action", required=True)

    p = subparsers.add_parser("list-pods", help="List pods in a namespace")
    p.add_argument("--namespace", default="default", help="Namespace (default: default)")

    p = subparsers.add_parser("create-pod", help="Create a single pod")
    p.add_argument("pod_name", help="Name for the pod")
    p.add_argument("image", help="Container image, e.g. nginx:latest")
    p.add_argument("--namespace", default="default", help="Namespace (default: default)")
    p.add_argument("--port", type=int, default=None, help="Container port to expose")

    p = subparsers.add_parser("delete-pod", help="Delete a pod")
    p.add_argument("pod_name", help="Name of the pod to delete")
    p.add_argument("--namespace", default="default", help="Namespace (default: default)")

    p = subparsers.add_parser("list-deployments", help="List deployments in a namespace")
    p.add_argument("--namespace", default="default", help="Namespace (default: default)")

    p = subparsers.add_parser("create-deployment", help="Create a deployment")
    p.add_argument("name", help="Name for the deployment")
    p.add_argument("image", help="Container image, e.g. nginx:latest")
    p.add_argument("--replicas", type=int, default=1, help="Number of replicas (default: 1)")
    p.add_argument("--namespace", default="default", help="Namespace (default: default)")
    p.add_argument("--port", type=int, default=None, help="Container port to expose")

    p = subparsers.add_parser("delete-deployment", help="Delete a deployment")
    p.add_argument("name", help="Name of the deployment to delete")
    p.add_argument("--namespace", default="default", help="Namespace (default: default)")

    p = subparsers.add_parser("scale-deployment", help="Scale a deployment's replica count")
    p.add_argument("name", help="Name of the deployment to scale")
    p.add_argument("replicas", type=int, help="New number of replicas")
    p.add_argument("--namespace", default="default", help="Namespace (default: default)")

    args = parser.parse_args()

    if args.action == "list-pods":
        list_pods(args.namespace)
    elif args.action == "create-pod":
        create_pod(args.pod_name, args.image, args.namespace, args.port)
    elif args.action == "delete-pod":
        delete_pod(args.pod_name, args.namespace)
    elif args.action == "list-deployments":
        list_deployments(args.namespace)
    elif args.action == "create-deployment":
        create_deployment(args.name, args.image, args.replicas, args.namespace, args.port)
    elif args.action == "delete-deployment":
        delete_deployment(args.name, args.namespace)
    elif args.action == "scale-deployment":
        scale_deployment(args.name, args.replicas, args.namespace)


if __name__ == "__main__":
    main()
