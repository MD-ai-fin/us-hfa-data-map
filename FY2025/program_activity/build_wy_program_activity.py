"""
Builds docs/wy_program_activity.json from the Wyoming Community Development
Authority's (WCDA) "2025 Annual Report" (50th anniversary edition) -- a FULL
build: two KPI categories (homeownership + multifamily) plus a 6-development
per-project cohort list for the bubble map.

Source
------------------------------------------------------------------------
"Annual Report 2025 -- 50th anniversary edition", Wyoming Community
Development Authority (WCDA):
    https://www.wyomingcda.com/wp-content/uploads/2025/12/Final_2025_WebPages_AR_WCDA.pdf
The report's table of contents (PDF p.2) lists the relevant sections:
"Homeownership & Lender Partnerships" (p.8), "2024-2025 accomplishments"
(p.10), and "Housing Development" (p.16) / "Multi-Family Projects Awarded"
(p.17). The director's message (PDF p.4-5) is signed above a QR pointer to
"the audited financial statements for the fiscal year ending June 30, 2025",
framing the report as FY2025. Every figure below is transcribed from a local
text extraction of that PDF (pypdf, page-by-page), not from memory or a
secondary source.

Fiscal-year discipline
------------------------------------------------------------------------
WCDA's fiscal year ends June 30, confirmed by both this annual report (the
"fiscal year ending June 30, 2025" QR line) and the matching audited
financial statements FY2025/txt/WY_WCDA_FY2025_ACFR.txt (title "June 30, 2025
and June 30, 2024"). The "Accomplishments 2024-2025" (PDF p.10) and the
"48 units placed in service in 2025" line (PDF p.15) are therefore FY2025
(July 1, 2024 - June 30, 2025) program-output figures; fiscal_year = "FY2025".
The report also carries 50-year CUMULATIVE figures (62,000 families helped,
$6.2B in single-family loans, 6,369 multifamily units, ~15,000 mortgages
serviced, $143M in federal-program investment, $25M CDBG, $111M HOME -- PDF
p.4/p.6/p.7): those are historical totals, NOT FY2025 activity, and are
excluded from this build.

Two honest cohort distinctions (the heart of this build)
------------------------------------------------------------------------
1. HOMEOWNERSHIP: 713 families is the FY2025 TOTAL single-family
   homeownership figure ("713 LOW-TO-MODERATE INCOME FAMILIES ACHIEVED
   HOMEOWNERSHIP", PDF p.10). The EDGE program is a NEW single-family loan
   product launched this year ("In its first year alone, WCDA financed more
   than $26.6 million in EDGE loans", PDF p.4) -- it is a SUBSET of the 713
   families, not a separate partition, and the report does not disclose how
   many of the 713 were EDGE loans. So the homeownership category headline is
   713 families; the single_family subprogram carries the 713 (the full
   cohort, whose total dollar production the report does not state), and the
   edge subprogram carries the $26.6M with units=None (count not disclosed).
   The $26.6M is NOT asserted as the 713-families total, and the category is
   additive=False.

2. MULTIFAMILY: the report splits its 6 developments into two cohorts that do
   NOT collapse into one KPI number:
     * "Housing Development" (PDF p.16) -- 2 projects PLACED IN SERVICE in
       FY2025, each with a disclosed LIHTC allocation: Parker Flats Sheridan
       (24 units, $405,605, 9%) and Pioneer Village II (24 units, $915,000,
       9%). These 48 units ARE the p.15 KPI ("Of the 48 units placed in
       service in 2025: 8% ... 33% ... 58% ... 50% rural").
     * "Multi-Family Projects Awarded" (PDF p.17) -- 4 projects AWARDED in
       FY2025 (not yet placed in service), with NO dollar amounts disclosed:
       Pioneer III (24, Cody), McKinney Crossing (24, Buffalo), Cathy Garden
       (40-unit rehabilitation, Rawlins), Meadowlark Place (24, Powell).
   The 6 projects total 160 units (24+24+24+24+40+24): 48 placed in service +
   112 awarded. The multifamily category headline is the 48 units placed in
   service (the report's own production KPI); the projects array lists all 6
   developments (160 units) with a "cohort" field marking each as
   "placed_in_service" or "awarded". The 48 vs 160 difference is a genuine
   two-cohort scope difference, disclosed not force-fit (see verify).

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
Source: FY2025/txt/WY_WCDA_FY2025_ACFR.txt. VERIFIED before use: the title
page reads "WYOMING COMMUNITY DEVELOPMENT AUTHORITY FINANCIAL REPORT June 30,
2025 and June 30, 2024"; the auditor's opinion covers "the financial
statements of the Wyoming Community Development Authority, a component unit
of the State of Wyoming, as of and for the years ended June 30, 2025 and
2024". Note 1 states "The Authority is a component unit of the State and is
reported as an enterprise fund" (.txt line 1763); Note 2 states the
statements use "the proprietary-fund concept" and are "considered a single
enterprise fund for financial reporting purposes" (.txt lines 1773, 1779).
Classification follows from that:
  - "proprietary" (HIGH confidence) -- single_family and edge. Note 2's
    "Single Family Program Funds" (.txt lines 1782-1787) are "established
    under the Housing Revenue Bonds 1994 Indenture ... to account for the
    proceeds from the sale of Single Family Mortgage Bonds ... limited to the
    purchase of mortgage loans collateralized by eligible mortgages on single
    family residential housing" -- WCDA's own MRB/enterprise lending business,
    which is where both the headline single-family loans and the EDGE product
    live. (EDGE is not individually named in the ACFR, but it is a
    single-family loan product of the same enterprise fund; the fund-level
    classification is high confidence, the product name is descriptive.)
  - "off_balance_sheet" (HIGH confidence) -- lihtc (9% LIHTC). The 9% federal
    Low-Income Housing Tax Credit is allocated directly to developers and
    their investors and is never booked as a WCDA asset; the ACFR's only
    LIHTC-adjacent mentions are the "Tax Credit Assistance Program" and "Tax
    Credit Exchange Program" as federal pass-through programs inside the
    Housing & Neighborhood Development Fund (.txt lines 1801-1803), not the
    credits themselves. Same off-balance-sheet logic as every other pilot
    state's LIHTC. fund_name is left None (the credits sit off the books).
  - "proprietary" (HIGH confidence) -- home (HOME co-funding). Note 2's
    "Housing & Neighborhood Development Fund" (.txt lines 1799-1804) is
    "established for the purpose of receiving and disbursing funds relating to
    projects funded by ... HOME Investment Partnership, Neighborhood
    Stabilization Program, National Housing Trust Fund, Tax Credit Assistance
    Program, Community Development Block Grant program and other federal
    programs. These funds are restricted by federal law" -- and the Authority
    recognizes "Federal program income $13,817,027" / "Federal program
    expenses ($16,375,218)" as nonoperating items within its own single
    enterprise fund (.txt lines 1452-1453, 1950). So HOME pass-through funds
    sit on WCDA's own books (proprietary), unlike an HFA that never books the
    money. The FY2025 HOME dollar amount is NOT reconciled to a specific ACFR
    line (this project's standing no-forced-reconciliation rule).

Category-level methodology (two categories)
------------------------------------------------------------------------
1. homeownership -- "713 LOW-TO-MODERATE INCOME FAMILIES ACHIEVED
   HOMEOWNERSHIP" (PDF p.10). The same page also prints "566 COMPLETED
   HOMEBUYER EDUCATION", an outreach/training metric (not housing production);
   it is quoted for completeness but not modeled. additive=False (EDGE is a
   nested subset, not a partition).

2. multifamily_development -- "Of the 48 units placed in service in 2025: 8%
   [<=30% AMI] / 33% [30.1-50% AMI] / 58% [50.1-60% AMI]; 50% [rural]" (PDF
   p.15). The 48-unit headline maps to the two p.16 placed-in-service
   developments, whose LIHTC allocations sum to $1,320,605 ($405,605 +
   $915,000). The report discloses NO HOME dollar or unit amount for any of
   the 6 projects, and NO LIHTC amount for the 4 p.17 awarded projects, so
   $1,320,605 is the sum of the TWO placed-in-service projects' LIHTC
   allocations only -- not the 6-project LIHTC total (which the report never
   states). additive=False: HOME overlaps LIHTC on every project, and the
   placed-in-service/awarded split is not a unit partition. The AMI/rural
   breakdowns are KPI-level only (no per-project split disclosed), quoted in
   fy2025_source_quote but not modeled as subprograms.

CDBG (PDF p.18-21) is community-development grants (a homeless-shelter
renovation, food-bank programs, infrastructure) -- NOT housing production --
and is excluded from this build, same as every other pilot state's CDBG.

HOME/NHTF co-funding note: p.16 lists "OTHER WCDA FINANCING: HOME/NHTF"
(Parker Flats Sheridan) and "HOME" (Pioneer Village II); p.17's four awarded
projects each "include 9% tax credits and HOME funding". NHTF appears once
(in Parker Flats' card) with no amount, so it is folded into the general
federal co-funding note rather than modeled as its own subprogram.

fy2026
------------------------------------------------------------------------
The annual report is backward-looking with no forward-projected activity, so
every fy2026 field is {value: None, amount: None, closed: False,
note_key: "wyFy26NotePending"} -- nothing is invented.

Geocoding
------------------------------------------------------------------------
The source gives a city for all 6 developments and a street address for 4 of
them (Parker Flats Sheridan, Pioneer Village II, Pioneer III, Cathy Garden),
but the developments are new construction / under-development, so
street-level geocoding is unreliable and city-center is the honest precision
level for this build. Every project is geocoded to city precision: primary
query "{city}, {county} County, Wyoming", falling back to "{city}, Wyoming",
with geocode_status uniformly "city_center" ("ok" is reserved for a resolved
street address). The disclosed street addresses are retained in the "address"
field for reference but are NOT used for the coordinates. Self-throttled to
<=1 request/second with an identifying User-Agent per Nominatim's usage
policy. A deterministic CITY_COORDS fallback (OpenStreetMap city-center place
nodes, the same OSM data Nominatim serves) is used when the live lookup fails
(e.g. the HTTP 429 block this environment hit during the 2026-08-16 pilot
builds), so a re-run stays reproducible without a cache file.
"""

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "wy_program_activity.json"

