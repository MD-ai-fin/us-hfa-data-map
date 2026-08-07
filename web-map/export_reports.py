#!/usr/bin/env python3
"""Export FY2025 Word analysis reports to HTML for the web map."""

from __future__ import annotations

from pathlib import Path

import mammoth

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = Path(__file__).resolve().parent / "reports"

SOURCES = {
    "fy2025-zh.html": ROOT / "FY2025" / "FY2025_美国州级住房金融机构ACFR综合分析报告.docx",
    "fy2025-en.html": ROOT / "FY2025" / "FY2025_US_State_HFA_ACFR_Analysis_Report.docx",
}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, src in SOURCES.items():
        if not src.exists():
            raise FileNotFoundError(src)
        with src.open("rb") as f:
            result = mammoth.convert_to_html(f)
        out = OUT_DIR / name
        out.write_text(result.value, encoding="utf-8")
        print(f"Wrote {out} ({len(result.value)} chars, {len(result.messages)} messages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
