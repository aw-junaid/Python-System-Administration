#!/usr/bin/env python3
"""
generate_pdf_report.py
========================
Create a print-ready PDF report using ReportLab: a title, intro
paragraph, and a styled data table, built from CSV data.

Usage
-----
    python generate_pdf_report.py --file data.csv --output report.pdf --title "Sales Report"

If --file is omitted, sample CSV data is generated first.

Expected output
----------------
A single PDF file (--output) containing a title heading, a short
paragraph, and a table rendering every row of the CSV with alternating
row shading and a bold header row.

Requirements
------------
    pip install reportlab
"""

import argparse
import csv
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def create_sample_csv(path: str) -> None:
    content = (
        "Product,Units Sold,Revenue\n"
        "Wireless Mouse,120,3600\n"
        "Mechanical Keyboard,85,6800\n"
        "USB-C Hub,60,1740\n"
        "Monitor Stand,40,1200\n"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[info] No --file given, created a sample CSV at: {path}")


def generate_pdf_report(csv_path: str, output: str, title: str) -> None:
    if not os.path.exists(csv_path):
        print(f"[error] File not found: {csv_path}")
        return

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        table_data = list(reader)

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(output, pagesize=letter,
                             topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    elements = []

    elements.append(Paragraph(title, styles["Title"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(
        "This report was generated automatically from CSV source data using ReportLab.",
        styles["Normal"],
    ))
    elements.append(Spacer(1, 18))

    if table_data:
        table = Table(table_data, hAlign="LEFT")
        style_commands = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]
        # Alternate row shading for readability
        for row_idx in range(1, len(table_data)):
            if row_idx % 2 == 0:
                style_commands.append(("BACKGROUND", (0, row_idx), (-1, row_idx), colors.HexColor("#F2F2F2")))
        table.setStyle(TableStyle(style_commands))
        elements.append(table)
    else:
        elements.append(Paragraph("(no data found in CSV)", styles["Normal"]))

    doc.build(elements)
    print(f"[success] PDF report written to: {output}")
    print(f"          Table rows (incl. header): {len(table_data)}")


def main():
    parser = argparse.ArgumentParser(description="Generate a print-ready PDF report from CSV data.")
    parser.add_argument("--file", default=None, help="Path to the input CSV file")
    parser.add_argument("--output", default="report.pdf", help="Path for the output PDF")
    parser.add_argument("--title", default="Automated Report", help="Title shown at the top of the PDF")
    args = parser.parse_args()

    path = args.file
    if path is None:
        path = "sample.csv"
        create_sample_csv(path)

    generate_pdf_report(path, args.output, args.title)


if __name__ == "__main__":
    main()
