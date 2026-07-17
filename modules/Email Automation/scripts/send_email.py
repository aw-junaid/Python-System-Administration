#!/usr/bin/env python3
"""
send_email.py

Purpose:
    Send a plain text email via SMTP using Python's built-in smtplib
    and email libraries.

Usage:
    Set your SMTP credentials as environment variables first (see
    README.md), then run:

        python3 send_email.py --to recipient@example.com --subject "Hello" --body "This is a test email."

    If no arguments are given, this script runs in DRY-RUN demo mode:
    it builds a sample email and prints it instead of actually sending
    anything, so you can see the expected output safely.

Required environment variables (for real sending):
    SMTP_HOST      e.g. smtp.gmail.com
    SMTP_PORT      e.g. 587
    SMTP_USER      your email address / login
    SMTP_PASSWORD  your email password or app-specific password

Expected Output (real send):
    Connecting to smtp.gmail.com:587 as you@example.com...
    Email sent successfully to recipient@example.com.

Expected Output (dry-run demo, no env vars / no args):
    DRY RUN (no SMTP_HOST configured or no --to given) - email not sent.
    ---- Email that would be sent ----
    From: you@example.com
    To: recipient@example.com
    Subject: Hello
    <body text>
    -----------------------------------

Caution:
    - NEVER hard-code your real email password inside this script.
      Always supply credentials via environment variables (or a
      secrets manager), never commit them to version control.
    - Most providers (Gmail, Outlook, Yahoo) require an "app password"
      rather than your normal account password when 2FA is enabled;
      check your provider's documentation.
    - Sending real email to real recipients has real consequences —
      double check the --to address before running outside dry-run
      mode, especially in loops or automation.
    - This script uses STARTTLS on the given SMTP_PORT (typically 587).
      If your provider requires implicit SSL (port 465), use
      smtplib.SMTP_SSL instead — see the comment in the code.
"""

import os
import smtplib
import sys
from email.mime.text import MIMEText


def send_plain_email(smtp_host, smtp_port, smtp_user, smtp_password,
                      to_addr, subject, body):
    msg = MIMEText(body, "plain")
    msg["From"] = smtp_user
    msg["To"] = to_addr
    msg["Subject"] = subject

    print(f"Connecting to {smtp_host}:{smtp_port} as {smtp_user}...")
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()  # Use smtplib.SMTP_SSL(host, 465) instead if your provider needs implicit SSL
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, [to_addr], msg.as_string())

    print(f"Email sent successfully to {to_addr}.")


def dry_run(to_addr, subject, body, from_addr="you@example.com"):
    print("DRY RUN (no SMTP_HOST configured or no --to given) - email not sent.")
    print("---- Email that would be sent ----")
    print(f"From: {from_addr}")
    print(f"To: {to_addr}")
    print(f"Subject: {subject}")
    print(body)
    print("-----------------------------------")


def parse_args():
    args = sys.argv[1:]
    to_addr, subject, body = None, None, None
    i = 0
    while i < len(args):
        if args[i] == "--to" and i + 1 < len(args):
            to_addr = args[i + 1]; i += 2
        elif args[i] == "--subject" and i + 1 < len(args):
            subject = args[i + 1]; i += 2
        elif args[i] == "--body" and i + 1 < len(args):
            body = args[i + 1]; i += 2
        else:
            i += 1
    return to_addr, subject, body


def main():
    to_addr, subject, body = parse_args()
    to_addr = to_addr or "recipient@example.com"
    subject = subject or "Hello"
    body = body or "This is a test email."

    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = os.environ.get("SMTP_PORT")
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    if smtp_host and smtp_port and smtp_user and smtp_password:
        try:
            send_plain_email(smtp_host, int(smtp_port), smtp_user, smtp_password,
                              to_addr, subject, body)
        except smtplib.SMTPAuthenticationError:
            print("Error: SMTP authentication failed. Check SMTP_USER/SMTP_PASSWORD "
                  "(you may need an app-specific password).")
        except (smtplib.SMTPException, OSError) as e:
            print(f"Error sending email: {e}")
    else:
        dry_run(to_addr, subject, body, from_addr=smtp_user or "you@example.com")


if __name__ == "__main__":
    main()
