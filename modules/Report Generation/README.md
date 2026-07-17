# Report Generation

Ten standalone Python automation scripts that generate reports in different
formats — HTML, Markdown, PDF, CSV, Excel, JSON, XML, chart images, an
interactive web dashboard, and inline terminal graphs.

Every script:
- Runs completely on its own (no shared modules to import).
- Works out of the box with **built-in sample data** — you don't need any
  input file to try it.
- Accepts `--help` for full usage details.
- Optionally accepts your own data via `--input` (CSV, or JSON for one script).

> ⚠️ **Before you run anything:** these scripts write files to your current
> working directory (or wherever you point `--output`/`--outdir`), and
> `generate_dashboard.py` starts a local web server on your machine. Review
> any script before running it, run it inside a project folder or virtual
> environment (not a system directory), and never run automation scripts
> from an untrusted repo without reading the code first. This applies to
> every script in this repo, not just this module.

---

## 1. Install

Clone the repo, then from inside this module's folder:

```bash
# (Recommended) create a virtual environment first
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install all dependencies for every script
pip install -r requirements.txt
```

Requires **Python 3.8+**. If you only care about one or two scripts, see the
per-script sections below — several scripts need no extra packages at all.

---

## 2. Scripts overview

| # | Script | Output format | Extra dependency |
|---|--------|---------------|-------------------|
| 1 | `generate_html_report.py` | `.html` | none (stdlib only) |
| 2 | `generate_markdown_report.py` | `.md` | none (stdlib only) |
| 3 | `generate_pdf_report.py` | `.pdf` | `reportlab` |
| 4 | `generate_csv_report.py` | `.csv` | none (stdlib only) |
| 5 | `generate_excel_report.py` | `.xlsx` | `openpyxl` |
| 6 | `generate_json_report.py` | `.json` | none (stdlib only) |
| 7 | `generate_xml_report.py` | `.xml` | none (stdlib only) |
| 8 | `generate_charts.py` | `.png` × 3 | `matplotlib` |
| 9 | `generate_dashboard.py` | live web app | `dash`, `plotly`, `pandas` |
| 10 | `generate_inline_graph.py` | terminal text | `asciichartpy` (optional) |

Run any script with `-h` to see its exact options:

```bash
python generate_html_report.py -h
```

---

## 3. Usage and expected output, per script

### 1. `generate_html_report.py`
Creates a responsive, styled HTML table report.

```bash
python generate_html_report.py
python generate_html_report.py --input data.csv --output report.html --title "Server Status"
```
**Expected output:** an `report.html` file. Open it in any browser — you'll
see a card-style page with a colored header, a table that scrolls
horizontally on narrow screens, and a footer with the generation timestamp.

---

### 2. `generate_markdown_report.py`
Creates a clean Markdown report for docs repos or wikis.

```bash
python generate_markdown_report.py
python generate_markdown_report.py --input data.csv --output report.md --title "Sprint Report"
```
**Expected output:** a `report.md` file with a title, a timestamp, and a
Markdown pipe-table. Renders correctly on GitHub/GitLab/any Markdown viewer.

---

### 3. `generate_pdf_report.py`
Creates a page-oriented PDF with a header and footer on every page.

```bash
pip install reportlab
python generate_pdf_report.py
python generate_pdf_report.py --input data.csv --output report.pdf --title "Invoice Summary"
```
**Expected output:** a `report.pdf` file. Every page shows the report title
and generation date at the top, a formatted data table in the body, and
"Page X" plus the script name in the footer.

---

### 4. `generate_csv_report.py`
Creates a plain tabular CSV extract from JSON input.

```bash
python generate_csv_report.py
python generate_csv_report.py --input data.json --output report.csv
```
Note: this script's `--input` expects a **JSON file** (a list of flat
objects), since the other scripts already cover CSV → other-format
conversion — this one demonstrates JSON → CSV.

