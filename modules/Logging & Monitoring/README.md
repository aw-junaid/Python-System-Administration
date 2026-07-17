# Logging & Monitoring — Python Automation Scripts

A collection of standalone Python scripts covering common **logging** and
**monitoring** tasks for Linux system administration: generating and
rotating logs, monitoring system resources, running health checks, and
sending alerts to Email, Slack, Telegram, and Discord.

This module belongs to the
[Python-System-Administration](https://github.com/aw-junaid/Python-System-Administration)
repository, under:
`modules/Logging & Monitoring/scripts/`

> **Repository note for contributors:** if you are adding this code to the
> repo linked above, place all `.py` files from the `scripts/` folder into
> `modules/Logging & Monitoring/scripts/`, and place **this file**
> (`README.md`) at `modules/Logging & Monitoring/README.md` (i.e. one level
> up from `scripts/`, replacing/updating the existing README there). Put
> `requirements.txt` in the same folder as the README (or at the repo root,
> if that is the repo's existing convention — check how other modules in
> the repo do it and stay consistent).

---

## ⚠️ Caution Before You Start

- These scripts are for **learning and legitimate system administration**
  on systems you own or are authorized to manage.
- Several scripts read real system stats (CPU, memory, disk, processes) —
  run them on a machine/VM you control.
- Alerting scripts (`email_alert.py`, `slack_alert.py`, `telegram_alert.py`,
  `discord_webhook.py`) require **your own credentials/tokens/webhook
  URLs**. Never commit real credentials to GitHub — use environment
  variables (as shown below) or a local `.env` file excluded via
  `.gitignore`.
- `remote_log_sender.py` sends log data over a **plain TCP socket** (no
  encryption). Only use it on a trusted network, or place it behind a VPN/
  TLS proxy for production use.
- Scripts that monitor "services" (`monitor_services.py`, `health_check.py`)
  check for **running processes by name** — they do not require root, but
  results depend on what's actually running on your machine.
- Always review a script's code before running it, especially before
  scheduling it with `cron` or a systemd timer.

---

## 📁 Folder Structure

```
Logging & Monitoring/
├── README.md
├── requirements.txt
└── scripts/
    ├── generate_warnings.py
    ├── logging_basics.py
    ├── log_warnings_errors.py
    ├── log_exceptions.py
    ├── rotate_logs.py
    ├── compress_logs.py
    ├── remote_log_sender.py
    ├── monitor_app_logs.py
    ├── monitor_disk.py
    ├── monitor_cpu.py
    ├── monitor_memory.py
    ├── monitor_network.py
    ├── monitor_services.py
    ├── health_check.py
    ├── email_alert.py
    ├── slack_alert.py
    ├── telegram_alert.py
    ├── discord_webhook.py
    └── audit_log.py
```

---

## 🔧 Installation

Requires **Python 3.7+** on Linux (some scripts also work on macOS/WSL;
`monitor_services.py` process-name matching is most reliable on Linux).

```bash
# 1. Clone the repo (or navigate to this module if already cloned)
git clone https://github.com/aw-junaid/Python-System-Administration.git
cd "Python-System-Administration/modules/Logging & Monitoring"

# 2. (Recommended) create a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

`requirements.txt` contains:
```
psutil>=5.9.0
requests>=2.31.0
```

All scripts are run individually with `python3 scripts/<script_name>.py`.
Each script is self-contained — you do NOT need to run all of them, only
the ones relevant to your task.

---

## 📜 Script-by-Script Guide

### 1. `generate_warnings.py` — Generate warning messages
Demonstrates Python's built-in `warnings` module (distinct from logging).
```bash
python3 scripts/generate_warnings.py
```
**Expected output:** Console lines showing `RuntimeWarning`,
`DeprecationWarning`, and a custom `DiskSpaceWarning` being raised.

---

### 2. `logging_basics.py` — Python logging module fundamentals
Shows how to configure the `logging` module: levels, formatting, named
loggers.
```bash
python3 scripts/logging_basics.py
```
**Expected output:** Timestamped DEBUG/INFO/WARNING/ERROR/CRITICAL lines
printed to the console.

---

### 3. `log_warnings_errors.py` — Log warnings & error codes
Logs WARNING/ERROR messages tagged with custom error codes to a file.
```bash
python3 scripts/log_warnings_errors.py
```
**Expected output:** Console confirms the log path; a new file
`logs/warnings_errors.log` is created containing lines like:
```
2026-07-17 05:55:37 [WARNING] [code=W101] Disk usage above 80%
```

---

### 4. `log_exceptions.py` — Log exceptions with traceback
Shows `logger.exception()` and `exc_info=True` for capturing full
tracebacks (not just the error message).
```bash
python3 scripts/log_exceptions.py
```
**Expected output:** `logs/exceptions.log` is created with full Python
tracebacks for a `ZeroDivisionError` and a `ValueError`.

---

### 5. `rotate_logs.py` — Rotate log files
Uses `RotatingFileHandler` to rotate logs automatically once a file
exceeds a size limit, keeping a fixed number of backups.
```bash
python3 scripts/rotate_logs.py
```
**Expected output:** In `logs/`, you'll see `rotating.log`,
`rotating.log.1`, `.2`, `.3` — older entries pushed into numbered backups.

---

### 6. `compress_logs.py` — Compress old logs
Scans a directory and gzip-compresses `.log` files older than N days,
removing the original.
```bash
# Demo: compress everything immediately
python3 scripts/compress_logs.py --dir logs --days 0

# Production: only compress logs older than 7 days
python3 scripts/compress_logs.py --dir logs --days 7
```
**Expected output:** Console lines like
`Compressed: logs/exceptions.log -> logs/exceptions.log.gz`; original
`.log` files are removed and replaced with `.gz` files.

---

### 7. `remote_log_sender.py` — Send logs to a remote server
Includes both a demo TCP log receiver (server) and a sender (client)
using `logging.handlers.SocketHandler`.
```bash
# Terminal 1 (start receiver)
python3 scripts/remote_log_sender.py --mode server --port 9020

# Terminal 2 (send sample logs)
python3 scripts/remote_log_sender.py --mode client --host 127.0.0.1 --port 9020
```
**Expected output:** The server terminal prints
`[REMOTE LOG] INFO: Client started - sending sample log messages` and
similar lines for WARNING/ERROR as they arrive from the client.

---

### 8. `monitor_app_logs.py` — Monitor application logs
Tails a log file (like `tail -f`) and flags lines containing keywords
such as `ERROR`, `CRITICAL`, `FAILED`.
```bash
python3 scripts/monitor_app_logs.py --file logs/warnings_errors.log
```
**Expected output:** Runs continuously; prints `[ALERT] Matched 'ERROR': ...`
whenever a new matching line is appended to the file. Stop with `Ctrl+C`.

---

### 9. `monitor_disk.py` — Monitor disk usage
```bash
python3 scripts/monitor_disk.py --path / --threshold 80
```
**Expected output:** Disk usage percentage, total/used/free space, and an
`[OK]` or `[WARNING]` verdict based on the threshold.

---

### 10. `monitor_cpu.py` — Monitor CPU usage
```bash
python3 scripts/monitor_cpu.py --threshold 85 --interval 1
```
**Expected output:** Overall and per-core CPU percentage, plus an `[OK]`/
`[WARNING]` verdict.

---

### 11. `monitor_memory.py` — Monitor memory usage
```bash
python3 scripts/monitor_memory.py --threshold 80
```
**Expected output:** RAM total/used/available and swap usage percentages,
with an `[OK]`/`[WARNING]` verdict.

---

### 12. `monitor_network.py` — Monitor network usage
```bash
python3 scripts/monitor_network.py --interval 2
```
**Expected output:** Upload/download throughput in KB/s over the sampling
window, plus per-interface UP/DOWN status.

---

### 13. `monitor_services.py` — Monitor running services
Checks whether named processes (e.g. `sshd`, `nginx`, `mysql`) are
currently running.
```bash
python3 scripts/monitor_services.py --services sshd,cron,nginx
```
**Expected output:** `[OK]`/`[WARNING]` per service, plus a summary of any
that are down.

---

### 14. `health_check.py` — Combined health check script
Runs CPU, memory, disk, and service checks together in one report. Exits
with status code `1` if any check fails (useful for cron/CI).
```bash
python3 scripts/health_check.py --cpu-threshold 85 --mem-threshold 80 \
    --disk-threshold 80 --disk-path / --services sshd,cron
```
**Expected output:** A full report ending in either
`HEALTH CHECK PASSED - all systems normal` (exit code 0) or
`HEALTH CHECK FAILED - N issue(s) found` (exit code 1).

---

### 15. `email_alert.py` — Email alerts
Sends an alert email via SMTP (Gmail, Outlook, etc.).
```bash
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=you@gmail.com
export SMTP_PASSWORD=your_app_password   # use an App Password, not your real password
python3 scripts/email_alert.py --to admin@example.com --subject "Disk Alert" --message "Disk usage is at 90%"
```
**Expected output:** `Email alert sent to admin@example.com` if
credentials/env vars are correct; a clear error message otherwise. Gmail
users must enable 2FA and generate an **App Password** — normal account
passwords are rejected.

---

### 16. `slack_alert.py` — Slack alerts
Sends a message to a Slack channel via an Incoming Webhook.
```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/XXX/YYY/ZZZ"
python3 scripts/slack_alert.py --message "Disk usage is at 90% on server1"
```
Setup: Slack → https://api.slack.com/apps → Create app → Enable Incoming
Webhooks → copy Webhook URL.
**Expected output:** `Slack alert sent successfully.` and the message
appears in the configured Slack channel.

---

### 17. `telegram_alert.py` — Telegram alerts
Sends a message to a Telegram chat via a Telegram Bot.
```bash
export TELEGRAM_BOT_TOKEN="123456789:ABC-defGhIJKlmNoPQRstuVWXyz"
export TELEGRAM_CHAT_ID="123456789"
python3 scripts/telegram_alert.py --message "Backup job failed on server1"
```
Setup: message `@BotFather` on Telegram → `/newbot` → get token → start a
chat with the bot → get your chat ID from
`https://api.telegram.org/bot<token>/getUpdates`.
**Expected output:** `Telegram alert sent successfully.` and the message
appears in the Telegram chat.

---

### 18. `discord_webhook.py` — Discord webhook notifications
Sends a message to a Discord channel via a Webhook URL.
```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/XXX/YYY"
python3 scripts/discord_webhook.py --message "CPU usage exceeded 90% on server1"
```
Setup: Discord channel → Edit Channel → Integrations → Webhooks → New
Webhook → copy URL.
**Expected output:** `Discord alert sent successfully.` and the message
appears in the Discord channel.

---

### 19. `audit_log.py` — Generate audit logs
Writes structured, JSON-Lines-formatted audit trail entries (who did
what, when) — easy to feed into tools like ELK or Splunk.
```bash
python3 scripts/audit_log.py
```
**Expected output:** `logs/audit.log` is created with one JSON object per
line, e.g.:
```json
{"timestamp": "2026-07-17T05:55:37+00:00", "level": "INFO", "event": "login", "user": "ahmad", "details": "User logged in from 192.168.1.10"}
```

---

## 🗓️ Automating with Cron (optional)

Once you've verified a script works manually, you can schedule it, e.g.
run the health check every 15 minutes:
```bash
crontab -e
# add this line:
*/15 * * * * /usr/bin/python3 /path/to/scripts/health_check.py --services sshd,nginx >> /var/log/health_check_cron.log 2>&1
```

---

## 🩺 Troubleshooting

| Problem | Likely Cause |
|---|---|
| `ModuleNotFoundError: No module named 'psutil'` or `'requests'` | Run `pip install -r requirements.txt` inside your active virtual environment |
| Email alert fails with auth error | Use an App Password (Gmail), not your normal login password |
| Slack/Telegram/Discord script prints "Missing ... environment variable" | You forgot to `export` the required variable in the current shell session |
| `monitor_services.py` shows a service as "NOT RUNNING" that you know is running | Process name matching is case-insensitive substring match — check the exact process name with `ps aux \| grep <name>` |
| Permission errors monitoring disk/processes | Some systems restrict `psutil` process info for other users — try running with appropriate permissions, not necessarily root |
