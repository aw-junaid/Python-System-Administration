#!/usr/bin/env python3
"""
send_html_email.py

Purpose:
    Send an HTML-formatted email via SMTP, with a plain text fallback
    for email clients that don't render HTML.

Usage:
    Set your SMTP credentials as environment variables first (see
    README.md), then run:

        python3 send_html_email.py --to recipient@example.com --subject "Newsletter"

    If no arguments are given, or SMTP env vars are missing, this
    script runs in DRY-RUN demo mode and prints the email instead of
    sending it.

Required environment variables (for real sending):
    SMTP_HOST      e.g. smtp.gmail.com
    SMTP_PORT      e.g. 587
    SMTP_USER      your email address / login
    SMTP_PASSWORD  your email password or app-specific password

Expected Output (real send):
    Connecting to smtp.gmail.com:587 as you@example.com...
    HTML email sent successfully to recipient@example.com.

Expected Output (dry-run demo):
    DRY RUN (no SMTP_HOST configured or no --to given) - email not sent.
    ---- Email that would be sent ----
    From: you@example.com
    To: recipient@example.com
    Subject: Newsletter
    --- Plain text part ---
    Please view this email in an HTML-capable client.
    --- HTML part ---
    <html>...<h1>Hello!</h1>...</html>
    -----------------------------------

Caution:
    - NEVER hard-code your real email password inside this script; use
      environment variables (see send_email.py's caution notes, which
      apply here too).
    - HTML emails can trigger spam filters more easily than plain text
      if they contain too many links/images or suspicious formatting —
      test with a real inbox before bulk sending.
    - Always include a plain-text alternative part (this script does,
      via MIMEMultipart("alternative")) so clients that block HTML
      still show something readable.
    - Do not embed remote-tracking pixels or third-party scripts in
      HTML email bodies without the recipient's awareness/consent.
"""

import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

DEMO_HTML = """\
<html>
  <body>
    <h1>Hello!</h1>
    <p>This is a <strong>demo HTML email</strong> sent by send_html_email.py.</p>
  </body>
</html>
"""
DEMO_PLAIN_FALLBACK = "Please view this email in an HTML-capable client."


def send_html_email(smtp_host, smtp_port, smtp_user, smtp_password,
                     to_addr, subject, html_body, plain_fallback):
    msg = MIMEMultipart("alternative")
    msg["From"] = smtp_user
    msg["To"] = to_addr
    msg["Subject"] = subject

    msg.attach(MIMEText(plain_fallback, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    print(f"Connecting to {smtp_host}:{smtp_port} as {smtp_user}...")
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, [to_addr], msg.as_string())

    print(f"HTML email sent successfully to {to_addr}.")


def dry_run(to_addr, subject, html_body, plain_fallback, from_addr="you@example.com"):
    print("DRY RUN (no SMTP_HOST configured or no --to given) - email not sent.")
    print("---- Email that would be sent ----")
    print(f"From: {from_addr}")
    print(f"To: {to_addr}")
    print(f"Subject: {subject}")
    print("--- Plain text part ---")
    print(plain_fallback)
    print("--- HTML part ---")
    print(html_body)
    print("-----------------------------------")


def parse_args():
    args = sys.argv[1:]
    to_addr, subject = None, None
    i = 0
    while i < len(args):
        if args[i] == "--to" and i + 1 < len(args):
            to_addr = args[i + 1]; i += 2
        elif args[i] == "--subject" and i + 1 < len(args):
            subject = args[i + 1]; i += 2
        else:
            i += 1
    return to_addr, subject


def main():
    to_addr, subject = parse_args()
    to_addr = to_addr or "recipient@example.com"
    subject = subject or "Newsletter"

    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = os.environ.get("SMTP_PORT")
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    if smtp_host and smtp_port and smtp_user and smtp_password:
        try:
            send_html_email(smtp_host, int(smtp_port), smtp_user, smtp_password,
                             to_addr, subject, DEMO_HTML, DEMO_PLAIN_FALLBACK)
        except smtplib.SMTPAuthenticationError:
            print("Error: SMTP authentication failed. Check SMTP_USER/SMTP_PASSWORD.")
        except (smtplib.SMTPException, OSError) as e:
            print(f"Error sending email: {e}")
    else:
        dry_run(to_addr, subject, DEMO_HTML, DEMO_PLAIN_FALLBACK,
                 from_addr=smtp_user or "you@example.com")


if __name__ == "__main__":
    main()