**Expected output:** a `report.csv` file with a header row and one row per
record, openable in Excel, Google Sheets, or LibreOffice Calc.

---

### 5. `generate_excel_report.py`
Creates a formatted `.xlsx` workbook with a live formula and an embedded chart.

```bash
pip install openpyxl
python generate_excel_report.py
python generate_excel_report.py --input data.csv --output report.xlsx --title "Sales Report"
```
**Expected output:** a `report.xlsx` file with a styled header row, your
data, a **TOTAL** row using a real `=SUM(...)` Excel formula (recalculates
if you edit the numbers), and an embedded bar chart. Open in Excel or
LibreOffice Calc.

---

### 6. `generate_json_report.py`
Creates a structured, hierarchical JSON report for APIs/dashboards.

```bash
python generate_json_report.py
python generate_json_report.py --input data.csv --output report.json --title "Infra Health"
```
**Expected output:** a `report.json` file with a top-level `report` object
containing `metadata` (title, timestamp, record count, field list) and a
`data` array of one object per row. Valid JSON, parses with `json.load()`.

---

### 7. `generate_xml_report.py`
Creates a well-formed XML report for legacy enterprise tooling.

```bash
python generate_xml_report.py
python generate_xml_report.py --input data.csv --output report.xml --title "Order Summary"
```
**Expected output:** a `report.xml` file with a `<report>` root, a
`<metadata>` block, and a `<records>` block containing one `<record>` per
row (fields as child elements). Indented and UTF-8 declared.

---

### 8. `generate_charts.py`
Creates bar, line, and pie chart images from data.

```bash
pip install matplotlib
python generate_charts.py
python generate_charts.py --input data.csv --outdir charts --label-col Month --value-col Sales
```
**Expected output:** a folder (default `charts/`) containing three PNG
images: `bar_chart.png`, `line_chart.png`, `pie_chart.png`. Open them with
any image viewer or embed them in a document/email.

---

### 9. `generate_dashboard.py`
Launches a live, interactive dashboard in your browser.

```bash
pip install dash plotly pandas
python generate_dashboard.py
python generate_dashboard.py --input data.csv --port 8050
```
**Expected output:** the terminal prints a local URL, e.g.
`http://127.0.0.1:8050`. Open that URL in your browser to see a dropdown
filter, a bar chart, and a line chart that update live as you change the
filter. Stop the server with `Ctrl+C` in the terminal — closing the browser
tab alone does not stop it.

---

### 10. `generate_inline_graph.py`
Prints an ASCII/ANSI graph straight into your terminal — no file created.

```bash
# Works with zero extra installs (falls back to a plain-ASCII bar chart)
python generate_inline_graph.py

# For a smoother multi-row line plot:
pip install asciichartpy
python generate_inline_graph.py --color

python generate_inline_graph.py --input data.csv --value-col cpu_percent --color
```
**Expected output:** a graph made of text characters printed directly in
your terminal window (optionally in color with `--color`), along with
min/max/average stats. Nothing is written to disk.

---

## 4. Providing your own data

Most scripts accept `--input path/to/file.csv` where the first row is the
header row. If you don't pass `--input`, the script uses realistic built-in
sample data so you can see expected output immediately, with no setup.

`generate_csv_report.py` is the exception and takes `--input path/to/file.json`
(a JSON array of flat objects) instead of CSV, since it demonstrates a
JSON → CSV conversion.

---

## 5. Troubleshooting

- **`ModuleNotFoundError`** — you skipped `pip install -r requirements.txt`,
  or need the specific package listed in the table above for that script.
- **`generate_dashboard.py` won't start / port already in use** — pass a
  different port: `--port 8060`.
- **PDF/Excel file won't open / looks empty** — make sure the script printed
  "written to: ..." with no errors above it; re-run and check the full
  console output for a traceback.
- **Permission errors writing output** — point `--output`/`--outdir` at a
  folder you have write access to, e.g. your home directory or `./out/`.
