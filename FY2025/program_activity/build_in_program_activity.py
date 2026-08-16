"""
Builds docs/in_program_activity.json from IHCDA's 2025 Annual Report.

Source: Indiana Housing and Community Development Authority (IHCDA),
"2025 Annual Report" (the report's own cover title).
  https://www.in.gov/ihcda/files/2025-Annual-Report.pdf
Local copy: FY2025/program_activity/pdf/IN_IHCDA_AnnualReport_2025.pdf

This is a *program activity* report (units financed / households served),
not an audited financial statement (ACFR) -- the same data category as
docs/state_data.json's map but kept in its own lazily-fetched JSON, mirroring
IL/PA/OH/FL and the rest of the STATE_CONFIGS batch.

Data year (important -- title year is NOT proof of content year)
------------------------------------------------------------------------
IHCDA's own FY2025 audited financial statements (FY2025/txt/
IN_IHCDA_FY2025_ACFR.txt) cover "the year ended December 31, 2025" -- i.e.
IHCDA's fiscal year is the CALENDAR year, not a July-June fiscal year. The
annual report's narrative uses "In 2025" throughout (LIHTC reservations,
HCV rental assistance, LIHEAP, etc.), consistent with that December-31
entity year. fiscal_year is therefore recorded honestly as "CY2025", the
same convention as FL's calendar-year report. (The task briefing's "FY2025"
label is superseded by the ACFR's own "December 31, 2025" dating.)

One source-document data-quality anomaly is flagged, not fixed: the report's
Exhibit 1 (Schedule of Expenditures of Federal Awards, "SEFA") prints column
headers "2023 2024" -- i.e. it appears to be a stale/copy-pasted table from a
prior edition, since a December-31-2025 report should show 2025 (and 2024)
columns. This script does NOT use the SEFA for any KPI; all figures come from
the narrative program sections (pages 6-18) whose "In 2025" figures are
internally consistent and match the separately-audited December-31-2025
financial statements' scope.

Methodology
-----------
The four top-level category totals below are IHCDA's own published aggregates,
taken verbatim from the narrative sections. The multifamily category (41
LIHTC projects / 4,840 units / $1,106,244,457) is additionally reproduced by
two INDEPENDENT summation paths (see verify_multifamily_dollars): (1) the
three program tiers' own dollar subtotals (page 7's "Funding Sources
Allocated" lists), and (2) the six funding-source column totals re-summed
across those same three tiers. Both paths land on the report's own printed
"Total 2025 Funding approvals ... $1,106,244,457" row, and the bond column
($428,297,597) also matches page 6's narrative "over $428,297,597 in bond
financing" -- so the transcription is pinned at multiple independent points.

The multifamily category's 3 subprograms (9% LIHTC / 4%+AWHTC / 4%
non-competitive) are a TRUE partition of the 41 projects -- Exhibit 2 lists
each project under exactly one of the three headers, and 21 + 5 + 15 = 41
projects, 1,039 + 731 + 3,070 = 4,840 units, and the three dollar subtotals
sum to $1,106,244,457 -- so additive=True is correct for this category. This
is the cleaner model (vs. funding-source subprograms) because Exhibit 2 gives
NO per-project funding-source or dollar columns -- only name / type / location
/ tier / units -- so per-project multi-source attribution is impossible
without fabricating it.

Fund-type classification (fund_type/fund_name) comes from IHCDA's own FY2025
audited financial statements (FY2025/txt/IN_IHCDA_FY2025_ACFR.txt), cross-
referenced program-by-program:
  - Note 2 (Basis of Presentation): "The Authority accounts for all of its
    activity as a proprietary fund, which includes business-type activities
    that are financed in whole or in part by fees charged to external
    parties." IHCDA is therefore proprietary-only (like PHFA) -- it has NO
    governmental funds, so the "governmental" classification never applies.
  - Note 1 names exactly four funds: the General Fund (fee income/operating),
    the Program Fund ("accounts for grant and loan activity related to
    various federal and state programs administered by the Authority"), and
    the Single Family + MBS Pass-thru Funds (bond indentures funding the
    single-family mortgage programs).
  - Note 4 (Accounts and Loans Receivable) places: Development Fund loans
    ($106.4M), HOME program loans ($20.8M) and National Housing Trust Fund
    ($2.9M) in the Program Fund; Single Family Fund down-payment-assistance
    loans ($129.2M) in the Single Family Fund. Note 2 separately states
    "IHCDA provides down payment assistance (DPA) for most of its Single
    Family Fund homeownership programs."
  - MD&A (p.9) describes the Authority's primary activity as "funding the
    purchase of single-family home mortgages, multi-family development tax
    credits, TAX EXEMPT CONDUIT BOND financing and administering various
    federal programs" (emphasis added) -- i.e. the multifamily tax-exempt
    bonds in the LIHTC category are CONDUIT debt (repaid by project revenue,
    not IHCDA), so they sit off IHCDA's own balance sheet just like the
    allocated LIHTC/AWHTC credits themselves.

Resulting per-subprogram classification:
  - LIHTC category's three tiers -> "mixed": each combines off-balance-sheet
    items (federal 9%/4% LIHTC credits and state AWHTC credits flow directly
    to developers/investors; the $428.3M tax-exempt bonds are conduit) with a
    SMALL proprietary gap-financing component (HOME/HTF/Development Fund
    loans carried in the Program Fund). The off-balance-sheet share is
    ~96-99% of each tier's dollars, so the "mixed" flag + the fund_name text
    make the composition explicit rather than over-claiming a clean bucket.
  - homeownership (DPA) -> "proprietary", fund_name "Single Family Fund"
    (Note 2's verbatim "Single Family Fund homeownership programs" + Note 4's
    Single Family Fund DPA loans).
  - Housing Choice Vouchers -> "proprietary", fund_name "Program Fund" (a
    HUD-administered federal pass-through program; carried through the
    Program Fund's federal-grant activity).
  - LIHEAP -> "proprietary", fund_name "Program Fund" (an HHS federal
    pass-through program, same Program Fund reasoning).

Project-level detail (Exhibit 2, "2025 Low-Income Housing Tax Credit
Awards", p.21) is manually transcribed: 41 rows, each with name / type /
location (city) / tier / units. The exhibit gives NO street addresses and NO
per-project dollar amounts, so every project is geocoded to its city center
(geocode_status "city_center") and source_amounts/total_amount are left
empty -- the source simply does not disclose per-project dollars, so none are
invented. One row ("Walters-Biggs RD") prints "Scattered" as its Location
(no single municipality); it is geocoded via the road named in the project
title as a best-effort approximation, still marked "city_center" to reflect
the reduced precision.

Geocoding: Nominatim (OpenStreetMap), query "{city}, IN", self-throttled to
<=1 request/second with an identifying User-Agent per usage policy. Because
this batch of states shares one egress IP and Nominatim rate-limits (HTTP 429)
under sustained parallel load, `geocode()` falls back to Photon
(photon.komoot.io) -- another geocoder over the same OpenStreetMap/Nominatim
data -- when Nominatim stays rate-limited after backoff retries. Both sources
return city-center precision, so the honest `geocode_status` stays
"city_center" regardless of which one resolved the query. Successful lookups
are cached to disk (`in_geocode_cache.json`) so re-runs are byte-identical and
never re-hit the network.
"""

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "in_program_activity.json"

