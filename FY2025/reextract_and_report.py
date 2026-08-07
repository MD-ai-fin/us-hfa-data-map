#!/usr/bin/env python3
"""Re-extract metrics from downloaded PDFs and regenerate Word report."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collect_and_analyze import (  # noqa: E402
    CATALOG_PATH,
    DATA_PATH,
    PDF_DIR,
    TXT_DIR,
    AgencyMetrics,
    build_reports,
    extract_metrics,
    extract_text_from_pdf,
    load_catalog,
)


def main() -> int:
    catalog = {a["state"]: a for a in load_catalog()}
    metrics: list[AgencyMetrics] = []

    for agency in load_catalog():
        state = agency["state"]
        abbr = agency["abbr"]
        pdf_path = PDF_DIR / f"{state}_{abbr}_FY2025_ACFR.pdf"
        metric = AgencyMetrics(state=state, name=agency["name"], abbr=abbr)
        if pdf_path.exists() and pdf_path.stat().st_size > 5000:
            metric.status = "downloaded"
            metric.source_file = pdf_path.name
            txt_path = TXT_DIR / pdf_path.with_suffix(".txt").name
            try:
                text = extract_text_from_pdf(pdf_path)
                txt_path.write_text(text, encoding="utf-8", errors="replace")
                extracted = extract_metrics(text, agency)
                for field in (
                    "net_position_2025",
                    "net_position_2024",
                    "net_position_change",
                    "net_position_change_pct",
                    "total_assets_2025",
                    "total_assets_2024",
                    "total_liabilities_2025",
                    "total_liabilities_2024",
                    "revenues_2025",
                    "expenses_2025",
                    "net_position_ratio",
                    "notes",
                ):
                    val = getattr(extracted, field)
                    if val is not None and val != []:
                        setattr(metric, field, val)
            except Exception as exc:
                metric.notes.append(f"文本提取失败: {exc}")
        else:
            metric.status = "missing"
            metric.notes.append("未找到FY2025 PDF链接")
        metrics.append(metric)

    DATA_PATH.write_text(
        json.dumps([m.__dict__ for m in metrics], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    build_reports(metrics)
    downloaded = sum(1 for m in metrics if m.status == "downloaded")
    print(f"Rebuilt report from {downloaded} PDFs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
