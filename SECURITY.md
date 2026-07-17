# 🔐 Security Policy

Thank you for helping keep **Python System Administration** and its users safe. This document outlines which versions receive security updates, how to report a vulnerability, and what to expect after you do.

---

## 📌 Supported Versions

This repository is a collection of standalone scripts and utilities rather than a versioned software package. Security fixes are applied to the **latest commit on the `main` branch** only.

| Branch / Version | Supported |
|---|---|
| `main` (latest) | ✅ Yes |
| Older commits / forks | ❌ No |
| Archived or deprecated scripts | ❌ No |

> [!NOTE]
> If a specific script or folder is later split into its own versioned package (e.g., published to PyPI), that package will maintain its own supported-version table.

---

## 🚨 Reporting a Vulnerability

If you discover a security vulnerability in any script, dependency usage, or documentation in this repository, **please do not open a public GitHub issue**. Public disclosure before a fix is available can put users at risk.

Instead, report it privately using one of the following methods, in order of preference:

1. **GitHub Private Vulnerability Reporting** (preferred)
   Go to the [Security tab](https://github.com/aw-junaid/Python-System-Administration/security) of this repository and select **"Report a vulnerability"**.

2. **Email**
   Send details to **awjunaid@proton.me** with the subject line: `SECURITY: [short description]`

3. **Discord (for initial contact only)**
   You may reach out on [Discord](https://discord.gg/Neddn8gPqY) to establish a private communication channel — do **not** post vulnerability details in public channels.

### What to Include in Your Report

To help us triage and resolve the issue quickly, please include as much of the following as possible:

- A clear description of the vulnerability and its potential impact
- The affected script(s), file path(s), or folder(s)
- Steps to reproduce (proof-of-concept code, commands, or inputs)
- The environment in which it was discovered (OS, Python version, dependency versions)
- Any suggested remediation or patch, if you have one
- Whether the issue is already publicly known or exploited

---

## ⏱️ Response Process & Timeline

| Stage | Target Timeframe |
|---|---|
| Acknowledgment of report | Within 3 business days |
| Initial assessment / triage | Within 7 business days |
| Status update to reporter | At least every 14 days until resolved |
| Fix, mitigation, or advisory published | Depends on severity and complexity |

Once a fix is available:
- A patched version of the affected script(s) will be committed to `main`.
- A **GitHub Security Advisory** will be published for confirmed, meaningful vulnerabilities.
- Credit will be given to the reporter in the advisory and/or release notes, unless anonymity is requested.

We ask that you give us reasonable time to investigate and remediate before any public disclosure (**coordinated disclosure**), generally **90 days** from initial report, unless otherwise agreed.

---

## 🎯 Scope

### In Scope
- Vulnerabilities in scripts contained within this repository (e.g., insecure subprocess calls, command injection, path traversal, insecure deserialization, hardcoded credentials, unsafe use of `eval`/`exec`, SSRF in API/web automation scripts, credential leakage, insecure default configurations)
- Misuse of cloud SDKs (AWS/Azure/GCP) that could lead to privilege escalation or unintended resource exposure
- Insecure handling of secrets, tokens, or SSH keys in example code
- Supply-chain concerns involving pinned dependencies referenced by this repository

### Out of Scope
- Vulnerabilities in third-party libraries themselves (please report these directly to the upstream project, e.g., `boto3`, `paramiko`, `psutil`)
- Issues requiring physical access to a user's machine
- Vulnerabilities resulting from a user modifying scripts insecurely for their own environment
- Social engineering or phishing attempts unrelated to repository content
- Automated vulnerability scanner output submitted without validation or context

---

## ✅ Security Best Practices for Users

Since this repository contains **example and educational automation scripts**, please observe the following before using any script in a production environment:

- 🔍 **Review every script** before execution — understand what it does, especially scripts that touch credentials, run shell commands, or make network/cloud API calls.
- 🔑 **Never hardcode secrets** (API keys, passwords, tokens). Use environment variables, `.env` files (excluded via `.gitignore`), or a secrets manager (e.g., HashiCorp Vault, AWS Secrets Manager).
- 🧪 **Test in a staging/sandbox environment** before running automation against production systems.
- 🔒 **Apply the principle of least privilege** when configuring cloud IAM roles, SSH keys, or database credentials used by these scripts.
- 📦 **Keep dependencies updated** — run `pip list --outdated` and audit with tools like `pip-audit` or `safety` regularly.
- 🧾 **Enable logging and monitoring** for any script that performs destructive or system-altering operations (e.g., backup/restore, user management, firewall changes).
- 🚫 **Do not commit `.env`, credentials, `.pem`/`.key` files, or cloud config files** to version control.

---

## 📢 Disclosure Policy

- We follow a **coordinated disclosure** model: vulnerabilities are kept private until a fix is available and users have had reasonable time to update.
- Publicly disclosed CVEs or advisories relevant to dependencies used in this repo will be noted in the repository's [Issues](https://github.com/aw-junaid/Python-System-Administration/issues) or a `SECURITY-ADVISORIES.md` file if applicable.
- Reporters acting in good faith, making a reasonable effort to avoid privacy violations, data destruction, or service disruption, and reporting through the proper channel above will not face legal action from the maintainer for their research.

---

## 🙏 Acknowledgments

We appreciate the security research community and everyone who responsibly discloses issues. Confirmed reporters will be credited here and/or in relevant advisories (unless anonymity is requested).

---

## 📬 Contact

- **Email:** awjunaid@proton.me
- **GitHub Security Advisories:** [github.com/aw-junaid/Python-System-Administration/security](https://github.com/aw-junaid/Python-System-Administration/security)
- **Discord:** [Join Server](https://discord.gg/Neddn8gPqY)
- **Website:** [awjunaid.com](https://awjunaid.com/)

---

<p align="center">
  Thank you for helping keep this project and its community secure. 🔐
</p>
