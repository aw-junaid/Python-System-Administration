#!/usr/bin/env python3
"""
xslt_transform.py
---------------------
Topic 358: Transform XML with XSLT

Applies an XSLT stylesheet to an XML document for structural
transformation/formatting (e.g. XML -> HTML, or reshaping one XML
schema into another). Requires `lxml` (see requirements.txt) since
the standard library has no XSLT engine.

USAGE
    # Run built-in demo (transforms a sample <employees> XML document
    # into an HTML table using a built-in stylesheet)
    python3 xslt_transform.py

    # Use your own XML + XSLT files
    python3 xslt_transform.py --xml data.xml --xslt style.xsl --output result.html

EXPECTED OUTPUT
    The transformed output (HTML/XML/text depending on the
    stylesheet), printed to the terminal and written to --output if
    given.
"""
import argparse
import sys
from pathlib import Path

try:
    from lxml import etree
except ImportError:
    sys.exit(
        "ERROR: lxml is not installed.\n"
        "Install dependencies first:  pip install -r requirements.txt"
    )

DEMO_XML = """<?xml version="1.0"?>
<employees>
  <employee>
    <name>Alice</name>
    <role>Engineer</role>
  </employee>
  <employee>
    <name>Bob</name>
    <role>Designer</role>
  </employee>
</employees>
"""

DEMO_XSLT = """<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" indent="yes"/>
  <xsl:template match="/employees">
    <table border="1">
      <tr><th>Name</th><th>Role</th></tr>
      <xsl:for-each select="employee">
        <tr>
          <td><xsl:value-of select="name"/></td>
          <td><xsl:value-of select="role"/></td>
        </tr>
      </xsl:for-each>
    </table>
  </xsl:template>
</xsl:stylesheet>
"""


def main():
    parser = argparse.ArgumentParser(description="Transform XML using an XSLT stylesheet")
    parser.add_argument("--xml", help="Path to the source XML file")
    parser.add_argument("--xslt", help="Path to the XSLT stylesheet file")
    parser.add_argument("--output", help="Path to write the transformed output")
    args = parser.parse_args()

    xml_text = Path(args.xml).read_text(encoding="utf-8") if args.xml else DEMO_XML
    xslt_text = Path(args.xslt).read_text(encoding="utf-8") if args.xslt else DEMO_XSLT

    try:
        xml_doc = etree.fromstring(xml_text.encode("utf-8"))
        xslt_doc = etree.fromstring(xslt_text.encode("utf-8"))
        transform = etree.XSLT(xslt_doc)
        result = transform(xml_doc)
    except Exception as exc:
        sys.exit(f"ERROR: XSLT transform failed: {exc}")

    output_text = str(result)
    print(output_text)
    if args.output:
        Path(args.output).write_text(output_text, encoding="utf-8")
        print(f"[written to {args.output}]", file=sys.stderr)


if __name__ == "__main__":
    main()
