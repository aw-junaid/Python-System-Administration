# Container & Virtualization Automation

Python automation scripts for programmatically managing Docker containers,
Docker Compose stacks, virtual machines (libvirt/VirtualBox), Vagrant
environments, LXC/LXD containers, and Kubernetes/Helm deployments — without
manually typing `docker`, `virsh`, `vagrant`, `lxc`, `kubectl`, or `helm`
commands by hand.


Repo: https://github.com/aw-junaid/Python-System-Administration

---

## ⚠️ Read this before running anything

- **These scripts talk to real infrastructure.** They can create, stop, and
  delete real containers, VMs, disk images, and Kubernetes resources on
  whatever host/cluster you point them at. Run them against a test/dev
  environment first, not production, until you're comfortable with what
  each one does.
- **Nothing here works "out of the box" with just `pip install`.** Every
  script depends on a system-level tool or service (Docker Engine, libvirt,
  Vagrant, LXD, a Kubernetes cluster, Helm) already being installed and
  running on your machine. The Python packages in `requirements.txt` are
  only clients/wrappers around those tools — see the table below for what
  each script additionally needs.
- **Never commit real credentials.** `docker_registry_transfer.py` takes a
  username/password for a registry — pass these as environment variables or
  via a secrets manager, never hardcode them in a script or commit history.
- Every script is standalone and can be copied/run individually — none of
  them import from one another.

---

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/aw-junaid/Python-System-Administration.git
cd "Python-System-Administration/modules/Container & Virtualization Automation/scripts"

