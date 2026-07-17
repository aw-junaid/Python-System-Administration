#!/usr/bin/env python3
"""
telegram_alert.py
---------------------
Sends an alert message to a Telegram chat using a Telegram Bot.
Requires the `requests` library.

Setup:
    1. Message @BotFather on Telegram, send /newbot, follow prompts
       to get a Bot Token (looks like 123456789:ABC-defGhIJKlmNoPQRstuVWXyz)
    2. Start a chat with your new bot (send it any message)
    3. Get your chat ID: visit
       https://api.telegram.org/bot<YourBOTToken>/getUpdates
       and look for "chat":{"id": ...}
    4. Set environment variables:
       export TELEGRAM_BOT_TOKEN="123456789:ABC-defGhIJKlmNoPQRstuVWXyz"
       export TELEGRAM_CHAT_ID="123456789"

Usage:
    python3 telegram_alert.py --message "Backup job failed on server1"
"""

import argparse
import os
import requests


def send_telegram_alert(message):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("Missing TELEGRAM_BOT_TOKEN and/or TELEGRAM_CHAT_ID environment variables.")
        print("Set them before running this script (see the script docstring).")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}

    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            print("Telegram alert sent successfully.")
            return True
        else:
            print(f"Telegram API returned status {response.status_code}: {response.text}")
            return False
    except requests.RequestException as e:
        print(f"Failed to send Telegram alert: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Send an alert message to Telegram")
    parser.add_argument("--message", required=True, help="Alert message text")
    args = parser.parse_args()

    send_telegram_alert(args.message)


if __name__ == "__main__":
    main()
