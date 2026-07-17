#!/usr/bin/env python3
"""
download_images.py
-----------------------
Downloads one or more images from URLs and saves them to a local
folder, with content-type validation so you don't accidentally save
an error page as a ".jpg". Requires the `requests` library.

Usage:
    python3 download_images.py --url https://example.com/photo.jpg --output-dir images
    python3 download_images.py --urls-file image_urls.txt --output-dir images
"""

import argparse
import os
from urllib.parse import urlparse
import requests


def download_image(url, output_dir):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; WebOpsBot/1.0)"}
        response = requests.get(url, headers=headers, timeout=15, stream=True)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            print(f"[SKIPPED] Not an image (Content-Type: {content_type}): {url}")
            return False

        os.makedirs(output_dir, exist_ok=True)

        filename = os.path.basename(urlparse(url).path) or "downloaded_image"
        if "." not in filename:
            ext = content_type.split("/")[-1].split(";")[0]
            filename = f"{filename}.{ext}"

        output_path = os.path.join(output_dir, filename)

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)

        print(f"[OK] Saved: {output_path}")
        return True

    except requests.RequestException as e:
        print(f"[FAILED] {url} - {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Download images from one or more URLs")
    parser.add_argument("--url", help="A single image URL")
    parser.add_argument("--urls-file", help="Text file with one image URL per line")
    parser.add_argument("--output-dir", default="images", help="Directory to save images to")
    args = parser.parse_args()

    if not args.url and not args.urls_file:
        print("Provide either --url or --urls-file")
        return

    urls = []
    if args.url:
        urls.append(args.url)
    if args.urls_file:
        with open(args.urls_file, "r") as f:
            urls.extend(line.strip() for line in f if line.strip())

    success_count = 0
    for url in urls:
        if download_image(url, args.output_dir):
            success_count += 1

    print(f"\nDone. {success_count}/{len(urls)} image(s) downloaded successfully.")


if __name__ == "__main__":
    main()
