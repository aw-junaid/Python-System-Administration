#!/usr/bin/env python3
"""
upload_file.py
------------------
Uploads a local file to a remote server via an HTTP POST multipart
form request (the standard way most APIs and web forms accept file
uploads). Requires the `requests` library.

Usage:
    python3 upload_file.py --url https://httpbin.org/post --file report.pdf
    python3 upload_file.py --url https://api.example.com/upload --file image.png --field avatar
"""

import argparse
import os
import requests


def upload_file(url, filepath, field_name="file"):
    if not os.path.isfile(filepath):
        print(f"File not found: {filepath}")
        return False

    try:
        with open(filepath, "rb") as f:
            files = {field_name: (os.path.basename(filepath), f)}
            response = requests.post(url, files=files, timeout=30)

        print(f"Status code: {response.status_code}")
        print(f"Response body (first 500 chars):\n{response.text[:500]}")

        if response.ok:
            print("Upload succeeded.")
            return True
        else:
            print("Upload failed (non-2xx status code).")
            return False

    except requests.RequestException as e:
        print(f"Upload failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Upload a file to a server via HTTP POST")
    parser.add_argument("--url", required=True, help="Upload endpoint URL")
    parser.add_argument("--file", required=True, help="Path to the local file to upload")
    parser.add_argument("--field", default="file", help="Form field name expected by the server")
    args = parser.parse_args()

    upload_file(args.url, args.file, args.field)


if __name__ == "__main__":
    main()
