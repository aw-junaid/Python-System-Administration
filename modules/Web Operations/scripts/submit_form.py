#!/usr/bin/env python3
"""
submit_form.py
-------------------
Submits an HTML form via HTTP POST (the same request a browser would
send when you click "Submit"), using the `requests` library. Field
data is supplied as JSON so you can submit any form fields your
target expects.

Usage:
    python3 submit_form.py --url https://httpbin.org/post --data '{"username": "ahmad", "password": "secret"}'
"""

import argparse
import json
import requests


def submit_form(url, form_data):
    try:
        response = requests.post(url, data=form_data, timeout=15)

        print(f"Status code: {response.status_code}")
        print(f"Response body (first 800 chars):\n{response.text[:800]}")

        if response.ok:
            print("\nForm submitted successfully.")
        else:
            print("\nForm submission returned a non-success status code.")

        return response

    except requests.RequestException as e:
        print(f"Form submission failed: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Submit an HTML form via HTTP POST")
    parser.add_argument("--url", required=True, help="Form action URL")
    parser.add_argument(
        "--data",
        required=True,
        help='Form fields as a JSON string, e.g. \'{"username": "ahmad", "password": "secret"}\'',
    )
    args = parser.parse_args()

    form_data = json.loads(args.data)
    submit_form(args.url, form_data)


if __name__ == "__main__":
    main()
