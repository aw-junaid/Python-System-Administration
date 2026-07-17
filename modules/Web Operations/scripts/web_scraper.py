#!/usr/bin/env python3
"""
web_scraper.py
------------------
Scrapes a web page and extracts data using BeautifulSoup: page title,
all links, and all headings. Requires `requests` and `beautifulsoup4`.

IMPORTANT: Always check a site's robots.txt and Terms of Service
before scraping, respect rate limits, and only scrape data you're
authorized to collect.

Usage:
    python3 web_scraper.py --url https://example.com
    python3 web_scraper.py --url https://example.com --selector "h2.title"
"""

import argparse
import requests
from bs4 import BeautifulSoup


def scrape_page(url, css_selector=None):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; WebOpsBot/1.0)"}

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch page: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.title.string.strip() if soup.title else "(no title found)"
    print(f"Page title: {title}\n")

    if css_selector:
        elements = soup.select(css_selector)
        print(f"Found {len(elements)} element(s) matching selector '{css_selector}':")
        for el in elements[:20]:
            print(f"  - {el.get_text(strip=True)[:100]}")
        return

    # Default: show headings and links
    headings = soup.find_all(["h1", "h2", "h3"])
    print(f"Headings found: {len(headings)}")
    for h in headings[:10]:
        print(f"  <{h.name}> {h.get_text(strip=True)[:80]}")

    links = soup.find_all("a", href=True)
    print(f"\nLinks found: {len(links)}")
    for link in links[:10]:
        print(f"  {link.get_text(strip=True)[:40] or '(no text)'} -> {link['href']}")


def main():
    parser = argparse.ArgumentParser(description="Scrape a web page using BeautifulSoup")
    parser.add_argument("--url", required=True, help="Page URL to scrape")
    parser.add_argument("--selector", help="Optional CSS selector to extract specific elements")
    args = parser.parse_args()

    scrape_page(args.url, args.selector)


if __name__ == "__main__":
    main()
