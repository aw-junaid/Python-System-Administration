#!/usr/bin/env python3
"""
download_webpage.py
------------------------
Downloads the raw HTML of a web page and saves it to a local file -
useful for archiving, offline analysis, or feeding into a separate
parsing step. Requires the `requests` library.

Usage:
    python3 download_webpage.py --url https://example.com --output page.html
"""

import argparse
import requests


def download_webpage(url, output_path):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; WebOpsBot/1.0)"}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(response.text)

        print(f"Saved {len(response.text)} characters of HTML to: {output_path}")
        print(f"Status code: {response.status_code}")
        return True

    except requests.RequestException as e:
        print(f"Failed to download page: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Download a web page's HTML to a local file")
    parser.add_argument("--url", required=True, help="Web page URL")
    parser.add_argument("--output", default="page.html", help="Output HTML file path")
    args = parser.parse_args()

    download_webpage(args.url, args.output)


if __name__ == "__main__":
    main()