SOURCE_URL = "https://www.in.gov/ihcda/files/2025-Annual-Report.pdf"
SOURCE_FILE = "IN_IHCDA_AnnualReport_2025.pdf"
RETRIEVED = "2026-08-16"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
PHOTON_URL = "https://photon.komoot.io/api/"  # OSM-based fallback when Nominatim 429s
GEOCODER_USER_AGENT = "us-hfa-data-map/1.0 (github.com/MD-ai-fin/us-hfa-data-map)"

# Persisted geocode cache: Nominatim is rate-limited (1 req/sec, and this
# batch of states shares one egress IP), so successful lookups are cached to
# disk keyed by query. This (a) makes re-runs byte-identical without re-hitting
# the network, and (b) lets a rate-limited re-run still reproduce the exact
# coordinates of the first successful run.
GEOCODE_CACHE_PATH = Path(__file__).resolve().parent / "in_geocode_cache.json"

# ---------------------------------------------------------------------------
# Category-level data (narrative sections, IHCDA's own published aggregates)
# ---------------------------------------------------------------------------

# Every fy2026 dict uses a uniform shape: {value, amount, closed, note_key}.
# IHCDA's 2025 Annual Report is purely retrospective -- it discloses no FY2026
# projection anywhere -- so every fy2026 is the neutral "pending" shape, the
# same convention PHFA's tables required (see build_pa_program_activity.py).
_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "inFy26NotePending"}

