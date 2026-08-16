"""
Builds docs/ri_program_activity.json from RIHousing's "2026 Report on
RIHousing Development Activity and 8% Tax" (covering CY2025), plus
RIHousing's own audited financial statements (for GASB fund-type
classification).

Source (CY2025 = calendar year January 1 - December 31, 2025)
------------------------------------------------------------------------
1. "2026 Report on RIHousing Development Activity and 8% Tax"
     https://www.rihousing.com/wp-content/uploads/2026/03/2026-8-Percent-Report-Final.pdf
   Local copy: FY2025/program_activity/pdf/RI_RIHousing_8PercentReport_CY2025.pdf
   The report's TWO development tables ("RIHousing Financed Developments
   Closed in 2025" and "RIHousing Financed Developments Placed in Service
   in 2025") are the source of every number below.

2. RIHousing's audited financial statements (used ONLY for fund-type
   classification): FY2024/pdf/RI_RIHousing_FY2024_ACFR.pdf. NOTE the
   filename is misleading -- despite "FY2024" it is actually "FINANCIAL
   STATEMENTS AND SUPPLEMENTARY INFORMATION, YEARS ENDED JUNE 30, 2025 AND
   2024" (64 pages), i.e. RIHousing's FY2025 audited statements. There is
   no FY2025/txt/RI_*.txt in the corpus (RI is one of the 6 no-txt
   jurisdictions), and no FY2025/pdf/RI_*.pdf either; this FY2024-named
   PDF is the correct, most recent audited statement available.

IMPORTANT title-year trap (explicitly flagged in the task brief)
------------------------------------------------------------------------
RIHousing's "2025 Report" is CY2024 data; its "2026 Report" is CY2025 data.
This build uses the **2026** edition (uploaded 2026/03), whose own prose
says "In 2025, RIHousing provided financing ... 20 developments, containing
1,183 units". fiscal_year is recorded honestly as "CY2025" (RIHousing's
development-activity reporting is calendar-year; its audited statements are
June-30 fiscal-year, but the 8% report's development tables are CY).

What is (and is not) included
------------------------------------------------------------------------
Two macro categories, both unit-counted (not households), both with the
report's own printed totals:

  1. multifamily_financed  -- 1,183 units / 20 developments / $429.1M total
     development cost / $254.6M RIHousing resources invested, split
     additively into new_production (871 units, 16 projects) vs
     preservation (312 units, 4 projects). This is the table the bubble map
     is built from (the "Financed Developments Closed in 2025" list has
     name + municipality + units + deed-restricted + cost + RIH resources
     per project).

  2. placed_in_service     -- 1,119 units / 20 developments / $351.1M total
     development cost, split additively into rental (1,101) vs
     homeownership (18). (The source prints a "Grand Total" row for this
     table; the rental/homeownership unit split is the report's own prose
     "1101 rental units, and 18 homeownership units".)

The report's population breakdowns are recorded in the source quotes but are
NOT modeled as additive subprograms, because they sit on a different axis
and (in the financed table) do not sum to the headline total:
  - financed table: "665 families / 118 elderly-disabled / 106 mixed" are
    DEED-RESTRICTED units (665+118+106 = 889, plus East Point's 12
    deed-restricted-but-100%-AMI units = 901 deed-restricted total), not a
    partition of the 1,183 total units. Verified: family deed-restricted
    units sum to 677; the report's "665" is exactly 677 - East Point's 12
    units (footnote 2: those 12 are deed-restricted at 100% AMI for
    middle-income families, above the law's 80%-AMI "affordable"
    threshold). Elderly (36+82=118) and Mixed Use (35+71=106) are the
    table's total-unit values (which equal deed-restricted for those rows).
  - placed-in-service table: "595 families / 348 elderly / 176 special
    needs" DO partition the 1,119 placed-in-service units (595+348+176 =
    1,119), but they are a population-served axis, orthogonal to the
    rental/homeownership split the report itself headlines -- so they stay
    in the quote, not the subprograms.

The report's THIRD table -- "8% Tax Revenue Collected in FY 2025 by
Municipality" ($19,210,781.20 total) -- is deliberately EXCLUDED: it is
municipal tax revenue collected by cities/towns (pursuant to RIGL
44-5-13.11) and reported TO RIHousing, not a RIHousing program output; it
discloses no unit/household count; and it is measured on a fiscal-year
(FY2025) basis while the two development tables are calendar-year. Per the
project's "dollars without a paired unit count are not a KPI" rule it would
at most be a dollar chip, and its subject matter (a municipal tax) falls
outside "program activity" entirely.

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
Cross-referenced against RIHousing's FY2025 audited statements
(FY2024/pdf/RI_RIHousing_FY2024_ACFR.pdf), which report:
  - "The Corporation engages only in business-type activities" (MD&A,
    printed p.5).
  - Three proprietary/business-type funds on the Combining Statement of Net
    Position (printed pp.12-13): Operating Fund, Single-Family Fund, and
    Multi-Family Fund. The Multi-Family Fund carries "Loans Receivable
    $426,219,984" and "Bonds and Notes Payable $390,438,333" at June 30,
    2025 -- RIHousing's multifamily development lending. The Single-Family
    Fund carries the single-family mortgage program (Loans Receivable
    $324,606,743).
  - One discretely-presented fiduciary component unit: the Affordable
    Housing Trust Fund (a private-purpose trust, printed p.5).
  - NO governmental funds, and NO reference anywhere in the 64 pages to
    "low-income", "tax credit", "LIHTC", or "Building Homes" (verified by
    full-text search -- zero occurrences). Federal LIHTC credits flow
    directly to developers/investors and are never booked as a RIHousing
    asset, so they are off-balance-sheet in the same sense PA/IL document.
    The 8% report's title "8% Tax" refers to the municipal 8%-of-rent tax
    (RIGL 44-5-13.11), NOT the 8%/9% LIHTC credit, and the report does not
    disclose any per-project LIHTC allocation -- so no off_balance_sheet
    subprogram is invented.

Classification (confidence: high -- names match the ACFR's combining
statement verbatim):
  - new_production / preservation -> "proprietary", fund_name
    "Multi-Family Fund" (RIHousing's own multifamily mortgage products,
    financed per MD&A p.10 by "$114.4 million of multi-family bonds" issued
    during 2025). The report's footnote 1 confirms "RIH Resources
    Invested" = "Funds awarded and administered by RIHousing, including our
    mortgage products."
  - rental -> "proprietary", fund_name "Multi-Family Fund" (same as above).
  - homeownership -> "proprietary", fund_name "Single-Family Fund"
    (for-sale homeownership units are RIHousing's single-family lending
    program; confidence: high for fund placement, medium for the exact
    unit-to-fund mapping since the 8% report does not name the fund).

Verification gates (dual)
------------------------------------------------------------------------
Internal (reproduce the report's own printed totals):
  - Financed table: 20 rows transcribed; column sums must equal the
    printed footer "$429,126,324.71 / 1,183 / 901 / $254,554,721.68", and
    the new/preservation split must be 871 (16) / 312 (4) with cost
    $308,999,819.59 + $120,126,505.12 = $429,126,324.71.
  - Placed-in-service table: 20 rows transcribed (verification-only, not
    surfaced as projects); column sums must equal the printed "Grand Total"
    "1177 / 32 / $351,080,164 / 1209 / 1014 / 1119".
External (independent restatement within the same report):
  - The page-1 prose independently states "20 developments ... 1,183 units;
    871 ... new production; 312 ... preservation; 665 ... families; 118 ...
    elderly/disabled; 106 ... mixed" and "1101 rental units, and 18
    homeownership units ... placed in service ... 373 preservation ... 746
    new construction". All are asserted against the transcribed table sums.
    No separate RIHousing press release for CY2025 activity was located;
    the prose-vs-table cross-check is the second gate.

Geocoding
------------------------------------------------------------------------
The source discloses only MUNICIPALITY per development (there is no street
address column; some project names happen to include a street number, e.g.
"23 Central Street", but that is the development's name, not a disclosed
address). Every project is therefore geocoded "{city}, RI" with
geocode_status "city_center" -- honest city-center precision, never "ok".
Self-throttled Nominatim at <=1 request/second with an identifying
User-Agent.

Because the public Nominatim endpoint intermittently rate-limits (HTTP 429)
the shared CI/build IP, the script also carries a small static
CITY_CENTER_FALLBACK table of the 8 Rhode Island municipalities' well-known
center coordinates, used ONLY when a Nominatim query fails. These are
factual municipality-center coordinates (not invented project figures) and
the geocode_status is still "city_center" either way, so precision honesty
is unchanged. When Nominatim is reachable it wins; the fallback only
guarantees a deterministic, byte-identical build.
"""

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "ri_program_activity.json"

