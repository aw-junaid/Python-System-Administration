#!/usr/bin/env python3
"""
rest_api_call.py
---------------------
Demonstrates calling a REST API (GET/POST/PUT/DELETE) with a JSON
body and JSON response handling — the typical shape of interacting
with a REST service. Uses https://jsonplaceholder.typicode.com as a
free public test API by default.

Usage:
    python3 rest_api_call.py --method GET --url https://jsonplaceholder.typicode.com/posts/1
    python3 rest_api_call.py --method POST --url https://jsonplaceholder.typicode.com/posts \
        --json '{"title": "foo", "body": "bar", "userId": 1}'
"""

import argparse
import json
import requests


def call_rest_api(method, url, json_body=None):
    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            json=json_body,
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        response.raise_for_status()

        print(f"Status code: {response.status_code}")

        try:
            data = response.json()
            print("Response JSON:")
            print(json.dumps(data, indent=2)[:1500])
            return data
        except ValueError:
            print("Response was not valid JSON:")
            print(response.text[:500])
            return None

    except requests.RequestException as e:
        print(f"API call failed: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Perform a REST API call")
    parser.add_argument("--method", default="GET", choices=["GET", "POST", "PUT", "DELETE", "PATCH"])
    parser.add_argument(
        "--url",
        default="https://jsonplaceholder.typicode.com/posts/1",
        help="REST API endpoint URL",
    )
    parser.add_argument("--json", help="JSON request body as a string, e.g. '{\"key\": \"value\"}'")
    args = parser.parse_args()

    json_body = json.loads(args.json) if args.json else None
    call_rest_api(args.method, args.url, json_body)


if __name__ == "__main__":
    main()
