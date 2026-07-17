#!/usr/bin/env python3
"""
pdf_metadata.py
================
Read PDF metadata (author, title, subject, creation date, page count)
and optionally update metadata fields or add a text watermark to every
page of an existing PDF.

Usage
-----
    # Read metadata only
    python pdf_metadata.py --file document.pdf --mode read

    # Update metadata fields
    python pdf_metadata.py --file document.pdf --mode update --title "New Title" \
        --author "Jane Doe" --output updated.pdf

    # Add a watermark
    python pdf_metadata.py --file document.pdf --mode watermark --watermark-text "CONFIDENTIAL" \
        --output watermarked.pdf

If --file is omitted, a small sample PDF is generated first (requires
reportlab for sample generation only).

Expected output
----------------
- read mode: prints title/author/subject/creator/producer/page count.
- update mode: writes --output with the metadata fields changed.
- watermark mode: writes --output with the given text stamped
  diagonally across every page.

Requirements
------------
    pip install pypdf reportlab
    (reportlab is only needed to auto-generate the sample PDF and to
    render the watermark overlay)
"""

import argparse
import io
import os

from pypdf import PdfReader, PdfWriter


def create_sample_pdf(path: str) -> None:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    c = canvas.Canvas(path, pagesize=letter)
    c.setTitle("Sample Document")
    c.setAuthor("Automation Script")
    c.setSubject("Demonstration PDF for pdf_metadata.py")
    c.drawString(72, 750, "Sample PDF Document")
    c.drawString(72, 730, "This file was generated automatically for testing.")
    c.showPage()
    c.drawString(72, 750, "Page 2")
    c.save()
    print(f"[info] No --file given, created a sample PDF at: {path}")


def read_metadata(path: str) -> None:
    reader = PdfReader(path)
    meta = reader.metadata or {}
    print(f"PDF: {path}")
    print(f"  Pages:    {len(reader.pages)}")
    print(f"  Title:    {meta.get('/Title', '(none)')}")
    print(f"  Author:   {meta.get('/Author', '(none)')}")
    print(f"  Subject:  {meta.get('/Subject', '(none)')}")
    print(f"  Creator:  {meta.get('/Creator', '(none)')}")
    print(f"  Producer: {meta.get('/Producer', '(none)')}")


def update_metadata(path: str, output: str, title, author, subject) -> None:
    reader = PdfReader(path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    new_meta = dict(reader.metadata or {})
    if title is not None:
        new_meta["/Title"] = title
    if author is not None:
        new_meta["/Author"] = author
    if subject is not None:
        new_meta["/Subject"] = subject
    writer.add_metadata(new_meta)

    with open(output, "wb") as f:
        writer.write(f)

    print(f"[success] Metadata updated. File written to: {output}")
    print(f"          Title={new_meta.get('/Title')} Author={new_meta.get('/Author')} Subject={new_meta.get('/Subject')}")


def add_watermark(path: str, output: str, text: str) -> None:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    # Build a single-page watermark overlay in memory
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.saveState()
    c.setFont("Helvetica-Bold", 40)
    c.setFillGray(0.5, 0.4)  # light grey, semi-transparent look
    c.translate(300, 400)
    c.rotate(45)
    c.drawCentredString(0, 0, text)
    c.restoreState()
    c.save()
    buf.seek(0)

    watermark_reader = PdfReader(buf)
    watermark_page = watermark_reader.pages[0]

    reader = PdfReader(path)
    writer = PdfWriter()
    for page in reader.pages:
        page.merge_page(watermark_page)
        writer.add_page(page)

    with open(output, "wb") as f:
        writer.write(f)

    print(f"[success] Watermark '{text}' applied to {len(reader.pages)} page(s). File written to: {output}")


def main():
    parser = argparse.ArgumentParser(description="Read/edit PDF metadata or add a watermark.")
    parser.add_argument("--file", default=None, help="Path to the input PDF")
    parser.add_argument("--mode", choices=["read", "update", "watermark"], default="read")
    parser.add_argument("--output", default="output.pdf", help="Output PDF path for update/watermark modes")
    parser.add_argument("--title", default=None, help="New title (update mode)")
    parser.add_argument("--author", default=None, help="New author (update mode)")
    parser.add_argument("--subject", default=None, help="New subject (update mode)")
    parser.add_argument("--watermark-text", default="CONFIDENTIAL", help="Text to stamp on every page (watermark mode)")
    args = parser.parse_args()

    path = args.file
    if path is None:
        path = "sample.pdf"
        create_sample_pdf(path)

    if not os.path.exists(path):
        print(f"[error] File not found: {path}")
        return

    if args.mode == "read":
        read_metadata(path)
    elif args.mode == "update":
        update_metadata(path, args.output, args.title, args.author, args.subject)
    else:
        add_watermark(path, args.output, args.watermark_text)


if __name__ == "__main__":
    main()
