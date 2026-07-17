#!/usr/bin/env python3
"""
monitor_website.py
-----------------------
Periodically checks a web page and alerts (prints) when its content
changes, by comparing a hash of the page content between checks.
Useful for watching a pricing page, job listing, or announcement
page for updates.

Usage:
    python3 monitor_website.py --url https://example.com --interval 300
    (checks every 300 seconds / 5 minutes; Ctrl+C to stop)

    # Single check against a previously saved hash file (good for cron):
    python3 monitor_website.py --url https://example.com --once
"""

import argparse
import hashlib
import os
import time
import requests

HASH_STORE_DIR = "monitor_state"


def get_page_hash(url):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; WebOpsBot/1.0)"}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return hashlib.sha256(response.text.encode("utf-8")).hexdigest()


def get_state_file(url):
    os.makedirs(HASH_STORE_DIR, exist_ok=True)
    safe_name = hashlib.md5(url.encode("utf-8")).hexdigest()
    return os.path.join(HASH_STORE_DIR, f"{safe_name}.hash")


def check_once(url):
    state_file = get_state_file(url)
    current_hash = get_page_hash(url)

    if os.path.isfile(state_file):
        with open(state_file, "r") as f:
            previous_hash = f.read().strip()

        if current_hash != previous_hash:
            print(f"[CHANGED] Page content has changed: {url}")
            changed = True
        else:
            print(f"[NO CHANGE] Page content is the same: {url}")
            changed = False
    else:
        print(f"[BASELINE] First check - saving initial hash for: {url}")
        changed = False

    with open(state_file, "w") as f:
        f.write(current_hash)

    return changed


def monitor_loop(url, interval):
    print(f"Monitoring '{url}' every {interval} second(s). Press Ctrl+C to stop.\n")
    try:
        while True:
            check_once(url)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped monitoring.")


def main():
    parser = argparse.ArgumentParser(description="Monitor a website for content changes")
    parser.add_argument("--url", required=True, help="URL to monitor")
    parser.add_argument("--interval", type=int, default=300, help="Check interval in seconds")
    parser.add_argument("--once", action="store_true", help="Check once and exit (good for cron)")
    args = parser.parse_args()

    try:
        if args.once:
            check_once(args.url)
        else:
            monitor_loop(args.url, args.interval)
    except requests.RequestException as e:
        print(f"Failed to check page: {e}")


if __name__ == "__main__":
    main()
