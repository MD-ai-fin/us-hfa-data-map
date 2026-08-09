#!/usr/bin/env python3
"""Patch metadata on the Word-exported report PDFs and sanity-check tagging.

Word's COM automation reliably tags the PDF's content (headings, table
headers, reading order via ExportAsFixedFormat's DocStructureTags) but two
pieces come out wrong from this environment's Word:
  - /Info Title is blank (setting BuiltInDocumentProperties("Title") via
    COM automation fails silently here).
  - The PDF catalog's /Lang is always "en" regardless of the document's
    actual language (doc.Content.LanguageID controls per-run proofing
    language, not the docDefaults language Word's PDF exporter reads for
    the catalog-level /Lang).

This script fixes both directly with pikepdf, which edits the trailer /
catalog objects in place rather than rebuilding the whole PDF graph (unlike
pypdf's append/rewrite path), so it doesn't risk corrupting the tag tree
that's the whole point of this exercise.

This does NOT replace a real accessibility audit (Acrobat's Accessibility
Checker or the PAC tool) -- it just verifies the basic PDF/UA building
blocks are present: a tag tree, /Lang, a Title, and DisplayDocTitle.

Usage:
    python docs/postprocess_report_pdfs.py
"""
import os
import sys

import pikepdf

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(HERE, "reports")

TITLES = {
    "en": "FY2025 U.S. State Housing Finance Agencies — ACFR and Financial Statement Analysis",
    "zh": "FY2025 美国州级住房金融机构综合年报与财务报表分析",
    "es": "Agencias Estatales de Financiamiento de Vivienda de EE. UU. — FY2025 Análisis del ACFR y de los Estados Financieros",
    "pl": "Amerykańskie Stanowe Agencje Finansowania Budownictwa Mieszkaniowego — FY2025 Analiza ACFR i sprawozdań finansowych",
}
LANG_TAGS = {"en": "en-US", "zh": "zh-CN", "es": "es-ES", "pl": "pl-PL"}


def patch_and_check(lang):
    path = os.path.join(REPORTS_DIR, f"fy2025-{lang}.pdf")
    if not os.path.exists(path):
        print(f"[{lang}] MISSING: {path}")
        return False

    with pikepdf.open(path, allow_overwriting_input=True) as pdf:
        pdf.docinfo["/Title"] = TITLES[lang]
        pdf.docinfo["/Author"] = "MD-ai-fin"
        pdf.docinfo["/Subject"] = "FY2025 U.S. State HFA ACFR and Financial Statement Analysis"
        pdf.Root["/Lang"] = pikepdf.String(LANG_TAGS[lang])
        if "/ViewerPreferences" not in pdf.Root:
            pdf.Root["/ViewerPreferences"] = pikepdf.Dictionary()
        pdf.Root["/ViewerPreferences"]["/DisplayDocTitle"] = True
        struct_ok = "/StructTreeRoot" in pdf.Root
        marked_ok = bool(pdf.Root.get("/MarkInfo", {}).get("/Marked", False))
        pdf.save(path)

    # Re-read to report what actually landed on disk.
    with pikepdf.open(path) as check:
        title = str(check.docinfo.get("/Title", ""))
        lang_tag = str(check.Root.get("/Lang", ""))
        disp_title = bool(check.Root.get("/ViewerPreferences", {}).get("/DisplayDocTitle", False))
        struct_ok = "/StructTreeRoot" in check.Root
        marked_ok = bool(check.Root.get("/MarkInfo", {}).get("/Marked", False))
        npages = len(check.pages)

    ok = marked_ok and struct_ok and bool(lang_tag) and bool(title)
    status = "OK" if ok else "CHECK NEEDED"
    print(f"[{lang}] {status}  pages={npages} tagged={marked_ok} "
          f"structTree={struct_ok} lang={lang_tag!r} displayTitle={disp_title} "
          f"title={title!r}")
    return ok


def main():
    results = [patch_and_check(lang) for lang in ("en", "zh", "es", "pl")]
    if all(results):
        print("\nAll 4 report PDFs look tagged and have title/language metadata.")
        print("This is a basic sanity check, not a full PDF/UA audit -- for a")
        print("real compliance check, run Acrobat's Accessibility Checker or")
        print("the PAC tool (https://www.access-for-all.ch/en/pdf-lab/pdf-accessibility-checker-pac.html) over these files.")
    else:
        print("\nSome PDFs are missing or failed the basic checks -- see above.")


if __name__ == "__main__":
    main()
