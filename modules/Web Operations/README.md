# Web Operations — Python Automation Scripts

A collection of standalone Python scripts covering common **web
operations** tasks: making HTTP/REST requests, authenticating with
APIs, parsing JSON/XML, downloading files/images/PDFs, web scraping,
monitoring sites for changes, browser automation, and handling
cookies/sessions/forms.

This module belongs to the
[Python-System-Administration](https://github.com/aw-junaid/Python-System-Administration)
repository, under:
`modules/Web Operations/scripts/`

> **Repository note for contributors:** if you are adding this code to the
> repo linked above, place all `.py` files from the `scripts/` folder into
> `modules/Web Operations/scripts/`, and place **this file** (`README.md`)
> at `modules/Web Operations/README.md` (one level up from `scripts/` —
> that's where the repo's existing README link points). Put
> `requirements.txt` in the same folder as the README (or the repo root,
> if that's the existing convention — check how other modules do it and
> stay consistent).

---

## ⚠️ Caution Before You Start

- These scripts make **real network requests**. Only point them at sites
  and APIs you own, are authorized to test, or that explicitly allow this
  kind of traffic (e.g. public test APIs like `jsonplaceholder.typicode.com`
  or `httpbin.org`, used as defaults/examples below).
- **Web scraping (`web_scraper.py`) and site monitoring
  (`monitor_website.py`):** always check the target site's `robots.txt`
  and Terms of Service first, respect rate limits, and don't hammer a
  site with frequent requests. Scraping copyrighted content for
  redistribution can have legal implications — this is for personal data
  extraction/analysis, not content republishing.
- **Never hard-code real credentials, API keys, or tokens** into these
  scripts if you plan to commit them to GitHub. All auth-related scripts
  read secrets from command-line flags or environment variables instead.
- **`browser_automation.py`** launches a real Chrome/Chromium browser via
  Selenium. On a headless server/container, keep `--headless` (the
  default) — a visible window requires a display.
- **`upload_file.py` / `submit_form.py`** send real POST requests with
  file/form data — double-check the target URL before running against a
  production endpoint.
- Always review a script's code before running it, especially before
  scheduling it with `cron` or a systemd timer.

---

## 📁 Folder Structure

```
Web Operations/
├── README.md
├── requirements.txt
└── scripts/
    ├── open_webpage.py
    ├── download_file.py
    ├── upload_file.py
    ├── http_requests.py
    ├── rest_api_call.py
    ├── api_authentication.py
    ├── parse_json.py
    ├── parse_xml.py
    ├── download_webpage.py
    ├── check_website.py
    ├── web_scraper.py
    ├── monitor_website.py
    ├── browser_automation.py
    ├── handle_cookies.py
    ├── handle_sessions.py
    ├── download_images.py
    ├── download_pdfs.py
    └── submit_form.py
```

---

## 🔧 Installation

Requires **Python 3.7+**.

```bash
# 1. Clone the repo (or navigate to this module if already cloned)
git clone https://github.com/aw-junaid/Python-System-Administration.git
cd "Python-System-Administration/modules/Web Operations"

# 2. (Recommended) create a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

`requirements.txt` contains:
```
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
selenium>=4.15.0
webdriver-manager>=4.0.0
```

**Note on `browser_automation.py` only:** it needs a Chrome/Chromium
browser installed on the machine. `webdriver-manager` automatically
downloads a matching `chromedriver` on first run — no manual driver
setup needed. If Chrome isn't installed:
```bash
# Debian/Ubuntu
sudo apt-get install -y chromium-browser
```

All other scripts only need `requests` (and `beautifulsoup4`/`lxml` for
`web_scraper.py`). If you don't plan to use `browser_automation.py`, you
can skip installing `selenium`/`webdriver-manager`.

---

## 📜 Script-by-Script Guide

### 1. `open_webpage.py` — Open a web page
Opens a URL in the system's default browser (`webbrowser` module, no
external dependency).
```bash
python3 scripts/open_webpage.py --url https://example.com
```
**Expected output:** On a desktop/GUI machine, your default browser opens
the URL and the console prints `Opened in default browser: ...`. On a
headless server/container (no display), it prints a message explaining
that a graphical browser isn't available.

---

### 2. `download_file.py` — Download files
Streams a file download to disk with a progress percentage.
```bash
python3 scripts/download_file.py --url https://example.com/file.zip --output file.zip
```
**Expected output:** A live `Downloading... XX.X%` progress line, then
`Downloaded N bytes to: file.zip`.

---

### 3. `upload_file.py` — Upload files
Uploads a local file via multipart POST.
```bash
python3 scripts/upload_file.py --url https://httpbin.org/post --file report.pdf
```
**Expected output:** The HTTP status code and the first 500 characters of
the server's response (httpbin.org echoes back what it received, useful
for confirming the upload worked).

---

### 4. `http_requests.py` — Send HTTP requests
A generic GET/POST/PUT/DELETE/PATCH command-line HTTP client.
```bash
python3 scripts/http_requests.py --method GET --url https://example.com
python3 scripts/http_requests.py --method POST --url https://httpbin.org/post --data '{"key": "value"}'
```
**Expected output:** Status code, response headers, and the first 1000
characters of the response body.

---

### 5. `rest_api_call.py` — Perform REST API calls
Calls a JSON REST API and pretty-prints the parsed response. Defaults to
the free `jsonplaceholder.typicode.com` test API.
```bash
python3 scripts/rest_api_call.py --method GET --url https://jsonplaceholder.typicode.com/posts/1
```
**Expected output:** Status code followed by pretty-printed JSON, e.g.:
```json
{
  "userId": 1,
  "id": 1,
  "title": "...",
  "body": "..."
}
```

---

### 6. `api_authentication.py` — Authenticate with APIs
Demonstrates API Key, Basic Auth, and Bearer Token authentication.
```bash
python3 scripts/api_authentication.py --mode apikey --url https://api.example.com/data --api-key YOUR_KEY
python3 scripts/api_authentication.py --mode basic --url https://api.example.com/data --username user --password pass
python3 scripts/api_authentication.py --mode bearer --url https://api.example.com/data --token YOUR_TOKEN
```
**Expected output:** Status code plus `Authenticated successfully.` (200)
or `Authentication failed - check your credentials.` (401/403).

---

### 7. `parse_json.py` — Parse JSON responses
Fetches JSON from a URL or local file and shows how to safely navigate
it (keys, lists, `.get()` for missing fields).
```bash
python3 scripts/parse_json.py --url https://jsonplaceholder.typicode.com/users
python3 scripts/parse_json.py --file data.json
```
**Expected output:** The top-level type, keys or first list item, and a
pretty-printed preview of the structure.

---

### 8. `parse_xml.py` — Parse XML responses
Fetches XML from a URL or local file and parses it with the built-in
`xml.etree.ElementTree` (no extra dependency).
```bash
python3 scripts/parse_xml.py --url https://www.w3schools.com/xml/note.xml
python3 scripts/parse_xml.py --file data.xml
```
**Expected output:** Root tag/attributes, a list of child elements, and
an example of finding elements by tag name.

---

### 9. `download_webpage.py` — Download web pages
Saves the raw HTML of a page to a local file (for archiving or offline
parsing).
```bash
python3 scripts/download_webpage.py --url https://example.com --output page.html
```
**Expected output:** `Saved N characters of HTML to: page.html` and the
HTTP status code.

---

### 10. `check_website.py` — Check website availability
A simple uptime/health check with response time. Exits with code `0` if
up, `1` if down (good for cron/monitoring).
```bash
python3 scripts/check_website.py --url https://example.com
```
**Expected output:**
```
URL: https://example.com
Status code: 200
Response time: 0.063 seconds
[UP] Website is reachable and returned a success status code.
```

---

### 11. `web_scraper.py` — Web scraping
Extracts the page title, headings, and links using BeautifulSoup, or a
custom CSS selector.
```bash
python3 scripts/web_scraper.py --url https://example.com
python3 scripts/web_scraper.py --url https://example.com --selector "h2.title"
```
**Expected output:** Page title, list of headings (`<h1>`/`<h2>`/`<h3>`),
and a list of links with their text and `href`.
*(Reminder: check `robots.txt` and the site's terms before scraping.)*

---

### 12. `monitor_website.py` — Monitor website changes
Hashes page content and alerts when it changes between checks. Stores
hashes in a local `monitor_state/` folder.
```bash
# Continuous monitoring (checks every 5 minutes, Ctrl+C to stop)
python3 scripts/monitor_website.py --url https://example.com --interval 300

# Single check - ideal for a cron job
python3 scripts/monitor_website.py --url https://example.com --once
```
**Expected output:** First run prints `[BASELINE] First check - saving
initial hash...`; later runs print `[NO CHANGE]` or `[CHANGED] Page
content has changed: ...`.

---

### 13. `browser_automation.py` — Automate browser tasks
Uses Selenium to open a page, print its title, list links, and
optionally take a screenshot.
```bash
python3 scripts/browser_automation.py --url https://example.com --screenshot page.png
```
**Expected output:** Page title, current URL, `Screenshot saved to:
page.png` (if requested), and a list of links found on the page. First
run downloads a matching `chromedriver` automatically.

---

### 14. `handle_cookies.py` — Handle cookies
Shows receiving cookies from a server, saving them to JSON, and reusing
them on a later request.
```bash
python3 scripts/handle_cookies.py --url https://httpbin.org/cookies/set?demo=value --save cookies.json
python3 scripts/handle_cookies.py --url https://httpbin.org/cookies --load cookies.json
```
**Expected output:** The cookies received/sent as a dictionary, and (if
`--save` used) confirmation the cookies were written to a JSON file.

---

### 15. `handle_sessions.py` — Handle sessions
Demonstrates `requests.Session()` for persisting cookies and headers
across multiple requests (e.g. login once, then make authenticated
calls).
```bash
python3 scripts/handle_sessions.py --base-url https://httpbin.org
```
**Expected output:** Three sequential requests showing the cookie set in
request 1 is automatically carried into requests 2 and 3.

---

### 16. `download_images.py` — Download images
Downloads one or more images, verifying `Content-Type` is actually an
image before saving.
```bash
python3 scripts/download_images.py --url https://example.com/photo.jpg --output-dir images
python3 scripts/download_images.py --urls-file image_urls.txt --output-dir images
```
**Expected output:** `[OK] Saved: images/photo.jpg` per image, and a
summary like `Done. 3/3 image(s) downloaded successfully.`

---

### 17. `download_pdfs.py` — Download PDFs
Downloads one or more PDFs, verifying they're actually PDF content
before saving.
```bash
python3 scripts/download_pdfs.py --url https://example.com/document.pdf --output-dir pdfs
python3 scripts/download_pdfs.py --urls-file pdf_urls.txt --output-dir pdfs
```
**Expected output:** `[OK] Saved: pdfs/document.pdf (123.4 KB)` per file,
and a summary count.

---

### 18. `submit_form.py` — Submit HTML forms
Submits form field data via HTTP POST, the same request your browser
sends when you click "Submit".
```bash
python3 scripts/submit_form.py --url https://httpbin.org/post --data '{"username": "ahmad", "password": "secret"}'
```
**Expected output:** Status code, the server's response body (httpbin.org
echoes back the submitted fields), and a success/failure message.

---

## 🗓️ Automating with Cron (optional)

Once verified manually, schedule recurring checks, e.g. an uptime check
every 5 minutes:
```bash
crontab -e
# add this line:
*/5 * * * * /usr/bin/python3 /path/to/scripts/check_website.py --url https://example.com >> /var/log/uptime_cron.log 2>&1
```

---

## 🩺 Troubleshooting

| Problem | Likely Cause |
|---|---|
| `ModuleNotFoundError: No module named 'requests'` (or `bs4`, `selenium`) | Run `pip install -r requirements.txt` inside your active virtual environment |
| `browser_automation.py` fails with a display/driver error | Keep `--headless` on servers/containers; ensure Chrome/Chromium is installed |
| `check_website.py` / `download_file.py` time out | Increase `--timeout`, check your network/firewall, or confirm the target site is actually reachable from your machine |
| `web_scraper.py` finds 0 links/headings | The page may render content via JavaScript (BeautifulSoup only sees static HTML) — try `browser_automation.py` instead, which uses a real browser |
| `parse_json.py` / `parse_xml.py` error on `--url` | Confirm the URL actually returns JSON/XML (check `Content-Type` in the response) rather than an HTML error page |
| `upload_file.py` / `submit_form.py` returns 4xx/5xx | Check the field name expected by the server (`--field` flag) and that the endpoint accepts the method/content type you're sending |
| `monitor_website.py` always says `[CHANGED]` | Some sites include dynamic content (timestamps, ads, CSRF tokens) on every load — consider scraping only a specific `--selector` and hashing just that instead of the full page |
