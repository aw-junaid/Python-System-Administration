#!/usr/bin/env python3
"""
download_pdfs.py
---------------------
Downloads one or more PDF files from URLs and saves them locally,
verifying the content type is actually a PDF before saving. Requires
the `requests` library.

Usage:
    python3 download_pdfs.py --url https://example.com/document.pdf --output-dir pdfs
    python3 download_pdfs.py --urls-file pdf_urls.txt --output-dir pdfs
"""

import argparse
import os
from urllib.parse import urlparse
import requests


def download_pdf(url, output_dir):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; WebOpsBot/1.0)"}
        response = requests.get(url, headers=headers, timeout=20, stream=True)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")
        if "pdf" not in content_type.lower() and not url.lower().endswith(".pdf"):
            print(f"[SKIPPED] Not a PDF (Content-Type: {content_type}): {url}")
            return False

        os.makedirs(output_dir, exist_ok=True)

        filename = os.path.basename(urlparse(url).path) or "downloaded_document.pdf"
        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"

        output_path = os.path.join(output_dir, filename)

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)

        size_kb = os.path.getsize(output_path) / 1024
        print(f"[OK] Saved: {output_path} ({size_kb:.1f} KB)")
        return True

    except requests.RequestException as e:
        print(f"[FAILED] {url} - {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Download PDF files from one or more URLs")
    parser.add_argument("--url", help="A single PDF URL")
    parser.add_argument("--urls-file", help="Text file with one PDF URL per line")
    parser.add_argument("--output-dir", default="pdfs", help="Directory to save PDFs to")
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
        if download_pdf(url, args.output_dir):
            success_count += 1

    print(f"\nDone. {success_count}/{len(urls)} PDF(s) downloaded successfully.")


if __name__ == "__main__":
    main()
