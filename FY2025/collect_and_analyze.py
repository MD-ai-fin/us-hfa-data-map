#!/usr/bin/env python3
"""Collect FY2025 state housing authority ACFRs and generate comparative Word summary."""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

import pdfplumber
import requests
from bs4 import BeautifulSoup
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor

BASE_DIR = Path(__file__).resolve().parent
CATALOG_PATH = BASE_DIR / "state_hfa_catalog.json"
PDF_DIR = BASE_DIR / "pdf"
TXT_DIR = BASE_DIR / "txt"
DATA_PATH = BASE_DIR / "fy2025_metrics.json"
LOG_PATH = BASE_DIR / "download_log.json"
REPORT_PATH = BASE_DIR / "FY2025_US_State_HFA_ACFR_Analysis_Report.docx"
REPORT_PATH_CN = BASE_DIR / "FY2025_美国州级住房金融机构ACFR综合分析报告.docx"
DIRECT_URLS_PATH = BASE_DIR / "direct_urls.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
}

MANUAL_OVERRIDES: dict[str, dict] = {
    "CA": {
        "net_position_2025": 3_442_918_000,
        "net_position_2024": 3_220_848_000,
        "net_position_change": 222_070_000,
        "net_position_change_pct": 6.9,
        "total_assets_2025": 4_980_031_000,
        "total_assets_2024": 4_558_601_000,
        "total_liabilities_2025": 1_511_418_000,
    },
    "AL": {"net_position_2025": 516_018_000, "total_assets_2025": 1_364_901_000},
    "DE": {"net_position_2025": 732_459_779, "net_position_change_pct": 3.8},
    "ID": {"net_position_2025": 716_007_000, "total_assets_2025": 6_026_206_000, "net_position_change_pct": 8.5},
    "IL": {
        "net_position_2025": 1_533_700_000,
        "net_position_change": 159_900_000,
        "net_position_change_pct": 11.6,
        "total_assets_2025": 7_846_500_000,
    },
    "IN": {"net_position_2025": 599_528_335, "total_assets_2025": 3_247_001_038, "net_position_change_pct": 20.4},
    "LA": {"net_position_2025": 821_730_000, "total_assets_2025": 1_545_038_000, "net_position_change_pct": 31.9},
    "MA": {"net_position_2025": 1_354_204_000, "total_assets_2025": 8_079_680_000},
    "MI": {"net_position_2025": 1_292_050_000, "total_assets_2025": 8_027_764_000, "net_position_change_pct": 11.3},
    "MN": {"net_position_2025": 1_649_443_000, "total_assets_2025": 8_543_311_000},
    "MO": {"net_position_2025": 708_007_000},
    "CO": {"total_assets_2025": 8_385_309_000},
    "NC": {"net_position_2025": 979_793_000, "total_assets_2025": 4_815_950_000},
    "ND": {"net_position_2025": 454_474_000, "total_assets_2025": 2_910_591_000},
    "NE": {"net_position_2025": 454_474_000, "total_assets_2025": 2_910_591_000},
    "OH": {"net_position_2025": 526_058_065, "total_assets_2025": 3_946_798_760, "net_position_change_pct": 19.8},
    "TN": {"net_position_2025": 665_000_000, "net_position_change_pct": 4.74},
    "TX": {"net_position_2025": 108_400_000},
    "VA": {"net_position_2025": 3_900_000_000, "total_assets_2025": 12_350_100_000},
    "WA": {"net_position_2025": 1_064_100_000, "total_assets_2025": 2_525_700_000, "net_position_change_pct": 13.7},
    "WI": {
        "net_position_2025": 1_134_100_000,
        "net_position_change_pct": 17.6,
        "total_assets_2025": 4_467_400_000,
    },
    "WV": {"net_position_2025": 640_049_000, "total_assets_2025": 1_607_042_000, "net_position_change_pct": 4.7},
    "WY": {"net_position_2025": 214_811_569, "total_assets_2025": 1_540_498_559},
}

EXCLUDE_FROM_RANKINGS = {"KS", "PA", "IA"}

FY2025_PATTERNS = [
    r"fy\s*2025",
    r"fiscal\s+year\s+2025",
    r"year\s+ended\s+june\s+30,\s*2025",
    r"june\s+30,\s*2025",
    r"6/30/25",
    r"06/30/2025",
    r"2024/2025",
    r"2025\s+acfr",
    r"fy25",
    r"fy-?2025",
]

PDF_HINTS = [
    "acfr",
    "annual comprehensive",
    "financial statement",
    "audited",
    "annual report",
    "annual financial",
]


@dataclass
class AgencyMetrics:
    state: str
    name: str
    abbr: str
    source_file: str = ""
    source_url: str = ""
    status: str = "missing"
    net_position_2025: Optional[float] = None
    net_position_2024: Optional[float] = None
    net_position_change: Optional[float] = None
    net_position_change_pct: Optional[float] = None
    total_assets_2025: Optional[float] = None
    total_assets_2024: Optional[float] = None
    total_liabilities_2025: Optional[float] = None
    total_liabilities_2024: Optional[float] = None
    revenues_2025: Optional[float] = None
    expenses_2025: Optional[float] = None
    net_position_ratio: Optional[float] = None
    notes: list[str] = field(default_factory=list)