SOURCE_URL = ("https://www.rihousing.com/wp-content/uploads/2026/03/"
              "2026-8-Percent-Report-Final.pdf")
SOURCE_FILE = "RI_RIHousing_8PercentReport_CY2025.pdf"
RETRIEVED = "2026-08-16"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
GEOCODER_USER_AGENT = "us-hfa-data-map/1.0 (github.com/MD-ai-fin/us-hfa-data-map)"

# ---------------------------------------------------------------------------
# Category-level data
# ---------------------------------------------------------------------------
_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                 "note_key": "riFy26NotePending"}

CATEGORIES = [
    {
        "key": "multifamily_financed",
        "unit_type": "units",
        "fy2025_actual": 1183,
        "fy2025_source_quote": (
            "\"In 2025, RIHousing provided financing for the development or "
            "preservation of 20 developments, containing 1,183 units. 871 of these "
            "units in 16 projects were new production and 312 units in 4 projects were "
            "preservation. These developments were in 8 different municipalities. Of "
            "these units, 665 will serve families, 118 will serve the elderly/disabled, "
            "and 106 will serve mixed populations.\" (2026 Report, p.1) -- table footer "
            "row: Total Development Cost $429,126,324.71, Units 1,183, Deed Restricted "
            "Units 901, RIH Resources Invested $254,554,721.68. Population note: the "
            "665/118/106 split counts DEED-RESTRICTED units (665 family + 118 elderly + "
            "106 mixed = 889, plus East Point's 12 deed-restricted-but-100%-AMI units = "
            "901), not total units -- see docstring."
        ),
        "fy2025_amounts": [
            {"label_key": "ri_amt_total_dev_cost", "amount": 429126324.71},
            {"label_key": "ri_amt_rih_resources", "amount": 254554721.68},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "new_production", "fy2025_units": 871,
             "fy2025_amount": 308999819.59,
             "color_group": "bond",
             # RIHousing's own multifamily mortgage products, carried in the
             # Multi-Family Fund (business-type/proprietary) -- see docstring.
             "fund_type": "proprietary", "fund_name": "Multi-Family Fund",
             "fy2026": _FY26_PENDING},
            {"key": "preservation", "fy2025_units": 312,
             "fy2025_amount": 120126505.12,
             "color_group": "bond",
             # Same Multi-Family Fund; preservation lending is the same
             # business-type multifamily mortgage activity, not a separate fund.
             "fund_type": "proprietary", "fund_name": "Multi-Family Fund",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "placed_in_service",
        "unit_type": "units",
        "fy2025_actual": 1119,
        "fy2025_source_quote": (
            "\"Also in 2025, 1101 rental units, and 18 homeownership units in 20 "
            "RIHousing financed developments were placed in service. ... 373 "
            "preservation units were placed in service, and 746 new construction units "
            "were placed in service. These developments served a mix of populations "
            "with 595 units serving families, 348 serving the elderly, and 176 serving "
            "special needs populations.\" (2026 Report, p.1) -- table Grand Total row: "
            "Multi-Family Units 1,177, HO Units 32, Total Development Cost "
            "$351,080,164, Total Units 1,209, Deed Restricted Units 1,014, Units PIS "
            "2025 1,119. Note: the $351.1M cost covers the full 1,209-unit cohort, "
            "while the 1,119 headline is the placed-in-service-in-2025 subset (three "
            "projects had partial-year placement)."
        ),
        "fy2025_amounts": [
            {"label_key": "ri_amt_pis_total_cost", "amount": 351080164},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "rental", "fy2025_units": 1101, "fy2025_amount": None,
             "color_group": "bond",
             # Rental (multi-family) placements are Multi-Family Fund lending.
             # Per-project dollar split between rental/homeownership is not
             # disclosed by the report (the $351.1M is a single cohort total),
             # so the subprogram amount is left null rather than apportioned.
             "fund_type": "proprietary", "fund_name": "Multi-Family Fund",
             "fy2026": _FY26_PENDING},
            {"key": "homeownership", "fy2025_units": 18, "fy2025_amount": None,
             "color_group": "bond",
             # For-sale homeownership units are RIHousing's single-family
             # lending program (Single-Family Fund) -- see docstring.
             "fund_type": "proprietary", "fund_name": "Single-Family Fund",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# ---------------------------------------------------------------------------
# Multifamily project-level detail ("RIHousing Financed Developments Closed in
# 2025", p.1). Manually transcribed via pdfplumber table extraction; the
# source gives municipality only (no street address), so address=None and all
# geocoding is city-center.
#   tuple: (name, city, total_units, deed_restricted, building_type,
#           total_dev_cost, rih_resources, population)
# building_type is "New" or "Preservation"; population is Family / Elderly /
# Mixed Use (not surfaced in JSON -- see docstring).
# ---------------------------------------------------------------------------
RAW_PROJECTS = [
    ("23 Central Street", "Central Falls", 12, 12, "New",
     5090575.00, 3743575.00, "Family"),
    ("24 Inkerman Street", "Providence", 3, 3, "New",
     890431.00, 175000.00, "Family"),
    ("42 Washington St Apartments", "Central Falls", 3, 3, "New",
     1284680.00, 284680.00, "Family"),
    ("321 Knight St", "Providence", 41, 41, "New",
     21096194.05, 17924337.05, "Family"),
    ("Broad Street Homes", "Central Falls", 46, 46, "New",
     26651396.00, 24151396.00, "Family"),
    # Source prints the name as "Center City Apartments - 9 %" (a 9%-LIHTC
    # tag, not part of the development name) in East Providence -- verified
    # via character x-positions: "East" sits in the Municipality column, not
    # the name column.
    ("Center City Apartments", "East Providence", 95, 95, "New",
     47476879.00, 30308201.00, "Family"),
    ("Crossroads Health & Housing (371 Pine)", "Providence", 35, 35, "New",
     18880248.00, 4000000.00, "Mixed Use"),
    # footnote 2: 12 of East Point's 50 units are deed-restricted at 100% AMI
    # (middle-income), not "affordable" per R.I. law's 80%-AMI threshold.
    ("East Point", "East Providence", 50, 12, "New",
     13345000.00, 10305000.00, "Family"),
    # footnote 3: Frontline received only Building Homes Rhode Island funding,
    # which RIHousing administers but does not award; RIH resources = $0.
    ("Frontline Childcare Worker Residence", "Woonsocket", 4, 4, "New",
     600000.00, 0.00, "Family"),
    ("The Presley", "Warwick", 190, 38, "New",
     21679501.00, 2295000.00, "Family"),
    ("Jenks Park Residences", "Central Falls", 28, 28, "New",
     1601816.00, 280000.00, "Family"),
    ("Lippitt Mill", "West Warwick", 71, 71, "New",
     23001994.11, 8045479.01, "Mixed Use"),
    ("Omni Newark", "Providence", 52, 52, "New",
     21836351.31, 18117506.31, "Family"),
    ("Park Holm V", "Newport", 45, 45, "New",
     22357666.00, 21048066.00, "Family"),
    ("The Village at Manville", "Lincoln", 72, 72, "New",
     27270809.00, 26572442.00, "Family"),
    ("Walker Lofts", "Lincoln", 124, 32, "New",
     55936279.12, 5700000.00, "Family"),
    ("Hillside Village", "Providence", 42, 42, "Preservation",
     27573644.52, 16808361.25, "Family"),
    ("Mt. Hope Court Apartments", "Providence", 36, 36, "Preservation",
     1855191.00, 1625000.00, "Elderly"),
    ("Pocasset Manor", "Providence", 82, 82, "Preservation",
     33727565.82, 20535801.82, "Elderly"),
    ("Rock Ridge Apartments", "Woonsocket", 152, 152, "Preservation",
     56970103.78, 42634876.24, "Family"),
]

# The report's own printed footer row (p.1) -- used as the internal
# verification target.
FINANCED_TOTALS = {
    "count": 20,
    "units": 1183,
    "deed_restricted": 901,
    "total_dev_cost": 429126324.71,
    "rih_resources": 254554721.68,
}
# new/preservation split (prose + computed column sums).
FINANCED_SPLIT = {
    "new_count": 16, "new_units": 871, "new_cost": 308999819.59,
    "pres_count": 4, "pres_units": 312, "pres_cost": 120126505.12,
}
# Prose population split (p.1) -- the report's own independent restatement.
FINANCED_POPULATION = {"family": 665, "elderly": 118, "mixed": 106}

# ---------------------------------------------------------------------------
# Placed-in-service table (p.2), transcribed VERIFICATION-ONLY (not surfaced
# as projects -- the bubble map uses the "closed" table above).
#   tuple: (name, population, mf_units, ho_units, total_dev_cost,
#           total_units, deed_restricted, pis_units)
# ---------------------------------------------------------------------------
PIS_ROWS = [
    ("Frenchtown I - 9%", "Family", 33, 0, 16013056.00, 33, 26, 33),
    ("Frenchtown II 4%", "Family", 30, 0, 15601528.00, 30, 30, 30),
    ("Millrace District - Residential", "Family", 70, 0, 34537495.00, 70, 55, 70),
    ("Park Holm IV", "Family", 51, 0, 23741345.00, 51, 51, 51),
    ("Tempo - 4%", "Family", 29, 0, 16270005.00, 29, 29, 29),
    ("Tempo - 9%", "Family", 37, 0, 14443562.00, 37, 16, 37),
    ("West House II", "Elderly", 54, 0, 18414148.00, 54, 54, 54),
    ("Looking Upwards", "Family", 12, 0, 5377265.00, 12, 12, 12),
    ("1624 Lonsdale", "Family", 26, 0, 6979964.00, 26, 26, 26),
    ("Summer Street", "Special Needs", 176, 0, 83513392.00, 176, 176, 176),
    ("The Avenue", "Family", 85, 0, 32536761.00, 85, 85, 46),
    ("Rumford Towers", "Elderly", 294, 0, 25572088.00, 294, 294, 294),
    ("Potters Tigrai", "Family", 57, 0, 16789234.00, 57, 57, 20),
    ("Ralph aRusso", "Family", 22, 0, 4093400.00, 22, 22, 22),
    ("The Pier Apartments", "Family", 9, 0, 1247003.00, 9, 9, 9),
    ("Galego Court", "Family", 2, 0, 627624.00, 2, 2, 2),
    ("The Presley", "Family", 190, 0, 21679501.00, 190, 38, 190),
    ("Ivy Place", "Family", 0, 13, 6360690.00, 13, 13, 13),
    ("Cardinal Lane Phase II", "Family", 0, 4, 1281124.00, 4, 4, 4),
    ("Old County Village - Phase II", "Family", 0, 15, 6000979.00, 15, 15, 1),
]

# The report's own printed "Grand Total" row (p.2).
PIS_TOTALS = {
    "count": 20,
    "mf_units": 1177,
    "ho_units": 32,
    "total_dev_cost": 351080164.00,
    "total_units": 1209,
    "deed_restricted": 1014,
    "pis_units": 1119,
}
# Prose split (p.1).
PIS_SPLIT = {"rental": 1101, "homeownership": 18,
             "new_construction": 746, "preservation": 373}
PIS_POPULATION = {"family": 595, "elderly": 348, "special_needs": 176}

FUNDING_COLOR_GROUP = {"new_production": "bond", "preservation": "bond"}
# Priority order for a project's single "primary" color (single-source
# projects, so this is trivial, but kept for parity with other builds).
FUNDING_PRIORITY = ["new_production", "preservation"]

# Static municipality-center coordinates for the 8 RI municipalities named
# in the report, used ONLY when Nominatim is unreachable (see docstring).
# These are widely-published town/city centers; geocode_status remains
# "city_center".
CITY_CENTER_FALLBACK = {
    "Providence": (41.8240, -71.4128),
    "Central Falls": (41.8870, -71.3923),
    "East Providence": (41.8137, -71.3701),
    "Woonsocket": (42.0029, -71.5148),
    "Warwick": (41.7001, -71.4162),
    "West Warwick": (41.6969, -71.5194),
    "Newport": (41.4901, -71.3128),
    "Lincoln": (41.9212, -71.4350),
}


def _money(a, b):
    return round(a, 2) == round(b, 2)


def verify_financed_table():
    errors = []
    if len(RAW_PROJECTS) != FINANCED_TOTALS["count"]:
        errors.append(f"project count: expected {FINANCED_TOTALS['count']}, "
                      f"got {len(RAW_PROJECTS)}")
    units = sum(r[2] for r in RAW_PROJECTS)
    if units != FINANCED_TOTALS["units"]:
        errors.append(f"units: expected {FINANCED_TOTALS['units']}, got {units}")
    deed = sum(r[3] for r in RAW_PROJECTS)
    if deed != FINANCED_TOTALS["deed_restricted"]:
        errors.append(f"deed-restricted: expected {FINANCED_TOTALS['deed_restricted']}, "
                      f"got {deed}")
    cost = sum(r[5] for r in RAW_PROJECTS)
    if not _money(cost, FINANCED_TOTALS["total_dev_cost"]):
        errors.append(f"total dev cost: expected {FINANCED_TOTALS['total_dev_cost']}, "
                      f"got {cost}")
    rih = sum(r[6] for r in RAW_PROJECTS)
    if not _money(rih, FINANCED_TOTALS["rih_resources"]):
        errors.append(f"RIH resources: expected {FINANCED_TOTALS['rih_resources']}, "
                      f"got {rih}")

    new = [r for r in RAW_PROJECTS if r[4] == "New"]
    pres = [r for r in RAW_PROJECTS if r[4] == "Preservation"]
    if len(new) != FINANCED_SPLIT["new_count"]:
        errors.append(f"new count: expected {FINANCED_SPLIT['new_count']}, got {len(new)}")
    if len(pres) != FINANCED_SPLIT["pres_count"]:
        errors.append(f"preservation count: expected {FINANCED_SPLIT['pres_count']}, "
                      f"got {len(pres)}")
    if sum(r[2] for r in new) != FINANCED_SPLIT["new_units"]:
        errors.append(f"new units: expected {FINANCED_SPLIT['new_units']}, "
                      f"got {sum(r[2] for r in new)}")
    if sum(r[2] for r in pres) != FINANCED_SPLIT["pres_units"]:
        errors.append(f"preservation units: expected {FINANCED_SPLIT['pres_units']}, "
                      f"got {sum(r[2] for r in pres)}")
    new_cost = sum(r[5] for r in new)
    pres_cost = sum(r[5] for r in pres)
    if not _money(new_cost, FINANCED_SPLIT["new_cost"]):
        errors.append(f"new cost: expected {FINANCED_SPLIT['new_cost']}, got {new_cost}")
    if not _money(pres_cost, FINANCED_SPLIT["pres_cost"]):
        errors.append(f"preservation cost: expected {FINANCED_SPLIT['pres_cost']}, "
                      f"got {pres_cost}")
    if not _money(new_cost + pres_cost, FINANCED_TOTALS["total_dev_cost"]):
        errors.append("new + preservation cost does not equal printed total")

    # External gate #1: the page-1 prose's population split is a deed-restricted
    # breakdown; "665 families" = family deed-restricted (677) minus East Point's
    # 12 deed-restricted-but-100%-AMI units. Elderly and Mixed are total units
    # (which equal deed-restricted for those rows).
    fam_dr = sum(r[3] for r in RAW_PROJECTS if r[7] == "Family")
    eld = sum(r[3] for r in RAW_PROJECTS if r[7] == "Elderly")
    mixed = sum(r[3] for r in RAW_PROJECTS if r[7] == "Mixed Use")
    if fam_dr - 12 != FINANCED_POPULATION["family"]:
        errors.append(f"family (deed-restricted, ex-East Point): expected "
                      f"{FINANCED_POPULATION['family']}, got {fam_dr - 12}")
    if eld != FINANCED_POPULATION["elderly"]:
        errors.append(f"elderly: expected {FINANCED_POPULATION['elderly']}, got {eld}")
    if mixed != FINANCED_POPULATION["mixed"]:
        errors.append(f"mixed: expected {FINANCED_POPULATION['mixed']}, got {mixed}")

    if errors:
        raise SystemExit("Financed-table verification failed:\n" + "\n".join(errors))
    print("Financed table verified: 20 projects, 1,183 units, $429,126,324.71 cost, "
          "$254,554,721.68 RIH resources; 871 new / 312 preservation; population "
          "split 665/118/106 reproduces the prose (deed-restricted basis).")


def verify_placed_in_service():
    errors = []
    if len(PIS_ROWS) != PIS_TOTALS["count"]:
        errors.append(f"project count: expected {PIS_TOTALS['count']}, got {len(PIS_ROWS)}")
    mf = sum(r[2] for r in PIS_ROWS)
    ho = sum(r[3] for r in PIS_ROWS)
    cost = sum(r[4] for r in PIS_ROWS)
    total_units = sum(r[5] for r in PIS_ROWS)
    deed = sum(r[6] for r in PIS_ROWS)
    pis = sum(r[7] for r in PIS_ROWS)
    if mf != PIS_TOTALS["mf_units"]:
        errors.append(f"MF units: expected {PIS_TOTALS['mf_units']}, got {mf}")
    if ho != PIS_TOTALS["ho_units"]:
        errors.append(f"HO units: expected {PIS_TOTALS['ho_units']}, got {ho}")
    if not _money(cost, PIS_TOTALS["total_dev_cost"]):
        errors.append(f"total dev cost: expected {PIS_TOTALS['total_dev_cost']}, got {cost}")
    if total_units != PIS_TOTALS["total_units"]:
        errors.append(f"total units: expected {PIS_TOTALS['total_units']}, got {total_units}")
    if deed != PIS_TOTALS["deed_restricted"]:
        errors.append(f"deed-restricted: expected {PIS_TOTALS['deed_restricted']}, got {deed}")
    if pis != PIS_TOTALS["pis_units"]:
        errors.append(f"PIS units: expected {PIS_TOTALS['pis_units']}, got {pis}")

    # External gate #2: prose rental/homeownership split (PIS units by HO-vs-MF).
    rental = sum(r[7] for r in PIS_ROWS if r[3] == 0)
    homeown = sum(r[7] for r in PIS_ROWS if r[3] > 0)
    if rental != PIS_SPLIT["rental"]:
        errors.append(f"rental PIS: expected {PIS_SPLIT['rental']}, got {rental}")
    if homeown != PIS_SPLIT["homeownership"]:
        errors.append(f"homeownership PIS: expected {PIS_SPLIT['homeownership']}, "
                      f"got {homeown}")

    # External gate #3: prose population split (595/348/176) partitions 1,119.
    fam = sum(r[7] for r in PIS_ROWS if r[1] == "Family")
    eld = sum(r[7] for r in PIS_ROWS if r[1] == "Elderly")
    sn = sum(r[7] for r in PIS_ROWS if r[1] == "Special Needs")
    if fam != PIS_POPULATION["family"]:
        errors.append(f"family PIS: expected {PIS_POPULATION['family']}, got {fam}")
    if eld != PIS_POPULATION["elderly"]:
        errors.append(f"elderly PIS: expected {PIS_POPULATION['elderly']}, got {eld}")
    if sn != PIS_POPULATION["special_needs"]:
        errors.append(f"special-needs PIS: expected {PIS_POPULATION['special_needs']}, "
                      f"got {sn}")
    if fam + eld + sn != PIS_TOTALS["pis_units"]:
        errors.append("population split does not sum to 1,119")

    if errors:
        raise SystemExit("Placed-in-service verification failed:\n" + "\n".join(errors))
    print("Placed-in-service table verified: 20 projects, 1,119 PIS units "
          "(1,101 rental / 18 homeownership), $351,080,164 cost, population "
          "595/348/176.")


def geocode(query, cache):
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
        print(f"  geocode failed for {query!r}: {exc}")
    cache[query] = result
    time.sleep(1.0)  # Nominatim usage policy: max 1 request/second
    return result


def slug(name):
    s = name.lower()
    s = s.replace("&", "and").replace("%", "")
    s = s.replace("(", "").replace(")", "").replace("'", "").replace(".", "")
    s = s.replace("/", "-")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def build_projects():
    cache = {}
    projects = []
    for name, city, units, _deed, btype, cost, _rih, _pop in RAW_PROJECTS:
        sub = "new_production" if btype == "New" else "preservation"
        coords = geocode(f"{city}, RI", cache)
        if coords is None:
            coords = CITY_CENTER_FALLBACK.get(city)
        status = "city_center" if coords else "unresolved"
        projects.append({
            "id": slug(name),
            "name": name,
            "address": None,  # source gives municipality only, no street address
            "city": city,
            "lat": round(coords[0], 5) if coords else None,
            "lon": round(coords[1], 5) if coords else None,
            "units": units,
            "funding_sources": [sub],
            "source_amounts": {sub: cost},
            "total_amount": cost,
            "primary_color_group": FUNDING_COLOR_GROUP[sub],
            "overlaps": False,
            "geocode_status": status,
        })
    return projects


def main():
    verify_financed_table()
    verify_placed_in_service()
    print("Geocoding project municipalities via Nominatim...")
    projects = build_projects()
    unresolved = [p["name"] for p in projects if p["geocode_status"] == "unresolved"]
    if unresolved:
        print(f"  {len(unresolved)} project(s) could not be geocoded: {unresolved}")
    city_center = [p["name"] for p in projects if p["geocode_status"] == "city_center"]
    if city_center:
        print(f"  {len(city_center)} project(s) geocoded at city-center precision "
              f"(source discloses municipality only).")

    payload = {
        "RI": {
            "hfa_name": "Rhode Island Housing and Mortgage Finance Corporation",
            "hfa_abbr": "RIHousing",
            "fiscal_year": "CY2025",
            "source_title": "2026 Report on RIHousing Development Activity and 8% Tax",
            "source_url": SOURCE_URL,
            "source_file": SOURCE_FILE,
            "retrieved": RETRIEVED,
            "categories": CATEGORIES,
            "projects": projects,
        }
    }
    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    print(f"Wrote {OUT_PATH} ({len(projects)} projects, {len(CATEGORIES)} categories)")


if __name__ == "__main__":
    main()
