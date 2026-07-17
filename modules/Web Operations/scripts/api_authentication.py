#!/usr/bin/env python3
"""
api_authentication.py
--------------------------
Demonstrates three common API authentication patterns:
  1. API Key (in headers)
  2. Basic Auth (username/password)
  3. Bearer Token (OAuth2 / JWT style)

Credentials are read from environment variables or command-line
flags - never hard-code real credentials into a script you commit
to version control.

Usage:
    # API key auth
    python3 api_authentication.py --mode apikey --url https://api.example.com/data --api-key YOUR_KEY

    # Basic auth
    python3 api_authentication.py --mode basic --url https://api.example.com/data --username user --password pass

    # Bearer token auth
    python3 api_authentication.py --mode bearer --url https://api.example.com/data --token YOUR_TOKEN
"""

import argparse
import requests


def auth_with_api_key(url, api_key, header_name="X-API-Key"):
    headers = {header_name: api_key}
    response = requests.get(url, headers=headers, timeout=15)
    return response


def auth_with_basic(url, username, password):
    response = requests.get(url, auth=(username, password), timeout=15)
    return response


def auth_with_bearer_token(url, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers, timeout=15)
    return response


def main():
    parser = argparse.ArgumentParser(description="Demonstrate common API authentication methods")
    parser.add_argument("--mode", required=True, choices=["apikey", "basic", "bearer"])
    parser.add_argument("--url", required=True, help="API endpoint URL")
    parser.add_argument("--api-key", help="API key (for --mode apikey)")
    parser.add_argument("--username", help="Username (for --mode basic)")
    parser.add_argument("--password", help="Password (for --mode basic)")
    parser.add_argument("--token", help="Bearer token (for --mode bearer)")
    args = parser.parse_args()

    try:
        if args.mode == "apikey":
            if not args.api_key:
                print("--api-key is required for --mode apikey")
                return
            response = auth_with_api_key(args.url, args.api_key)

        elif args.mode == "basic":
            if not (args.username and args.password):
                print("--username and --password are required for --mode basic")
                return
            response = auth_with_basic(args.url, args.username, args.password)

        else:  # bearer
            if not args.token:
                print("--token is required for --mode bearer")
                return
            response = auth_with_bearer_token(args.url, args.token)

        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("Authenticated successfully.")
        elif response.status_code in (401, 403):
            print("Authentication failed - check your credentials.")
        print(f"Response body (first 500 chars):\n{response.text[:500]}")

    except requests.RequestException as e:
        print(f"Request failed: {e}")


if __name__ == "__main__":
    main()