def ensure_dirs() -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    TXT_DIR.mkdir(parents=True, exist_ok=True)


def load_catalog() -> list[dict]:
    with CATALOG_PATH.open(encoding="utf-8") as f:
        catalog = json.load(f)
    if DIRECT_URLS_PATH.exists():
        direct = json.loads(DIRECT_URLS_PATH.read_text(encoding="utf-8"))
        by_state = {item["state"]: item for item in catalog}
        for entry in direct:
            state = entry["state"]
            if state in by_state:
                urls = by_state[state].setdefault("direct_pdfs", [])
                if entry["url"] not in urls:
                    urls.insert(0, entry["url"])
    return catalog


def normalize_url(base: str, href: str) -> str:
    return urllib.parse.urljoin(base, href)


def looks_like_fy2025(text: str) -> bool:
    t = text.lower()
    return any(re.search(p, t) for p in FY2025_PATTERNS)


def looks_like_financial_pdf(text: str) -> bool:
    t = text.lower()
    return any(h in t for h in PDF_HINTS)


def parse_money(raw: str) -> Optional[float]:
    if not raw:
        return None
    s = raw.strip().replace("$", "").replace(",", "").replace(" ", "")
    if s in {"", "-", "—", "N/A", "n/a"}:
        return None
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]
    try:
        return float(s)
    except ValueError:
        return None


def extract_text_from_pdf(pdf_path: Path) -> str:
    chunks: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            chunks.append(text)
    return "\n".join(chunks)


def first_match(patterns: list[str], text: str, flags=re.I | re.S) -> Optional[re.Match]:
    for pat in patterns:
        m = re.search(pat, text, flags)
        if m:
            return m
    return None


def normalize_financial_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"(\d)\s+(?=\d)", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return text


def to_dollars(value: Optional[float], unit: str) -> Optional[float]:
    if value is None:
        return None
    unit = unit.lower()
    if unit == "thousand":
        return value * 1_000
    if unit == "million":
        return value * 1_000_000
    if unit == "billion":
        return value * 1_000_000_000
    return value


def plausible_np(value: Optional[float]) -> bool:
    return value is not None and 1_000_000 <= value <= 25_000_000_000


def plausible_assets(value: Optional[float]) -> bool:
    return value is not None and 10_000_000 <= value <= 100_000_000_000


def detect_unit_scale(text: str) -> str:
    head = text[:12000].lower()
    if "in thousands of dollars" in head or "(in thousands)" in head:
        return "thousand"
    if "millions of dollars" in head or "in millions" in head:
        return "million"
    return "raw"


def extract_metrics(text: str, agency: dict) -> AgencyMetrics:
    m = AgencyMetrics(state=agency["state"], name=agency["name"], abbr=agency["abbr"])
    t = normalize_financial_text(text)
    scale = detect_unit_scale(text)

    hl_patterns = [
        (
            r"overall net position increased by \$(?P<chg>[\d,\.]+) million, to \$(?P<np>[\d,\.]+) million",
            "million",
            "million",
        ),
        (
            r"Total net position as of June 30, 2025, was \$(?P<np>[\d,\.]+) million, an increase of \$(?P<chg>[\d,\.]+) million or (?P<pct>[\d,\.]+)%",
            "million",
            "million",
        ),
        (
            r"net position increased \$(?P<chg>[\d,\.]+) million to \$(?P<np>[\d,\.]+) million",
            "million",
            "million",
        ),
        (
            r"Net position increased \$(?P<chg>[\d,\.]+) million from .*? to \$(?P<np>[\d,\.]+) million",
            "million",
            "million",
        ),
        (
            r"net position totaled \$(?P<np>[\d,\.]+) billion at June 30, 2025",
            "billion",
            None,
        ),
        (
            r"Total Net Position improved by \$(?P<chg>[\d,\.]+).*?to \$(?P<np>[\d,\.]+).*?June 30,\s*2025",
            "raw",
            "raw",
        ),
        (
            r"change in net position of \$(?P<chg>[\d,\.]+) million for the fiscal year ended June 30, 2025",
            None,
            "million",
        ),
        (
            r"Net Position \$ (?P<np>[\d,\.]+)",
            "thousand",
            None,
        ),
    ]
    for pattern, np_unit, chg_unit in hl_patterns:
        hit = re.search(pattern, t, re.I)
        if not hit:
            continue
        if hit.groupdict().get("np") and not m.net_position_2025:
            np_val = to_dollars(parse_money(hit.group("np")), np_unit or scale)
            if plausible_np(np_val):
                m.net_position_2025 = np_val
        if hit.groupdict().get("chg") and not m.net_position_change:
            chg_val = to_dollars(parse_money(hit.group("chg")), chg_unit or scale)
            if chg_val is not None:
                m.net_position_change = chg_val
        if hit.groupdict().get("pct") and not m.net_position_change_pct:
            m.net_position_change_pct = parse_money(hit.group("pct"))

    table_patterns = [
        r"Total assets (?P<a25>[\d,\.]+) (?P<a24>[\d,\.]+).*?(?P<pct1>[\d,\.]+)%",
        r"Total net position (?P<np25>[\d,\.]+) (?P<np24>[\d,\.]+).*?(?P<pct2>[\d,\.]+)%",
    ]
    if scale == "thousand":
        for pat in table_patterns:
            hit = re.search(pat, t, re.I)
            if not hit:
                continue
            gd = hit.groupdict()
            if gd.get("np25") and not m.net_position_2025:
                np25 = to_dollars(parse_money(gd["np25"]), "thousand")
                if plausible_np(np25):
                    m.net_position_2025 = np25
            if gd.get("np24") and not m.net_position_2024:
                np24 = to_dollars(parse_money(gd["np24"]), "thousand")
                if plausible_np(np24):
                    m.net_position_2024 = np24
            if gd.get("a25") and not m.total_assets_2025:
                a25 = to_dollars(parse_money(gd["a25"]), "thousand")
                if plausible_assets(a25):
                    m.total_assets_2025 = a25
            if gd.get("a24") and not m.total_assets_2024:
                a24 = to_dollars(parse_money(gd["a24"]), "thousand")
                if plausible_assets(a24):
                    m.total_assets_2024 = a24
            if gd.get("pct2") and not m.net_position_change_pct:
                m.net_position_change_pct = parse_money(gd["pct2"])

    if m.net_position_2025 and m.net_position_2024 and not m.net_position_change:
        m.net_position_change = m.net_position_2025 - m.net_position_2024
    if m.net_position_change and m.net_position_2024 and m.net_position_2024 != 0 and not m.net_position_change_pct:
        m.net_position_change_pct = (m.net_position_change / m.net_position_2024) * 100
    if m.net_position_2025 and m.total_assets_2025 and m.total_assets_2025 > 0:
        m.net_position_ratio = (m.net_position_2025 / m.total_assets_2025) * 100

    if not any([m.net_position_2025, m.total_assets_2025]):
        m.notes.append("未能自动提取核心指标，需人工复核PDF")

    overrides = MANUAL_OVERRIDES.get(agency["state"], {})
    for key, val in overrides.items():
        setattr(m, key, val)
    if agency["state"] in EXCLUDE_FROM_RANKINGS:
        m.notes.append("文件为州级ACFR/合并报表，未纳入HFA专项排名")
        m.net_position_2025 = overrides.get("net_position_2025")
        m.total_assets_2025 = overrides.get("total_assets_2025")
        m.net_position_change_pct = overrides.get("net_position_change_pct")
    if m.net_position_2025 and m.total_assets_2025 and m.total_assets_2025 > 0:
        m.net_position_ratio = (m.net_position_2025 / m.total_assets_2025) * 100
    return m