SOURCE_URL = ("https://www.wyomingcda.com/wp-content/uploads/2025/12/"
              "Final_2025_WebPages_AR_WCDA.pdf")
SOURCE_FILE = ("Final_2025_WebPages_AR_WCDA.pdf (WCDA 2025 Annual Report, "
               "50th anniversary edition)")
RETRIEVED = "2026-08-16"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
GEOCODER_USER_AGENT = "us-hfa-data-map/1.0 (github.com/MD-ai-fin/us-hfa-data-map)"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                 "note_key": "wyFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data (WCDA 2025 Annual Report, 50th anniversary edition).
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "homeownership",
        "unit_type": "households",
        # "713 LOW-TO-MODERATE INCOME FAMILIES ACHIEVED HOMEOWNERSHIP" (p.10).
        # The page's "566 COMPLETED HOMEBUYER EDUCATION" is an outreach metric,
        # not housing production, and is not modeled.
        "fy2025_actual": 713,
        "fy2025_source_quote": (
            "\"713 LOW-TO-MODERATE INCOME FAMILIES ACHIEVED HOMEOWNERSHIP. 566 "
            "COMPLETED HOMEBUYER EDUCATION.\" (WCDA 2025 Annual Report, "
            "\"Accomplishments 2024-2025\", PDF p.10). The 713-family figure is "
            "the FY2025 single-family homeownership KPI; the 566 figure is an "
            "outreach/training count (not housing production) and is quoted here "
            "for completeness only. The report does not disclose a total dollar "
            "figure for the 713 families. The EDGE program is a NEW single-family "
            "loan product launched in FY2025: \"We launched the EDGE program, a "
            "new initiative that makes homeownership accessible by allowing more "
            "borrowers to qualify based on expanded income limits and fewer "
            "purchase price constraints. In its first year alone, WCDA financed "
            "more than $26.6 million in EDGE loans...\" (PDF p.4). EDGE is a "
            "SUBSET of the 713 families (the report does not say how many of the "
            "713 were EDGE loans), so the $26.6M is modeled as the edge "
            "subprogram's amount with units=None -- NOT as the 713-families "
            "total, which the report never states. additive=False because edge is "
            "nested inside single_family, not a partition."
        ),
        "fy2025_amounts": [],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "single_family", "fy2025_units": 713, "fy2025_amount": None,
             "color_group": "bond",
             # ACFR Note 2 "Single Family Program Funds" (1994 Indenture):
             # single-family MRB lending is WCDA's own enterprise fund.
             "fund_type": "proprietary",
             "fund_name": "Single Family Program Funds (Housing Revenue Bonds 1994 Indenture)",
             "fy2026": _FY26_PENDING},
            {"key": "edge", "fy2025_units": None, "fy2025_amount": 26600000,
             "color_group": "bond",
             # EDGE is a single-family loan product of the same enterprise fund;
             # count of the 713 that were EDGE loans is not disclosed.
             "fund_type": "proprietary",
             "fund_name": "Single Family Program Funds (Housing Revenue Bonds 1994 Indenture) — EDGE product",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "multifamily_development",
        "unit_type": "units",
        # "Of the 48 units placed in service in 2025" (p.15) -- the report's
        # own production KPI. This is the PLACED-IN-SERVICE cohort only (the
        # two p.16 projects); the 4 p.17 projects are a separate AWARDED
        # cohort (112 more units) that is listed in the projects array but not
        # folded into this headline.
        "fy2025_actual": 48,
        "fy2025_source_quote": (
            "\"Of the 48 units placed in service in 2025: 8% [Allocated to "
            "tenants earning up to 30% AMI]; 33% [up to 30.1-50% AMI]; 58% [up "
            "to 50.1-60% AMI]; 50% [Percentage of the units to be located in "
            "rural areas].\" (WCDA 2025 Annual Report, \"Housing & Neighborhood "
            "Development Update\", PDF p.15). The 48 placed-in-service units map "
            "to the two \"Housing Development\" cards on PDF p.16 -- Parker Flats "
            "Sheridan (24 units, \"LHTC ALLOCATION: $405,605\", 9%) and Pioneer "
            "Village II (24 units, \"LHTC ALLOCATION: $915,000\", 9%) -- whose "
            "LIHTC allocations sum to $1,320,605. The report's OTHER cohort, "
            "\"Multi-Family Projects Awarded\" (PDF p.17), lists 4 further "
            "developments AWARDED in FY2025 but not yet placed in service: "
            "Pioneer III (24, Cody), McKinney Crossing (24, Buffalo), Cathy "
            "Garden (40-unit rehabilitation, Rawlins) and Meadowlark Place (24, "
            "Powell) -- 112 additional units with NO dollar amounts disclosed. "
            "These 6 developments total 160 units (48 placed in service + 112 "
            "awarded); the two cohorts are disclosed separately (see the "
            "projects array's \"cohort\" field), not force-fit into one number. "
            "HOME is a co-funding source on every project (p.16 \"OTHER WCDA "
            "FINANCING: HOME/NHTF\" and \"HOME\"; p.17 \"Award includes 9% tax "
            "credits and HOME funding\"), but no HOME dollar or unit amount is "
            "disclosed anywhere in the report, so the home subprogram carries "
            "no figures. The AMI/rural breakdowns are KPI-level only (no "
            "per-project split disclosed). additive=False: HOME overlaps LIHTC, "
            "and the placed-in-service/awarded split is not a unit partition."
        ),
        "fy2025_amounts": [],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "lihtc", "fy2025_units": 48, "fy2025_amount": 1320605,
             "color_group": "credit",
             # 9% federal LIHTC -- allocated to developers/investors, never a
             # WCDA asset. $1,320,605 = $405,605 + $915,000 (the two p.16
             # placed-in-service projects' LIHTC allocations); the 4 awarded
             # projects' LIHTC amounts are not disclosed.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "home", "fy2025_units": None, "fy2025_amount": None,
             "color_group": "trust",
             # ACFR Note 2 "Housing & Neighborhood Development Fund": HOME is a
             # federal pass-through that sits on WCDA's own books (proprietary).
             # No HOME dollar/unit amount is disclosed in the annual report.
             "fund_type": "proprietary",
             "fund_name": "Housing & Neighborhood Development Fund (HOME Investment Partnerships Program)",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# ---------------------------------------------------------------------------
# Multifamily project-level detail. The report presents two cohorts:
#   p.16 "Housing Development" (2 projects, PLACED IN SERVICE, with LIHTC
#       allocations) -- these back the 48-unit headline.
#   p.17 "Multi-Family Projects Awarded" (4 projects, AWARDED, no amounts).
# "cohort" marks each honestly ("placed_in_service" / "awarded"). The source
# gives city for all 6 and a street address for 4; geocoding is city-center
# precision (see module docstring). funding_sources == ["lihtc", "home"] on
# every project (p.16/p.17 state HOME co-funding throughout); source_amounts
# carries only the LIHTC allocation, and only where the source prints one.
# ---------------------------------------------------------------------------

RAW_PROJECTS = [
    {
        "name": "Parker Flats Sheridan",
        "city": "Sheridan",
        "county": "Sheridan",
        "units": 24,
        "cohort": "placed_in_service",
        "funding_sources": ["lihtc", "home"],
        "source_amounts": {"lihtc": 405605},
        "address": "1425 Parker Avenue, Sheridan, Wyoming",
    },
    {
        "name": "Pioneer Village II",
        "city": "Cody",
        "county": "Park",
        "units": 24,
        "cohort": "placed_in_service",
        "funding_sources": ["lihtc", "home"],
        "source_amounts": {"lihtc": 915000},
        "address": "2407 Pioneer Avenue, Cody, Wyoming",
    },
    {
        "name": "Pioneer III",
        "city": "Cody",
        "county": "Park",
        "units": 24,
        "cohort": "awarded",
        "funding_sources": ["lihtc", "home"],
        "source_amounts": {},
        "address": "2421 Pioneer Avenue, Cody, Wyoming",
    },
    {
        "name": "McKinney Crossing",
        "city": "Buffalo",
        "county": "Johnson",
        "units": 24,
        "cohort": "awarded",
        "funding_sources": ["lihtc", "home"],
        "source_amounts": {},
        "address": None,
    },
    {
        "name": "Cathy Garden",
        "city": "Rawlins",
        "county": "Carbon",
        "units": 40,
        "cohort": "awarded",
        "funding_sources": ["lihtc", "home"],
        "source_amounts": {},
        "address": "548 15th Street, Rawlins, Wyoming",
    },
    {
        "name": "Meadowlark Place",
        "city": "Powell",
        "county": "Park",
        "units": 24,
        "cohort": "awarded",
        "funding_sources": ["lihtc", "home"],
        "source_amounts": {},
        "address": None,
    },
]

# Deterministic city-center fallback coordinates (lat, lon), sourced from
# OpenStreetMap place nodes -- the same OSM data Nominatim serves. Used only
# when the live Nominatim lookup fails (e.g. the HTTP 429 block seen at build
# time); geocode_status stays "city_center" either way.
CITY_COORDS = {
    "Sheridan": (44.7972, -106.9562),
    "Cody": (44.5263, -109.0565),
    "Buffalo": (44.3483, -106.6989),
    "Rawlins": (41.7911, -107.2387),
    "Powell": (44.7538, -108.7574),
}

# Headline constants for the verify gates (transcribed independently).
EXPECTED_HOMEOWNERSHIP = 713
EXPECTED_EDGE_AMOUNT = 26600000
EXPECTED_PLACED_IN_SERVICE = 48
EXPECTED_LIHTC_ALLOCATION = 1320605  # $405,605 + $915,000
EXPECTED_PROJECT_COUNT = 6
EXPECTED_AWARDED_UNITS = 112          # 24 + 24 + 40 + 24
EXPECTED_TOTAL_UNITS = 160            # 48 placed in service + 112 awarded


def verify_category_consistency():
    errors = []
    warnings = []

    # homeownership: single_family carries the full 713 cohort (no total
    # dollar disclosed); edge is a nested subset ($26.6M, count not disclosed).
    ho = next(c for c in CATEGORIES if c["key"] == "homeownership")
    sf = next(sp for sp in ho["subprograms"] if sp["key"] == "single_family")
    edge = next(sp for sp in ho["subprograms"] if sp["key"] == "edge")
    if sf["fy2025_units"] != EXPECTED_HOMEOWNERSHIP:
        errors.append(f"homeownership: single_family units {sf['fy2025_units']} "
                      f"!= headline {EXPECTED_HOMEOWNERSHIP}")
    if edge["fy2025_amount"] != EXPECTED_EDGE_AMOUNT:
        errors.append(f"homeownership: edge amount {edge['fy2025_amount']} "
                      f"!= ${EXPECTED_EDGE_AMOUNT:,}")
    if edge["fy2025_units"] is not None:
        errors.append("homeownership: edge units must be None (count of the 713 "
                      "that were EDGE loans is not disclosed)")
    if ho["additive"]:
        errors.append("homeownership: must be additive=False (edge is nested, "
                      "not a partition)")

    # multifamily_development: lihtc = the 48 placed-in-service units / the
    # summed LIHTC allocation; home = co-funding with no disclosed figures.
    mf = next(c for c in CATEGORIES if c["key"] == "multifamily_development")
    lihtc = next(sp for sp in mf["subprograms"] if sp["key"] == "lihtc")
    home = next(sp for sp in mf["subprograms"] if sp["key"] == "home")
    if lihtc["fy2025_units"] != EXPECTED_PLACED_IN_SERVICE:
        errors.append(f"multifamily_development: lihtc units {lihtc['fy2025_units']} "
                      f"!= {EXPECTED_PLACED_IN_SERVICE} (placed in service)")
    if lihtc["fy2025_amount"] != EXPECTED_LIHTC_ALLOCATION:
        errors.append(f"multifamily_development: lihtc amount ${lihtc['fy2025_amount']:,} "
                      f"!= ${EXPECTED_LIHTC_ALLOCATION:,} ($405,605 + $915,000)")
    if home["fy2025_units"] is not None or home["fy2025_amount"] is not None:
        errors.append("multifamily_development: home units/amount must be None "
                      "(no HOME figures disclosed)")
    if mf["additive"]:
        errors.append("multifamily_development: must be additive=False (HOME "
                      "overlaps LIHTC; two-cohort split)")

    # No category should fall back to the generic 📊 icon in program_activity.js.
    for c in CATEGORIES:
        key = c["key"]
        if not re.search(r"homeown|homebuyer|single_family|downpayment|sonyma|covenant", key) \
           and not re.search(r"multifamily|rental|units_completed|placed_in_service|build_for|neighborhood|housing_solutions", key):
            warnings.append(f"category key {key!r} matches no known icon bucket "
                            "(would fall back to 📊)")

    if errors:
        raise SystemExit("Category consistency mismatch(es):\n" + "\n".join(errors))
    for w in warnings:
        print(f"WARNING: {w}")
    print("Category verification passed: homeownership 713 (single_family) + "
          "EDGE $26.6M subset; multifamily_development 48 placed in service / "
          "$1,320,605 LIHTC + HOME co-funding (no figures).")


def verify_projects():
    errors = []

    if len(RAW_PROJECTS) != EXPECTED_PROJECT_COUNT:
        errors.append(f"project count: expected {EXPECTED_PROJECT_COUNT}, got {len(RAW_PROJECTS)}")
    names = [p["name"] for p in RAW_PROJECTS]
    if len(set(names)) != len(names):
        errors.append("duplicate project name(s) in RAW_PROJECTS")

    placed = [p for p in RAW_PROJECTS if p["cohort"] == "placed_in_service"]
    awarded = [p for p in RAW_PROJECTS if p["cohort"] == "awarded"]
    if len(placed) != 2 or len(awarded) != 4:
        errors.append(f"cohort split: expected 2 placed_in_service + 4 awarded, "
                      f"got {len(placed)} + {len(awarded)}")

    placed_units = sum(p["units"] for p in placed)
    awarded_units = sum(p["units"] for p in awarded)
    if placed_units != EXPECTED_PLACED_IN_SERVICE:
        errors.append(f"placed-in-service units sum: expected {EXPECTED_PLACED_IN_SERVICE}, "
                      f"got {placed_units}")
    if awarded_units != EXPECTED_AWARDED_UNITS:
        errors.append(f"awarded units sum: expected {EXPECTED_AWARDED_UNITS}, got {awarded_units}")
    if placed_units + awarded_units != EXPECTED_TOTAL_UNITS:
        errors.append(f"total units: expected {EXPECTED_TOTAL_UNITS}, got {placed_units + awarded_units}")

    for p in RAW_PROJECTS:
        if p["funding_sources"] != ["lihtc", "home"]:
            errors.append(f"{p['name']}: funding_sources must be ['lihtc', 'home'] "
                          f"(p.16/p.17 state 9% LIHTC + HOME co-funding), got {p['funding_sources']}")
        for s in p["source_amounts"]:
            if s != "lihtc":
                errors.append(f"{p['name']}: unexpected source_amount key {s!r} "
                              "(only LIHTC amounts are disclosed)")
        if p["cohort"] == "awarded" and p["source_amounts"]:
            errors.append(f"{p['name']}: awarded projects have no disclosed amounts, "
                          f"got {p['source_amounts']}")
        if p["cohort"] == "placed_in_service" and "lihtc" not in p["source_amounts"]:
            errors.append(f"{p['name']}: placed-in-service project missing its LIHTC amount")

    lihtc_sum = sum(p["source_amounts"].get("lihtc", 0) for p in RAW_PROJECTS)
    if lihtc_sum != EXPECTED_LIHTC_ALLOCATION:
        errors.append(f"LIHTC allocation sum: expected ${EXPECTED_LIHTC_ALLOCATION:,}, "
                      f"got ${lihtc_sum:,}")

    if errors:
        raise SystemExit("Project transcription mismatch(es):\n" + "\n".join(errors))

    print(f"Project verification passed: {len(RAW_PROJECTS)} projects, "
          f"{placed_units} placed in service + {awarded_units} awarded = "
          f"{placed_units + awarded_units} total units; LIHTC allocations sum to "
          f"${lihtc_sum:,}.")


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def geocode(query, cache, city=None):
    if query in cache:
        return cache[query]
    params = urllib.parse.urlencode({"q": query, "format": "json", "limit": 1})
    url = f"{NOMINATIM_URL}?{params}"
    result = None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": GEOCODER_USER_AGENT})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.load(resp)
        if data:
            result = (float(data[0]["lat"]), float(data[0]["lon"]))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError,
            KeyError, ValueError, IndexError) as exc:
        if not (isinstance(exc, urllib.error.HTTPError) and exc.code == 429):
            print(f"  geocode failed for {query!r}: {exc}")
    if result is None and city and city in CITY_COORDS:
        result = CITY_COORDS[city]  # deterministic OSM city-center fallback
    cache[query] = result
    time.sleep(1.0)  # Nominatim usage policy: max 1 request/second
    return result


