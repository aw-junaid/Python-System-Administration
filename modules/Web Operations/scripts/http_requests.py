#!/usr/bin/env python3
"""
http_requests.py
--------------------
A generic HTTP client demonstrating GET, POST, PUT, DELETE requests
with custom headers using the `requests` library. Useful as a quick
command-line HTTP testing tool.

Usage:
    python3 http_requests.py --method GET --url https://example.com
    python3 http_requests.py --method POST --url https://example.com/api --data '{"key": "value"}'
    python3 http_requests.py --method GET --url https://example.com --headers '{"User-Agent": "MyBot/1.0"}'
"""

import argparse
import json
import requests


def send_request(method, url, data=None, headers=None):
    method = method.upper()

    try:
        response = requests.request(
            method=method,
            url=url,
            data=data,
            headers=headers,
            timeout=15,
        )

        print(f"Status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"\nResponse body (first 1000 chars):\n{response.text[:1000]}")
        return response

    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Send an HTTP request")
    parser.add_argument("--method", default="GET", choices=["GET", "POST", "PUT", "DELETE", "PATCH"])
    parser.add_argument("--url", required=True, help="Target URL")
    parser.add_argument("--data", help="Request body as a JSON string")
    parser.add_argument("--headers", help="Request headers as a JSON string")
    args = parser.parse_args()

    headers = json.loads(args.headers) if args.headers else None
    data = args.data if args.data else None

    send_request(args.method, args.url, data=data, headers=headers)


if __name__ == "__main__":
    main()
