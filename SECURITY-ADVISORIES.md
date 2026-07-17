# 📋 Security Advisories

This document is a running log of security advisories relevant to the **Python System Administration** repository — including vulnerabilities found in repository scripts, as well as notable CVEs in third-party dependencies commonly used by these scripts (e.g., `boto3`, `paramiko`, `psutil`, `requests`).

For how to report a new vulnerability, see [SECURITY.md](./SECURITY.md).

---

## 📖 How to Read This Log

Each advisory entry follows this format:

```
### [ADV-YYYY-NNN] Short Title
- **Date Published:**
- **Severity:** Critical / High / Medium / Low  (CVSS score if available)
- **Type:** Repository Script | Dependency (Third-Party)
- **Affected Component(s):**
- **Affected Versions / Commits:**
- **Fixed In:**
- **Credit:**
- **Description:**
- **Impact:**
- **Remediation / Mitigation:**
- **References:**
```

- **Repository Script** advisories cover vulnerabilities found directly in code within this repo (e.g., command injection, insecure defaults, credential leakage).
- **Dependency (Third-Party)** advisories cover CVEs in libraries this repo's scripts rely on, published here for visibility even though the fix originates upstream.

Advisories are listed in **reverse chronological order** (newest first).

---

## 🗂️ Active Advisories

> _No active advisories at this time._

There are currently no known unresolved vulnerabilities affecting this repository. This log will be updated as soon as a report is triaged and confirmed. To report a suspected vulnerability, see the [reporting process in SECURITY.md](./SECURITY.md#-reporting-a-vulnerability).

---

## ✅ Resolved Advisories

> _No resolved advisories have been published yet._

Once a reported vulnerability is confirmed and patched, its full advisory record will be moved here for historical reference and transparency.

---

## 🔎 Monitoring Third-Party Dependencies

In addition to advisories on this page, users are encouraged to independently monitor CVEs for libraries used across this repository, since upstream vulnerabilities can affect any script that imports them:

| Library | Used For | Advisory Source |
|---|---|---|
| `boto3` / `botocore` | AWS Automation | [GitHub Advisories](https://github.com/boto/boto3/security/advisories) |
| `paramiko` | SSH Automation | [GitHub Advisories](https://github.com/paramiko/paramiko/security/advisories) |
| `requests` | REST API / Web Automation | [GitHub Advisories](https://github.com/psf/requests/security/advisories) |
| `psutil` | System Monitoring | [GitHub Advisories](https://github.com/giampaolo/psutil/security/advisories) |
| `pymongo` | Database Administration | [GitHub Advisories](https://github.com/mongodb/mongo-python-driver/security/advisories) |
| `psycopg2` | Database Administration | [PostgreSQL Security](https://www.postgresql.org/support/security/) |
| `docker` (SDK) | Docker Automation | [GitHub Advisories](https://github.com/docker/docker-py/security/advisories) |
| `kubernetes` client | Kubernetes Automation | [Kubernetes Security](https://kubernetes.io/docs/reference/issues-security/security/) |
| `cryptography` | Security Automation | [PyPA Advisory DB](https://github.com/pypa/advisory-database) |

Running the following locally is recommended to catch known vulnerabilities in your installed environment:

```bash
pip install pip-audit
pip-audit
```

or

```bash
pip install safety
safety check
```

---

## 📬 Reporting

To report a new vulnerability for inclusion in this log, follow the private reporting process outlined in [SECURITY.md](./SECURITY.md#-reporting-a-vulnerability). Do not open a public issue for unpatched vulnerabilities.

---

<p align="center">
  This log is maintained as part of the project's commitment to transparency and user safety. 🔐
</p>
