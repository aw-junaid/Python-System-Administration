#!/usr/bin/env python3
"""
receive_emails.py

Purpose:
    Connect to an IMAP mailbox and list recent emails (sender, subject,
    date), optionally limited to unread messages.

Usage:
    Set your IMAP credentials as environment variables first (see
    README.md), then run:

        python3 receive_emails.py --limit 5
        python3 receive_emails.py --limit 5 --unread-only

    If IMAP env vars are missing, this script runs in DEMO mode and
    prints sample email listings instead of connecting anywhere.

Required environment variables (for real use):
    IMAP_HOST      e.g. imap.gmail.com
    IMAP_USER      your email address / login
    IMAP_PASSWORD  your email password or app-specific password

Expected Output (real use):
    Connecting to imap.gmail.com as you@example.com...
    Found 5 message(s) in INBOX (showing most recent first):

    1. From: sender@example.com
       Subject: Meeting tomorrow
       Date: Thu, 17 Jul 2026 09:00:00 +0000

    2. From: newsletter@example.com
       Subject: Weekly digest
       Date: Wed, 16 Jul 2026 08:00:00 +0000

Expected Output (demo mode, no env vars):
    DEMO MODE (no IMAP_HOST configured) - showing sample data.

    1. From: sender@example.com
       Subject: Demo: Meeting tomorrow
       Date: (demo data, not a real email)

Caution:
    - THIS SCRIPT IS READ-ONLY: it only lists emails, it does not
      delete, move, or mark anything as read. See parse_email.py in
      this same folder if you also want to read full message bodies.
    - NEVER hard-code your real email password inside this script; use
      environment variables (IMAP_PASSWORD).
    - This script connects over SSL (imaplib.IMAP4_SSL) by default,
      which is standard for IMAP on port 993.
    - Some providers (Gmail, Outlook) require you to explicitly enable
      IMAP access and/or generate an app-specific password before this
      will work; check your provider's account security settings.
"""

import email
import imaplib
import os
import sys


def list_emails(imap_host, imap_user, imap_password, limit=5, unread_only=False):
    print(f"Connecting to {imap_host} as {imap_user}...")
    conn = imaplib.IMAP4_SSL(imap_host)
    conn.login(imap_user, imap_password)
    conn.select("INBOX")

    criterion = "UNSEEN" if unread_only else "ALL"
    status, data = conn.search(None, criterion)
    if status != "OK":
        print("Error: could not search mailbox.")
        conn.logout()
        return

    message_ids = data[0].split()
    message_ids = message_ids[-limit:]  # most recent N
    message_ids.reverse()

    print(f"Found {len(message_ids)} message(s) in INBOX (showing most recent first):\n")

    for i, msg_id in enumerate(message_ids, start=1):
        status, msg_data = conn.fetch(msg_id, "(RFC822)")
        if status != "OK":
            continue
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        print(f"{i}. From: {msg.get('From')}")
        print(f"   Subject: {msg.get('Subject')}")
        print(f"   Date: {msg.get('Date')}\n")

    conn.logout()


def demo_mode(limit=2):
    print("DEMO MODE (no IMAP_HOST configured) - showing sample data.\n")
    samples = [
        {"from": "sender@example.com", "subject": "Demo: Meeting tomorrow"},
        {"from": "newsletter@example.com", "subject": "Demo: Weekly digest"},
    ]
    for i, sample in enumerate(samples[:limit], start=1):
        print(f"{i}. From: {sample['from']}")
        print(f"   Subject: {sample['subject']}")
        print(f"   Date: (demo data, not a real email)\n")


def parse_args():
    args = sys.argv[1:]
    limit = 5
    unread_only = "--unread-only" in args
    if "--limit" in args:
        idx = args.index("--limit")
        if idx + 1 < len(args):
            limit = int(args[idx + 1])
    return limit, unread_only


def main():
    limit, unread_only = parse_args()

    imap_host = os.environ.get("IMAP_HOST")
    imap_user = os.environ.get("IMAP_USER")
    imap_password = os.environ.get("IMAP_PASSWORD")

    if imap_host and imap_user and imap_password:
        try:
            list_emails(imap_host, imap_user, imap_password, limit, unread_only)
        except imaplib.IMAP4.error as e:
            print(f"Error: IMAP login/search failed - {e}")
        except (OSError, ConnectionError) as e:
            print(f"Error connecting to IMAP server: {e}")
    else:
        demo_mode(limit)


if __name__ == "__main__":
    main()
