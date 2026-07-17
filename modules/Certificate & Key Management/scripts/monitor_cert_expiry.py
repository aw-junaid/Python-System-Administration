#!/usr/bin/env python3
"""
monitor_cert_expiry.py - Continuously (or once) scan a list of certificates/hosts
and send a notification (email or webhook) when any of them are within a
warning window of expiring.

Usage:
    # one-off scan of local cert files
    python3 monitor_cert_expiry.py --cert cert1.pem --cert cert2.pem --warn-days 30

    # scan remote hosts on an interval, notify via webhook
    python3 monitor_cert_expiry.py --host example.com:443 --host example.org:443 \
        --warn-days 14 --interval 3600 --webhook https://hooks.example.com/notify

    # notify via email (requires SMTP settings)
    python3 monitor_cert_expiry.py --cert cert.pem --smtp-host smtp.example.com \
        --smtp-user user --smtp-password secret --email-to admin@example.com

Output:
    Console log of each check; outbound notification when a cert is expiring soon.
"""
import argparse
import datetime
import smtplib
import socket
import ssl
import sys
import time
from email.mime.text import MIMEText

import requests
from cryptography import x509


def get_cert_from_file(path):
    with open(path, "rb") as f:
        data = f.read()
    try:
        return x509.load_pem_x509_certificate(data)
    except ValueError:
        return x509.load_der_x509_certificate(data)


def get_cert_from_host(host, port, timeout=10):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with socket.create_connection((host, port), timeout=timeout) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as ssock:
            der = ssock.getpeercert(binary_form=True)
    return x509.load_der_x509_certificate(der)


def days_remaining(cert):
    not_after = cert.not_valid_after_utc if hasattr(cert, "not_valid_after_utc") else cert.not_valid_after
    now = datetime.datetime.now(datetime.timezone.utc) if hasattr(cert, "not_valid_after_utc") \
        else datetime.datetime.utcnow()
    return (not_after - now).days


def send_webhook(url, message):
    try:
        requests.post(url, json={"text": message}, timeout=10)
    except Exception as e:
        print(f"[!] Failed to send webhook: {e}", file=sys.stderr)


def send_email(smtp_host, smtp_port, smtp_user, smtp_password, to_addr, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_addr
    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, [to_addr], msg.as_string())
    except Exception as e:
        print(f"[!] Failed to send email: {e}", file=sys.stderr)


def run_once(targets, warn_days, webhook, email_cfg):
    alerts = []
    for kind, value in targets:
        try:
            if kind == "file":
                cert = get_cert_from_file(value)
                label = value
            else:
                host, port = value
                cert = get_cert_from_host(host, port)
                label = f"{host}:{port}"

            remaining = days_remaining(cert)
            status = "EXPIRED" if remaining < 0 else ("WARNING" if remaining <= warn_days else "OK")
            print(f"[{status}] {label} -> {remaining} days remaining")

            if status != "OK":
                alerts.append(f"{label}: {remaining} days remaining ({status})")

        except Exception as e:
            print(f"[!] Failed to check {value}: {e}", file=sys.stderr)

    if alerts:
        message = "Certificate expiry alert:\n" + "\n".join(alerts)
        if webhook:
            send_webhook(webhook, message)
        if email_cfg:
            send_email(*email_cfg, subject="Certificate Expiry Alert", body=message)


def main():
    parser = argparse.ArgumentParser(description="Monitor certificates for upcoming expiry.")
    parser.add_argument("--cert", action="append", default=[], help="Local cert file, repeatable")
    parser.add_argument("--host", action="append", default=[], help="host:port, repeatable")
    parser.add_argument("--warn-days", type=int, default=30)
    parser.add_argument("--interval", type=int, default=0, help="Seconds between checks; 0 = run once")
    parser.add_argument("--webhook", default=None, help="Webhook URL for notifications")
    parser.add_argument("--smtp-host", default=None)
    parser.add_argument("--smtp-port", type=int, default=587)
    parser.add_argument("--smtp-user", default=None)
    parser.add_argument("--smtp-password", default=None)
    parser.add_argument("--email-to", default=None)
    args = parser.parse_args()

    targets = [("file", c) for c in args.cert]
    for h in args.host:
        host, _, port = h.partition(":")
        targets.append(("host", (host, int(port) if port else 443)))

    if not targets:
        print("[!] Provide at least one --cert or --host", file=sys.stderr)
        sys.exit(1)

    email_cfg = None
    if args.smtp_host and args.smtp_user and args.smtp_password and args.email_to:
        email_cfg = (args.smtp_host, args.smtp_port, args.smtp_user, args.smtp_password, args.email_to)

    if args.interval <= 0:
        run_once(targets, args.warn_days, args.webhook, email_cfg)
    else:
        print(f"[*] Monitoring every {args.interval}s. Press Ctrl+C to stop.")
        try:
            while True:
                run_once(targets, args.warn_days, args.webhook, email_cfg)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n[*] Monitoring stopped.")


if __name__ == "__main__":
    main()