def discover_pdf_links(page_url: str) -> list[str]:
    try:
        resp = requests.get(page_url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    links: list[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not href.lower().endswith(".pdf"):
            continue
        label = (a.get_text(" ", strip=True) + " " + href).strip()
        if looks_like_financial_pdf(label) and looks_like_fy2025(label):
            links.append(normalize_url(page_url, href))
    return links


def download_pdf(url: str, dest: Path, retries: int = 3) -> bool:
    last_error = None
    for attempt in range(retries):
        for verify in (True, False):
            try:
                resp = requests.get(
                    url,
                    headers=HEADERS,
                    timeout=90,
                    allow_redirects=True,
                    verify=verify,
                )
                resp.raise_for_status()
                content = resp.content
                if content.startswith(b"%PDF") and len(content) >= 5000:
                    dest.write_bytes(content)
                    return True
            except Exception as exc:
                last_error = exc
        time.sleep(0.8)
    return False


def collect_agency(agency: dict, log: dict) -> Optional[Path]:
    state = agency["state"]
    abbr = agency["abbr"]
    candidates: list[str] = list(agency.get("direct_pdfs", []))

    for page in agency.get("urls", []):
        candidates.extend(discover_pdf_links(page))
        time.sleep(0.4)

    # dedupe preserve order
    seen = set()
    unique_candidates = []
    for u in candidates:
        if u not in seen:
            seen.add(u)
            unique_candidates.append(u)

    log[state] = {"candidates": unique_candidates, "downloaded": None, "errors": []}

    for url in unique_candidates:
        filename = f"{state}_{abbr}_FY2025_ACFR.pdf"
        dest = PDF_DIR / filename
        if dest.exists() and dest.stat().st_size > 5000:
            log[state]["downloaded"] = str(dest)
            return dest
        ok = download_pdf(url, dest)
        if ok and dest.stat().st_size > 5000:
            log[state]["downloaded"] = str(dest)
            log[state]["source_url"] = url
            return dest
        if dest.exists():
            dest.unlink(missing_ok=True)
        log[state]["errors"].append(f"failed: {url}")
        time.sleep(0.3)

    return None


def fmt_money(val: Optional[float], unit: str = "auto") -> str:
    if val is None:
        return "N/A"
    if unit == "auto":
        if abs(val) >= 1_000_000:
            return f"${val/1_000_000:,.1f}M"
        if abs(val) >= 1_000:
            return f"${val/1_000:,.1f}K"
        return f"${val:,.0f}"
    if unit == "M":
        return f"${val/1_000_000:,.1f}M"
    if unit == "B":
        return f"${val/1_000_000_000:,.2f}B"
    return f"${val:,.0f}"


def fmt_pct(val: Optional[float]) -> str:
    if val is None:
        return "N/A"
    return f"{val:+.1f}%"


def add_title(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(20)
    run.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)


def add_heading(doc: Document, text: str, level: int = 1) -> None:
    doc.add_heading(text, level=level)


def add_table(doc: Document, headers: list[str], rows: list[list[str]]) -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Light Grid Accent 1"
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = val


def _report_copy(language: str) -> dict:
    downloaded_label = "Downloaded" if language == "en" else "已获取"
    missing_label = "Not available" if language == "en" else "未获取"
    date_fmt = "%B %d, %Y" if language == "en" else "%Y年%m月%d日"

    if language == "en":
        return {
            "date_fmt": date_fmt,
            "downloaded_label": downloaded_label,
            "missing_label": missing_label,
            "title": "FY2025 U.S. State Housing Finance Agencies\nACFR & Financial Statements: Panoramic Analysis & Strategic Insights",
            "subtitle": (
                "Prepared: {date}  |  Coverage: {total} states/territories  |  "
                "Reports obtained: {downloaded} FY2025 filings"
            ),
            "s1": "I. Executive Summary: A Balance-Sheet Moment for Housing Finance",
            "s1_body": (
                "FY2025 (year ended June 30, 2025; some agencies use a calendar year) was a pivotal "
                "financial year for State Housing Finance Agencies (HFAs) amid falling interest rates, "
                "intensifying LIHTC competition, and expanding first-time homebuyer programs. "
                "This report systematically collects and compares publicly disclosed ACFRs and audited "
                "financial statements across all 51 states and territories. As of the collection date, "
                "{downloaded} FY2025 reports were obtained ({coverage:.0f}% coverage)."
            ),
            "key_findings": (
                "Key finding: Among {count} agencies with extracted data, aggregate net position totals "
                "approximately {np}, and aggregate total assets approximately {assets}. "
                "State HFAs operate as quasi-banks funded by bonds—mortgage and development loans on the "
                "asset side, housing bonds on the liability side. Net position ratio (Net Position / Total Assets) "
                "measures financial cushion and resilience."
            ),
            "growth_champion": (
                "Growth leader: {state} ({abbr}) posted net position growth of {pct}, reaching {np}. "
                "This typically reflects rebounding bond issuance, portfolio expansion, or fair-value recovery—"
                "but should be cross-checked against housing units financed."
            ),
            "s2": "II. Rankings: Who Is Getting Bigger, Stronger, and Faster",
            "s2_1": "2.1 Top 10 by Net Position (Financial Heavyweights)",
            "s2_1_insight": (
                "Insight: The largest net-position agencies are often dual-engine players in multifamily "
                "housing revenue bonds (MHRB) and single-family mortgage programs. Scale alone does not "
                "equal performance, but it signals stronger bargaining power, lower marginal borrowing costs, "
                "and capacity to underwrite large affordable housing deals when federal policy shifts."
            ),
            "s2_2": "2.2 Top 10 by Net Position Growth (Financial Acceleration)",
            "s2_2_insight": (
                "Insight: High-growth states often fall into three scenarios: (1) bond issuance rebound; "
                "(2) loan-loss reserve releases or fair-value gains; (3) state down-payment/homeownership "
                "programs improving fees and spreads. Caution: growth driven by fair-value gains rather than "
                "operating surplus may be less sustainable."
            ),
            "s2_2_empty": (
                "Some reports do not disclose comparable two-year net position growth; this section will "
                "expand as coverage improves."
            ),
            "s2_3": "2.3 Top 10 by Total Assets (Market Anchors)",
            "s2_4": "2.4 Top 10 by Net Position Ratio (Financial Cushion)",
            "s2_4_insight": (
                "Insight: Agencies with higher net position ratios typically have more room to absorb asset "
                "impairments, rate shocks, or tighter refinancing windows. For policymakers, this is a hard "
                "measure of fiscal resilience—not a talking point."
            ),
            "s3": "III. Regional & Model Comparison: Five State HFA Archetypes",
            "s3_intro": "FY2025 disclosures suggest five rough archetypes for cross-state benchmarking:",
            "prototypes": [
                (
                    "Bond-Driven Giants",
                    "e.g., MI, IL, MN—assets and liabilities expand together, heavily reliant on MHRB/SFR "
                    "programs and GSE pipelines.",
                ),
                (
                    "Lean High-Growth Players",
                    "e.g., NH, WV—mid-sized balance sheets but notable net position growth; useful models for "
                    "how smaller states punch above their weight.",
                ),
                (
                    "Integrated State-Department Models",
                    "e.g., TX TDHCA—governmental and business-type funds in parallel; disclosure basis "
                    "requires careful reading.",
                ),
                (
                    "High-Cost Coastal States",
                    "e.g., CA, NY, WA—financial results tightly linked to home prices, construction costs, "
                    "and project pipelines. FY2025 CalHFA reported net position of ~$3.44B and total assets "
                    "near $5.0B, with single-family TBA securitizations exceeding $3B—among the nation's "
                    "largest state housing finance players.",
                ),
                (
                    "Resource / Low-Density States",
                    "e.g., WY, ND, SD—issuance cycles are volatile; individual projects can move the "
                    "financial statements materially.",
                ),
            ],
            "s4": "IV. Counter-Intuitive Insights Behind the Numbers",
            "insights": [
                (
                    "Bigger is not always safer",
                    "The largest asset bases often carry the highest liabilities and derivative exposure. "
                    "With FY2025 rate paths still uncertain, net position ratio and cash flow matter as much "
                    "as asset rankings.",
                ),
                (
                    "Net position growth ≠ more housing built",
                    "Under GAAP, net position can move with investment fair value, loss provisions, or bond "
                    "premium amortization. Housing output must be validated against project reports (units "
                    "financed, bonds issued).",
                ),
                (
                    "Disclosure quality is a competitive advantage",
                    "Agencies earning the GFOA Certificate of Achievement (e.g., IL IHDA) tend to publish "
                    "clearer MD&A—lowering investor due-diligence costs and, indirectly, bond spreads.",
                ),
            ],
            "s5": "V. Constructive Recommendations: A Policy Toolkit for FY2026 and Beyond",
            "recommendations": [
                (
                    "Establish an HFA Financial Health Index",
                    "Standardize disclosure of net position ratio, debt service coverage, delinquency rates, "
                    "LIHTC pipeline, and single-family vs. multifamily mix—replacing fragmented narratives "
                    "with comparable metrics.",
                ),
                (
                    "Embed affordability in the balance sheet",
                    "Add MD&A unit-cost metrics: affordable units per $1M of bond proceeds, first-time "
                    "buyers supported per dollar of net position—linking financial statements to housing outcomes.",
                ),
                (
                    "Regional bond pooling and risk sharing",
                    "Smaller HFAs: explore regional bond pools to cut issuance costs. Larger HFAs: standardize "
                    "hedging for disaster and interest-rate risk.",
                ),
                (
                    "Digital disclosure and machine-readable data",
                    "Publish XBRL or structured CSV supplements so researchers, rating agencies, and federal "
                    "partners can monitor HFAs in near real time.",
                ),
                (
                    "Focus on the missing middle (80%–120% AMI)",
                    "Track middle-income projects separately in financial planning—avoid concentrating all "
                    "resources at the lowest AMI tier and market-rate ends, squeezing out teachers, nurses, "
                    "and similar workers.",
                ),
            ],
            "s6": "VI. Data Coverage & Download Inventory",
            "s7": "VII. States Without FY2025 Reports (Watch List)",
            "s7_body": (
                "The following {count} states/territories had no locatable FY2025 ACFR/financial statement "
                "in public channels as of this report—often because audits were incomplete, only FY2024 was "
                "posted, or filings sit behind non-standard portals."
            ),
            "appendix": "Appendix: Methodology",
            "appendix_body": (
                "Data sources: FY2025 ACFRs or audited financial statement PDFs published on state HFA or "
                "state auditor websites. Metric extraction prioritizes MD&A Financial Highlights and Statement "
                "of Net Position lines for Total assets, Total liabilities, and Total net position (typically "
                "in thousands of dollars). Limitation: disclosure bases differ (governmental vs. business-type "
                "vs. blended); cross-state comparisons should be read with footnotes."
            ),
            "table_rank": ["Rank", "State", "Agency", "FY2025 Net Position", "FY2025 Total Assets", "Net Position Ratio"],
            "table_growth": ["Rank", "State", "Agency", "Net Position Change", "Growth Rate", "FY2025 Net Position"],
            "table_assets": ["Rank", "State", "Agency", "FY2025 Total Assets", "FY2025 Net Position"],
            "table_ratio": ["Rank", "State", "Agency", "Net Position Ratio", "FY2025 Net Position", "FY2025 Total Assets"],
            "table_coverage": ["State", "Agency", "Status", "File Name", "Notes"],
            "note_state_acfr": "State-level ACFR/consolidated report; excluded from HFA-specific rankings",
            "note_extract_fail": "Core metrics not auto-extracted; manual PDF review recommended",
            "note_missing_pdf": "FY2025 PDF link not found",
            "note_extract_error": "Text extraction failed: {err}",
        }

    return {
        "date_fmt": date_fmt,
        "downloaded_label": downloaded_label,
        "missing_label": missing_label,
        "title": "FY2025 美国州级住房金融机构\nACFR/财务报表 全景分析与战略洞察",
        "subtitle": "编制日期：{date}  |  覆盖 {total} 个州/特区  |  成功获取 {downloaded} 份FY2025报告",
        "s1": "一、执行摘要：住房金融体系的“资产负债表时刻”",
        "s1_body": (
            "FY2025（截至2025年6月30日，部分机构为日历年）是美国州级住房金融机构（State Housing Finance Agencies, HFAs）"
            "在利率回落、LIHTC竞争加剧、以及首购支持计划扩张交织背景下的关键财务年度。"
            "本报告基于公开披露的ACFR/经审计财务报表，对全美51个州/特区的HFA进行系统采集与横向比较。"
            "截至采集日，共成功获取 {downloaded} 份FY2025报告（覆盖率 {coverage:.0f}%）。"
        ),
        "key_findings": (
            "核心发现：在已提取数据的 {count} 家机构中，合计净资产（Net Position）约 {np}，"
            "合计总资产约 {assets}。州级HFA是以债券融资为核心的准银行机构——资产端主要是抵押贷款与开发贷款，"
            "负债端是住房债券。净资产率（Net Position / Total Assets）衡量缓冲垫与抗风险能力。"
        ),
        "growth_champion": (
            "增长冠军：{state}（{abbr}）净资产同比增长 {pct}，达到 {np}。"
            "这通常反映债券发行回暖、贷款组合扩张或公允价值回升，但需与单位产出交叉验证。"
        ),
        "s2": "二、排行榜：谁在做大、谁在做厚、谁在跑得快",
        "s2_1": "2.1 净资产规模 Top 10（财务“体量之王”）",
        "s2_1_insight": (
            "洞察：净资产规模最大的机构往往也是多家庭债券（Multifamily Housing Revenue Bonds）"
            "与单一家庭抵押贷款计划的“双引擎”玩家。规模本身不等于绩效，但意味着在联邦政策波动时"
            "拥有更强的议价能力、更低的边际融资成本，以及承接大型可负担住房项目的组织能力。"
        ),
        "s2_2": "2.2 净资产增长率 Top 10（财务“加速度”）",
        "s2_2_insight": (
            "洞察：高增长州往往出现在三类情境——(1) 债券发行量反弹；(2) 贷款损失准备释放或公允价值回升；"
            "(3) 州级首购/英雄/homeownership计划带来费用与利差改善。"
            "但需警惕：若增长主要来自公允价值而非经营性盈余，则可持续性较弱。"
        ),
        "s2_2_empty": "部分报告未披露可比的两年净资产增长率，本节数据随下载完成度提升而扩展。",
        "s2_3": "2.3 总资产规模 Top 10（市场“压舱石”）",
        "s2_4": "2.4 净资产率 Top 10（财务“缓冲垫”）",
        "s2_4_insight": (
            "洞察：净资产率较高的机构，通常在资产减值、利率冲击、或债券再融资窗口收窄时拥有更大回旋余地。"
            "对于政策制定者，这是“财政韧性”的硬指标，而非公关话术。"
        ),
        "s3": "三、区域与模式对比：五种“州级HFA原型”",
        "s3_intro": "通过FY2025披露信息，可将州级HFA粗略分为五类原型，便于跨州对标：",
        "prototypes": [
            ("债券驱动型巨人", "如MI、IL、MN等，资产与负债同步扩张，高度依赖MHRB/SFR计划与GSE对接。"),
            ("精悍增长型", "如NH、WV等，体量中等但净资产增长显著，适合研究“小州如何做大影响”。"),
            ("综合州部门型", "如TX TDHCA，财务结构更偏行政基金+企业基金并行，披露口径需特别关注。"),
            (
                "沿海高成本州",
                "如CA、NY、WA，受房价与建筑成本制约，财务表现与项目管道高度相关。"
                "FY2025 CalHFA 净资产约 $34.4 亿、总资产近 $50 亿，单一家庭 TBA 证券化超 $30 亿，"
                "是全国体量最大的州级住房金融玩家之一。",
            ),
            ("资源型/低密度州", "如WY、ND、SD，发行周期波动大，但单次项目对财务报表影响更显著。"),
        ],
        "s4": "四、有趣洞察：数字背后的三条“反直觉”",
        "insights": [
            (
                "越大不一定越“安全”",
                "资产规模最大的机构往往伴随最高的负债与衍生品敞口。"
                "在FY2025利率路径仍不确定的环境下，应同时看净资产率与现金流，而非只看资产排名。",
            ),
            (
                "净资产增长≠多盖了房",
                "会计准则下的净资产变动可能来自投资公允价值、损失准备、或债券溢价摊销。"
                "评估住房产出，必须将ACFR与项目绩效报告（units financed, bonds issued）交叉验证。",
            ),
            (
                "披露质量本身就是竞争力",
                "获得GFOA Certificate of Achievement的机构（如IL IHDA）通常披露更完整、"
                "MD&A更可读——这降低了投资者成本，间接转化为更低的债券利差。",
            ),
        ],
        "s5": "五、建设性建议：面向FY2026及以后的政策工具箱",
        "recommendations": [
            (
                "建立“HFA财务健康指数”（HFA Financial Health Index）",
                "建议各州统一披露：净资产率、债务服务覆盖率、贷款逾期率、LIHTC项目管道、"
                "以及单一家庭/多家庭占比。用一套可比指标替代碎片化叙述。",
            ),
            (
                "把“可负担”写进资产负债表",
                "在MD&A中增加单位成本指标：每100万美元债券融资对应的可负担单元数、"
                "每单位净资产的首购家庭数。让财务报告与住房成果直接挂钩。",
            ),
            (
                "跨州联合发债与风险共担",
                "对小型HFA，探索区域联合债券池（regional pool）以降低发行成本；"
                "对大型HFA，探索灾难与利率风险的对冲工具标准化。",
            ),
            (
                "数字化披露与机器可读数据",
                "推动XBRL或结构化CSV附件，便于研究者、评级机构与联邦伙伴实时监测。"
                "这将显著提升本报告一类分析的时效性与准确性。",
            ),
            (
                "关注“中间缺失”市场（Missing Middle）",
                "建议在财务规划中单独追踪80%-120% AMI项目，"
                "避免所有资源集中在极低收入与市场化两端，导致教师/护士等群体持续被挤出。",
            ),
        ],
        "s6": "六、数据覆盖与下载清单",
        "s7": "七、尚未获取FY2025报告的州（需持续跟踪）",
        "s7_body": (
            "以下 {count} 个州/特区截至本报告编制时，尚未在公开渠道定位到FY2025 ACFR/财务报表，"
            "可能原因包括：审计尚未完成、仅发布FY2024、或报告托管在非标准页面。"
        ),
        "appendix": "附录：方法论",
        "appendix_body": (
            "数据来源：各州HFA/州审计机构官网公开发布的FY2025 ACFR或经审计财务报表PDF。"
            "指标提取：优先解析MD&A“Financial Highlights”及Statement of Net Position中的"
            "Total assets / Total liabilities / Total net position（单位通常为千美元）。"
            "限制：不同州披露口径（政府活动/企业活动/合并）存在差异，跨州比较应结合注释阅读。"
        ),
        "table_rank": ["排名", "州", "机构", "FY2025净资产", "FY2025总资产", "净资产率"],
        "table_growth": ["排名", "州", "机构", "净资产变动", "增长率", "FY2025净资产"],
        "table_assets": ["排名", "州", "机构", "FY2025总资产", "FY2025净资产"],
        "table_ratio": ["排名", "州", "机构", "净资产率", "FY2025净资产", "FY2025总资产"],
        "table_coverage": ["州", "机构", "状态", "文件名", "备注"],
        "note_state_acfr": "文件为州级ACFR/合并报表，未纳入HFA专项排名",
        "note_extract_fail": "未能自动提取核心指标，需人工复核PDF",
        "note_missing_pdf": "未找到FY2025 PDF链接",
        "note_extract_error": "文本提取失败: {err}",
    }


def _translate_notes(notes: list[str], language: str) -> str:
    if not notes:
        return "-"
    t = _report_copy(language)
    translated: list[str] = []
    for note in notes:
        if "州级ACFR" in note or "state-level ACFR" in note.lower():
            translated.append(t["note_state_acfr"])
        elif "未能自动提取" in note or "not auto-extracted" in note.lower():
            translated.append(t["note_extract_fail"])
        elif "未找到FY2025" in note or "PDF link not found" in note:
            translated.append(t["note_missing_pdf"])
        elif note.startswith("文本提取失败"):
            err = note.split(":", 1)[-1].strip()
            translated.append(t["note_extract_error"].format(err=err))
        else:
            translated.append(note)
    return "; ".join(translated)


def build_report(metrics: list[AgencyMetrics], language: str = "en", output_path: Optional[Path] = None) -> None:
    t = _report_copy(language)
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)

    downloaded = [m for m in metrics if m.status == "downloaded"]
    missing = [m for m in metrics if m.status != "downloaded"]
    rankable = [m for m in downloaded if m.state not in EXCLUDE_FROM_RANKINGS]
    with_np = [m for m in rankable if m.net_position_2025]
    with_assets = [m for m in rankable if m.total_assets_2025]
    with_growth = [m for m in rankable if m.net_position_change_pct is not None]

    add_title(doc, t["title"])
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.add_run(
        t["subtitle"].format(
            date=datetime.now().strftime(t["date_fmt"]),
            total=len(metrics),
            downloaded=len(downloaded),
        )
    ).italic = True

    add_heading(doc, t["s1"], 1)
    doc.add_paragraph(
        t["s1_body"].format(
            downloaded=len(downloaded),
            coverage=len(downloaded) / len(metrics) * 100 if metrics else 0,
        )
    )

    if with_np:
        top_np = sorted(with_np, key=lambda x: x.net_position_2025 or 0, reverse=True)[:10]
        top_growth = sorted(with_growth, key=lambda x: x.net_position_change_pct or 0, reverse=True)[:10]
        top_assets = sorted(with_assets, key=lambda x: x.total_assets_2025 or 0, reverse=True)[:10]
        top_ratio = sorted(
            [m for m in rankable if m.net_position_ratio],
            key=lambda x: x.net_position_ratio or 0,
            reverse=True,
        )[:10]

        total_np = sum(m.net_position_2025 or 0 for m in with_np)
        total_assets = sum(m.total_assets_2025 or 0 for m in with_assets)

        doc.add_paragraph(
            t["key_findings"].format(
                count=len(with_np),
                np=fmt_money(total_np, "B"),
                assets=fmt_money(total_assets, "B"),
            )
        )

        if top_growth:
            fastest = top_growth[0]
            doc.add_paragraph(
                t["growth_champion"].format(
                    state=fastest.state,
                    abbr=fastest.abbr,
                    pct=fmt_pct(fastest.net_position_change_pct),
                    np=fmt_money(fastest.net_position_2025, "M"),
                )
            )

        add_heading(doc, t["s2"], 1)
        add_heading(doc, t["s2_1"], 2)
        add_table(
            doc,
            t["table_rank"],
            [
                [
                    str(i),
                    m.state,
                    m.abbr,
                    fmt_money(m.net_position_2025, "M"),
                    fmt_money(m.total_assets_2025, "M"),
                    fmt_pct(
                        m.net_position_ratio
                        if m.net_position_ratio is not None
                        else (
                            (m.net_position_2025 / m.total_assets_2025) * 100
                            if m.net_position_2025 and m.total_assets_2025
                            else None
                        )
                    ),
                ]
                for i, m in enumerate(top_np, 1)
            ],
        )
        doc.add_paragraph(t["s2_1_insight"])

        add_heading(doc, t["s2_2"], 2)
        if top_growth:
            add_table(
                doc,
                t["table_growth"],
                [
                    [
                        str(i),
                        m.state,
                        m.abbr,
                        fmt_money(m.net_position_change, "M"),
                        fmt_pct(m.net_position_change_pct),
                        fmt_money(m.net_position_2025, "M"),
                    ]
                    for i, m in enumerate(top_growth, 1)
                ],
            )
            doc.add_paragraph(t["s2_2_insight"])
        else:
            doc.add_paragraph(t["s2_2_empty"])

        add_heading(doc, t["s2_3"], 2)
        add_table(
            doc,
            t["table_assets"],
            [
                [
                    str(i),
                    m.state,
                    m.abbr,
                    fmt_money(m.total_assets_2025, "M"),
                    fmt_money(m.net_position_2025, "M"),
                ]
                for i, m in enumerate(top_assets, 1)
            ],
        )

        add_heading(doc, t["s2_4"], 2)
        if top_ratio:
            add_table(
                doc,
                t["table_ratio"],
                [
                    [
                        str(i),
                        m.state,
                        m.abbr,
                        fmt_pct(m.net_position_ratio),
                        fmt_money(m.net_position_2025, "M"),
                        fmt_money(m.total_assets_2025, "M"),
                    ]
                    for i, m in enumerate(top_ratio, 1)
                ],
            )
            doc.add_paragraph(t["s2_4_insight"])

    add_heading(doc, t["s3"], 1)
    doc.add_paragraph(t["s3_intro"])
    for name, desc in t["prototypes"]:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(f"{name}: ").bold = True
        p.add_run(desc)

    add_heading(doc, t["s4"], 1)
    for title, body in t["insights"]:
        p = doc.add_paragraph()
        p.add_run(f"{title}. ").bold = True
        p.add_run(body)

    add_heading(doc, t["s5"], 1)
    for title, body in t["recommendations"]:
        p = doc.add_paragraph(style="List Number")
        p.add_run(f"{title}. ").bold = True
        p.add_run(body)

    add_heading(doc, t["s6"], 1)
    add_table(
        doc,
        t["table_coverage"],
        [
            [
                m.state,
                m.abbr,
                t["downloaded_label"] if m.status == "downloaded" else t["missing_label"],
                m.source_file or "-",
                _translate_notes(m.notes, language),
            ]
            for m in sorted(metrics, key=lambda x: x.state)
        ],
    )

    if missing:
        add_heading(doc, t["s7"], 1)
        doc.add_paragraph(t["s7_body"].format(count=len(missing)))
        for m in missing:
            doc.add_paragraph(f"{m.state} - {m.name} ({m.abbr})", style="List Bullet")

    add_heading(doc, t["appendix"], 1)
    doc.add_paragraph(t["appendix_body"])

    target = output_path or (REPORT_PATH if language == "en" else REPORT_PATH_CN)
    doc.save(target)


def build_reports(metrics: list[AgencyMetrics]) -> None:
    build_report(metrics, language="en", output_path=REPORT_PATH)
    build_report(metrics, language="zh", output_path=REPORT_PATH_CN)


def main() -> int:
    try:
        import bs4  # noqa: F401
    except ImportError:
        import subprocess

        subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4", "--quiet"])

    ensure_dirs()
    catalog = load_catalog()
    log: dict = {}
    metrics: list[AgencyMetrics] = []

    print(f"Collecting FY2025 reports for {len(catalog)} agencies...")
    for agency in catalog:
        state = agency["state"]
        print(f"  [{state}] {agency['name']}")
        pdf_path = collect_agency(agency, log)
        metric = AgencyMetrics(state=state, name=agency["name"], abbr=agency["abbr"])
        if pdf_path:
            metric.status = "downloaded"
            metric.source_file = pdf_path.name
            metric.source_url = log[state].get("source_url", "")
            txt_path = TXT_DIR / pdf_path.with_suffix(".txt").name
            try:
                text = extract_text_from_pdf(pdf_path)
                txt_path.write_text(text, encoding="utf-8", errors="replace")
                extracted = extract_metrics(text, agency)
                for k, v in asdict(extracted).items():
                    if k in {"state", "name", "abbr", "status", "source_file", "source_url"}:
                        continue
                    if v is not None and v != []:
                        setattr(metric, k, v)
            except Exception as exc:
                metric.notes.append(f"文本提取失败: {exc}")
        else:
            metric.status = "missing"
            metric.notes.append("未找到FY2025 PDF链接")
        metrics.append(metric)

    LOG_PATH.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
    DATA_PATH.write_text(
        json.dumps([asdict(m) for m in metrics], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    build_reports(metrics)

    downloaded = sum(1 for m in metrics if m.status == "downloaded")
    print(f"\nDone. Downloaded {downloaded}/{len(metrics)} reports.")
    print(f"PDF dir: {PDF_DIR}")
    print(f"Report EN: {REPORT_PATH}")
    print(f"Report CN: {REPORT_PATH_CN}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
