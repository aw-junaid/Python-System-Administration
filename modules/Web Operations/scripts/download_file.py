#!/usr/bin/env python3
"""
download_file.py
--------------------
Downloads a file from a URL and saves it to disk, streaming the
content so large files don't get loaded fully into memory. Shows a
simple progress indicator. Requires the `requests` library.

Usage:
    python3 download_file.py --url https://example.com/file.zip --output file.zip
"""

import argparse
import os
import sys
import requests


def download_file(url, output_path, chunk_size=8192):
    try:
        with requests.get(url, stream=True, timeout=30) as response:
            response.raise_for_status()
            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0

            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size:
                            percent = downloaded / total_size * 100
                            sys.stdout.write(f"\rDownloading... {percent:.1f}%")
                            sys.stdout.flush()

            print(f"\nDownloaded {downloaded} bytes to: {output_path}")
            return True

    except requests.RequestException as e:
        print(f"\nDownload failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Download a file from a URL")
    parser.add_argument("--url", required=True, help="File URL")
    parser.add_argument("--output", required=True, help="Local path to save the file")
    args = parser.parse_args()

    download_file(args.url, args.output)


if __name__ == "__main__":
    main()
