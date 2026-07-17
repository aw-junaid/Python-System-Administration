#!/usr/bin/env python3
"""
email_alert.py
------------------
Sends an email alert via SMTP. Works with Gmail, Outlook, or any
SMTP provider. Credentials are read from environment variables so
they are never hard-coded in the script.

Required environment variables:
    SMTP_HOST       e.g. smtp.gmail.com
    SMTP_PORT       e.g. 587
    SMTP_USER       your email address / SMTP username
    SMTP_PASSWORD   your email password or app-specific password

Usage:
    export SMTP_HOST=smtp.gmail.com
    export SMTP_PORT=587
    export SMTP_USER=you@gmail.com
    export SMTP_PASSWORD=your_app_password
    python3 email_alert.py --to admin@example.com --subject "Disk Alert" --message "Disk usage is at 90%"

Note (Gmail users): You must create an "App Password" in your Google
account security settings - normal account passwords will not work
if 2-Step Verification is enabled.
"""

import argparse
import os
import smtplib
from email.mime.text import MIMEText


def send_email_alert(to_addr, subject, message):
    host = os.environ.get("SMTP_HOST")
    port = os.environ.get("SMTP_PORT")
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASSWORD")

    missing = [name for name, val in [
        ("SMTP_HOST", host), ("SMTP_PORT", port),
        ("SMTP_USER", user), ("SMTP_PASSWORD", password)
    ] if not val]

    if missing:
        print(f"Missing required environment variables: {', '.join(missing)}")
        print("Set them before running this script (see the script docstring).")
        return False

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to_addr

    try:
        with smtplib.SMTP(host, int(port)) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(user, [to_addr], msg.as_string())
        print(f"Email alert sent to {to_addr}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Send an email alert via SMTP")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--subject", default="System Alert", help="Email subject")
    parser.add_argument("--message", required=True, help="Email body text")
    args = parser.parse_args()

    send_email_alert(args.to, args.subject, args.message)


if __name__ == "__main__":
    main()
