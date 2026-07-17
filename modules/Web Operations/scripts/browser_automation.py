#!/usr/bin/env python3
"""
browser_automation.py
--------------------------
Demonstrates basic browser automation using Selenium WebDriver:
opening a page, waiting for it to load, taking a screenshot, and
reading the page title. Requires `selenium` and a Chrome/Chromium
browser plus a matching chromedriver (handled automatically via
`webdriver-manager`).

Usage:
    python3 browser_automation.py --url https://example.com --screenshot page.png
    python3 browser_automation.py --url https://example.com --headless

Notes:
    - Runs headless by default in this script's --headless flag off
      means it will try to open a visible browser window, which
      requires a display (won't work on a bare server/container
      without a virtual display like Xvfb).
    - On first run, webdriver-manager downloads the correct
      chromedriver version automatically.
"""

import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def run_browser_task(url, screenshot_path=None, headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,800")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        print(f"Opening: {url}")
        driver.get(url)

        print(f"Page title: {driver.title}")
        print(f"Current URL: {driver.current_url}")

        if screenshot_path:
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved to: {screenshot_path}")

        # Example: extract all visible link text on the page
        links = driver.find_elements("tag name", "a")
        print(f"\nFound {len(links)} link(s) on the page. First 10:")
        for link in links[:10]:
            text = link.text.strip() or "(no visible text)"
            href = link.get_attribute("href")
            print(f"  {text} -> {href}")

    finally:
        driver.quit()


def main():
    parser = argparse.ArgumentParser(description="Automate a basic browser task with Selenium")
    parser.add_argument("--url", required=True, help="URL to open")
    parser.add_argument("--screenshot", help="Path to save a screenshot (e.g. page.png)")
    parser.add_argument("--headless", action="store_true", default=True, help="Run without a visible window (default: on)")
    parser.add_argument("--visible", dest="headless", action="store_false", help="Run with a visible browser window")
    args = parser.parse_args()

    run_browser_task(args.url, args.screenshot, args.headless)


if __name__ == "__main__":
    main()
