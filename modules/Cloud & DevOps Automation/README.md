# Cloud & DevOps Automation — Python Automation Scripts

This folder contains **13 standalone Python scripts**, each automating a single, specific cloud or DevOps task (AWS, Azure, GCP, Docker, Docker Compose, Kubernetes, Terraform, Ansible, Git, GitHub, GitLab, CI/CD pipelines, and serverless deployment).

Every script:
- Is completely **independent** — you only need the one file (plus its specific dependency) for the task you want.
- Can be run directly from the command line.
- Uses `argparse` with subcommands, so running it with `-h` shows help and usage.
- Fails gracefully with a clear message when credentials, tools, or packages are missing — no raw stack traces.

> **Repository:** https://github.com/aw-junaid/Python-System-Administration/tree/main/modules/Cloud%20%26%20DevOps%20Automation/scripts

---

## ⚠️ Important Cautions Before You Start

1. **These scripts can create, modify, and delete real cloud resources, containers, repositories, and pipelines.** Starting/stopping cloud VMs incurs cost; creating Lambda functions, Kubernetes deployments, or GitHub releases has real, visible effects. **Always test against a sandbox/free-tier account or a disposable test project first.**
2. **None of these scripts embed credentials.** They all read credentials from the standard mechanism for that platform (environment variables, CLI login sessions, or config files) — see the Requirements section for each. Never hardcode secrets into these scripts or commit them to git.
3. **Destructive actions have no built-in "undo.":** deleting a Kubernetes deployment, force-removing a Docker container, running `terraform destroy`, or merging a PR/MR are all immediate and (mostly) irreversible from the script's point of view.
4. **`terraform_execution.py apply` and `destroy` can create or delete real infrastructure and cost money.** Always run `plan` first and read the output before `apply`. Use `--auto-approve` only once you're confident — it skips Terraform's own interactive confirmation.
5. **`docker_automation.py` requires Docker Desktop/Engine to be installed and running** — it talks to the local Docker daemon, not a remote service.
6. **`kubernetes_automation.py` acts on whatever cluster your current kubeconfig context points to** — double-check `kubectl config current-context` before creating/deleting/scaling resources, especially if you have both a local and production cluster configured.
7. **`ansible_integration.py` is Linux/macOS only** as a control node (run it inside WSL if you're on Windows).
8. **API tokens (GitHub, GitLab) should have the minimum scope needed** and be treated like passwords — prefer environment variables (`GITHUB_TOKEN`, `GITLAB_TOKEN`) over passing them as command-line flags where possible, since command-line arguments can be visible in shell history and process lists.

---

## 📦 Requirements

- **Python 3.9+** installed on your system.
- Check your version:
  ```bash
  python3 --version
  ```
- Each script needs only **its own specific package(s)** — you do not need to install everything in `requirements.txt` unless you plan to use all 13 scripts. See the mapping inside `requirements.txt` or each script's docstring.
- Several scripts also require an **external CLI tool or running service** already installed (Docker Engine, Terraform CLI, Ansible, Azure Functions Core Tools) — these are **not** Python packages and must be installed separately. Each script checks for these and tells you exactly what's missing and how to install it.

---

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/aw-junaid/Python-System-Administration.git
   cd "Python-System-Administration/modules/Cloud & DevOps Automation/scripts"
   ```

2. **(Recommended) Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate        # On Windows: venv\Scripts\activate
   ```

3. **Install only what you need**, for example:
   ```bash
   pip install boto3                    # for aws_automation.py
   pip install GitPython                # for git_automation.py
   pip install PyGithub                 # for github_api_automation.py
   ```
   Or install everything at once:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run any script:**
   ```bash
   python3 script_name.py --help
   ```
   This shows every subcommand and argument the script supports.

---

## 🗂 Full List of Scripts, Usage & Expected Output

Below, `python3` is used for Linux/macOS. On Windows, use `python` instead.

### 264. `aws_automation.py` — AWS Automation (boto3)
**Requires:** `pip install boto3` + AWS credentials (`aws configure`, env vars, or IAM role)
```bash
python3 aws_automation.py ec2-list --region us-east-1
python3 aws_automation.py s3-upload my-bucket ./report.pdf --key reports/report.pdf
python3 aws_automation.py iam-list-users
```
**Expected output:** Tables of EC2 instances (ID/state/type/name), S3 buckets/objects, or IAM users. Missing credentials produce a clear error pointing to `aws configure`, not a stack trace.

---

### 265. `azure_automation.py` — Azure Automation
**Requires:** `pip install azure-identity azure-mgmt-compute azure-storage-blob` + `az login` or a service principal
```bash
python3 azure_automation.py vm-list <subscription_id> <resource_group>
python3 azure_automation.py blob-upload https://myaccount.blob.core.windows.net mycontainer ./report.pdf
```
**Expected output:** VM name/size/power-state listings, or blob container listings and upload confirmations.

---

### 266. `gcp_automation.py` — Google Cloud Automation
**Requires:** `pip install google-cloud-compute google-cloud-storage` + `gcloud auth application-default login`
```bash
python3 gcp_automation.py compute-list my-project us-central1-a
python3 gcp_automation.py storage-upload my-bucket ./report.pdf
```
**Expected output:** Compute Engine instance name/status/type, or Cloud Storage bucket listings and upload confirmations.

---

### 267. `docker_automation.py` — Docker Automation
**Requires:** `pip install docker` + Docker Desktop/Engine running
```bash
python3 docker_automation.py build myapp:latest .
python3 docker_automation.py run myapp:latest --name myapp-container --ports 8080:80 --detach
python3 docker_automation.py list
python3 docker_automation.py logs myapp-container
python3 docker_automation.py stop myapp-container
```
**Expected output:** Build log streamed to console, container ID/name on run, a table of containers with status, log output, or stop/remove confirmations.

---

### 268. `docker_compose_automation.py` — Docker Compose Automation
**Requires:** `pip install pyyaml` + Docker with the `docker compose` plugin
```bash
python3 docker_compose_automation.py list-services docker-compose.yml
python3 docker_compose_automation.py set-image docker-compose.yml web nginx:1.25
python3 docker_compose_automation.py up docker-compose.yml --detach
```
**Expected output:** Service listings, confirmation of YAML edits (image/env changes actually written back to the file), or live `docker compose up`/`down` output.

---

### 269. `kubernetes_automation.py` — Kubernetes Automation
**Requires:** `pip install kubernetes` + a working kubeconfig
```bash
python3 kubernetes_automation.py list-pods --namespace default
python3 kubernetes_automation.py create-deployment web-app nginx:latest --replicas 3 --port 80
python3 kubernetes_automation.py scale-deployment web-app 5
```
**Expected output:** Pod/deployment tables with status and ready-replica counts, or creation/scaling/deletion confirmations.
**Caution:** Acts on whichever cluster your current kubeconfig context points to.

---

### 270. `terraform_execution.py` — Terraform Execution
**Requires:** the `terraform` CLI installed (no Python packages needed)
```bash
python3 terraform_execution.py generate ./infra --provider aws --region us-east-1
python3 terraform_execution.py init ./infra
python3 terraform_execution.py plan ./infra
python3 terraform_execution.py apply ./infra --auto-approve
```
**Expected output:** A generated starter `main.tf`, then live `terraform init/plan/apply/destroy` output streamed to your console.
**Caution:** `apply`/`destroy` create/delete real infrastructure — always review `plan` output first.

---

### 271. `ansible_integration.py` — Ansible Integration
**Requires:** `pip install ansible` (Linux/macOS control node only)
```bash
python3 ansible_integration.py generate-inventory inventory.ini --hosts 10.0.0.1,10.0.0.2 --group webservers
python3 ansible_integration.py ping inventory.ini
python3 ansible_integration.py run-playbook deploy.yml --inventory inventory.ini
```
**Expected output:** A generated INI inventory file, live `ansible`/`ansible-playbook` output (host reachability, task results per host).

---

### 272. `git_automation.py` — Git Automation
**Requires:** `pip install GitPython` + git installed
```bash
python3 git_automation.py status ./myproject
python3 git_automation.py commit ./myproject "Fix login bug" --add-all
python3 git_automation.py push ./myproject
python3 git_automation.py clone https://github.com/user/repo.git ./repo
python3 git_automation.py log ./myproject --count 10
```
**Expected output:** Status summary (modified/staged/untracked files), commit hash confirmation, push/pull result summaries, or a commit history table. Works correctly on brand-new repos with zero commits as well as established ones.

---

### 273. `github_api_automation.py` — GitHub API Automation
**Requires:** `pip install PyGithub` + a GitHub token (`GITHUB_TOKEN` env var or `--token`)
```bash
export GITHUB_TOKEN=ghp_yourtokenhere
python3 github_api_automation.py list-prs octocat/Hello-World
python3 github_api_automation.py create-pr myorg/myrepo "Add feature X" feature-branch main
python3 github_api_automation.py create-release myorg/myrepo v1.2.0 "Version 1.2.0"
```
**Expected output:** PR/release listings with numbers, titles, and branches; creation confirmations with the resulting URL.

---

### 274. `gitlab_api_automation.py` — GitLab API Automation
**Requires:** `pip install python-gitlab` + a GitLab token (`GITLAB_TOKEN` env var or `--token`)
```bash
export GITLAB_TOKEN=glpat-yourtokenhere
python3 gitlab_api_automation.py list-mrs 12345678
python3 gitlab_api_automation.py trigger-pipeline 12345678 main
python3 gitlab_api_automation.py pipeline-status 12345678 987654321
```
**Expected output:** MR/pipeline listings with IDs and statuses; pipeline trigger confirmation with a live status and URL.

---

### 275. `cicd_automation.py` — CI/CD Automation
**Requires:** `pip install pyyaml`
```bash
python3 cicd_automation.py generate pipeline.yml
python3 cicd_automation.py run pipeline.yml
python3 cicd_automation.py run pipeline.yml --continue-on-error
```
**Expected output:** Generates an example YAML pipeline (edit the `command` per stage), then runs each stage as a shell command in order, printing PASS/FAIL per stage and a final summary table. Stops at the first failure unless `--continue-on-error` is given; exits non-zero if any stage failed.

---

### 276. `serverless_deploy.py` — Serverless Function Deployment
**Requires:** `pip install boto3` (AWS path); Azure Functions Core Tools CLI (Azure path)
```bash
python3 serverless_deploy.py package ./my_function ./my_function.zip
python3 serverless_deploy.py aws-deploy my-function ./my_function.zip arn:aws:iam::123456789012:role/lambda-role
python3 serverless_deploy.py aws-update my-function ./my_function.zip
python3 serverless_deploy.py azure-deploy my-function-app ./my_function
```
**Expected output:** A ZIP package (excluding `__pycache__`/`.git`/venvs), then AWS Lambda create/update confirmation with the function ARN/version, or live Azure Functions Core Tools publish output.

---

## 🧪 Quick Test Workflow

To safely try the credential-free / local scripts without touching real cloud resources:

```bash
mkdir test_area && cd test_area
python3 ../cicd_automation.py generate pipeline.yml
python3 ../cicd_automation.py run pipeline.yml
python3 ../terraform_execution.py generate ./infra --provider aws --region us-east-1
git init && git config user.email "you@example.com" && git config user.name "You"
echo "hello" > file.txt
python3 ../git_automation.py status .
python3 ../git_automation.py commit . "Test commit" --add-all
python3 ../git_automation.py log . --count 5
```

---

## 📄 License / Usage Notes

- These scripts are provided for educational and administrative automation purposes.
- Always review a script's code before running it against real cloud accounts, production clusters, or shared repositories.
- The author is not responsible for cloud costs, data loss, or service disruption resulting from misuse — especially with resource creation/deletion, `terraform apply`/`destroy`, and Kubernetes scaling/deletion operations.
