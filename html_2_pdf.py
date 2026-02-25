#!/usr/bin/env python3
"""
Convert downloaded HTML files to PDF (A4, smart margins, page breaks, long line wrapping)
Optimized for Termux + WeasyPrint - especially good for ARM docs with long code/comments
"""

import os
from pathlib import Path
import time
import sys

def get_weasyprint_css():
    """CSS with A4 layout, page-break control + aggressive long-line breaking"""
    return """
    @page {
        size: A4 portrait;
        margin: 0cm 0cm 0cm 0cm;    /* top right bottom left */
    }

    @page :first {
        margin-top: 3.2cm;
    }

    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        line-height: 1.45;
        font-size: 10.5pt;
    }

    /* ────────────── Aggressive wrapping for long unbreakable content ────────────── */
    pre, code, tt, kbd, samp, var,
    .hljs, .token, .string, .number, .literal, .comment,
    .bit-pattern, .hex-value, .register, .mnemonic, .instruction,
    span.token, .hljs-string, .hljs-number, .hljs-comment {
        white-space: pre-wrap;
        word-break: break-all;           /* break anywhere in long words/tokens */
        overflow-wrap: break-word;
        line-break: anywhere;            /* very aggressive modern break */
        hyphens: none;                   /* no hyphens in code */
        font-size: 9.2pt;                /* smaller → more fits per line */
        max-width: 100%;
    }

    /* Even stronger for table cells with code */
    table pre, table code, td pre, td code, th code {
        word-break: break-all;
        white-space: pre-wrap;
        line-break: anywhere;
        font-size: 9pt;
    }

    /* Tables */
    table {
        width: 100%;
        border-collapse: collapse;
        page-break-inside: auto;
        font-size: 9.8pt;
    }

    tr {
        page-break-inside: avoid;        /* don't break inside rows */
        page-break-after: auto;
    }

    thead { display: table-header-group; }
    tfoot { display: table-footer-group; }

    /* Blocks that should stay together */
    pre, blockquote, figure, .big-block, .avoid-break,
    div.table-responsive, .table-container {
        page-break-inside: avoid;
    }

    h1, h2, h3, h4 {
        page-break-after: avoid;
        page-break-inside: avoid;
    }

    p {
        orphans: 3;
        widows: 3;
    }

    /* Extra safety for very dense content */
    @media print {
        pre, code {
            font-size: 9pt;
        }
    }
    """


def convert_html_to_pdf():
    html_dir = Path("downloaded_html_fixed")
    pdf_dir = Path("pdf_output")

    if not html_dir.exists():
        print(f"❌ Directory not found: {html_dir}")
        print("   Run your download script first.")
        return False

    pdf_dir.mkdir(exist_ok=True)
    print(f"📁 Output folder: {pdf_dir.absolute()}")
    print("=" * 70)

    html_files = sorted(html_dir.glob("*.html"))

    if not html_files:
        print("❌ No .html files found in downloaded_html_fixed/")
        return False

    print(f"Found {len(html_files)} HTML files to convert")
    print("=" * 70)

    try:
        from weasyprint import HTML, CSS
    except ImportError:
        print("❌ WeasyPrint not installed.")
        print("   Run:  pip install weasyprint")
        print("   Termux deps (if needed): pkg install python-dev libjpeg-turbo-dev zlib-dev")
        return False

    successful = 0
    failed = 0

    custom_css = CSS(string=get_weasyprint_css())

    for i, html_path in enumerate(html_files, 1):
        pdf_name = html_path.stem + ".pdf"
        pdf_path = pdf_dir / pdf_name

        print(f"[{i:2d}/{len(html_files)}]  {html_path.name} → {pdf_name}")

        try:
            HTML(filename=str(html_path)).write_pdf(
                target=str(pdf_path),
                stylesheets=[custom_css]
            )

            size_kb = pdf_path.stat().st_size / 1024
            print(f"      ✓ Success  ({size_kb:6.1f} KB)")
            successful += 1

        except Exception as e:
            print(f"      ✗ Failed   {type(e).__name__}: {str(e)}")
            failed += 1

        if i < len(html_files):
            time.sleep(0.4)

    print("=" * 70)
    print("Conversion summary:")
    print(f"  Successful : {successful:3d}")
    print(f"  Failed     : {failed:3d}")
    print(f"  Total      : {successful + failed:3d}")
    if successful > 0:
        print(f"\nAll PDFs saved to: {pdf_dir.absolute()}")
    return successful > 0


def main():
    print("HTML → PDF Converter   (A4 + smart breaks + long-line wrapping)")
    print("=" * 70)

    html_dir = Path("downloaded_html_fixed")
    if not html_dir.exists() or not list(html_dir.glob("*.html")):
        print("\nNo HTML files found in 'downloaded_html_fixed'.")
        print("Please run your download script first.\n")
        sys.exit(1)

    print("\nThis will convert all HTML files in:")
    print(f"  {html_dir.absolute()}")
    print(f"  → PDF files in pdf_output/\n")

    answer = input("Proceed? [y/N]: ").strip().lower()
    if answer not in ('y', 'yes'):
        print("Cancelled.")
        return

    print("\nStarting conversion...\n")
    try:
        success = convert_html_to_pdf()
        if not success:
            print("\nNo files were converted successfully.")
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")


if __name__ == "__main__":
    main()