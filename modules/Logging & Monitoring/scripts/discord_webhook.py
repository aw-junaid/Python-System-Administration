#!/usr/bin/env python3
"""
discord_webhook.py
----------------------
Sends an alert message to a Discord channel using a Discord Webhook
URL. Requires the `requests` library.

Setup:
    1. In Discord, go to your channel -> Edit Channel -> Integrations -> Webhooks
    2. Click "New Webhook", copy the Webhook URL
    3. Set it as an environment variable:
       export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/XXX/YYY"

Usage:
    python3 discord_webhook.py --message "CPU usage exceeded 90% on server1"
"""

import argparse
import os
import requests


def send_discord_alert(message):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        print("Missing DISCORD_WEBHOOK_URL environment variable.")
        print("Set it before running this script (see the script docstring).")
        return False

    payload = {"content": message}

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code in (200, 204):
            print("Discord alert sent successfully.")
            return True
        else:
            print(f"Discord API returned status {response.status_code}: {response.text}")
            return False
    except requests.RequestException as e:
        print(f"Failed to send Discord alert: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Send an alert message to a Discord channel")
    parser.add_argument("--message", required=True, help="Alert message text")
    args = parser.parse_args()

    send_discord_alert(args.message)


if __name__ == "__main__":
    main()
