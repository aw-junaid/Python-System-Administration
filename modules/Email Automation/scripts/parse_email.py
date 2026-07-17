#!/usr/bin/env python3
"""
parse_email.py

Purpose:
    Parse a raw email (.eml file, or the latest message fetched live
    via IMAP) and extract structured info: sender, subject, date, body
    text, and a list of attachment filenames.

Usage:
    python3 parse_email.py path/to/message.eml

    If no path is given, this script creates a small demo .eml file
    and parses that instead, so you can see expected output safely.

Expected Output:
    From:    sender@example.com
    To:      recipient@example.com
    Subject: Demo message
    Date:    Thu, 17 Jul 2026 09:00:00 +0000

    --- Body (text/plain) ---
    Hello, this is a demo email body.

    --- Attachments ---
    (none found)

Caution:
    - This script only reads/parses an .eml file already saved to
      disk; it does not connect to any mail server itself. Use
      receive_emails.py to list/fetch real emails from an IMAP
      mailbox first, then save one as .eml if you want to parse it
      here (many mail clients support "Save As .eml" / "Export").
    - HTML-only emails will have their raw HTML printed as the body;
      this script does not strip HTML tags for you.
    - This script does NOT extract/save attachment file contents by
      default — it only lists attachment filenames, to avoid writing
      arbitrary files from an email to disk without you asking for it.
"""

import email
import os
import sys
from email import policy
from email.parser import BytesParser

DEMO_FILE = "demo_message.eml"
DEMO_CONTENT = (
    "From: sender@example.com\n"
    "To: recipient@example.com\n"
    "Subject: Demo message\n"
    "Date: Thu, 17 Jul 2026 09:00:00 +0000\n"
    "Content-Type: text/plain; charset=UTF-8\n"
    "\n"
    "Hello, this is a demo email body.\n"
)


def parse_eml(path: str) -> None:
    if not os.path.isfile(path):
        print(f"Error: file not found: {path}")
        return

    with open(path, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)

    print(f"From:    {msg.get('From')}")
    print(f"To:      {msg.get('To')}")
    print(f"Subject: {msg.get('Subject')}")
    print(f"Date:    {msg.get('Date')}")
    print()

    body_part = msg.get_body(preferencelist=("plain", "html"))
    if body_part:
        content_type = body_part.get_content_type()
        print(f"--- Body ({content_type}) ---")
        print(body_part.get_content())
    else:
        print("--- Body ---")
        print("(no readable body part found)")

    attachments = [
        part.get_filename()
        for part in msg.iter_attachments()
        if part.get_filename()
    ]
    print("\n--- Attachments ---")
    if attachments:
        for name in attachments:
            print(f"  {name}")
    else:
        print("(none found)")


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        print("No file path given, creating and parsing a demo .eml file.\n")
        if not os.path.isfile(DEMO_FILE):
            with open(DEMO_FILE, "w", encoding="utf-8") as f:
                f.write(DEMO_CONTENT)
        path = DEMO_FILE
    parse_eml(path)


if __name__ == "__main__":
    main()
