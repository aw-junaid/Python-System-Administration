#!/usr/bin/env python3
"""
generate_html_report.py

Generates a responsive, styled HTML report (table-based) from CSV data
or from built-in sample data if no input file is given.

Usage:
    python generate_html_report.py
    python generate_html_report.py --input data.csv --output report.html --title "My Report"

Expected output:
    An .html file that opens in any browser, showing a styled, responsive
    table with alternating row colors, a header banner, and a footer with
    the generation timestamp. Resize the browser window to see the table
    scroll horizontally on small screens.
"""

import argparse
import csv
import datetime
import html
import os
import sys


def load_sample_data():
    headers = ["Server", "CPU Usage (%)", "Memory Usage (%)", "Disk Usage (%)", "Status"]
    rows = [
        ["web-01", "42", "63", "71", "OK"],
        ["web-02", "88", "77", "54", "WARNING"],
        ["db-01", "35", "81", "90", "CRITICAL"],
        ["cache-01", "12", "22", "18", "OK"],
        ["worker-03", "67", "58", "40", "OK"],
    ]
    return headers, rows


def load_csv_data(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        raise ValueError("CSV file is empty.")
    return rows[0], rows[1:]


def status_class(value):
    v = value.strip().lower()
    if v in ("critical", "error", "fail", "failed"):
        return "status-critical"
    if v in ("warning", "warn"):
        return "status-warning"
    if v in ("ok", "good", "pass", "passed", "success"):
        return "status-ok"
    return ""


def build_html(headers, rows, title):
    generated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    header_html = "".join(f"<th>{html.escape(h)}</th>" for h in headers)

    body_rows = []
    for row in rows:
        cells = []
        for i, cell in enumerate(row):
            cls = status_class(cell) if headers[i].lower() == "status" else ""
            cells.append(f'<td class="{cls}">{html.escape(str(cell))}</td>')
        body_rows.append(f"<tr>{''.join(cells)}</tr>")
    body_html = "\n            ".join(body_rows)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<style>
    :root {{
        --primary: #2563eb;
        --bg: #f4f6fb;
        --card-bg: #ffffff;
        --border: #e2e8f0;
        --text: #1e293b;
        --muted: #64748b;
    }}
    * {{ box-sizing: border-box; }}
    body {{
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
        background: var(--bg);
        color: var(--text);
        padding: 24px;
    }}
    .container {{
        max-width: 1000px;
        margin: 0 auto;
        background: var(--card-bg);
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);
        overflow: hidden;
    }}
    header {{
        background: linear-gradient(135deg, var(--primary), #1d4ed8);
        color: #fff;
        padding: 24px 28px;
    }}
    header h1 {{ margin: 0 0 4px 0; font-size: 22px; }}
    header p {{ margin: 0; opacity: 0.85; font-size: 13px; }}
    .table-wrap {{ overflow-x: auto; padding: 0 0 8px 0; }}
    table {{
        width: 100%;
        border-collapse: collapse;
        min-width: 500px;
        font-size: 14px;
    }}
    thead th {{
        text-align: left;
        background: #f1f5f9;
        color: var(--muted);
        text-transform: uppercase;
        font-size: 11px;
        letter-spacing: 0.05em;
        padding: 12px 16px;
        border-bottom: 2px solid var(--border);
        position: sticky;
        top: 0;
    }}
    tbody td {{
        padding: 12px 16px;
        border-bottom: 1px solid var(--border);
    }}
    tbody tr:nth-child(even) {{ background: #fafbfe; }}
    tbody tr:hover {{ background: #eef2ff; }}
    .status-ok {{ color: #15803d; font-weight: 600; }}
    .status-warning {{ color: #b45309; font-weight: 600; }}
    .status-critical {{ color: #b91c1c; font-weight: 600; }}
    footer {{
        padding: 14px 28px;
        font-size: 12px;
        color: var(--muted);
        border-top: 1px solid var(--border);
    }}
    @media (max-width: 600px) {{
        body {{ padding: 8px; }}
        header {{ padding: 18px; }}
    }}
</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{html.escape(title)}</h1>
            <p>Generated on {generated_at}</p>
        </header>
        <div class="table-wrap">
            <table>
                <thead><tr>{header_html}</tr></thead>
                <tbody>
            {body_html}
                </tbody>
            </table>
        </div>
        <footer>Report generated automatically by generate_html_report.py &mdash; {len(rows)} row(s).</footer>
    </div>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description="Generate a responsive HTML report from CSV data.")
    parser.add_argument("--input", "-i", help="Path to input CSV file. If omitted, sample data is used.")
    parser.add_argument("--output", "-o", default="report.html", help="Path to output HTML file (default: report.html)")
    parser.add_argument("--title", "-t", default="System Status Report", help="Report title")
    args = parser.parse_args()

    if args.input:
        if not os.path.isfile(args.input):
            print(f"Error: input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        headers, rows = load_csv_data(args.input)
    else:
        headers, rows = load_sample_data()
        print("No --input provided, using built-in sample data.")

    html_content = build_html(headers, rows, args.title)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML report written to: {os.path.abspath(args.output)}")
    print("Open it in any web browser to view.")


if __name__ == "__main__":
    main()
