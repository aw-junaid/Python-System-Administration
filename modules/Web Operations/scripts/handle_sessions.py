#!/usr/bin/env python3
"""
handle_sessions.py
-----------------------
Demonstrates using requests.Session() to persist cookies, headers,
and connection pooling across multiple requests - the standard
pattern for scripts that need to log in once and then make several
authenticated requests (e.g. a login page followed by API calls).

Usage:
    python3 handle_sessions.py --base-url https://httpbin.org
"""

import argparse
import requests


def demo_session(base_url):
    session = requests.Session()

    # Common headers applied to every request made through this session
    session.headers.update({"User-Agent": "WebOpsBot/1.0"})

    print("=== Request 1: sets a cookie ===")
    r1 = session.get(f"{base_url}/cookies/set?session_demo=hello")
    print(f"Status: {r1.status_code}")
    print(f"Session cookies after request 1: {dict(session.cookies)}")

    print("\n=== Request 2: same session, cookie is sent automatically ===")
    r2 = session.get(f"{base_url}/cookies")
    print(f"Status: {r2.status_code}")
    print(f"Response body (first 300 chars): {r2.text[:300]}")

    print("\n=== Request 3: check what headers the session sent ===")
    r3 = session.get(f"{base_url}/headers")
    print(f"Status: {r3.status_code}")
    print(f"Response body (first 300 chars): {r3.text[:300]}")

    session.close()
    print("\nSession closed.")


def main():
    parser = argparse.ArgumentParser(description="Demonstrate persistent sessions with requests.Session()")
    parser.add_argument(
        "--base-url",
        default="https://httpbin.org",
        help="Base URL of a test API that supports /cookies and /headers endpoints",
    )
    args = parser.parse_args()

    demo_session(args.base_url)


if __name__ == "__main__":
    main()