def build_projects():
    cache = {}
    projects = []
    for p in RAW_PROJECTS:
        coords = geocode(f"{p['city']}, {p['county']} County, Wyoming", cache,
                         city=p["city"])
        if coords is None:
            coords = geocode(f"{p['city']}, Wyoming", cache, city=p["city"])
        # City-level source precision -> honest "city_center", never "ok"
        # (which would over-claim street accuracy the source does not warrant
        # for these new-construction developments).
        status = "city_center" if coords else "unresolved"
        projects.append({
            "id": slugify(p["name"]),
            "name": p["name"],
            "address": p["address"],
            "city": p["city"],
            "lat": round(coords[0], 5) if coords else None,
            "lon": round(coords[1], 5) if coords else None,
            "units": p["units"],
            "cohort": p["cohort"],
            "funding_sources": p["funding_sources"],
            "source_amounts": p["source_amounts"],
            "total_amount": sum(p["source_amounts"].values()) if p["source_amounts"] else None,
            "primary_color_group": "credit",  # funding_sources[0] == "lihtc"
            "overlaps": len(p["funding_sources"]) > 1,
            "geocode_status": status,
        })
    return projects


def main():
    verify_category_consistency()
    verify_projects()
    print("Geocoding project cities via Nominatim (city-center precision)...")
    projects = build_projects()
    unresolved = [p["name"] for p in projects if p["geocode_status"] == "unresolved"]
    if unresolved:
        print(f"  {len(unresolved)} project(s) could not be geocoded: {unresolved}")
    placed = [p for p in projects if p["cohort"] == "placed_in_service"]
    awarded = [p for p in projects if p["cohort"] == "awarded"]
    print(f"  Cohorts: {len(placed)} placed_in_service / {len(awarded)} awarded.")

    payload = {
        "WY": {
            "hfa_name": "Wyoming Community Development Authority",
            "hfa_abbr": "WCDA",
            "fiscal_year": "FY2025",
            "source_title": "WCDA 2025 Annual Report (50th anniversary edition) — "
                            "Homeownership & Lender Partnerships and Housing "
                            "Development sections",
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
