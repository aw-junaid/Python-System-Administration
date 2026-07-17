#!/usr/bin/env python3
"""
send_email_with_attachment.py

Purpose:
    Send an email with one or more file attachments via SMTP.

Usage:
    Set your SMTP credentials as environment variables first (see
    README.md), then run:

        python3 send_email_with_attachment.py --to recipient@example.com \\
            --subject "Report" --body "See attached." --attach report.pdf

    You can pass --attach multiple times for multiple files.

    If no arguments are given, or SMTP env vars are missing, this
    script creates a small demo attachment file and runs in DRY-RUN
    mode, printing what would be sent instead of sending it.

Required environment variables (for real sending):
    SMTP_HOST      e.g. smtp.gmail.com
    SMTP_PORT      e.g. 587
    SMTP_USER      your email address / login
    SMTP_PASSWORD  your email password or app-specific password

Expected Output (real send):
    Connecting to smtp.gmail.com:587 as you@example.com...
    Attached: report.pdf (24.3 KB)
    Email with attachment(s) sent successfully to recipient@example.com.

Expected Output (dry-run demo):
    DRY RUN (no SMTP_HOST configured or no --to given) - email not sent.
    ---- Email that would be sent ----
    From: you@example.com
    To: recipient@example.com
    Subject: Report
    See attached.
    Attachments: ['demo_attachment.txt']
    -----------------------------------

Caution:
    - NEVER hard-code your real email password inside this script; use
      environment variables (see send_email.py's caution notes).
    - Most email providers cap total message size (attachments +
      body), commonly 20-25 MB; large files will be rejected by the
      SMTP server with an error, not silently truncated.
    - Be careful attaching sensitive files (e.g. reports with personal
      data) — verify the recipient address before sending, especially
      in scripted/bulk contexts.
    - This script reads the entire attachment into memory before
      sending; extremely large files may need a streaming approach
      instead.
"""

import os
import smtplib
import sys
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders

DEMO_ATTACHMENT = "demo_attachment.txt"
DEMO_ATTACHMENT_CONTENT = "This is a demo attachment created by send_email_with_attachment.py.\n"


def build_message(smtp_user, to_addr, subject, body, attachment_paths):
    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    for path in attachment_paths:
        if not os.path.isfile(path):
            print(f"Warning: attachment not found, skipping: {path}")
            continue
        with open(path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        filename = os.path.basename(path)
        part.add_header("Content-Disposition", f"attachment; filename={filename}")
        msg.attach(part)
        size_kb = os.path.getsize(path) / 1024
        print(f"Attached: {filename} ({size_kb:.1f} KB)")

    return msg


def send_with_attachments(smtp_host, smtp_port, smtp_user, smtp_password,
                           to_addr, subject, body, attachment_paths):
    msg = build_message(smtp_user, to_addr, subject, body, attachment_paths)

    print(f"Connecting to {smtp_host}:{smtp_port} as {smtp_user}...")
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, [to_addr], msg.as_string())

    print(f"Email with attachment(s) sent successfully to {to_addr}.")


def dry_run(to_addr, subject, body, attachment_paths, from_addr="you@example.com"):
    print("DRY RUN (no SMTP_HOST configured or no --to given) - email not sent.")
    print("---- Email that would be sent ----")
    print(f"From: {from_addr}")
    print(f"To: {to_addr}")
    print(f"Subject: {subject}")
    print(body)
    print(f"Attachments: {[os.path.basename(p) for p in attachment_paths]}")
    print("-----------------------------------")


def parse_args():
    args = sys.argv[1:]
    to_addr, subject, body = None, None, None
    attachments = []
    i = 0
    while i < len(args):
        if args[i] == "--to" and i + 1 < len(args):
            to_addr = args[i + 1]; i += 2
        elif args[i] == "--subject" and i + 1 < len(args):
            subject = args[i + 1]; i += 2
        elif args[i] == "--body" and i + 1 < len(args):
            body = args[i + 1]; i += 2
        elif args[i] == "--attach" and i + 1 < len(args):
            attachments.append(args[i + 1]); i += 2
        else:
            i += 1
    return to_addr, subject, body, attachments


def main():
    to_addr, subject, body, attachments = parse_args()
    to_addr = to_addr or "recipient@example.com"
    subject = subject or "Report"
    body = body or "See attached."

    if not attachments:
        if not os.path.isfile(DEMO_ATTACHMENT):
            with open(DEMO_ATTACHMENT, "w", encoding="utf-8") as f:
                f.write(DEMO_ATTACHMENT_CONTENT)
        attachments = [DEMO_ATTACHMENT]
        print("No --attach given, using a demo attachment file.\n")

    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = os.environ.get("SMTP_PORT")
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    if smtp_host and smtp_port and smtp_user and smtp_password:
        try:
            send_with_attachments(smtp_host, int(smtp_port), smtp_user, smtp_password,
                                   to_addr, subject, body, attachments)
        except smtplib.SMTPAuthenticationError:
            print("Error: SMTP authentication failed. Check SMTP_USER/SMTP_PASSWORD.")
        except (smtplib.SMTPException, OSError) as e:
            print(f"Error sending email: {e}")
    else:
        dry_run(to_addr, subject, body, attachments, from_addr=smtp_user or "you@example.com")


if __name__ == "__main__":
    main()
