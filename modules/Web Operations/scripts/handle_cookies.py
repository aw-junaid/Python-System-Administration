#!/usr/bin/env python3
"""
handle_cookies.py
----------------------
Demonstrates sending, receiving, saving, and reusing cookies with
the `requests` library - useful for scripts that need to stay
"logged in" or carry session state across multiple requests.

Usage:
    python3 handle_cookies.py --url https://httpbin.org/cookies/set?demo=value
    python3 handle_cookies.py --url https://httpbin.org/cookies --load cookies.json
"""

import argparse
import json
import requests


def fetch_and_show_cookies(url, save_path=None):
    response = requests.get(url, timeout=15)

    print(f"Status code: {response.status_code}")
    print(f"Cookies received from server: {dict(response.cookies)}")

    if save_path:
        cookie_dict = requests.utils.dict_from_cookiejar(response.cookies)
        with open(save_path, "w") as f:
            json.dump(cookie_dict, f, indent=2)
        print(f"Cookies saved to: {save_path}")

    return response.cookies


def fetch_with_saved_cookies(url, load_path):
    with open(load_path, "r") as f:
        cookie_dict = json.load(f)

    print(f"Loaded cookies from {load_path}: {cookie_dict}")

    response = requests.get(url, cookies=cookie_dict, timeout=15)
    print(f"Status code: {response.status_code}")
    print(f"Response body (first 500 chars):\n{response.text[:500]}")
    return response


def main():
    parser = argparse.ArgumentParser(description="Handle cookies with requests")
    parser.add_argument("--url", required=True, help="URL to request")
    parser.add_argument("--save", help="Path to save received cookies as JSON")
    parser.add_argument("--load", help="Path to a JSON file of cookies to send with the request")
    args = parser.parse_args()

    if args.load:
        fetch_with_saved_cookies(args.url, args.load)
    else:
        fetch_and_show_cookies(args.url, args.save)


if __name__ == "__main__":
    main()
