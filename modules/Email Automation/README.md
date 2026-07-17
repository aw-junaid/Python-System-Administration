# Email Automation — Python Scripts

Companion scripts for the **Email Automation** module of
[Python-System-Administration](https://github.com/aw-junaid/Python-System-Administration/tree/main/modules/Email%20Automation/scripts).

**Every script can be run directly. If you haven't configured real email credentials
yet, each script safely runs in **DRY-RUN / DEMO mode** and prints exactly what it *would* have
sent or fetched — nothing goes out over the network until you configure credentials.**

---

## ⚠️ Read This Before Running Anything

- These scripts **send and receive real email** once you configure credentials. Double-check
  recipient addresses, especially in `bulk_email_sender.py`, before running outside dry-run mode
  — there is no confirmation prompt before sending.
- **Never hard-code your email password inside any script.** All credentials are read from
  environment variables (see below). Do not commit real credentials to version control.
- Most providers (Gmail, Outlook, Yahoo, etc.) require an **app-specific password** instead of
  your normal login password when two-factor authentication is enabled. Check your provider's
  account security settings to generate one.
- Some providers require you to **explicitly enable IMAP/SMTP access** in account settings before
  these scripts can connect at all.
- `bulk_email_sender.py` sends to every row in your CSV file. Only use it for recipients who have
  actually opted in, and follow anti-spam laws that apply to you (e.g. CAN-SPAM, GDPR, CASL),
  including offering a way to unsubscribe.
- `receive_emails.py` and `parse_email.py` are **read-only** — they never delete, modify, or mark
  emails as read/unread.

---

## Requirements

- Python 3.8+
- No third-party packages are required — everything uses the standard library
  (`smtplib`, `imaplib`, `email`, `csv`).

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/aw-junaid/Python-System-Administration.git
cd "Python-System-Administration/modules/Email Automation/scripts"

# 2. (Recommended) create a virtual environment
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. (Optional) install requirements — kept for consistency, currently empty
pip install -r requirements.txt
```

---

## Configure Your Email Credentials

All sending scripts (`send_email.py`, `send_html_email.py`,
`send_email_with_attachment.py`, `bulk_email_sender.py`, `email_notifier.py`) read SMTP
credentials from environment variables:

```bash
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=you@example.com
export SMTP_PASSWORD=your-app-specific-password
```

The receiving script (`receive_emails.py`) reads IMAP credentials:

```bash
export IMAP_HOST=imap.gmail.com
export IMAP_USER=you@example.com
export IMAP_PASSWORD=your-app-specific-password
```

On Windows (PowerShell), use `$env:SMTP_HOST = "smtp.gmail.com"` instead of `export`.

**If these variables are not set, every script runs safely in DRY-RUN / DEMO mode** and prints
sample output instead of connecting to a real server.

---

## How to Run Any Script

```bash
python3 <script_name>.py [arguments]
```

If you run a script **with no arguments** (and no credentials configured), it shows you exactly
what it would do, using demo data it generates itself.

---

## Script Reference

| # | Script | Topic | Run Example |
|---|--------|-------|-------------|
| 1 | `send_email.py` | Send Emails | `python3 send_email.py --to a@example.com --subject "Hi" --body "Hello"` |
| 2 | `send_html_email.py` | Send HTML Emails | `python3 send_html_email.py --to a@example.com --subject "Newsletter"` |
| 3 | `send_email_with_attachment.py` | Send Attachments | `python3 send_email_with_attachment.py --to a@example.com --attach report.pdf` |
| 4 | `receive_emails.py` | Receive Emails | `python3 receive_emails.py --limit 5` |
| 5 | `parse_email.py` | Parse Email Contents | `python3 parse_email.py message.eml` |
| 6 | `bulk_email_sender.py` | Bulk Email Automation | `python3 bulk_email_sender.py --csv recipients.csv` |
| 7 | `email_notifier.py` | Email Notifications | `python3 email_notifier.py --to a@example.com --event "Backup" --status success` |

---

## Detailed Usage & Expected Output

### 1. `send_email.py`
Sends a plain text email via SMTP.
```bash
python3 send_email.py --to recipient@example.com --subject "Hello" --body "This is a test email."
```
**Expected output (real send):**
```
Connecting to smtp.gmail.com:587 as you@example.com...
Email sent successfully to recipient@example.com.
```
**Caution:** uses STARTTLS on the configured port (typically 587). If your provider needs
implicit SSL (port 465), switch to `smtplib.SMTP_SSL` as noted in the script's comments.

### 2. `send_html_email.py`
Sends an HTML email with an automatic plain-text fallback part.
```bash
python3 send_html_email.py --to recipient@example.com --subject "Newsletter"
```
**Caution:** always includes a plain-text alternative so non-HTML clients still show readable
content. HTML with excessive links/images can trigger spam filters — test with a real inbox
first.

### 3. `send_email_with_attachment.py`
Sends an email with one or more file attachments.
```bash
python3 send_email_with_attachment.py --to recipient@example.com --subject "Report" \
    --body "See attached." --attach report.pdf --attach summary.xlsx
```
**Caution:** most providers cap total message size around 20-25 MB; oversized attachments are
rejected by the SMTP server, not silently truncated. The whole file is read into memory before
sending.

### 4. `receive_emails.py`
Lists recent emails from an IMAP mailbox (sender, subject, date).
```bash
python3 receive_emails.py --limit 5 --unread-only
```
**Caution:** read-only — never deletes, moves, or marks messages. Connects over IMAP SSL
(port 993) by default.

### 5. `parse_email.py`
Parses a saved `.eml` file and extracts sender, subject, date, body text, and attachment
filenames.
```bash
python3 parse_email.py message.eml
```
**Caution:** does not connect to any mail server — it only reads a file already on disk (export
one from your mail client, or save one fetched via `receive_emails.py`'s underlying IMAP
connection). Does not extract attachment file contents, only lists filenames, to avoid writing
arbitrary files to disk unexpectedly.

### 6. `bulk_email_sender.py`
Sends a personalized email to every recipient listed in a CSV file, substituting columns like
`{name}` into your subject/body templates.
```bash
python3 bulk_email_sender.py --csv recipients.csv \
    --subject "Hello {name}" --body "Hi {name}, thanks for signing up!"
```
CSV format:
```csv
email,name
alice@example.com,Alice
bob@example.com,Bob
```
**⚠️ Sends to every row in the CSV with no confirmation prompt.** Includes a 1-second delay
between sends to reduce rate-limit risk — increase `SEND_DELAY_SECONDS` in the script for larger
lists. Only email people who have opted in.

### 7. `email_notifier.py`
A reusable notification helper for your own automation scripts — send yourself an alert when a
job succeeds or fails.
```bash
python3 email_notifier.py --to you@example.com --event "Backup Job" \
    --status success --message "Backup completed in 4m12s."
```
**Tip:** import `send_notification()` directly into your own scripts instead of shelling out:
```python
from email_notifier import send_notification
send_notification(smtp_host, smtp_port, smtp_user, smtp_password,
                   "you@example.com", "Backup Job", "success", "Backup completed in 4m12s.")
```
**Caution:** avoid calling this in a tight retry loop without your own cooldown logic, or you may
flood your inbox or hit provider rate limits.

---

## General Notes

- Every script can be run standalone — none depend on each other at import time (except
  `email_notifier.py`, which is also designed to be imported as a helper — see above).
- Every sending/receiving script falls back to a **safe DRY-RUN or DEMO mode** automatically when
  SMTP/IMAP environment variables aren't set, so you can always see expected output before
  connecting to a real server.
- Where a script sends real email or touches a real mailbox, its docstring contains an explicit
  **Caution** section — read it before configuring real credentials.
- Tested on Linux (Ubuntu) with Python 3.12. All scripts use standard library modules only and
  should work unmodified on macOS and Windows.
