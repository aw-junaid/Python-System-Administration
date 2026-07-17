#!/usr/bin/env python3
"""
email_notifier.py

Purpose:
    A small reusable notification helper for automation scripts: send
    yourself (or a team) an email alert when something happens — e.g.
    a backup finishes, a job fails, disk space is low, etc.

Usage:
    Set your SMTP credentials as environment variables first (see
    README.md), then run:

        python3 email_notifier.py --to you@example.com \\
            --event "Backup Job" --status success --message "Backup completed in 4m12s."

        python3 email_notifier.py --to you@example.com \\
            --event "Disk Space" --status failure --message "Disk usage at 95% on /var."

    If no arguments are given, or SMTP env vars are missing, this
    script runs in DRY-RUN demo mode and prints the notification
    instead of sending it.

Required environment variables (for real sending):
    SMTP_HOST      e.g. smtp.gmail.com
    SMTP_PORT      e.g. 587
    SMTP_USER      your email address / login
    SMTP_PASSWORD  your email password or app-specific password

Expected Output (real send):
    Connecting to smtp.gmail.com:587 as you@example.com...
    Notification email sent to you@example.com. Subject: [SUCCESS] Backup Job

Expected Output (dry-run demo):
    DRY RUN (no SMTP_HOST configured or no --to given) - notification not sent.
    ---- Notification that would be sent ----
    To: you@example.com
    Subject: [SUCCESS] Backup Job
    Backup completed in 4m12s.
    ------------------------------------------

Caution:
    - NEVER hard-code your real email password inside this script; use
      environment variables (see send_email.py's caution notes).
    - This script is designed to be imported as a function
      (send_notification) from your OWN automation scripts, not just
      run standalone — see the "Importing into your own scripts"
      section of README.md for an example.
    - Sending notifications too frequently (e.g. inside a tight retry
      loop) can flood your inbox or hit provider rate limits; consider
      adding your own cooldown/throttling logic in scripts that call
      this repeatedly.
    - --status only affects the subject line prefix and is for your
      own organization; it does not change how the email is actually
      sent.
"""

import os
import smtplib
import sys
from email.mime.text import MIMEText


def send_notification(smtp_host, smtp_port, smtp_user, smtp_password,
                       to_addr, event, status, message):
    status_label = status.upper()
    subject = f"[{status_label}] {event}"

    msg = MIMEText(message, "plain")
    msg["From"] = smtp_user
    msg["To"] = to_addr
    msg["Subject"] = subject

    print(f"Connecting to {smtp_host}:{smtp_port} as {smtp_user}...")
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, [to_addr], msg.as_string())

    print(f"Notification email sent to {to_addr}. Subject: {subject}")


def dry_run(to_addr, event, status, message):
    subject = f"[{status.upper()}] {event}"
    print("DRY RUN (no SMTP_HOST configured or no --to given) - notification not sent.")
    print("---- Notification that would be sent ----")
    print(f"To: {to_addr}")
    print(f"Subject: {subject}")
    print(message)
    print("------------------------------------------")


def parse_args():
    args = sys.argv[1:]
    to_addr, event, status, message = None, None, None, None
    i = 0
    while i < len(args):
        if args[i] == "--to" and i + 1 < len(args):
            to_addr = args[i + 1]; i += 2
        elif args[i] == "--event" and i + 1 < len(args):
            event = args[i + 1]; i += 2
        elif args[i] == "--status" and i + 1 < len(args):
            status = args[i + 1]; i += 2
        elif args[i] == "--message" and i + 1 < len(args):
            message = args[i + 1]; i += 2
        else:
            i += 1
    return to_addr, event, status, message


def main():
    to_addr, event, status, message = parse_args()
    to_addr = to_addr or "you@example.com"
    event = event or "Backup Job"
    status = status or "success"
    message = message or "Backup completed in 4m12s."

    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = os.environ.get("SMTP_PORT")
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    if smtp_host and smtp_port and smtp_user and smtp_password:
        try:
            send_notification(smtp_host, int(smtp_port), smtp_user, smtp_password,
                               to_addr, event, status, message)
        except smtplib.SMTPAuthenticationError:
            print("Error: SMTP authentication failed. Check SMTP_USER/SMTP_PASSWORD.")
        except (smtplib.SMTPException, OSError) as e:
            print(f"Error sending notification: {e}")
    else:
        dry_run(to_addr, event, status, message)


if __name__ == "__main__":
    main()