# 2. (Recommended) create a virtual environment
python3 -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt
```

Then install whatever system-level tool the script(s) you want to use
require, per the table below, before running anything.

---

## Scripts overview

| Script | What it does | System requirement | Run it |
|---|---|---|---|
| `docker_build_image.py` | Builds a Docker image from a Dockerfile without running `docker build` | Docker Engine/Desktop running | `python docker_build_image.py --path ./myapp --tag myapp:latest` |
| `docker_run_container.py` | Runs/stops/removes containers with custom ports, volumes, env vars | Docker Engine/Desktop running | `python docker_run_container.py run --image nginx --name web --port 8080:80` |
| `docker_manage_volumes.py` | Creates/lists/inspects/removes/prunes Docker volumes | Docker Engine/Desktop running | `python docker_manage_volumes.py create --name app_data` |
| `docker_manage_networks.py` | Creates/lists/removes networks; connects/disconnects containers | Docker Engine/Desktop running | `python docker_manage_networks.py create --name backend` |
| `docker_compose_orchestration.py` | Controls a multi-service app's full lifecycle (up/down/ps/logs) | Docker Engine + Compose plugin, a `docker-compose.yml` | `python docker_compose_orchestration.py up --file docker-compose.yml` |
| `docker_prune_resources.py` | Cleans up dangling images, stopped containers, unused volumes/networks | Docker Engine/Desktop running | `python docker_prune_resources.py --all` |
| `docker_monitor_logs.py` | Streams and filters live container logs | Docker Engine/Desktop running | `python docker_monitor_logs.py --name web --follow` |
| `docker_exec_command.py` | Runs a shell command inside a running container | Docker Engine/Desktop running | `python docker_exec_command.py --name web --cmd "ls -la /app"` |
| `docker_registry_transfer.py` | Logs in, pulls, and pushes images to a registry (Docker Hub, ECR, private) | Docker Engine/Desktop running, registry credentials | `python docker_registry_transfer.py pull --image nginx:latest` |
| `vm_create_libvirt.py` | Provisions a full VM (CPU/RAM/disk) via libvirt/KVM | Linux host with libvirt/KVM, `qemu-img` on PATH | `python vm_create_libvirt.py --name test-vm --vcpus 2 --memory-mb 2048 --disk-path /var/lib/libvirt/images/test-vm.qcow2` |
| `vm_clone.py` | Duplicates an entire VM (disks + settings) | Linux host with libvirt, `virt-clone` (virtinst) installed | `python vm_clone.py --original test-vm --clone test-vm-copy` |
| `vm_snapshot.py` | Creates/lists/reverts/deletes point-in-time VM snapshots | Linux host with libvirt, VM disk in qcow2 format | `python vm_snapshot.py create --domain test-vm --name before-update` |
| `vagrant_manage.py` | Spins up, provisions, halts, or destroys Vagrant boxes | `vagrant` CLI + a provider (VirtualBox/libvirt) installed, a Vagrantfile | `python vagrant_manage.py up --dir ./my-vagrant-project` |
| `lxc_manage.py` | Launches/lists/stops/starts/deletes LXD system containers | LXD installed and initialized (`lxd init`) | `python lxc_manage.py launch --name test-ct --image ubuntu:22.04` |
| `k8s_pod_management.py` | Creates/lists/checks status of/deletes Kubernetes pods | Reachable cluster, valid `~/.kube/config` | `python k8s_pod_management.py create --name test-pod --image nginx:latest` |
| `k8s_deploy.py` | Applies a Deployment manifest, checks rollout status, scales, deletes | Reachable cluster, a Deployment YAML manifest | `python k8s_deploy.py apply --file deployment.yaml` |
| `helm_deploy.py` | Installs/upgrades/lists/uninstalls Helm releases | `helm` CLI installed, reachable cluster, a chart | `python helm_deploy.py install --release my-release --chart ./mychart` |
| `container_health_check.py` | Attaches a Docker HEALTHCHECK and polls readiness/liveness status | Docker Engine/Desktop running | `python container_health_check.py check --name web --wait 60` |
| `container_resource_limits.py` | Sets/updates/inspects CPU and memory limits on containers | Docker Engine/Desktop running | `python container_resource_limits.py run --image nginx --name web --cpus 1.5 --memory 512m` |

Every script also has a full docstring at the top of the file with detailed
usage examples, requirements, and expected output — run `python
<script_name>.py --help` at any time to see the CLI options.

---

## Detailed setup by tool

### Docker scripts
1. Install Docker Engine or Docker Desktop: https://docs.docker.com/get-docker/
2. Make sure it's running: `docker info` should succeed without errors.
3. On Linux, add your user to the `docker` group so you don't need `sudo`:
   `sudo usermod -aG docker $USER` (log out/in afterward).
4. `docker_compose_orchestration.py` additionally needs the Compose plugin
   (`docker compose version` should work) and the `python-on-whales` package.

### Virtual machine scripts (libvirt/VirtualBox)
1. Linux only. Install KVM + libvirt:
   `sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients virtinst`
2. Install libvirt's development headers so `pip install libvirt-python`
   can build: `sudo apt install libvirt-dev`
3. Add your user to the `libvirt` group, or run the scripts with `sudo`.
4. `vm_create_libvirt.py` needs `qemu-img` on PATH (comes with `qemu-kvm`).
5. `vm_clone.py` needs `virt-clone`, part of the `virtinst` package.

### Vagrant script
1. Install Vagrant: https://www.vagrantup.com/downloads
2. Install a provider (VirtualBox is the most common):
   https://www.virtualbox.org/wiki/Downloads
3. Have a working `Vagrantfile` in the directory you point `--dir` at.

### LXC/LXD script
1. Install and initialize LXD: `sudo snap install lxd && sudo lxd init`
2. Add your user to the `lxd` group, or run with `sudo`.

### Kubernetes scripts
1. Have access to a cluster (local via `minikube`/`kind`, or remote) and a
   valid `~/.kube/config` (or set the `KUBECONFIG` environment variable).
2. Confirm access first with `kubectl get nodes`.
3. Make sure your account/service account has RBAC permissions to
   create/list/delete pods and deployments in the target namespace.

### Helm script
1. Install Helm 3: https://helm.sh/docs/intro/install/
2. Confirm it works: `helm version`.
3. Have a chart directory or packaged `.tgz` chart ready.

---

## What "expected output" means in each script

Each script prints plain, human-readable confirmation lines so you can tell
at a glance whether the action succeeded — for example:

```
Image built successfully: myapp:latest (id=sha256:abc1234)
Container started: id=9f8e7d6c5b4a name=web status=running
Pod 'test-pod' created in namespace 'default'.
Release 'my-release' installed.
```

Failures print a clear error message (from the Docker/Kubernetes/libvirt
API or the underlying CLI tool) and the script exits with a non-zero exit
code, so you can chain these scripts in larger automation/CI pipelines and
detect failures reliably.

---

## Troubleshooting

- **"Cannot connect to the Docker daemon"** — Docker isn't running, or your
  user lacks permission to access `/var/run/docker.sock`.
- **`libvirt-python` fails to install via pip** — you're missing the system
  `libvirt-dev` (Debian/Ubuntu) or `libvirt-devel` (RHEL/Fedora) package.
- **`kubernetes` client raises a 403/Forbidden error** — your kubeconfig
  context doesn't have RBAC permission for that action in that namespace.
- **`helm` / `vagrant` / `virt-clone` "command not found"** — the
  corresponding CLI tool isn't installed or isn't on your `PATH`.

If you get stuck, re-run the failing script with `--help` to double check
the argument names, and confirm the underlying CLI tool works on its own
(e.g. `docker ps`, `virsh list`, `vagrant status`, `kubectl get pods`,
`helm list`) before assuming the Python script itself is broken.
