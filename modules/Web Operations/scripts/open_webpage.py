#!/usr/bin/env python3
"""
open_webpage.py
-------------------
Opens a URL in the system's default web browser using the built-in
`webbrowser` module. Useful for automation scripts that need to pop
open a dashboard, report, or login page for the user.

Usage:
    python3 open_webpage.py --url https://example.com
    python3 open_webpage.py --url https://example.com --new-tab
"""

import argparse
import webbrowser


def open_page(url, new_tab=False):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    if new_tab:
        opened = webbrowser.open_new_tab(url)
    else:
        opened = webbrowser.open(url)

    if opened:
        print(f"Opened in default browser: {url}")
    else:
        print(f"Could not open a browser for: {url}")
        print("Note: this only works on machines with a graphical browser available "
              "(headless servers/containers will fail here).")


def main():
    parser = argparse.ArgumentParser(description="Open a URL in the default web browser")
    parser.add_argument("--url", required=True, help="URL to open")
    parser.add_argument("--new-tab", action="store_true", help="Open in a new browser tab")
    args = parser.parse_args()

    open_page(args.url, args.new_tab)


if __name__ == "__main__":
    main()
