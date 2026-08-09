#!/usr/bin/env python3
"""Build combined state dataset for HFA interactive map."""

from __future__ import annotations

import csv
import io
import json
import re
import sys
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
FY2025_METRICS = BASE / "FY2025" / "fy2025_metrics.json"
FY2024_METRICS = BASE / "FY2024" / "fy2024_metrics.json"
CATALOG = BASE / "FY2025" / "state_hfa_catalog.json"
HFA_STAFF_COUNTS = BASE / "hfa_staff_counts.json"
OUT = BASE / "docs" / "state_data.json"

FIPS_TO_STATE = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT",
    "10": "DE", "11": "DC", "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL",
    "18": "IN", "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD",
    "25": "MA", "26": "MI", "27": "MN", "28": "MS", "29": "MO", "30": "MT", "31": "NE",
    "32": "NV", "33": "NH", "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND",
    "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD",
    "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA", "54": "WV",
    "55": "WI", "56": "WY",
}

STATE_NAMES = {
    "AL": {"en": "Alabama", "zh": "阿拉巴马州"},
    "AK": {"en": "Alaska", "zh": "阿拉斯加州"},
    "AZ": {"en": "Arizona", "zh": "亚利桑那州"},
    "AR": {"en": "Arkansas", "zh": "阿肯色州"},
    "CA": {"en": "California", "zh": "加利福尼亚州"},
    "CO": {"en": "Colorado", "zh": "科罗拉多州"},
    "CT": {"en": "Connecticut", "zh": "康涅狄格州"},
    "DE": {"en": "Delaware", "zh": "特拉华州"},
    "DC": {"en": "District of Columbia", "zh": "哥伦比亚特区"},
    "FL": {"en": "Florida", "zh": "佛罗里达州"},
    "GA": {"en": "Georgia", "zh": "佐治亚州"},
    "HI": {"en": "Hawaii", "zh": "夏威夷州"},
    "ID": {"en": "Idaho", "zh": "爱达荷州"},
    "IL": {"en": "Illinois", "zh": "伊利诺伊州"},
    "IN": {"en": "Indiana", "zh": "印第安纳州"},
    "IA": {"en": "Iowa", "zh": "艾奥瓦州"},
    "KS": {"en": "Kansas", "zh": "堪萨斯州"},
    "KY": {"en": "Kentucky", "zh": "肯塔基州"},
    "LA": {"en": "Louisiana", "zh": "路易斯安那州"},
    "ME": {"en": "Maine", "zh": "缅因州"},
    "MD": {"en": "Maryland", "zh": "马里兰州"},
    "MA": {"en": "Massachusetts", "zh": "马萨诸塞州"},
    "MI": {"en": "Michigan", "zh": "密歇根州"},
    "MN": {"en": "Minnesota", "zh": "明尼苏达州"},
    "MS": {"en": "Mississippi", "zh": "密西西比州"},
    "MO": {"en": "Missouri", "zh": "密苏里州"},
    "MT": {"en": "Montana", "zh": "蒙大拿州"},
    "NE": {"en": "Nebraska", "zh": "内布拉斯加州"},
    "NV": {"en": "Nevada", "zh": "内华达州"},
    "NH": {"en": "New Hampshire", "zh": "新罕布什尔州"},
    "NJ": {"en": "New Jersey", "zh": "新泽西州"},
    "NM": {"en": "New Mexico", "zh": "新墨西哥州"},
    "NY": {"en": "New York", "zh": "纽约州"},
    "NC": {"en": "North Carolina", "zh": "北卡罗来纳州"},
    "ND": {"en": "North Dakota", "zh": "北达科他州"},
    "OH": {"en": "Ohio", "zh": "俄亥俄州"},
    "OK": {"en": "Oklahoma", "zh": "俄克拉荷马州"},
    "OR": {"en": "Oregon", "zh": "俄勒冈州"},
    "PA": {"en": "Pennsylvania", "zh": "宾夕法尼亚州"},
    "RI": {"en": "Rhode Island", "zh": "罗德岛州"},
    "SC": {"en": "South Carolina", "zh": "南卡罗来纳州"},
    "SD": {"en": "South Dakota", "zh": "南达科他州"},
    "TN": {"en": "Tennessee", "zh": "田纳西州"},
    "TX": {"en": "Texas", "zh": "德克萨斯州"},
    "UT": {"en": "Utah", "zh": "犹他州"},
    "VT": {"en": "Vermont", "zh": "佛蒙特州"},
    "VA": {"en": "Virginia", "zh": "弗吉尼亚州"},
    "WA": {"en": "Washington", "zh": "华盛顿州"},
    "WV": {"en": "West Virginia", "zh": "西弗吉尼亚州"},
    "WI": {"en": "Wisconsin", "zh": "威斯康星州"},
    "WY": {"en": "Wyoming", "zh": "怀俄明州"},
}

NAME_TO_STATE = {v["en"]: k for k, v in STATE_NAMES.items()}
NAME_TO_STATE["District of Columbia"] = "DC"