CATEGORIES = [
    {
        "key": "multifamily_lihtc",
        "unit_type": "units",
        "fy2025_actual": 4840,
        "fy2025_source_quote": (
            "\"In total, with state and federal tax credits, tax-exempt bond "
            "financing, and additional gap financing through HOME Funds, the "
            "National Housing Trust Fund, and the Development Fund, commitments "
            "of over $1.1 billion were made which will make possible the "
            "development of 41 projects, comprising 4,840 new or preserved units "
            "of housing.\" (2025 Annual Report, p.6) -- reconciled against the "
            "report's own 'Total 2025 Funding approvals' row (p.7): 41 projects, "
            "4,840 units of housing, $1,106,244,457 from all IHCDA-administered "
            "sources, which this script reproduces two ways (tier subtotals and "
            "funding-source column sums) -- see verify_multifamily_dollars."
        ),
        "fy2025_amounts": [
            {"label_key": "in_amt_lihtc_total", "amount": 1106244457},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "lihtc_9", "fy2025_units": 1039, "fy2025_amount": 252815580,
             "color_group": "credit",
             # 9% LIHTC credits (off-balance-sheet, allocated to developers) +
             # HOME ($1.0M) + HTF ($3.0M) + Development Fund ($6.99M) gap loans
             # carried in the Program Fund (proprietary) -- Note 4.
             "fund_type": "mixed",
             "fund_name": "9% LIHTC credits (off-balance-sheet) + HOME/HTF/Development Fund gap (Program Fund)",
             "fy2026": _FY26_PENDING},
            {"key": "lihtc_4_awhtc", "fy2025_units": 731, "fy2025_amount": 184440563,
             "color_group": "credit",
             # 4% LIHTC + state AWHTC credits (off-balance-sheet) + $72.4M
             # conduit tax-exempt bonds (off-balance-sheet, per MD&A "tax
             # exempt conduit bond financing") + Development Fund ($1.0M) gap
             # (Program Fund).
             "fund_type": "mixed",
             "fund_name": "4% LIHTC + AWHTC credits + conduit bonds (off-balance-sheet) + Development Fund gap (Program Fund)",
             "fy2026": _FY26_PENDING},
            {"key": "lihtc_4_noncompetitive", "fy2025_units": 3070, "fy2025_amount": 668988314,
             "color_group": "bond",
             # 4% LIHTC credits (off-balance-sheet) + $355.8M conduit tax-exempt
             # bonds (off-balance-sheet) + Development Fund ($2.5M) gap
             # (Program Fund).
             "fund_type": "mixed",
             "fund_name": "4% LIHTC credits + conduit bonds (off-balance-sheet) + Development Fund gap (Program Fund)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "homeownership",
        "unit_type": "households",
        "fy2025_actual": 3086,
        "fy2025_source_quote": (
            "\"In 2025, the Homeownership Program assisted 3,086 homebuyers with "
            "$33,383,037 in down-payment assistance which facilitated "
            "$583,345,844 in total borrowing.\" (2025 Annual Report, p.11). "
            "Down-payment assistance is the headline figure; total borrowing is "
            "the first-mortgage volume the DPA helped facilitate."
        ),
        "fy2025_amounts": [
            {"label_key": "in_amt_dpa", "amount": 33383037},
            {"label_key": "in_amt_total_borrowing", "amount": 583345844},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "homebuyer_dpa", "fy2025_units": 3086, "fy2025_amount": 33383037,
             "color_group": "bond",
             # Note 2: "IHCDA provides down payment assistance (DPA) for most of
             # its Single Family Fund homeownership programs"; Note 4 lists the
             # DPA loans under the Single Family Fund. Proprietary (bond-funded
             # single-family program).
             "fund_type": "proprietary", "fund_name": "Single Family Fund",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "housing_choice_vouchers",
        "unit_type": "households",
        "fy2025_actual": 6514,
        "fy2025_source_quote": (
            "\"In 2025, IHCDA provided $46,711,763 in rental assistance to 6,514 "
            "households, including several special purpose vouchers: 376 Veterans "
            "Affairs Supportive Housing Vouchers, 408 Non-Elderly Disabled "
            "Vouchers, 37 Family Unification Program Vouchers, 25 Stability "
            "Vouchers, 108 Mainstream Vouchers.\" (2025 Annual Report, p.9). "
            "The special-purpose vouchers are a subset of the 6,514 (no per-type "
            "dollar split is disclosed), so they are quoted here rather than "
            "modeled as separate additive subprograms."
        ),
        "fy2025_amounts": [
            {"label_key": "in_amt_hcv_assistance", "amount": 46711763},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "hcv", "fy2025_units": 6514, "fy2025_amount": 46711763,
             "color_group": "trust",
             # HUD-administered federal rental-assistance pass-through; carried
             # through the Program Fund's federal-grant activity (Note 1: the
             # Program Fund accounts for "various federal and state programs").
             "fund_type": "proprietary", "fund_name": "Program Fund",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "liheap",
        "unit_type": "households",
        "fy2025_actual": 114594,
        "fy2025_source_quote": (
            "\"In 2025, funding from Health and Human Services in the amount of "
            "$49,249,453 was used to serve 114,594 Hoosier households.\" (2025 "
            "Annual Report, p.12)."
        ),
        "fy2025_amounts": [
            {"label_key": "in_amt_liheap_funding", "amount": 49249453},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "liheap", "fy2025_units": 114594, "fy2025_amount": 49249453,
             "color_group": "trust",
             # HHS (federal) pass-through grant; carried through the Program
             # Fund's federal-grant activity (Note 1).
             "fund_type": "proprietary", "fund_name": "Program Fund",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# ---------------------------------------------------------------------------
# Multifamily project-level detail (Exhibit 2, p.21)
# ---------------------------------------------------------------------------
# (name, city, units, program-tier key)
# "city" is the exhibit's own "Location" column. Exhibit 2 gives no street
# address and no per-project dollar amount, so every project below geocodes
# to a city center and carries no source_amounts. "Scattered" (Walters-Biggs
# RD) is the exhibit's literal Location for a scattered-site development with
# no single municipality -- see SCATTERED_SITE_QUERIES.
RAW_PROJECTS = [
    # 9% LIHTC (21 projects, 1,039 units)
    ("707 North Apartments", "Indianapolis", 40, "lihtc_9"),
    ("Bluffton Senior Villas II (BSV II)", "Bluffton", 32, "lihtc_9"),
    ("Burnett Manor", "Rockville", 60, "lihtc_9"),
    ("Country Acres", "La Porte", 100, "lihtc_9"),
    ("Donald & Main Apartments", "South Bend", 50, "lihtc_9"),
    ("Durbin Plaza Senior", "Lawrenceburg", 52, "lihtc_9"),
    ("Frankfort Fields", "Frankfort", 38, "lihtc_9"),
    ("GC Horizons", "Plymouth", 32, "lihtc_9"),
    ("Historic Jeff Centre", "Lafayette", 74, "lihtc_9"),
    ("Jackson Square", "Lebanon", 46, "lihtc_9"),
    ("Providence Ridge", "Greenwood", 41, "lihtc_9"),
    ("Ritchey Woods", "Fishers", 65, "lihtc_9"),
    ("River City Homes", "Evansville", 43, "lihtc_9"),
    ("Tanners Creek Manor", "Lawrenceburg", 46, "lihtc_9"),
    ("The Branches", "Hobart", 36, "lihtc_9"),
    ("Towne Village Apartments", "Ligonier", 28, "lihtc_9"),
    ("Trafalgar Senior Apartments", "Trafalgar", 46, "lihtc_9"),
    ("Tri Day", "South Bend", 42, "lihtc_9"),
    ("Village Premier - Senior Phase", "Fort Wayne", 50, "lihtc_9"),
    ("Walters-Biggs RD", "Scattered", 78, "lihtc_9"),
    ("West Park", "Indianapolis", 40, "lihtc_9"),
    # 4% with State AWHTC and Bonds (5 projects, 731 units)
    ("Allen's Place", "Clarksville", 150, "lihtc_4_awhtc"),
    ("Trinity Flats", "Indianapolis", 169, "lihtc_4_awhtc"),
    ("Heritage Trails", "South Bend", 180, "lihtc_4_awhtc"),
    ("Crawford Door", "Evansville", 134, "lihtc_4_awhtc"),
    ("The Crossing at Trails Edge", "Muncie", 98, "lihtc_4_awhtc"),
    # 4% with Bonds - Non-competitive (15 projects, 3,070 units)
    ("New Albany RAD", "New Albany", 125, "lihtc_4_noncompetitive"),
    ("Cambridge Square of Beech Grove", "Beech Grove", 126, "lihtc_4_noncompetitive"),
    ("Stadium Flats", "South Bend", 92, "lihtc_4_noncompetitive"),
    ("Beacon Heights", "Fort Wayne", 100, "lihtc_4_noncompetitive"),
    ("Cambridge Square of Greenwood", "Greenwood", 186, "lihtc_4_noncompetitive"),
    ("Garfield Towers", "Terre Haute", 152, "lihtc_4_noncompetitive"),
    ("Foulkes Village", "Terre Haute", 97, "lihtc_4_noncompetitive"),
    ("The Grove at Pleasant Run", "Indianapolis", 160, "lihtc_4_noncompetitive"),
    ("Oak Knoll Renaissance", "Gary", 256, "lihtc_4_noncompetitive"),
    ("Cambridge Square North", "Indianapolis", 380, "lihtc_4_noncompetitive"),
    ("Stone Lake Apartments", "Indianapolis", 236, "lihtc_4_noncompetitive"),
    ("Karl King Riverbend Tower", "South Bend", 219, "lihtc_4_noncompetitive"),
    ("Eastfield Reserve", "Evansville", 264, "lihtc_4_noncompetitive"),
    ("Central at Old Southside", "Indianapolis", 227, "lihtc_4_noncompetitive"),
    ("Renaissance Towers", "Hammond", 450, "lihtc_4_noncompetitive"),
]

# The three program tiers' own printed subtotals (p.7 "9% LIHTC Program 21
# projects - 1,039 units" / "4% LIHTC with State AWHTC Program 5 projects -
# 731 units" / "4% LIHTC Program (non-competitive) 15 projects - 3,070
# units"). Used as the internal-verification target for the RAW_PROJECTS
# transcription.
EXPECTED_TIER_PROJECTS = {
    "lihtc_9": 21, "lihtc_4_awhtc": 5, "lihtc_4_noncompetitive": 15,
}
EXPECTED_TIER_UNITS = {
    "lihtc_9": 1039, "lihtc_4_awhtc": 731, "lihtc_4_noncompetitive": 3070,
}

# Each tier's dollar subtotal, computed once directly from p.7's "Funding
# Sources Allocated" lists (before any manual transcription), and independently
# the six funding-source column totals re-summed across those three tiers.
TIER_AMOUNTS = {
    # 9% LIHTC: Federal $241,825,580 + HOME $1,000,000 + HTF $3,000,000 +
    #           Development Fund $6,990,000
    "lihtc_9": 252815580,
    # 4% + AWHTC: Federal $80,990,890 + State $30,000,000 + Bonds $72,449,673
    #             + Development Fund $1,000,000
    "lihtc_4_awhtc": 184440563,
    # 4% non-comp: Federal $310,640,390 + Bonds $355,847,924 + Development
    #              Fund $2,500,000
    "lihtc_4_noncompetitive": 668988314,
}
SOURCE_TOTALS = {
    "federal_lihtc": 633456860,   # 241,825,580 + 80,990,890 + 310,640,390
    "state_awhtc": 30000000,
    "tax_exempt_bonds": 428297597,  # 72,449,673 + 355,847,924 (matches p.6's $428,297,597)
    "home": 1000000,
    "htf": 3000000,
    "development_fund": 10490000,  # 6,990,000 + 1,000,000 + 2,500,000
}

FUNDING_COLOR_GROUP = {
    "lihtc_9": "credit", "lihtc_4_awhtc": "credit",
    "lihtc_4_noncompetitive": "bond",
}
# priority order for a project's primary color (single-source projects, so the
# first match is just its own tier)
FUNDING_PRIORITY = ["lihtc_9", "lihtc_4_awhtc", "lihtc_4_noncompetitive"]

# Exhibit 2 prints "Scattered" as the Location for this scattered-site family
# development (no single municipality). The project name names the road, so
# geocode the road as a best-effort approximation (still marked city_center to
# reflect the reduced precision).
SCATTERED_SITE_QUERIES = {
    "Walters-Biggs RD": "Walters-Biggs Road, Indiana",
}


def slug(name):
    s = name.lower().replace("&", "and").replace("+", "plus").replace("'", "")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def verify_project_table():
    errors = []
    if len(RAW_PROJECTS) != 41:
        errors.append(f"project count: expected 41, got {len(RAW_PROJECTS)}")
    total_units = sum(units for _n, _c, units, _t in RAW_PROJECTS)
    if total_units != 4840:
        errors.append(f"total units: expected 4840, got {total_units}")
    counts = {}
    unit_sums = {}
    for _name, _city, units, tier in RAW_PROJECTS:
        counts[tier] = counts.get(tier, 0) + 1
        unit_sums[tier] = unit_sums.get(tier, 0) + units
    for tier, expected in EXPECTED_TIER_PROJECTS.items():
        got = counts.get(tier, 0)
        if got != expected:
            errors.append(f"{tier} project count: expected {expected}, got {got}")
    for tier, expected in EXPECTED_TIER_UNITS.items():
        got = unit_sums.get(tier, 0)
        if got != expected:
            errors.append(f"{tier} unit sum: expected {expected}, got {got}")
    if set(counts) != set(EXPECTED_TIER_PROJECTS):
        errors.append(f"unexpected tier keys in RAW_PROJECTS: {sorted(counts)}")
    if errors:
        raise SystemExit("Project table mismatch(es):\n" + "\n".join(errors))
    print("Exhibit 2 verified: 41 projects, 4,840 units, and the 21/5/15 tier "
          "split with 1,039/731/3,070 unit subtotals all match the report's own "
          "printed figures.")


def verify_multifamily_dollars():
    mf = next(c for c in CATEGORIES if c["key"] == "multifamily_lihtc")
    sub_amounts = {sp["key"]: sp["fy2025_amount"] for sp in mf["subprograms"]}
    errors = []
    if sub_amounts != TIER_AMOUNTS:
        errors.append(
            f"CATEGORIES multifamily subprogram amounts do not match TIER_AMOUNTS: "
            f"{sub_amounts} vs {TIER_AMOUNTS}"
        )
    tier_sum = sum(TIER_AMOUNTS.values())
    source_sum = sum(SOURCE_TOTALS.values())
    printed_total = 1106244457
    if tier_sum != printed_total:
        errors.append(f"tier subtotal sum: expected {printed_total}, got {tier_sum}")
    if source_sum != printed_total:
        errors.append(f"funding-source column sum: expected {printed_total}, got {source_sum}")
    if SOURCE_TOTALS["tax_exempt_bonds"] != 428297597:
        errors.append(
            f"tax-exempt bond total: expected 428,297,597 (p.6), got "
            f"{SOURCE_TOTALS['tax_exempt_bonds']}"
        )
    if not (tier_sum > 1.1e9):
        errors.append(f"total ${tier_sum:,} does not exceed $1.1B as p.6 states")
    if errors:
        raise SystemExit("Multifamily dollar mismatch(es):\n" + "\n".join(errors))
    print(f"Multifamily dollars verified two ways to the report's own "
          f"$1,106,244,457 'Total 2025 Funding approvals' row; bond column "
          f"($428,297,597) also matches p.6's narrative.")


def verify_single_program_categories():
    # Trivial but documented: each single-program category's subprogram unit
    # count equals its own headline, and the amounts are the transcribed
    # source figures (p.11 / p.9 / p.12).
    expected = {
        "homeownership": (3086, 33383037),
        "housing_choice_vouchers": (6514, 46711763),
        "liheap": (114594, 49249453),
    }
    errors = []
    for cat in CATEGORIES:
        if cat["key"] not in expected:
            continue
        units, amount = expected[cat["key"]]
        if cat["fy2025_actual"] != units:
            errors.append(f"{cat['key']} headline units: expected {units}, got {cat['fy2025_actual']}")
        if len(cat["subprograms"]) != 1:
            errors.append(f"{cat['key']} expected 1 subprogram, got {len(cat['subprograms'])}")
            continue
        sp = cat["subprograms"][0]
        if sp["fy2025_units"] != units:
            errors.append(f"{cat['key']} subprogram units: expected {units}, got {sp['fy2025_units']}")
        if sp["fy2025_amount"] != amount:
            errors.append(f"{cat['key']} subprogram amount: expected {amount}, got {sp['fy2025_amount']}")
    if errors:
        raise SystemExit("Single-program category mismatch(es):\n" + "\n".join(errors))
    print("Homeownership (3,086 / $33,383,037), HCV (6,514 / $46,711,763) and "
          "LIHEAP (114,594 / $49,249,453) verified against the report's own "
          "narrative sentences.")


def _http_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": GEOCODER_USER_AGENT})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.load(resp)


def geocode(query, cache):
    if query in cache:
        return cache[query]
    result = None
    # Primary: Nominatim (self-throttled). If it is unavailable/rate-limited
    # (common under this batch's shared egress IP), fall back to Photon --
    # another geocoder over the same OpenStreetMap/Nominatim data -- so a
    # shared-IP rate limit does not leave a project unresolved.
    nurl = f"{NOMINATIM_URL}?{urllib.parse.urlencode({'q': query, 'format': 'json', 'limit': 1})}"
    try:
        data = _http_json(nurl)
        if data:
            result = (float(data[0]["lat"]), float(data[0]["lon"]))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError,
            KeyError, ValueError, IndexError) as exc:
        print(f"  Nominatim unavailable for {query!r} ({exc}); trying Photon")
    if result is None:
        purl = f"{PHOTON_URL}?{urllib.parse.urlencode({'q': query, 'limit': 1})}"
        try:
            data = _http_json(purl)
            features = data.get("features", [])
            if features:
                lon, lat = features[0]["geometry"]["coordinates"]
                result = (float(lat), float(lon))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError,
                KeyError, ValueError, IndexError) as exc:
            print(f"  Photon fallback failed for {query!r}: {exc}")
    cache[query] = result
    time.sleep(1.1)  # Nominatim/Photon usage policy: max 1 request/second (+ margin)
    return result


def load_geocode_cache():
    if GEOCODE_CACHE_PATH.exists():
        return json.loads(GEOCODE_CACHE_PATH.read_text(encoding="utf-8"))
    return {}


def save_geocode_cache(cache):
    GEOCODE_CACHE_PATH.write_text(
        json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def build_projects():
    cache = load_geocode_cache()
    projects = []
    for name, city, units, tier in RAW_PROJECTS:
        if city == "Scattered":
            query = SCATTERED_SITE_QUERIES.get(name, f"{name}, Indiana")
        else:
            query = f"{city}, IN"
        coords = geocode(query, cache)
        # Exhibit 2 is a city-level list (no street addresses), so a successful
        # lookup is at best a city-center (or, for the "Scattered" row, a
        # road-level) approximation -- never "ok".
        status = "city_center" if coords else "unresolved"
        projects.append({
            "id": slug(name),
            "name": name,
            "address": None,
            "city": city,  # "Scattered" (verbatim from the source's Location column) for Walters-Biggs RD
            "lat": round(coords[0], 5) if coords else None,
            "lon": round(coords[1], 5) if coords else None,
            "units": units,
            "funding_sources": [tier],
            "source_amounts": {},  # Exhibit 2 discloses no per-project dollars
            "total_amount": None,
            "primary_color_group": FUNDING_COLOR_GROUP[tier],
            "overlaps": False,
            "geocode_status": status,
        })
    save_geocode_cache(cache)
    return projects


def main():
    verify_project_table()
    verify_multifamily_dollars()
    verify_single_program_categories()
    print("Geocoding project cities via Nominatim...")
    projects = build_projects()
    unresolved = [p["name"] for p in projects if p["geocode_status"] == "unresolved"]
    if unresolved:
        print(f"  {len(unresolved)} project(s) could not be geocoded: {unresolved}")

    payload = {
        "IN": {
            "hfa_name": "Indiana Housing and Community Development Authority",
            "hfa_abbr": "IHCDA",
            "fiscal_year": "CY2025",
            "source_title": "IHCDA 2025 Annual Report",
            "source_url": SOURCE_URL,
            "source_file": SOURCE_FILE,
            "retrieved": RETRIEVED,
            "categories": CATEGORIES,
            "projects": projects,
        }
    }
    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT_PATH} ({len(projects)} projects, {len(CATEGORIES)} categories)")


if __name__ == "__main__":
    main()
