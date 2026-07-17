#!/usr/bin/env python3
"""
slack_alert.py
------------------
Sends an alert message to a Slack channel using an Incoming Webhook
URL. Requires the `requests` library.

Setup:
    1. Go to https://api.slack.com/apps -> Create New App -> From scratch
    2. Enable "Incoming Webhooks" and add a webhook to your workspace/channel
    3. Copy the Webhook URL (looks like https://hooks.slack.com/services/XXX/YYY/ZZZ)
    4. Set it as an environment variable: export SLACK_WEBHOOK_URL="https://hooks.slack.com/..."

Usage:
    export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/XXX/YYY/ZZZ"
    python3 slack_alert.py --message "Disk usage is at 90% on server1"
"""

import argparse
import os
import requests


def send_slack_alert(message):
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")

    if not webhook_url:
        print("Missing SLACK_WEBHOOK_URL environment variable.")
        print("Set it before running this script (see the script docstring).")
        return False

    payload = {"text": message}

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code == 200:
            print("Slack alert sent successfully.")
            return True
        else:
            print(f"Slack API returned status {response.status_code}: {response.text}")
            return False
    except requests.RequestException as e:
        print(f"Failed to send Slack alert: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Send an alert message to Slack")
    parser.add_argument("--message", required=True, help="Alert message text")
    args = parser.parse_args()

    send_slack_alert(args.message)


if __name__ == "__main__":
    main()
