#!/usr/bin/env python3
"""Apply manual overrides to saved metrics and regenerate Word report only."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collect_and_analyze import (  # noqa: E402
    DATA_PATH,
    AgencyMetrics,
    MANUAL_OVERRIDES,
    build_reports,
)


def main() -> int:
    raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    metrics: list[AgencyMetrics] = []
    for item in raw:
        m = AgencyMetrics(
            state=item["state"],
            name=item["name"],
            abbr=item["abbr"],
            source_file=item.get("source_file", ""),
            source_url=item.get("source_url", ""),
            status=item.get("status", "missing"),
            net_position_2025=item.get("net_position_2025"),
            net_position_2024=item.get("net_position_2024"),
            net_position_change=item.get("net_position_change"),
            net_position_change_pct=item.get("net_position_change_pct"),
            total_assets_2025=item.get("total_assets_2025"),
            total_assets_2024=item.get("total_assets_2024"),
            total_liabilities_2025=item.get("total_liabilities_2025"),
            total_liabilities_2024=item.get("total_liabilities_2024"),
            revenues_2025=item.get("revenues_2025"),
            expenses_2025=item.get("expenses_2025"),
            net_position_ratio=item.get("net_position_ratio"),
            notes=item.get("notes", []),
        )
        overrides = MANUAL_OVERRIDES.get(m.state, {})
        for key, val in overrides.items():
            setattr(m, key, val)
        if m.net_position_2025 and m.total_assets_2025 and m.total_assets_2025 > 0:
            m.net_position_ratio = (m.net_position_2025 / m.total_assets_2025) * 100
        metrics.append(m)

    DATA_PATH.write_text(
        json.dumps([m.__dict__ for m in metrics], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    build_reports(metrics)
    print("Word reports regenerated (EN + CN) with updated Total Assets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
