#!/usr/bin/env python3
"""
check_website.py
---------------------
Checks whether a website is up, and reports its HTTP status code and
response time. Useful as a simple uptime check, e.g. run from cron.

Usage:
    python3 check_website.py --url https://example.com
    python3 check_website.py --url https://example.com --timeout 5
"""

import argparse
import sys
import time
import requests


def check_website(url, timeout=10):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        start = time.time()
        response = requests.get(url, timeout=timeout)
        elapsed = time.time() - start

        print(f"URL: {url}")
        print(f"Status code: {response.status_code}")
        print(f"Response time: {elapsed:.3f} seconds")

        if response.ok:
            print("[UP] Website is reachable and returned a success status code.")
            return True
        else:
            print(f"[WARNING] Website responded but with a non-success status code: {response.status_code}")
            return False

    except requests.ConnectionError:
        print(f"[DOWN] Could not connect to {url}")
        return False
    except requests.Timeout:
        print(f"[DOWN] Request to {url} timed out after {timeout} seconds")
        return False
    except requests.RequestException as e:
        print(f"[DOWN] Request failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Check whether a website is up")
    parser.add_argument("--url", required=True, help="Website URL to check")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout in seconds")
    args = parser.parse_args()

    is_up = check_website(args.url, args.timeout)
    sys.exit(0 if is_up else 1)


if __name__ == "__main__":
    main()
