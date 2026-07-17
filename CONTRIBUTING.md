# 🤝 Contributing to Python System Administration

First off, thank you for considering contributing! This repository grows through community input, and every script, fix, or suggestion — big or small — is genuinely appreciated. 🙌

This document outlines how to contribute effectively, what we expect from submissions, and how the review process works.

---

## 📑 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Ways to Contribute](#-ways-to-contribute)
- [Before You Start](#-before-you-start)
- [Getting Set Up](#-getting-set-up)
- [Contribution Workflow](#-contribution-workflow)
- [Script Standards](#-script-standards)
- [Folder & Naming Conventions](#-folder--naming-conventions)
- [Commit Message Guidelines](#-commit-message-guidelines)
- [Pull Request Guidelines](#-pull-request-guidelines)
- [Review Process](#-review-process)
- [Reporting Bugs](#-reporting-bugs)
- [Suggesting Features](#-suggesting-features)
- [Reporting Security Issues](#-reporting-security-issues)
- [Recognition](#-recognition)

---

## 📜 Code of Conduct

This project adheres to a [Code of Conduct](./CODE_OF_CONDUCT.md). By participating, you agree to uphold it. Please read it before contributing.

---

## 🌱 Ways to Contribute

You don't need to write code to contribute. Here are ways to help:

- 🐍 **Add a new script** — a new automation example in an existing or new category
- 🐛 **Fix a bug** — correct broken logic, error handling, or edge cases
- 📝 **Improve documentation** — clarify comments, usage instructions, or the README
- ♻️ **Refactor existing code** — improve readability, performance, or PEP 8 compliance
- ✅ **Add tests** — unit tests for existing scripts (a currently underserved area!)
- 🌍 **Improve cross-platform support** — add Windows/macOS/Linux compatibility notes or handling
- 💡 **Suggest features** — propose new categories or automation ideas via Issues
- 🔍 **Report bugs or security issues**
- 🌐 **Translate documentation** (if/when translation support is added)

---

## ✅ Before You Start

- **Search existing [Issues](https://github.com/aw-junaid/Python-System-Administration/issues) and [Pull Requests](https://github.com/aw-junaid/Python-System-Administration/pulls)** to avoid duplicating work.
- For **large or structural changes** (new top-level categories, breaking changes to shared utilities), please open an Issue first to discuss the approach before investing significant time.
- For **small fixes** (typos, minor bugs, small script additions), feel free to open a PR directly.

---

## ⚙️ Getting Set Up

```bash
# 1. Fork the repository on GitHub, then clone your fork
git clone https://github.com/<your-username>/Python-System-Administration.git
cd Python-System-Administration

# 2. Add the upstream remote
git remote add upstream https://github.com/aw-junaid/Python-System-Administration.git

# 3. Create a virtual environment
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt
```

Keep your fork in sync before starting new work:

```bash
git fetch upstream
git checkout main
git merge upstream/main
```

---

## 🔁 Contribution Workflow

1. **Create a branch** from `main` with a descriptive name:
   ```bash
   git checkout -b feature/add-disk-usage-alert-script
   # or: fix/ssh-automation-timeout-bug
   ```
2. **Make your changes**, following the [Script Standards](#-script-standards) below.
3. **Test your changes** locally in a safe/sandbox environment.
4. **Commit** using the [commit message guidelines](#-commit-message-guidelines).
5. **Push** your branch to your fork:
   ```bash
   git push origin feature/add-disk-usage-alert-script
   ```
6. **Open a Pull Request** against the `main` branch of this repository.

---

## 🧑‍💻 Script Standards

To keep the repository consistent, professional, and genuinely useful, every script should:

- ✅ **Follow [PEP 8](https://peps.python.org/pep-0008/)** style conventions
- ✅ **Include a docstring or header comment** describing:
  - What the script does
  - Required dependencies (if any beyond the standard library)
  - Usage example / example command
  - Any platform-specific notes (Linux/Windows/macOS)
- ✅ **Use proper error handling** — avoid bare `except:`; catch specific exceptions and fail gracefully
- ✅ **Avoid hardcoded secrets** — use environment variables, config files (excluded via `.gitignore`), or placeholders clearly marked as such (e.g., `YOUR_API_KEY_HERE`)
- ✅ **Use logging** (`logging` module) instead of bare `print()` for anything beyond simple scripts, where practical
- ✅ **Be idempotent where possible** — safe to re-run without unintended side effects
- ✅ **Include a `requirements.txt` or inline pip install note** if the script needs third-party packages
- ❌ **Do not include destructive operations without safeguards** (e.g., confirmation prompts, dry-run flags) for anything that deletes data, modifies system state, or affects production infrastructure

### Example Header Template

```python
"""
Script: check_disk_usage.py
Description: Monitors disk usage and sends an alert if usage exceeds a threshold.
Platform: Linux, macOS, Windows
Dependencies: psutil (pip install psutil)
Usage: python3 check_disk_usage.py --threshold 85
"""
```

---

## 🗂️ Folder & Naming Conventions

- Place scripts in the most relevant existing category folder (e.g., `system-monitoring/`, `aws-automation/`).
- If your script doesn't fit an existing category, propose a new folder in your PR description.
- Use **snake_case** for filenames: `backup_mysql_database.py`, not `BackupMySQLDatabase.py`.
- Name files descriptively — prefer `list_ec2_instances.py` over `script1.py`.

---

## 📝 Commit Message Guidelines

Use clear, conventional commit messages:

```
<type>: <short description>

[optional longer description]
```

**Types:**
- `Add:` — new script or feature
- `Fix:` — bug fix
- `Update:` — modification to existing functionality
- `Docs:` — documentation-only changes
- `Refactor:` — code change that doesn't alter behavior
- `Test:` — adding or updating tests
- `Chore:` — maintenance tasks (dependencies, formatting, etc.)

**Examples:**
```
Add: script to automate S3 bucket lifecycle policies
Fix: handle timeout exception in ssh-automation/run_remote_commands.py
Docs: clarify usage instructions for backup-restore scripts
```

---

## 🔀 Pull Request Guidelines

When opening a PR, please:

- Give it a **clear, descriptive title** following the commit type convention above
- **Describe what changed and why** in the PR description
- **Reference related issues** (e.g., `Closes #42`)
- Confirm you've tested the script(s) and note the environment (OS, Python version)
- Keep PRs **focused** — one feature/fix per PR is easier to review than a large bundle of unrelated changes
- Ensure no secrets, credentials, or `.env` files are included in the diff

### PR Checklist

- [ ] Code follows PEP 8 style guidelines
- [ ] Script includes a header/docstring with description and usage
- [ ] No hardcoded secrets or credentials
- [ ] Tested locally in a safe environment
- [ ] Documentation updated (README/category notes) if applicable
- [ ] Commit messages follow the convention above

---

## 🔍 Review Process

- A maintainer will review your PR as soon as possible — response times may vary based on volume.
- You may be asked to make changes; this is a normal part of collaborative development, not a rejection.
- Once approved, your PR will be merged into `main`.
- If a PR is inactive for an extended period without response to review feedback, it may be closed and can be reopened later when you're ready to continue.

---

## 🐛 Reporting Bugs

Found something broken? [Open an Issue](https://github.com/aw-junaid/Python-System-Administration/issues/new) and include:

- A clear title and description
- Steps to reproduce
- Expected vs. actual behavior
- Environment details (OS, Python version, relevant package versions)
- Error messages / stack traces, if any

---

## 💡 Suggesting Features

Have an idea for a new script, category, or improvement? [Open an Issue](https://github.com/aw-junaid/Python-System-Administration/issues/new) with the `enhancement` label (if available) and describe:

- The problem it solves or use case it addresses
- A rough idea of implementation, if you have one
- Any relevant references or prior art

---

## 🔐 Reporting Security Issues

**Do not open a public issue for security vulnerabilities.** Please follow the private disclosure process outlined in [SECURITY.md](./SECURITY.md).

---

## 🌟 Recognition

All contributors are valued. Merged contributions are reflected in the repository's contributor graph, and significant contributions may be highlighted in release notes or the README.

---

## ❓ Questions?

If anything in this guide is unclear, reach out via [CONTACTME.md](./CONTACTME.md) or ask in the [Discord community](https://discord.gg/Neddn8gPqY).

---

<p align="center">
  Thank you for helping make this project better for everyone! 🐍💙
</p>
