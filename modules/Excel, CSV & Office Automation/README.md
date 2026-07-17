# Excel, CSV & Office Automation

A collection of standalone Python scripts for automating common Excel,
CSV, Word, PDF, and PowerPoint tasks. Every script is independent — you
only need to run the ones you actually want to use.

> **⚠️ Caution before you run anything**
> - These scripts create/modify files. Run them inside a scratch/test
>   folder first, not a directory with important files, until you're
>   comfortable with what each one does.
> - When a script is run **without input arguments**, it auto-generates
>   sample data (a `sample.xlsx`, `sample.csv`, `sample.pdf`, etc.) so
>   you can see it work immediately. Point it at your own real files
>   with the flags shown below once you've tried the sample run.
> - Scripts that write output (e.g. `--output`, `--output-dir`) will
>   **overwrite existing files** of the same name without asking for
>   confirmation. Double-check paths before running against real data.
> - `pdf_metadata.py` writes PDF **content and metadata** — always keep
>   a backup of the original PDF before running `update` or `watermark`
>   mode against it.
> - Some scripts (`word_automation.py`, `generate_pdf_report.py`,
>   `create_powerpoint.py`, `pdf_metadata.py`) depend on third-party
>   libraries listed in `requirements.txt` — install them first or the
>   script will fail with an `ImportError`.

---

## Installation

1. Clone this repository (or download this folder).
2. (Recommended) Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate      # on Windows: venv\Scripts\activate
   ```
3. Install all dependencies used by these scripts:
   ```bash
   pip install -r requirements.txt
   ```
4. Confirm your Python version is 3.8 or newer:
   ```bash
   python3 --version
   ```

Every script can then be run directly, e.g.:
```bash
python3 read_excel.py
```

---

## Scripts overview

| # | Script | What it does |
|---|--------|---------------|
| 172 | `read_excel.py` | Open an `.xlsx` file and print a summary/preview of every sheet |
| 173 | `write_excel.py` | Create a new formatted spreadsheet from scratch (or into a template) |
| 174 | `format_excel.py` | Apply header styling, auto column widths, and conditional formatting |
| 175 | `generate_reports.py` | Combine multiple CSVs into one multi-sheet analytical Excel report |
| 176 | `merge_csv.py` | Concatenate multiple CSV files with the same columns into one file |
| 177 | `split_csv.py` | Split a large CSV by row count or by a column's distinct values |
| 178 | `csv_to_excel.py` | Wrap a raw CSV into a formatted `.xlsx` workbook |
| 179 | `excel_to_csv.py` | Extract each sheet of an Excel workbook into its own CSV file |
| 180 | `word_automation.py` | Mail-merge a CSV of recipients into `.docx` letters, or generate a report `.docx` |
| 181 | `generate_pdf_report.py` | Build a print-ready PDF report (title + table) from CSV data |
| 182 | `create_powerpoint.py` | Build a `.pptx` deck from a simple CSV outline (Title, Body columns) |
| 183 | `pdf_metadata.py` | Read PDF metadata, update it, or add a text watermark to every page |

---

## Usage & expected output

### 172. `read_excel.py`
```bash
python3 read_excel.py --file sample.xlsx --max-rows 5
```
Prints each sheet's name, dimensions, header row, and a preview of up
to `--max-rows` data rows. Run with no arguments to auto-create and
read `sample.xlsx`.

### 173. `write_excel.py`
```bash
python3 write_excel.py --output report.xlsx
```
Creates `report.xlsx` with a bold header row, sample order data, and
auto-sized columns. Use `--template existing.xlsx --sheet "Data"` to
append into an existing workbook instead of starting from scratch.

### 174. `format_excel.py`
```bash
python3 format_excel.py --file sample.xlsx --value-column D --threshold 50
```
Styles the header (bold, colored fill), auto-sizes columns, and adds
conditional formatting to `--value-column`: cells below `--threshold`
turn red, cells at/above it turn green. Saves back to `--file` unless
`--output` is given.

### 175. `generate_reports.py`
```bash
python3 generate_reports.py --inputs sales.csv inventory.csv --output report.xlsx
```
Produces `report.xlsx` with one sheet per input CSV plus an
auto-generated **Summary** sheet (row counts, sum/average of the first
numeric column per sheet). Run with no `--inputs` to see it work on
built-in sample sales/inventory data.

### 176. `merge_csv.py`
```bash
python3 merge_csv.py --inputs jan.csv feb.csv mar.csv --output merged.csv
```
Writes `merged.csv` containing the header once, followed by every data
row from each input file in order. Warns (but still merges) if headers
don't match across files.

### 177. `split_csv.py`
```bash
# By row count
python3 split_csv.py --file data.csv --by rows --rows-per-file 200

# By column value
python3 split_csv.py --file data.csv --by column --column Region
```
Writes multiple CSV files into `--output-dir` (default
`split_output/`) — either `<name>_part1.csv`, `_part2.csv`, ... or
`<name>_<value>.csv` per unique value in `--column`.

### 178. `csv_to_excel.py`
```bash
python3 csv_to_excel.py --file data.csv --output data.xlsx
```
Wraps the CSV into `data.xlsx` with a bold, frozen header row and
auto-sized columns.

### 179. `excel_to_csv.py`
```bash
python3 excel_to_csv.py --file report.xlsx --output-dir csv_output
```
Writes one CSV per worksheet into `--output-dir`. Use
`--sheet "SheetName" --output single.csv` to extract just one sheet.

### 180. `word_automation.py`
```bash
# Mail merge
python3 word_automation.py --mode mail-merge --recipients recipients.csv --output-dir merged_letters

# Single generated report document
python3 word_automation.py --mode report --output report.docx
```
Mail-merge mode reads a CSV (columns: `name, product, order_id, city`
in the sample) and writes one personalized `.docx` letter per row.
Report mode writes a single formatted `.docx` with headings and a
table.

### 181. `generate_pdf_report.py`
```bash
python3 generate_pdf_report.py --file data.csv --output report.pdf --title "Sales Report"
```
Builds `report.pdf` with a title, an intro paragraph, and a styled
table of the CSV's rows (bold header, alternating row shading).

### 182. `create_powerpoint.py`
```bash
python3 create_powerpoint.py --file outline.csv --output deck.pptx --title "Quarterly Review"
```
Reads an outline CSV (columns: `Title, Body`, with `Body` bullets
separated by `|`) and builds `deck.pptx`: one title slide plus one
content slide per outline row.

### 183. `pdf_metadata.py`
```bash
# Read metadata
python3 pdf_metadata.py --file document.pdf --mode read

# Update metadata
python3 pdf_metadata.py --file document.pdf --mode update --title "New Title" --author "Jane Doe" --output updated.pdf

# Add a watermark
python3 pdf_metadata.py --file document.pdf --mode watermark --watermark-text "CONFIDENTIAL" --output watermarked.pdf
```
`read` mode prints title/author/subject/creator/producer/page count.
`update` and `watermark` modes write a new PDF to `--output`, leaving
the original file untouched.

---

## General notes

- Every script uses `argparse`, so run `python3 <script>.py --help` at
  any time to see its full list of options.
- Every script is safe to run with **zero arguments** — it will
  generate small sample data first so you can see expected output
  before pointing it at your own files.
- Scripts are independent of each other; you don't need to install or
  run all of them just to use one.
- Tested with Python 3.10+ on Linux; should work unmodified on macOS
  and Windows with the same `pip install -r requirements.txt` step.