def fetch_url(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def parse_money(s: str) -> float | None:
    if not s:
        return None
    s = s.strip().replace(",", "").replace("$", "")
    try:
        return float(s)
    except ValueError:
        return None


def to_dollars(val: float | None, unit: str) -> float | None:
    if val is None:
        return None
    mult = {"raw": 1, "thousand": 1_000, "million": 1_000_000, "billion": 1_000_000_000}
    return val * mult.get(unit, 1)


def detect_unit_scale(text: str) -> str:
    t = text.lower()
    if "in thousands" in t or "(in thousands)" in t or "amounts in thousands" in t:
        return "thousand"
    if "in millions" in t or "(in millions)" in t:
        return "million"
    return "raw"


def normalize_financial_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    # Fix broken OCR decimals like "8 00.0" -> "800.0" without merging table columns.
    text = re.sub(r"(\d)\s+(\d{2,3}\.\d+)", r"\1\2", text)
    # Fix broken thousands like "3 ,040,037" or "9 06,761"
    text = re.sub(r"(\d)\s+,", r"\1,", text)
    text = re.sub(r",\s+(\d)", r",\1", text)
    text = re.sub(r"(\d)\s+(\d{1,2})(?=,\d)", r"\1\2", text)
    return re.sub(r"\s+", " ", text)


def plausible_np(value: float | None) -> bool:
    return value is not None and 1_000_000 <= value <= 25_000_000_000


def plausible_assets(value: float | None) -> bool:
    return value is not None and 10_000_000 <= value <= 100_000_000_000


def plausible_liabilities(value: float | None) -> bool:
    return value is not None and 1_000_000 <= value <= 100_000_000_000


def detect_unit_scale(text: str) -> str:
    head = text[:100000].lower()
    if any(
        k in head
        for k in (
            "in thousands of dollars",
            "(in thousands)",
            "amounts in thousands",
            "dollars in thousands",
            "(dollars in thousands)",
        )
    ):
        return "thousand"
    if any(k in head for k in ("millions of dollars", "(in millions)", "in millions of dollars")):
        return "million"
    return "raw"


def scaled_pair(
    cur_raw: float | None,
    prior_raw: float | None,
    plausible,
    preferred: str | None = None,
) -> tuple[float | None, float | None]:
    if cur_raw is None or prior_raw is None:
        return None, None
    # Full-dollar statement amounts (e.g. 4,771,085,657)
    if cur_raw >= 10_000_000 and prior_raw >= 1_000_000:
        if plausible(cur_raw) and plausible(prior_raw):
            return cur_raw, prior_raw

    units: list[str] = []
    if preferred:
        units.append(preferred)
    units += ["million", "thousand", "raw", "billion"]

    best: tuple[float, float] | None = None
    seen: set[str] = set()
    for unit in units:
        if unit in seen:
            continue
        seen.add(unit)
        cur = to_dollars(cur_raw, unit)
        prior = to_dollars(prior_raw, unit)
        if plausible(cur) and plausible(prior):
            if best is None or cur > best[0]:
                best = (cur, prior)
    if best:
        return best
    return None, None


def numbers_from_line_segment(segment: str) -> list[float]:
    nums: list[float] = []
    for token in re.findall(r"[\d,\.]+", segment):
        val = parse_money(token)
        if val is None:
            continue
        if val == int(val) and 2018 <= val <= 2035:
            continue
        nums.append(val)
    return nums


def _candidates_from_match(
    m: re.Match, scale: str, col_current: int, col_prior: int
) -> tuple[float | None, float | None]:
    groups = m.groups()
    if len(groups) < 2:
        return None, None
    cur = to_dollars(parse_money(groups[col_current]), scale)
    prior = to_dollars(parse_money(groups[col_prior]), scale)
    return cur, prior


def extract_hfa_pair(text: str, report_fy: int) -> dict[str, dict[str, float | None]]:
    """Extract net position, total assets, and total liabilities for report_fy and prior year."""
    t = normalize_financial_text(text)
    scale = detect_unit_scale(text)
    current_key = str(report_fy)
    prior_key = str(report_fy - 1)
    out = {
        current_key: {"net_position": None, "total_assets": None, "total_liabilities": None},
        prior_key: {"net_position": None, "total_assets": None, "total_liabilities": None},
    }

    np_candidates: list[tuple[float, str]] = []
    asset_candidates: list[tuple[float, str]] = []
    liab_candidates: list[tuple[float, str]] = []

    def add_np(val: float | None, tag: str, year_key: str) -> None:
        if val and plausible_np(val):
            np_candidates.append((val, f"{tag}:{year_key}"))
            if out[year_key]["net_position"] is None or val > out[year_key]["net_position"]:
                out[year_key]["net_position"] = val

    def add_assets(val: float | None, tag: str, year_key: str) -> None:
        if val and plausible_assets(val):
            asset_candidates.append((val, f"{tag}:{year_key}"))
            if out[year_key]["total_assets"] is None or val > out[year_key]["total_assets"]:
                out[year_key]["total_assets"] = val

    def add_liabilities(val: float | None, tag: str, year_key: str) -> None:
        if val and plausible_liabilities(val):
            liab_candidates.append((val, f"{tag}:{year_key}"))
            if out[year_key]["total_liabilities"] is None or val > out[year_key]["total_liabilities"]:
                out[year_key]["total_liabilities"] = val

    default_scale = scale if scale != "raw" else "thousand"

    comparative_patterns = (
        (
            r"Total net position",
            add_np,
            plausible_np,
        ),
        (
            r"Total assets(?:\s+and\s+deferred\s+outflows(?:\s+of\s+resources)?)?",
            add_assets,
            plausible_assets,
        ),
        (
            r"Total liabilities(?:\s+and\s+deferred\s+inflows(?:\s+of\s+resources)?)?",
            add_liabilities,
            plausible_liabilities,
        ),
    )

    # Comparative statement / schedule lines (thousands, millions, or whole dollars)
    for label, add_fn, plausible in comparative_patterns:
        pat = rf"{label}\s+(.{{0,220}})"
        for m in re.finditer(pat, t, re.I):
            nums = numbers_from_line_segment(m.group(1))
            if len(nums) < 2:
                continue
            if len(nums) >= 4:
                cur_raw, prior_raw = nums[-2], nums[-1]
            else:
                cur_raw, prior_raw = nums[0], nums[1]
            cur, prior = scaled_pair(cur_raw, prior_raw, plausible, default_scale)
            add_fn(cur, "cmp", current_key)
            add_fn(prior, "cmp", prior_key)

    # MD&A condensed tables with repeated $ columns (gov / business-type / total)
    mda_labels = (
        ("Total Assets", add_assets, plausible_assets),
        ("Total Liabilities", add_liabilities, plausible_liabilities),
        ("Total Net Position", add_np, plausible_np),
    )
    for label, add_fn, plausible in mda_labels:
        for m in re.finditer(rf"{label}\s+((?:\$[\d,\.]+\s*)+)", t, re.I):
            amounts = [parse_money(x) for x in re.findall(r"\$([\d,\.]+)", m.group(1))]
            amounts = [a for a in amounts if a is not None]
            if len(amounts) < 3:
                continue
            if len(amounts) % 3 != 0:
                continue
            cur_raw, prior_raw = amounts[-3], amounts[-2]
            cur, prior = scaled_pair(cur_raw, prior_raw, plausible, "million")
            add_fn(cur, "mda_dollar", current_key)
            add_fn(prior, "mda_dollar", prior_key)

    # Statement-level lines with large raw dollar amounts (no unit scaling)
    for m in re.finditer(r"Total assets\s+([\d,]{8,})\s+([\d,]{8,})", t, re.I):
        cur, prior = _candidates_from_match(m, "raw", 0, 1)
        add_assets(cur, "stmt_raw", current_key)
        add_assets(prior, "stmt_raw", prior_key)

    for m in re.finditer(r"Total liabilities\s+([\d,]{8,})\s+([\d,]{8,})", t, re.I):
        cur, prior = _candidates_from_match(m, "raw", 0, 1)
        add_liabilities(cur, "stmt_raw", current_key)
        add_liabilities(prior, "stmt_raw", prior_key)

    for m in re.finditer(r"Total net position\s+\$?\s*([\d,]{8,})\s+\$?\s*([\d,]{8,})", t, re.I):
        cur, prior = _candidates_from_match(m, "raw", 0, 1)
        add_np(cur, "stmt_raw", current_key)
        add_np(prior, "stmt_raw", prior_key)

    # MD&A summary rows in millions (may omit $ prefix): "Total assets 7,722.4 6,805.0 917.4"
    mda_million_rows = (
        ("Total assets", add_assets, plausible_assets),
        ("Total liabilities", add_liabilities, plausible_liabilities),
        ("Total net position", add_np, plausible_np),
    )
    for label, add_fn, plausible in mda_million_rows:
        for m in re.finditer(
            rf"{label}\s+(?P<c1>[\d,\.]+)\s+(?P<c2>[\d,\.]+)\s+(?P<chg>[\d,\.]+)",
            t,
            re.I,
        ):
            cur, prior = scaled_pair(
                parse_money(m.group("c1")),
                parse_money(m.group("c2")),
                plausible,
                "million",
            )
            add_fn(cur, "mda_million_row", current_key)
            add_fn(prior, "mda_million_row", prior_key)

    # MD&A / summary tables (millions, no $ prefix)
    for m in re.finditer(
        r"Total assets and(?:\s+deferred)?(?:\s+outflows)?(?:\s+of resources)?\s+([\d,\.]+)\s+([\d,\.]+)",
        t,
        re.I,
    ):
        cur, prior = _candidates_from_match(m, "million", 0, 1)
        add_assets(cur, "mda_total_assets", current_key)
        add_assets(prior, "mda_total_assets", prior_key)

    for m in re.finditer(
        r"Total net position\s+(?P<c1>[\d,\.]+)\s+(?P<c2>[\d,\.]+)\s+(?P<pct>[\d,\.]+)%",
        t,
        re.I,
    ):
        cur = to_dollars(parse_money(m.group("c1")), "million")
        prior = to_dollars(parse_money(m.group("c2")), "million")
        add_np(cur, "mda_pct", current_key)
        add_np(prior, "mda_pct", prior_key)

    # Narrative patterns
    narrative = [
        (
            rf"position of \$(?P<prior>[\d,\.]+) million as of June 30, {report_fy - 1}",
            "million",
            "np_prior_only",
        ),
        (
            rf"Total net position as of June 30, {report_fy}, was \$(?P<cur>[\d,\.]+) million.*?position of \$(?P<prior>[\d,\.]+) million as of June 30, {report_fy - 1}",
            "million",
            "np",
        ),
        (
            rf"overall net position increased by .*? to \$(?P<cur>[\d,\.]+) million as of June 30, {report_fy}",
            "million",
            "np_cur_only",
        ),
        (
            rf"Total assets were \$(?P<cur>[\d,\.]+) billion as of June 30, {report_fy} compared to \$(?P<prior>[\d,\.]+) billion as of June 30, {report_fy - 1}",
            "billion",
            "assets",
        ),
        (
            rf"Total assets increased by .*? to \$(?P<cur>[\d,\.]+) billion compared to .*? \$(?P<prior>[\d,\.]+) billion",
            "billion",
            "assets",
        ),
        (
            rf"Total liabilities were \$(?P<cur>[\d,\.]+) billion as of June 30, {report_fy} compared to \$(?P<prior>[\d,\.]+) billion as of June 30, {report_fy - 1}",
            "billion",
            "liabilities",
        ),
        (
            rf"net position totaled \$(?P<cur>[\d,\.]+) billion at June 30, {report_fy}",
            "billion",
            "np_cur_only",
        ),
    ]
    for pat, unit, kind in narrative:
        m = re.search(pat, t, re.I)
        if not m:
            continue
        if kind == "np":
            add_np(to_dollars(parse_money(m.group("cur")), unit), "narr", current_key)
            add_np(to_dollars(parse_money(m.group("prior")), unit), "narr", prior_key)
        elif kind == "assets":
            add_assets(to_dollars(parse_money(m.group("cur")), unit), "narr", current_key)
            add_assets(to_dollars(parse_money(m.group("prior")), unit), "narr", prior_key)
        elif kind == "liabilities":
            add_liabilities(to_dollars(parse_money(m.group("cur")), unit), "narr", current_key)
            add_liabilities(to_dollars(parse_money(m.group("prior")), unit), "narr", prior_key)
        elif kind == "np_prior_only":
            add_np(to_dollars(parse_money(m.group("prior")), unit), "narr", prior_key)
        elif kind == "np_cur_only":
            add_np(to_dollars(parse_money(m.group("cur")), unit), "narr", current_key)

    # Prefer largest plausible asset figure (avoids partial "Total assets" subtotals)
    if asset_candidates:
        best_by_year = {current_key: None, prior_key: None}
        for val, tag in asset_candidates:
            yk = tag.split(":")[-1]
            if yk in best_by_year and (best_by_year[yk] is None or val > best_by_year[yk]):
                best_by_year[yk] = val
        for yk, val in best_by_year.items():
            if val:
                out[yk]["total_assets"] = val

    if liab_candidates:
        best_by_year = {current_key: None, prior_key: None}
        for val, tag in liab_candidates:
            yk = tag.split(":")[-1]
            if yk in best_by_year and (best_by_year[yk] is None or val > best_by_year[yk]):
                best_by_year[yk] = val
        for yk, val in best_by_year.items():
            if val:
                out[yk]["total_liabilities"] = val

    if np_candidates:
        best_by_year = {current_key: None, prior_key: None}
        for val, tag in np_candidates:
            yk = tag.split(":")[-1]
            if yk in best_by_year and (best_by_year[yk] is None or val > best_by_year[yk]):
                best_by_year[yk] = val
        for yk, val in best_by_year.items():
            if val:
                out[yk]["net_position"] = val

    return out


COMPONENT_UNIT_HFA: dict[str, str] = {
    "GA": r"Housing and Finance Authority",
}

# Typical single HFA net position is well below state consolidated totals.
HFA_NET_POSITION_CEILING = 5_500_000_000
HFA_ASSETS_CEILING = 15_000_000_000


def is_state_consolidated_report(text: str, state: str) -> bool:
    """True when the PDF/text is a state-wide ACFR, not the HFA entity report."""
    head = text[:15000]
    state_name = STATE_NAMES.get(state, {}).get("en", "")
    if not state_name:
        return False
    head_lower = head.lower()
    if re.search(rf"^State of {re.escape(state_name)}\s*$", head, re.I | re.M):
        return True
    if f"state of {state_name.lower()}" in head_lower[:2500] and "government-wide" in head_lower[:8000]:
        if not re.search(r"housing finance authority|housing and finance authority|housing development authority", head_lower[:4000], re.I):
            return True
    return False


def _component_unit_column_index(chunk: str, entity_pat: str) -> int | None:
    """Column index for an HFA in a state component-unit SNP table."""
    markers = [
        r"Environmental Finance",
        r"World Congress Center",
        r"Housing and Finance",
        r"Lottery Corporation",
        r"Ports Authority",
    ]
    found: list[str] = []
    for pat in markers:
        if re.search(pat, chunk, re.I):
            found.append(pat)
    for i, pat in enumerate(found):
        if re.search(entity_pat, pat, re.I) or re.search(entity_pat, chunk[:800], re.I):
            # Match entity_pat against known marker list order in header
            pass
    # Fixed order for GA component-unit header row
    ga_order = [
        r"Environmental Finance",
        r"World Congress Center",
        r"Housing and Finance",
        r"Lottery Corporation",
    ]
    if re.search(entity_pat, chunk, re.I):
        for i, pat in enumerate(ga_order):
            if re.search(pat, chunk[:1200], re.I):
                if re.search(entity_pat, pat, re.I):
                    return i
    return None


def extract_component_unit_hfa(text: str, report_fy: int, entity_pat: str) -> dict[str, dict[str, float | None]]:
    """Extract HFA figures from state component-unit SNP (amounts in thousands)."""
    t = normalize_financial_text(text)
    current_key = str(report_fy)
    empty = {"net_position": None, "total_assets": None, "total_liabilities": None}
    out = {current_key: dict(empty), str(report_fy - 1): dict(empty)}

    sections = list(
        re.finditer(
            r"Statement of Net Position[\s\S]{0,100}?Component Units[\s\S]{0,20000}",
            t,
            re.I,
        )
    )
    if not sections:
        return out

    chunk = sections[0].group(0)
    if not re.search(entity_pat, chunk, re.I):
        return out

    col = _component_unit_column_index(chunk, entity_pat)
    if col is None:
        # GA GHFA is the 3rd authority column in the standard layout
        if re.search(entity_pat, chunk, re.I):
            col = 2
        else:
            return out

    unit = "thousand"
    for label, field, plausible in (
        ("Total Assets", "total_assets", plausible_assets),
        ("Total Liabilities", "total_liabilities", plausible_liabilities),
        ("Total Net Position", "net_position", plausible_np),
    ):
        for m in re.finditer(rf"{label}\s+([\d,\.\$\(\)\s\-]+)", chunk, re.I):
            nums = numbers_from_line_segment(m.group(1))
            if len(nums) <= col:
                continue
            raw = nums[col]
            if raw is not None and raw < 0:
                raw = abs(raw)
            val = to_dollars(raw, unit)
            if plausible(val):
                out[current_key][field] = val
                break

    return out


def extract_hfa_mda_millions(text: str, report_fy: int) -> dict[str, dict[str, float | None]]:
    """Prefer MD&A summary tables labeled (Dollars in Millions) on entity-specific reports."""
    t = normalize_financial_text(text)
    current_key = str(report_fy)
    prior_key = str(report_fy - 1)
    empty = {"net_position": None, "total_assets": None, "total_liabilities": None}
    out = {current_key: dict(empty), prior_key: dict(empty)}

    if not re.search(r"dollars in millions|\(in millions\)|in millions of dollars", t[:100000], re.I):
        return out

    rows = (
        (r"Total assets", "total_assets", plausible_assets),
        (r"Total liabilities", "total_liabilities", plausible_liabilities),
        (r"Total net position", "net_position", plausible_np),
    )
    for label, field, plausible in rows:
        for m in re.finditer(
            rf"{label}\s+\$?\s*(?P<c1>[\d,\.]+)\s+\$?\s*(?P<c2>[\d,\.]+)",
            t,
            re.I,
        ):
            cur, prior = scaled_pair(parse_money(m.group("c1")), parse_money(m.group("c2")), plausible, "million")
            if not cur or not prior:
                continue
            if cur > HFA_NET_POSITION_CEILING and field == "net_position":
                continue
            if cur > 15_000_000_000:
                continue
            out[current_key][field] = cur
            out[prior_key][field] = prior
            break

    return out


def merge_pair_into_state(
    by_state: dict[str, dict],
    st: str,
    pair: dict[str, dict[str, float | None]],
    years: tuple[str, ...] = ("2024", "2025"),
) -> None:
    for ykey in years:
        if ykey not in pair:
            continue
        for field in ("net_position", "total_assets", "total_liabilities"):
            check = {
                "net_position": plausible_np,
                "total_assets": plausible_assets,
                "total_liabilities": plausible_liabilities,
            }[field]
            merge_field(by_state[st][ykey], field, pair.get(ykey, {}).get(field), check)


def find_txt_for_state(state: str, year: int, hfa_name: str | None = None) -> Path | None:
    candidates: list[Path] = []
    for d in (BASE / f"FY{year}" / "txt", BASE / f"FY{year}"):
        if not d.exists():
            continue
        candidates.extend(sorted(d.glob(f"{state}_*.txt")))
    if not candidates:
        return None
    if not hfa_name:
        return candidates[0]

    tokens = [w.lower() for w in re.findall(r"[A-Za-z]{4,}", hfa_name)]
    best: Path | None = None
    best_score = -999
    for path in candidates:
        try:
            if path.stat().st_size < 500:
                continue
            head_raw = path.read_text(encoding="utf-8", errors="ignore")[:12000]
        except OSError:
            continue
        if len(head_raw.strip()) < 500:
            continue
        head = head_raw.lower()
        score = sum(2 for tok in tokens if tok in head)
        if "fy2024" in path.name.lower() or "2024_acfr" in path.name.lower():
            score += 8
        if is_state_consolidated_report(head_raw, state):
            score -= 20
        if "housing finance" in head or "housing and finance" in head:
            score += 5
        if score > best_score:
            best_score = score
            best = path
    return best or next((p for p in candidates if p.stat().st_size >= 500), None)


MANUAL_OVERRIDES: dict[str, dict] = {
    "CA": {
        "net_position_2025": 3_442_918_000,
        "net_position_2024": 3_220_848_000,
        "total_assets_2025": 4_980_031_000,
        "total_assets_2024": 4_558_601_000,
        "total_liabilities_2025": 1_511_418_000,
        "total_liabilities_2024": 1_337_753_000,
        "net_position_change_pct": 6.9,
    },
    "AL": {
        "net_position_2025": 516_018_000,
        "net_position_2024": 484_375_000,
        "total_assets_2025": 1_364_901_000,
        "total_assets_2024": 1_082_234_000,
        "total_liabilities_2025": 846_539_000,
        "total_liabilities_2024": 596_731_000,
    },
    "DE": {
        "net_position_2025": 732_459_779,
        "net_position_2024": 705_352_858,
        "total_assets_2025": 1_564_907_790,
        "total_assets_2024": 1_033_142_200,
        "total_liabilities_2025": 831_012_336,
        "total_liabilities_2024": 321_660_800,
        "net_position_change_pct": 3.8,
    },
    "ID": {"net_position_2025": 716_007_000, "total_assets_2025": 6_026_206_000, "net_position_change_pct": 8.5},
    "IL": {
        "net_position_2025": 1_533_700_000,
        "net_position_2024": 1_373_800_000,
        "total_assets_2025": 7_846_500_000,
        "total_assets_2024": 6_526_900_000,
        "total_liabilities_2025": 6_247_600_000,
        "total_liabilities_2024": 5_110_300_000,
        "net_position_change_pct": 11.6,
    },
    "IN": {
        "net_position_2025": 599_528_335,
        "net_position_2024": 497_849_911,
        "total_assets_2025": 3_247_001_038,
        "total_assets_2024": 2_740_054_627,
        "total_liabilities_2025": 2_646_002_390,
        "total_liabilities_2024": 2_242_119_665,
        "net_position_change_pct": 20.4,
    },
    "LA": {"net_position_2025": 821_730_000, "total_assets_2025": 1_545_038_000, "net_position_change_pct": 31.9},
    "MA": {
        "net_position_2025": 2_083_948_000,
        "net_position_2024": 1_822_847_000,
        "total_assets_2025": 8_079_680_000,
        "total_assets_2024": 7_519_040_000,
        "total_liabilities_2025": 5_998_525_000,
        "total_liabilities_2024": 5_684_807_000,
        "net_position_change_pct": 14.3,
    },
    "MI": {
        "net_position_2025": 1_292_050_000,
        "net_position_2024": 1_160_992_000,
        "total_assets_2025": 8_027_764_000,
        "total_assets_2024": 6_868_705_000,
        "total_liabilities_2025": 6_685_707_000,
        "total_liabilities_2024": 5_662_217_000,
        "net_position_change_pct": 11.3,
    },
    "MN": {"net_position_2025": 1_649_443_000, "total_assets_2025": 8_543_311_000},
    "MO": {
        "net_position_2025": 708_007_000,
        "net_position_2024": 664_589_000,
        "total_assets_2025": 3_192_551_000,
        "total_assets_2024": 2_461_129_000,
        "total_liabilities_2025": 2_491_534_000,
        "total_liabilities_2024": 1_806_271_000,
        "net_position_change_pct": 6.5,
    },
    "CO": {
        "net_position_2025": 971_675_000,
        "net_position_2024": 828_465_000,
        "total_assets_2025": 8_385_309_000,
        "net_position_change_pct": 17.3,
    },
    "NC": {
        "net_position_2025": 979_793_000,
        "net_position_2024": 856_993_000,
        "total_assets_2025": 4_815_950_000,
        "net_position_change_pct": 14.3,
    },
    "ND": {
        "net_position_2025": 280_805_000,
        "net_position_2024": 256_450_000,
        "total_assets_2025": 2_818_952_000,
        "total_assets_2024": 2_255_841_000,
        "total_liabilities_2025": 2_521_600_000,
        "total_liabilities_2024": 1_978_564_000,
        "net_position_change_pct": 9.0,
    },
    "NE": {
        "net_position_2025": 454_474_000,
        "net_position_2024": 432_973_000,
        "total_assets_2025": 2_910_591_000,
        "total_assets_2024": 2_249_850_000,
        "total_liabilities_2025": 2_447_488_000,
        "total_liabilities_2024": 1_805_585_000,
        "net_position_change_pct": 5.0,
    },
    "AR": {
        "net_position_2025": 530_822_000,
        "net_position_2024": 505_820_000,
        "total_assets_2025": 1_142_207_000,
        "total_assets_2024": 1_008_195_000,
        "total_liabilities_2025": 611_156_000,
        "total_liabilities_2024": 502_172_000,
        "net_position_change_pct": 5.1,
    },
    "ME": {
        "net_position_2025": 508_535_000,
        "net_position_2024": 475_829_000,
        "net_position_change_pct": 6.9,
    },
    "UT": {
        "net_position_2025": 610_650_000,
        "net_position_2024": 514_400_000,
        "total_assets_2025": 3_861_330_000,
        "total_assets_2024": 2_923_819_000,
        "net_position_change_pct": 18.7,
    },
    "CT": {
        "net_position_2025": 957_039_000,
        "net_position_2024": 764_506_000,
        "total_assets_2025": 8_122_355_000,
        "total_assets_2024": 7_043_493_000,
        "total_liabilities_2025": 6_986_013_000,
        "total_liabilities_2024": 6_115_720_000,
        "net_position_change_pct": 25.2,
    },
    "KY": {
        "net_position_2025": 519_377_000,
        "net_position_2024": 486_274_000,
        "total_assets_2025": 1_434_509_000,
        "total_assets_2024": 1_180_300_000,
        "total_liabilities_2025": 915_132_000,
        "total_liabilities_2024": 694_000_000,
        "net_position_change_pct": 6.8,
    },
    "SC": {
        "net_position_2025": 612_736_978,
        "net_position_2024": 570_045_294,
        "total_assets_2025": 2_330_498_465,
        "total_assets_2024": 1_847_789_251,
        "total_liabilities_2025": 1_717_292_827,
        "total_liabilities_2024": 1_275_296_701,
        "net_position_change_pct": 7.5,
    },
    "VT": {
        "net_position_2025": 123_644_000,
        "net_position_2024": 112_192_000,
        "total_assets_2025": 679_864_000,
        "total_assets_2024": 565_610_000,
        "total_liabilities_2025": 581_488_000,
        "total_liabilities_2024": 480_222_000,
        "net_position_change_pct": 10.2,
    },
    "OK": {
        "net_position_2025": 417_517_722,
        "net_position_2024": 387_013_564,
        "total_assets_2025": 1_472_100_000,
        "total_assets_2024": 1_091_700_000,
        "total_liabilities_2025": 1_054_900_000,
        "total_liabilities_2024": 707_100_000,
        "net_position_change_pct": 7.9,
    },
    "KS": {
        "net_position_2025": 78_666_000,
        "net_position_2024": 74_066_000,
        "total_assets_2025": 96_859_000,
        "total_liabilities_2025": 20_134_000,
        "net_position_change_pct": 6.2,
    },
    "NM": {
        "net_position_2025": 323_285_000,
        "net_position_2024": 290_095_000,
        "total_assets_2025": 2_716_367_000,
        "total_assets_2024": 2_376_981_000,
        "total_liabilities_2025": 2_393_131_000,
        "total_liabilities_2024": 2_086_795_000,
        "net_position_change_pct": 11.4,
    },
    "OH": {
        "net_position_2025": 526_058_065,
        "net_position_2024": 438_942_146,
        "total_assets_2025": 3_946_798_760,
        "total_assets_2024": 3_040_037_194,
        "net_position_change_pct": 19.8,
    },
    "FL": {
        "net_position_2025": 4_771_085_657,
        "net_position_2024": 4_212_748_551,
        "total_assets_2025": 7_722_418_892,
        "total_assets_2024": 6_805_023_312,
        "total_liabilities_2025": 2_951_333_235,
        "total_liabilities_2024": 2_592_274_761,
        "net_position_change_pct": 13.25,
    },
    "GA": {
        "net_position_2025": 345_578_000,
        "net_position_2024": 303_769_317,
        "total_assets_2025": 4_089_816_000,
        "total_assets_2024": 3_223_377_883,
        "total_liabilities_2025": 3_744_238_000,
        "total_liabilities_2024": 2_919_608_566,
        "net_position_change_pct": 13.8,
    },
    "MD": {
        # Only the Housing Revenue Bonds fund (the report already linked for
        # MD) -- CDA also has separately-audited Revenue Obligation Funds and
        # Multi-Family Mortgage Revenue Bonds statements not included here.
        "net_position_2025": 78_170_000,
        "net_position_2024": 69_304_000,
        "net_position_change_pct": 12.79,
        "total_assets_2025": 786_372_000,
        "total_assets_2024": 625_655_000,
        "total_liabilities_2025": 708_202_000,
        "total_liabilities_2024": 556_351_000,
    },
    "TN": {
        "net_position_2025": 664_960_000,
        "net_position_2024": 634_885_000,
        "net_position_change_pct": 4.74,
        "total_assets_2025": 4_886_926_000,
        "total_assets_2024": 4_659_430_000,
        "total_liabilities_2025": 4_224_386_000,
        "total_liabilities_2024": 4_030_196_000,
    },
    "TX": {
        "net_position_2025": 1_078_974_997,
        "net_position_2024": 970_575_954,
        "total_assets_2025": 4_742_568_191,
        "total_assets_2024": 4_415_168_572,
        "total_liabilities_2025": 3_674_048_947,
        "total_liabilities_2024": 3_443_251_284,
    },
    "VA": {
        "net_position_2025": 3_963_105_718,
        "net_position_2024": 3_859_471_718,
        "net_position_change_pct": 2.7,
        "total_assets_2025": 12_350_130_739,
        "total_assets_2024": 10_909_544_382,
        "total_liabilities_2025": 8_313_327_538,
        "total_liabilities_2024": 6_984_867_188,
    },
    "WA": {
        "net_position_2025": 1_064_113_600,
        "net_position_2024": 935_580_289,
        "total_assets_2025": 2_525_718_782,
        "total_assets_2024": 2_162_353_345,
        "total_liabilities_2025": 1_456_138_353,
        "total_liabilities_2024": 1_221_592_287,
        "net_position_change_pct": 13.7,
    },
    "WI": {
        "net_position_2025": 1_134_100_000,
        "net_position_2024": 964_200_000,
        "net_position_change_pct": 17.6,
        "total_assets_2025": 4_467_400_000,
        "total_assets_2024": 4_160_100_000,
        "total_liabilities_2025": 3_316_300_000,
        "total_liabilities_2024": 3_174_000_000,
    },
    "MS": {
        "net_position_2025": 38_802_358,
        "net_position_2024": 17_545_424,
        "net_position_change_pct": 121.2,
        "total_assets_2025": 1_293_401_756,
        "total_assets_2024": 1_059_524_854,
        "total_liabilities_2025": 1_256_548_625,
        "total_liabilities_2024": 1_045_086_643,
    },
    "WV": {"net_position_2025": 640_049_000, "total_assets_2025": 1_607_042_000, "net_position_change_pct": 4.7},
    "WY": {
        "net_position_2025": 456_281_420,
        "net_position_2024": 441_265_649,
        "total_assets_2025": 1_540_498_559,
        "total_assets_2024": 1_405_305_159,
        "total_liabilities_2025": 1_070_832_241,
        "total_liabilities_2024": 948_673_149,
        "net_position_change_pct": 3.4,
    },
    "HI": {
        "net_position_2025": 2_653_188_757,
        "net_position_2024": 2_330_519_000,
        "total_assets_2025": 2_708_698_081,
        "total_assets_2024": 2_389_133_000,
        "total_liabilities_2025": 52_702_210,
        "net_position_change_pct": 13.8,
    },
    "MT": {
        "net_position_2025": 175_942_443,
        "net_position_2024": 169_439_799,
        "total_assets_2025": 886_009_021,
        "total_assets_2024": 794_690_515,
        "total_liabilities_2025": 710_209_004,
        "total_liabilities_2024": 625_413_802,
        "net_position_change_pct": 3.84,
    },
    # IFA ACFR amounts are in thousands; extractor mis-scaled them.
    "IA": {
        "net_position_2025": 1_664_618_000,
        "net_position_2024": 1_530_373_000,
        "total_assets_2025": 6_173_161_000,
        "total_assets_2024": 5_626_808_000,
        "total_liabilities_2025": 4_487_552_000,
        "total_liabilities_2024": 4_071_413_000,
        "net_position_change_pct": 8.8,
    },
    # PHFA MD&A condensed balance sheet (June 30, 2025 and 2024); source
    # figures are "Total Assets" / "Total Liabilities" lines, excluding
    # deferred outflows/inflows of resources (reported separately).
    "PA": {
        "net_position_2025": 890_304_000,
        "net_position_2024": 826_629_000,
        "total_assets_2025": 8_211_312_000,
        "total_assets_2024": 7_456_089_000,
        "total_liabilities_2025": 7_289_944_000,
        "total_liabilities_2024": 6_614_819_000,
        "net_position_change_pct": 7.7,
    },
}


def empty_hfa_year() -> dict:
    return {
        "net_position": None,
        "total_assets": None,
        "total_liabilities": None,
        "net_position_growth_pct": None,
        "families_served": None,
        "staff_count": None,
    }


def merge_field(rec: dict, field: str, val: float | None, check=None, overwrite: bool = False) -> None:
    if val is None:
        return
    if check and not check(val):
        return
    if not overwrite and rec.get(field) is not None:
        return
    rec[field] = val


def apply_manual_overrides(by_state: dict[str, dict]) -> None:
    for st, overrides in MANUAL_OVERRIDES.items():
        if st not in by_state:
            continue
        mapping = {
            "net_position_2025": ("2025", "net_position"),
            "net_position_2024": ("2024", "net_position"),
            "total_assets_2025": ("2025", "total_assets"),
            "total_assets_2024": ("2024", "total_assets"),
            "total_liabilities_2025": ("2025", "total_liabilities"),
            "total_liabilities_2024": ("2024", "total_liabilities"),
            "net_position_change_pct": ("2025", "net_position_growth_pct"),
        }
        for src, (year, field) in mapping.items():
            if src in overrides:
                merge_field(by_state[st][year], field, overrides[src], overwrite=True)


def compute_growth(by_state: dict[str, dict]) -> None:
    for rec in by_state.values():
        np24 = rec["2024"].get("net_position")
        np25 = rec["2025"].get("net_position")
        chg = rec["2025"].get("net_position_growth_pct")

        assets24 = rec["2024"].get("total_assets")
        liab24 = rec["2024"].get("total_liabilities")
        if assets24 and liab24 and rec["2024"].get("net_position") is None:
            derived_np = assets24 - liab24
            if plausible_np(derived_np):
                rec["2024"]["net_position"] = derived_np
                np24 = derived_np

        if np24 is None and np25 and chg is not None and chg != -100:
            calc = np25 / (1 + chg / 100)
            if plausible_np(calc):
                rec["2024"]["net_position"] = calc
                np24 = calc

        a24 = rec["2024"].get("total_assets")
        a25 = rec["2025"].get("total_assets")
        if a24 and a25 and a24 < a25 * 0.35:
            rec["2024"]["total_assets"] = None
        if np24 and np25 and np24 > np25 * 3:
            rec["2024"]["net_position"] = None
            np24 = None

        np24 = rec["2024"].get("net_position")
        np25 = rec["2025"].get("net_position")
        # Recompute after scale/plausibility cleanup so orphaned bad % cannot linger.
        if np24 and np25 and np24 != 0:
            rec["2025"]["net_position_growth_pct"] = ((np25 - np24) / np24) * 100
        elif np25 is None and np24 is None:
            rec["2025"]["net_position_growth_pct"] = None


def fix_scale_errors(by_state: dict[str, dict]) -> None:
    """Correct values that passed plausibility checks under the wrong unit (thousand vs million)."""
    for rec in by_state.values():
        for ykey in ("2024", "2025"):
            y = rec[ykey]
            assets = y.get("total_assets")
            liab = y.get("total_liabilities")
            np_val = y.get("net_position")

            if np_val and np_val > HFA_NET_POSITION_CEILING:
                y["net_position"] = None
                np_val = None
                if assets and assets > 10_000_000_000:
                    y["total_assets"] = None
                    assets = None
                if liab and liab > 10_000_000_000:
                    y["total_liabilities"] = None
                    liab = None

            if assets and assets > HFA_ASSETS_CEILING:
                y["total_assets"] = None
                y["total_liabilities"] = None
                assets = liab = None
                if np_val and np_val > HFA_NET_POSITION_CEILING:
                    y["net_position"] = None
                    np_val = None

            if assets and np_val and np_val < assets * 0.08 and np_val < 250_000_000:
                for mult in (1_000, 1_000_000):
                    candidate = np_val * mult
                    if plausible_np(candidate) and candidate <= assets * 1.02:
                        y["net_position"] = candidate
                        np_val = candidate
                        break

            if assets and np_val and assets < np_val * 0.3 and assets < 500_000_000:
                for mult in (1_000, 1_000_000):
                    candidate = assets * mult
                    if plausible_assets(candidate) and candidate >= np_val * 0.5:
                        y["total_assets"] = candidate
                        assets = candidate
                        break

            if assets and np_val and assets > np_val * 12 and assets > 2_000_000_000:
                for div in (1_000, 1_000_000):
                    candidate = assets / div
                    if plausible_assets(candidate) and candidate >= np_val * 0.4:
                        y["total_assets"] = candidate
                        if liab and liab > candidate:
                            scaled_liab = liab / div
                            if plausible_liabilities(scaled_liab):
                                y["total_liabilities"] = scaled_liab
                        assets = candidate
                        break

            liab = y.get("total_liabilities")
            assets = y.get("total_assets")
            if liab and assets and liab > assets * 1.5:
                for div in (1_000, 1_000_000):
                    candidate = liab / div
                    if candidate >= 1_000_000 and plausible_liabilities(candidate) and candidate <= (assets or candidate) * 1.2:
                        y["total_liabilities"] = candidate
                        break

            assets = y.get("total_assets")
            liab = y.get("total_liabilities")
            np_val = y.get("net_position")
            if assets and np_val and np_val < assets * 0.08:
                y["total_assets"] = None
                if liab and (not np_val or liab > np_val * 8):
                    y["total_liabilities"] = None

            assets = y.get("total_assets")
            liab = y.get("total_liabilities")
            if assets and liab and liab > assets * 1.2:
                y["total_liabilities"] = None


def reconcile_balance_sheet(by_state: dict[str, dict]) -> None:
    """Ensure assets ≈ liabilities + net position; fix or drop inconsistent values."""
    for rec in by_state.values():
        for ykey in ("2024", "2025"):
            y = rec[ykey]
            assets = y.get("total_assets")
            liab = y.get("total_liabilities")
            np_val = y.get("net_position")
            if assets and liab and assets < liab:
                y["total_liabilities"] = None
                liab = None
            if assets and np_val and liab:
                tol = max(assets * 0.03, 10_000_000)
                if abs(assets - liab - np_val) > tol:
                    derived_liab = assets - np_val
                    if plausible_liabilities(derived_liab):
                        y["total_liabilities"] = derived_liab
                    else:
                        derived_np = assets - liab
                        if plausible_np(derived_np):
                            y["net_position"] = derived_np
            elif assets and np_val and not liab:
                derived_liab = assets - np_val
                if plausible_liabilities(derived_liab):
                    y["total_liabilities"] = derived_liab
            elif assets and liab and not np_val:
                if assets > HFA_ASSETS_CEILING or liab > HFA_ASSETS_CEILING:
                    y["total_assets"] = None
                    y["total_liabilities"] = None
                else:
                    derived_np = assets - liab
                    if plausible_np(derived_np) and derived_np <= HFA_NET_POSITION_CEILING:
                        y["net_position"] = derived_np

            assets = y.get("total_assets")
            liab = y.get("total_liabilities")
            np_val = y.get("net_position")
            filled = sum(1 for v in (assets, liab, np_val) if v)
            if filled == 1:
                lone = assets or liab or np_val
                if lone and lone > 30_000_000_000:
                    y["total_assets"] = y["total_liabilities"] = y["net_position"] = None
                elif liab and not assets and not np_val:
                    y["total_liabilities"] = None
                elif assets and not liab and not np_val and assets > 25_000_000_000:
                    y["total_assets"] = None
            elif filled == 2:
                if assets and liab and (liab > assets * 1.2 or assets > liab * 200):
                    y["total_assets"] = None
                    y["total_liabilities"] = None
                elif np_val and liab and not assets and liab > np_val * 3:
                    y["total_liabilities"] = None
                elif np_val and liab and liab > np_val * 20:
                    y["total_liabilities"] = None
                elif np_val and assets and assets < np_val * 0.5:
                    y["total_assets"] = None


def compute_liabilities(by_state: dict[str, dict]) -> None:
    """Derive total liabilities from assets minus net position when not directly reported."""
    for rec in by_state.values():
        for ykey in ("2024", "2025"):
            y = rec[ykey]
            if y.get("total_liabilities") is not None:
                continue
            assets = y.get("total_assets")
            np_val = y.get("net_position")
            if assets is None or np_val is None or assets <= np_val:
                continue
            derived = assets - np_val
            if plausible_liabilities(derived):
                y["total_liabilities"] = derived


def plausible_staff_count(value: int | None) -> bool:
    if value is None:
        return False
    if 1990 <= value <= 2035:
        return False
    return 10 <= value <= 5_000


def load_hfa_staff_counts() -> dict[str, dict]:
    if not HFA_STAFF_COUNTS.exists():
        return {}
    raw = json.loads(HFA_STAFF_COUNTS.read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    for st, entry in raw.items():
        if st.startswith("_") or not isinstance(entry, dict):
            continue
        count = entry.get("staff_count")
        if not plausible_staff_count(count):
            continue
        out[st] = {
            "staff_count": int(count),
            "source": entry.get("source", "Reference"),
            "source_url": entry.get("source_url"),
        }
    return out


def apply_hfa_staff_counts(by_state: dict[str, dict], staff_ref: dict[str, dict]) -> None:
    """Fill staff_count only where ACFR (or other) did not already provide a value."""
    for st, meta in staff_ref.items():
        rec = by_state.get(st)
        if not rec:
            continue
        filled_any = False
        for ykey in ("2024", "2025"):
            if rec[ykey].get("staff_count") is not None:
                continue
            rec[ykey]["staff_count"] = meta["staff_count"]
            rec[ykey]["staff_count_source"] = meta.get("source")
            rec[ykey]["staff_count_source_url"] = meta.get("source_url")
            filled_any = True
        if filled_any and not rec.get("staff_count_source"):
            rec["staff_count_source"] = meta.get("source")
            rec["staff_count_source_url"] = meta.get("source_url")


def _years_in_block(block: str) -> list[int] | None:
    headers = re.findall(r"20\d{2}(?:\s+20\d{2}){2,9}", normalize_financial_text(block))
    if not headers:
        return None
    years = [int(y) for y in headers[-1].split()]
    return years if len(years) >= 3 else None


def _staff_for_fy(numbers: list[float], years: list[int] | None, fy: int) -> int | None:
    if years and fy in years:
        idx = years.index(fy)
        if idx < len(numbers):
            val = int(round(numbers[idx]))
            return val if plausible_staff_count(val) else None
    if numbers:
        # Ten-year statistical tables usually list the report year in the last column.
        val = int(round(numbers[-1]))
        if plausible_staff_count(val):
            return val
        val = int(round(numbers[0]))
        return val if plausible_staff_count(val) else None
    return None


def _set_acfr_staff(out: dict[str, dict], fy: int, count: int | None) -> None:
    if count is None or not plausible_staff_count(count):
        return
    key = str(fy)
    out[key] = {
        "staff_count": count,
        "staff_count_source": f"ACFR FY{fy}",
        "staff_count_source_url": None,
    }


def _parse_table_numbers(raw: str) -> list[float]:
    out: list[float] = []
    for x in re.findall(r"\d[\d,]*(?:\.\d+)?", raw.replace(",", "")):
        if x.count(".") > 1:
            continue
        try:
            val = float(x)
        except ValueError:
            continue
        if 0 < val < 10_000:
            out.append(val)
    return out


def extract_staff_from_acfr(text: str, report_fy: int) -> dict[str, dict]:
    """Extract this HFA unit's own FTE/employee headcount from its ACFR text."""
    t = normalize_financial_text(text)
    raw_text = text.replace("\u00a0", " ")
    found: dict[str, dict] = {}

    for m in re.finditer(
        r"(?:The\s+)?(?:Authority|Agency|Corporation|Commission|Fund|Department) had (\d[\d,]*) active employees as of June 30,\s*(\d{4})",
        t,
        re.I,
    ):
        n = int(m.group(1).replace(",", ""))
        fy = int(m.group(2))
        if fy in (2024, 2025):
            _set_acfr_staff(found, fy, n)

    for m in re.finditer(
        r"(\d[\d,]*)\s+(?:permanent |full[- ]time )?employees as of June 30,\s*(\d{4})",
        t,
        re.I,
    ):
        n = int(m.group(1).replace(",", ""))
        fy = int(m.group(2))
        if fy in (2024, 2025):
            _set_acfr_staff(found, fy, n)

    for pat in (
        r"currently employs (\d[\d,]*) employees",
        r"authorized (\d[\d,]*) full[- ]time equivalent employees",
        r"employs (?:approximately )?(\d[\d,]*) full[- ]time employees",
    ):
        m = re.search(pat, t, re.I)
        if m:
            n = int(m.group(1).replace(",", ""))
            _set_acfr_staff(found, report_fy, n)
            break

    m = re.search(
        r"active participant count \(employees only\)[^.]{0,80}?(\d[\d,]*)",
        t,
        re.I,
    )
    if m:
        n = int(m.group(1).replace(",", ""))
        _set_acfr_staff(found, report_fy, n)

    table_specs = [
        (
            r"IHDA FULL[- ]TIME EQUIVALENT EMPLOYEES BY FUNCTION.*?Total entity full[- ]time equivalent\s+([^\n\r]+)",
            "ihda_fte",
            10,
        ),
        (
            r"Number of Full Time Equivelent Employees by Function.*?Total Iowa Finance Authority\s+([^\n\r]+)",
            "ifa_fte",
            10,
        ),
        (
            r"Number of CalHFA Employees \(continued\).*?Total\s+((?:\d+\s+){3,8}\d+)\s+Source:\s*CalHFA",
            "calhfa_employees",
            5,
        ),
        (
            r"FOR THE YEARS ENDED JUNE 30.*?Number of employees by department / function:.*?Total number of employees\s+([^\n\r]+)",
            "wvhdf_employees",
            10,
        ),
    ]
    for pat, _label, max_cols in table_specs:
        m = re.search(pat, raw_text, re.I | re.S)
        if not m:
            continue
        numbers = _parse_table_numbers(m.group(1))[:max_cols]
        if not numbers:
            continue
        years = _years_in_block(m.group(0))
        if years and len(numbers) > len(years):
            numbers = numbers[: len(years)]
        for fy in (2024, 2025):
            count = _staff_for_fy(numbers, years, fy)
            if count is not None:
                _set_acfr_staff(found, fy, count)
        if years is None:
            _set_acfr_staff(found, report_fy, _staff_for_fy(numbers, None, report_fy))
        break

    return found


def merge_acfr_staff(by_state: dict[str, dict], st: str, staff: dict[str, dict]) -> None:
    if not staff:
        return
    rec = by_state[st]
    for ykey, meta in staff.items():
        if ykey not in rec:
            continue
        rec[ykey]["staff_count"] = meta["staff_count"]
        rec[ykey]["staff_count_source"] = meta["staff_count_source"]
        if meta.get("staff_count_source_url"):
            rec[ykey]["staff_count_source_url"] = meta["staff_count_source_url"]
    if staff.get("2025") or staff.get("2024"):
        src = staff.get("2025") or staff.get("2024")
        rec["staff_count_source"] = src["staff_count_source"]
        rec["staff_count_from_acfr"] = True


def extract_from_text(text: str, year: int) -> dict:
    t = normalize_financial_text(text)
    out = {"families_served": None, "staff_count": None}

    # Avoid matching dollar columns next to "Families First … Act" (seen in state ACFRs).
    best_family = 0
    for pat in [
        r"(?<!\$)\b(\d[\d,]{2,})\s+(families|households)\b(?!\s+First\b)",
        r"\bserved\s+(\d[\d,]{2,})\s+(?:families|households|people|individuals)\b",
    ]:
        for m in re.finditer(pat, t, re.I):
            raw = m.group(1)
            # Skip matches that sit in a money column: "... $ 6,603,370 Families First"
            start = m.start(1)
            window = t[max(0, start - 40) : start]
            if "$" in window or "Families First" in t[m.start() : m.start() + 40]:
                continue
            n = int(raw.replace(",", ""))
            # Plausible HFA program volumes; multi-million "families" is almost always $ amounts.
            if 100 < n < 2_000_000 and n > best_family:
                best_family = n
    if best_family:
        out["families_served"] = best_family

    return out


def load_population() -> dict[str, dict[str, int | None]]:
    result = {s: {"2024": None, "2025": None} for s in STATE_NAMES}
    for url in (
        "https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/state/totals/NST-EST2024-ALLDATA.csv",
        "https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/state/totals/NST-EST2025-ALLDATA.csv",
    ):
        try:
            text = fetch_url(url).decode("utf-8")
            for row in csv.DictReader(io.StringIO(text)):
                if row.get("SUMLEV") != "040":
                    continue
                st = FIPS_TO_STATE.get(row["STATE"].zfill(2))
                if not st:
                    continue
                if row.get("POPESTIMATE2024"):
                    result[st]["2024"] = int(row["POPESTIMATE2024"])
                if row.get("POPESTIMATE2025"):
                    result[st]["2025"] = int(row["POPESTIMATE2025"])
        except Exception as exc:
            print(f"WARN population: {exc}", file=sys.stderr)
    return result


def load_personal_income() -> dict[str, dict[str, float | None]]:
    result = {s: {"2023": None, "2024": None, "pc2023": None, "pc2024": None} for s in STATE_NAMES}
    try:
        zdata = fetch_url("https://apps.bea.gov/regional/zip/SAINC.zip")
        with zipfile.ZipFile(io.BytesIO(zdata)) as zf:
            text = zf.read("SAINC4__ALL_AREAS_1929_2025.csv").decode("latin-1")
        rows = list(csv.reader(io.StringIO(text)))
        header = rows[0]
        idx = {y: header.index(y) for y in ("2023", "2024") if y in header}
        for row in rows[1:]:
            fips = row[0].strip(' "')
            if len(fips) != 5:
                continue
            st = FIPS_TO_STATE.get(fips[:2])
            if not st:
                continue
            line = row[4]
            if line == "10":
                for y in ("2023", "2024"):
                    val = parse_money(row[idx[y]])
                    if val is not None:
                        result[st][y] = val * 1_000_000
            elif line == "30":
                for y in ("2023", "2024"):
                    val = parse_money(row[idx[y]])
                    if val is not None:
                        result[st][f"pc{y}"] = val
    except Exception as exc:
        print(f"WARN personal income: {exc}", file=sys.stderr)
    return result


def load_unemployment() -> dict[str, dict[str, float | None]]:
    result = {s: {"2023": None, "2024": None} for s in STATE_NAMES}
    fallback = BASE / "docs" / "acs_fallback.json"
    if fallback.exists():
        data = json.loads(fallback.read_text(encoding="utf-8"))
        for st, vals in data.items():
            if st in result:
                result[st]["2023"] = vals.get("unemployment_2023")
                result[st]["2024"] = vals.get("unemployment_2024")
    return result


def load_acs_quickfacts() -> dict[str, dict]:
    """ACS 2023 1-year estimates: poverty rate & median home value from Census subject tables."""
    result = {
        s: {
            "poverty_2023": None, "poverty_2024": None,
            "median_home_2023": None, "median_home_2024": None,
        }
        for s in STATE_NAMES
    }
    fallback = BASE / "docs" / "acs_fallback.json"
    if fallback.exists():
        data = json.loads(fallback.read_text(encoding="utf-8"))
        for st, vals in data.items():
            if st in result:
                result[st].update(vals)
    return result


def load_homeless_pit() -> dict[str, dict[str, int | None]]:
    """HUD AHAR Point-in-Time overall homeless counts by state (January PIT)."""
    result = {s: {"2024": None, "2025": None} for s in STATE_NAMES}
    fallback = BASE / "web-map" / "homeless_pit_fallback.json"
    if fallback.exists():
        data = json.loads(fallback.read_text(encoding="utf-8"))
        for st, vals in data.items():
            if st not in result:
                continue
            result[st]["2024"] = vals.get("homeless_2024")
            result[st]["2025"] = vals.get("homeless_2025")
    return result


def build_hfa_metrics() -> dict[str, dict]:
    fy25 = json.loads(FY2025_METRICS.read_text(encoding="utf-8"))
    catalog = {c["state"]: c for c in json.loads(CATALOG.read_text(encoding="utf-8"))}
    by_state: dict[str, dict] = {}

    for entry in fy25:
        st = entry["state"]
        by_state[st] = {
            "hfa_name": entry["name"],
            "hfa_abbr": entry["abbr"],
            "status": entry["status"],
            "2024": empty_hfa_year(),
            "2025": empty_hfa_year(),
        }
        merge_field(by_state[st]["2024"], "net_position", entry.get("net_position_2024"), plausible_np)
        merge_field(by_state[st]["2024"], "total_assets", entry.get("total_assets_2024"), plausible_assets)
        merge_field(by_state[st]["2024"], "total_liabilities", entry.get("total_liabilities_2024"), plausible_liabilities)
        merge_field(by_state[st]["2025"], "net_position", entry.get("net_position_2025"), plausible_np)
        merge_field(by_state[st]["2025"], "total_assets", entry.get("total_assets_2025"), plausible_assets)
        merge_field(by_state[st]["2025"], "total_liabilities", entry.get("total_liabilities_2025"), plausible_liabilities)
        if entry.get("net_position_change_pct") is not None:
            by_state[st]["2025"]["net_position_growth_pct"] = entry["net_position_change_pct"]

    for st in STATE_NAMES:
        if st not in by_state:
            c = catalog.get(st, {})
            by_state[st] = {
                "hfa_name": c.get("name", "N/A"),
                "hfa_abbr": c.get("abbr", ""),
                "status": "missing",
                "2024": empty_hfa_year(),
                "2025": empty_hfa_year(),
            }

    # Extract from FY2025 ACFR texts (includes 2024 comparatives)
    for st in STATE_NAMES:
        hfa_name = by_state[st].get("hfa_name")
        txt_path = find_txt_for_state(st, 2025, hfa_name)
        if not txt_path:
            continue
        try:
            text = txt_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if is_state_consolidated_report(text, st):
            entity = COMPONENT_UNIT_HFA.get(st)
            pair = extract_component_unit_hfa(text, 2025, entity) if entity else {}
        else:
            pair = extract_hfa_pair(text, 2025)
            mda = extract_hfa_mda_millions(text, 2025)
            for ykey in ("2024", "2025"):
                for field in ("net_position", "total_assets", "total_liabilities"):
                    merge_field(
                        pair.setdefault(ykey, {}),
                        field,
                        mda.get(ykey, {}).get(field),
                    )
        merge_pair_into_state(by_state, st, pair)
        ex = extract_from_text(text, 2025)
        if ex.get("families_served") is not None and by_state[st]["2025"].get("families_served") is None:
            by_state[st]["2025"]["families_served"] = ex["families_served"]
        merge_acfr_staff(by_state, st, extract_staff_from_acfr(text, 2025))

    # Supplement FY2024-only ACFR texts for fiscal 2024 figures
    for st in STATE_NAMES:
        hfa_name = by_state[st].get("hfa_name")
        txt_path = find_txt_for_state(st, 2024, hfa_name)
        if not txt_path:
            continue
        try:
            text = txt_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if is_state_consolidated_report(text, st):
            continue
        pair = extract_hfa_pair(text, 2024)
        mda = extract_hfa_mda_millions(text, 2024)
        for field in ("net_position", "total_assets", "total_liabilities"):
            merge_field(pair.setdefault("2024", {}), field, mda.get("2024", {}).get(field))
        merge_pair_into_state(by_state, st, pair, years=("2024",))
        ex = extract_from_text(text, 2024)
        if ex.get("families_served") is not None and by_state[st]["2024"].get("families_served") is None:
            by_state[st]["2024"]["families_served"] = ex["families_served"]
        staff_2024 = extract_staff_from_acfr(text, 2024)
        for ykey in ("2024", "2025"):
            if ykey in staff_2024 and by_state[st][ykey].get("staff_count") is None:
                meta = staff_2024[ykey]
                by_state[st][ykey]["staff_count"] = meta["staff_count"]
                by_state[st][ykey]["staff_count_source"] = meta["staff_count_source"]
        if staff_2024.get("2024") and not by_state[st].get("staff_count_from_acfr"):
            by_state[st]["staff_count_source"] = staff_2024["2024"]["staff_count_source"]
            by_state[st]["staff_count_from_acfr"] = True

    if FY2024_METRICS.exists():
        for entry in json.loads(FY2024_METRICS.read_text(encoding="utf-8")):
            st = entry.get("state")
            if not st or st not in by_state or entry.get("status") != "downloaded":
                continue
            y2024 = by_state[st]["2024"]
            merge_field(y2024, "net_position", entry.get("net_position"), plausible_np)
            merge_field(y2024, "total_assets", entry.get("total_assets"), plausible_assets)
            liab = entry.get("total_liabilities")
            if liab is None and y2024.get("total_assets") and y2024.get("net_position"):
                liab = y2024["total_assets"] - y2024["net_position"]
            merge_field(y2024, "total_liabilities", liab, plausible_liabilities)

    apply_manual_overrides(by_state)
    apply_hfa_staff_counts(by_state, load_hfa_staff_counts())
    compute_liabilities(by_state)
    fix_scale_errors(by_state)
    reconcile_balance_sheet(by_state)
    # Growth last: uses cleaned net position figures only.
    compute_growth(by_state)
    apply_manual_overrides(by_state)  # restore ACFR-stated growth % when provided
    return by_state


def main() -> None:
    print("Building map dataset...")
    hfa = build_hfa_metrics()
    pop = load_population()
    income = load_personal_income()
    unemp = load_unemployment()
    acs = load_acs_quickfacts()
    homeless = load_homeless_pit()

    states_out = []
    for st, names in STATE_NAMES.items():
        h = hfa.get(st, {})
        p = pop.get(st, {})
        inc = income.get(st, {})
        u = unemp.get(st, {})
        a = acs.get(st, {})
        hm = homeless.get(st, {})

        def year_block(
            fy: str,
            pop_key: str,
            inc_key: str,
            unemp_key: str,
            poverty_key: str,
            median_key: str,
            homeless_key: str,
        ):
            hfa_y = h.get(fy, {})
            pop_val = p.get(pop_key)
            inc_total = inc.get(inc_key)
            inc_pc = inc.get(f"pc{inc_key}")
            if inc_total is None and inc_pc and pop_val:
                inc_total = inc_pc * pop_val
            if inc_pc is None and inc_total and pop_val:
                inc_pc = inc_total / pop_val
            return {
                "net_position": hfa_y.get("net_position"),
                "net_position_growth_pct": hfa_y.get("net_position_growth_pct"),
                "total_assets": hfa_y.get("total_assets"),
                "total_liabilities": hfa_y.get("total_liabilities"),
                "families_served": hfa_y.get("families_served"),
                "staff_count": hfa_y.get("staff_count"),
                "staff_count_source": hfa_y.get("staff_count_source"),
                "population": pop_val,
                "personal_income_total": inc_total,
                "personal_income_per_capita": inc_pc,
                "unemployment_rate": u.get(unemp_key),
                "poverty_rate": a.get(poverty_key),
                "median_home_price": a.get(median_key),
                "homeless_count": hm.get(homeless_key),
            }

        states_out.append({
            "state": st,
            "name_en": names["en"],
            "name_zh": names["zh"],
            "hfa_name": h.get("hfa_name"),
            "hfa_abbr": h.get("hfa_abbr"),
            "hfa_status": h.get("status"),
            "staff_count_source": (
                h.get("2025", {}).get("staff_count_source")
                or h.get("2024", {}).get("staff_count_source")
                or h.get("staff_count_source")
            ),
            "staff_count_source_url": h.get("staff_count_source_url"),
            "2024": year_block("2024", "2024", "2024", "2024", "poverty_2023", "median_home_2023", "2024"),
            "2025": year_block("2025", "2025", "2024", "2024", "poverty_2024", "median_home_2024", "2025"),
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources": {
            "hfa_financials": "FY2024/FY2025 State Housing Finance Authority ACFR reports",
            "hfa_staff_acfr": "HFA ACFR full-time employee/FTE disclosures when reported",
            "hfa_staff_linkedin": "LinkedIn company pages (HFA staff counts when not in ACFR)",
            "hfa_staff_other": "Agency websites and state budget sources (hfa_staff_counts.json)",
            "population": "U.S. Census Bureau Population Estimates Program (Vintage 2024/2025)",
            "personal_income": "U.S. Bureau of Economic Analysis SAINC4 (State Personal Income)",
            "unemployment": "U.S. Bureau of Labor Statistics LAUS (2023-2024 annual averages)",
            "poverty_median_home": "U.S. Census Bureau ACS 1-year estimates",
            "homeless_count": "HUD AHAR Point-in-Time Estimates by State (January 2025)",
        },
        "states": states_out,
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    filled_np24 = sum(1 for s in states_out if s["2024"]["net_position"])
    filled_a24 = sum(1 for s in states_out if s["2024"]["total_assets"])
    filled_np25 = sum(1 for s in states_out if s["2025"]["net_position"])
    filled_liab24 = sum(1 for s in states_out if s["2024"]["total_liabilities"])
    filled_u = sum(1 for s in states_out if s["2025"]["unemployment_rate"])
    filled_staff = sum(1 for s in states_out if s["2025"]["staff_count"])
    filled_hm = sum(1 for s in states_out if s["2025"]["homeless_count"])
    print(
        f"Wrote {OUT} | 2024 net_position: {filled_np24}/52 | 2024 total_assets: {filled_a24}/52"
        f" | 2024 total_liabilities: {filled_liab24}/52"
        f" | 2025 net_position: {filled_np25}/52 | unemployment: {filled_u}/52"
        f" | staff_count: {filled_staff}/52 | homeless_count: {filled_hm}/52"
    )


if __name__ == "__main__":
    main()
