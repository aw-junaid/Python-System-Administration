#!/usr/bin/env python3
"""
bulk_email_sender.py

Purpose:
    Send a personalized email to many recipients at once, reading
    recipient data (email + name, or any other placeholders) from a
    CSV file and substituting them into a message template.

Usage:
    Prepare a CSV file with at least an "email" column, e.g.:

        email,name
        alice@example.com,Alice
        bob@example.com,Bob

    Set your SMTP credentials as environment variables first (see
    README.md), then run:

        python3 bulk_email_sender.py --csv recipients.csv \\
            --subject "Hello {name}" --body "Hi {name}, this is a bulk email."

    If no --csv is given, or SMTP env vars are missing, this script
    creates a demo CSV and runs in DRY-RUN mode, printing what would be
    sent to each recipient instead of actually sending anything.

Required environment variables (for real sending):
    SMTP_HOST      e.g. smtp.gmail.com
    SMTP_PORT      e.g. 587
    SMTP_USER      your email address / login
    SMTP_PASSWORD  your email password or app-specific password

Expected Output (real send):
    Connecting to smtp.gmail.com:587 as you@example.com...
    Sent to alice@example.com (1/2)
    Sent to bob@example.com (2/2)
    Bulk send complete: 2 succeeded, 0 failed.

Expected Output (dry-run demo):
    DRY RUN (no SMTP_HOST configured or no --csv given) - no emails sent.
    ---- Preview for alice@example.com ----
    Subject: Hello Alice
    Hi Alice, this is a bulk email.
    ----------------------------------------
    ---- Preview for bob@example.com ----
    Subject: Hello Bob
    Hi Bob, this is a bulk email.
    ----------------------------------------

Caution:
    - THIS SENDS REAL EMAIL TO EVERY ROW IN YOUR CSV when SMTP env vars
      are set. Double check your CSV file and template before running
      for real — there is no confirmation prompt.
    - Sending many emails quickly can trigger your provider's rate
      limits or spam protections; this script includes a small delay
      between sends (see SEND_DELAY_SECONDS) to reduce that risk, but
      you may need to increase it for large lists.
    - Never use bulk email to contact people who haven't opted in —
      follow applicable anti-spam laws (e.g. CAN-SPAM, GDPR, CASL) in
      your jurisdiction, including providing a way to unsubscribe.
    - NEVER hard-code your real email password inside this script; use
      environment variables (see send_email.py's caution notes).
"""

import csv
import os
import smtplib
import sys
import time
from email.mime.text import MIMEText

SEND_DELAY_SECONDS = 1  # polite delay between sends to avoid rate limits

DEMO_CSV = "demo_recipients.csv"
DEMO_CSV_CONTENT = "email,name\nalice@example.com,Alice\nbob@example.com,Bob\n"


def read_recipients(csv_path: str) -> list:
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def render_template(template: str, row: dict) -> str:
    try:
        return template.format(**row)
    except KeyError as e:
        # Missing placeholder column in CSV - leave template as-is for that field
        return template


def send_bulk(smtp_host, smtp_port, smtp_user, smtp_password,
              recipients, subject_template, body_template):
    print(f"Connecting to {smtp_host}:{smtp_port} as {smtp_user}...")
    succeeded, failed = 0, 0

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)

        for i, row in enumerate(recipients, start=1):
            to_addr = row.get("email")
            if not to_addr:
                print(f"Skipping row {i}: no 'email' column value.")
                failed += 1
                continue

            subject = render_template(subject_template, row)
            body = render_template(body_template, row)

            msg = MIMEText(body, "plain")
            msg["From"] = smtp_user
            msg["To"] = to_addr
            msg["Subject"] = subject

            try:
                server.sendmail(smtp_user, [to_addr], msg.as_string())
                print(f"Sent to {to_addr} ({i}/{len(recipients)})")
                succeeded += 1
            except smtplib.SMTPException as e:
                print(f"Failed to send to {to_addr}: {e}")
                failed += 1

            time.sleep(SEND_DELAY_SECONDS)

    print(f"Bulk send complete: {succeeded} succeeded, {failed} failed.")


def dry_run(recipients, subject_template, body_template):
    print("DRY RUN (no SMTP_HOST configured or no --csv given) - no emails sent.")
    for row in recipients:
        to_addr = row.get("email", "unknown@example.com")
        subject = render_template(subject_template, row)
        body = render_template(body_template, row)
        print(f"---- Preview for {to_addr} ----")
        print(f"Subject: {subject}")
        print(body)
        print("----------------------------------------")


def parse_args():
    args = sys.argv[1:]
    csv_path, subject, body = None, None, None
    i = 0
    while i < len(args):
        if args[i] == "--csv" and i + 1 < len(args):
            csv_path = args[i + 1]; i += 2
        elif args[i] == "--subject" and i + 1 < len(args):
            subject = args[i + 1]; i += 2
        elif args[i] == "--body" and i + 1 < len(args):
            body = args[i + 1]; i += 2
        else:
            i += 1
    return csv_path, subject, body


def main():
    csv_path, subject_template, body_template = parse_args()
    subject_template = subject_template or "Hello {name}"
    body_template = body_template or "Hi {name}, this is a bulk email."

    if not csv_path:
        print("No --csv given, creating a demo recipients file.\n")
        if not os.path.isfile(DEMO_CSV):
            with open(DEMO_CSV, "w", encoding="utf-8") as f:
                f.write(DEMO_CSV_CONTENT)
        csv_path = DEMO_CSV

    if not os.path.isfile(csv_path):
        print(f"Error: CSV file not found: {csv_path}")
        return

    recipients = read_recipients(csv_path)

    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = os.environ.get("SMTP_PORT")
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    if smtp_host and smtp_port and smtp_user and smtp_password:
        try:
            send_bulk(smtp_host, int(smtp_port), smtp_user, smtp_password,
                      recipients, subject_template, body_template)
        except smtplib.SMTPAuthenticationError:
            print("Error: SMTP authentication failed. Check SMTP_USER/SMTP_PASSWORD.")
        except (smtplib.SMTPException, OSError) as e:
            print(f"Error during bulk send: {e}")
    else:
        dry_run(recipients, subject_template, body_template)


if __name__ == "__main__":
    main()
