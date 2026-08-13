"""
Builds docs/pa_program_activity.json from PHFA's FY2025 Annual Report data
tables (annualreport.phfa.org/2025-report/) plus its own FY2025 audited
financial statements (for GASB fund-type classification).

Sources (all FY2025 = PHFA's fiscal year July 1, 2024 - June 30, 2025)
------------------------------------------------------------------------
1. Homeownership - 2025 Fiscal Year (county-by-county first-mortgage +
   assistance-loan table):
     https://annualreport.phfa.org/wp-content/uploads/2026/03/Homeownership-2025-Fiscal-Year.pdf
   Local copy: FY2025/program_activity/pdf/PA_PHFA_Homeownership_FY2025.pdf
2. HEMAP Loans - 2025 Fiscal Year (county-by-county foreclosure-prevention
   loan table):
     https://annualreport.phfa.org/wp-content/uploads/2026/03/HEMAP-Loans-2025-Fiscal-Year-FINAL.pdf
   Local copy: FY2025/program_activity/pdf/PA_PHFA_HEMAP_FY2025.pdf
3. PHARE Fund - 2025 Fiscal Year (county-by-county Realty Transfer Tax /
   Marcellus Shale funding table):
     https://annualreport.phfa.org/wp-content/uploads/2026/03/2025-PHARE-Funding-by-County.pdf
   Local copy: FY2025/program_activity/pdf/PA_PHFA_PHARE_FY2025.pdf
4. "Pennsylvania Housing Finance Agency 2024 Low Income Housing Tax Credit,
   PennHOMES, National Housing Trust Fund and PA Housing Tax Credit Awards"
   (dated October 9, 2025 -- the per-development multifamily award list,
   PHFA's own "Map Doc" used for its interactive award map):
     https://annualreport.phfa.org/wp-content/uploads/2026/03/2025-Final-Map-Doc-for-PPOS.pdf
   Local copy: FY2025/program_activity/pdf/PA_PHFA_MapDoc_FY2025.pdf
5. PHFA's own separately-issued FY2025 audited financial statements (used
   ONLY for fund-type classification, see below):
     https://www.phfa.org/forms/financial_reports/annual/current/2025-06-30-phfa-audited-financial-statements.pdf
   Local copy: FY2025/pdf/PA_PHFA_FY2025_ACFR.pdf

None of documents 1-4 is a narrative report like IHDA's Report of
Activities -- each is a bare data table (title, column headers, county
rows, a TOTALS/Grand Total row) with no surrounding prose and, unlike
IHDA's report, NO FY2026 projections anywhere. Every fy2026 field below is
therefore {value: None, amount: None, closed: False,
note_key: "paFy26NotePending"} -- PHFA's FY2025 annual-report tables simply
do not disclose a forward-looking figure, so none is invented.

IMPORTANT data-provenance note on the checked-in ACFR text
------------------------------------------------------------------------
FY2025/txt/PA_PHFA_FY2025_ACFR.txt (the file this build's task briefing
pointed at) is NOT PHFA's own financial statements -- it is a text dump of
the Commonwealth of Pennsylvania's statewide ACFR (in which PHFA appears
only as a two-paragraph discretely-presented component-unit summary with
no fund-level detail). The correctly-scoped source is the *PDF*
FY2025/pdf/PA_PHFA_FY2025_ACFR.pdf (89 pages, "PENNSYLVANIA HOUSING FINANCE
AGENCY Basic Financial Statements and Supplementary Information, June 30,
2025 and 2024"), which this script's docstring cites by page number below.
The .txt/.pdf mismatch under FY2025/txt/ appears to be a pre-existing
extraction-pipeline bug (the FY2024 files have the identical mismatch:
PA_PHFA_FY2024_ACFR.pdf is the 298-page Commonwealth-wide report, while
PA_2024-06-30-phfa-audited-financial-statements.pdf is the real PHFA-only
one) -- flagged here for awareness, not fixed by this script.

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
Unlike IHDA (which reports 7 major governmental funds + 4 major
proprietary funds + 14 nonmajor governmental funds), PHFA's own financial
statements report ONLY business-type activities: "For financial reporting
purposes, the Agency is considered a special-purpose government engaged in
business-type activities" (Note 2, "Basis of Accounting", p.24) plus a
separate, immaterial-to-this-file fiduciary activity (the employees'
retirement plan). PHFA has no governmental funds of its own. Note 2's
"Description of Programs" (pp.24-25) names 5 internal management
designations under that single business-type umbrella: General Activities,
Multifamily Housing Program, Single Family Mortgage Loan Program, Insurance
Program, and HEMAP.
  - "proprietary": an activity that PHFA's own MD&A/Notes confirm is
    carried inside one of its 5 named business-type programs:
      * Homeownership's base "Purchased Loans" + the K-FIT and Advantage
        down-payment/closing-cost assistance loans -> the "Single Family
        Mortgage Loan Program" (MD&A "Designated Net Position" table,
        p.15, lists a "Closing Cost Assistance" designation of $3.0M under
        this program, and p.11 separately describes "amortization of down
        payment assistance loans which are forgiven over a period of
        time" as a Single Family Program cost -- this matches K-FIT's
        forgivable-in-ten-years structure. PHFA's ACFR never uses the
        brand names "K-FIT"/"Advantage" verbatim, so this match is by
        program description, not literal name -- confidence: medium.)
      * The Multifamily category's PennHOMES-funded amounts -> the
        "Multifamily Housing Program" (MD&A p.15 lists a "Penn HOMES
        Program to lower development costs for apartments" designation of
        $10.0M under this exact program -- confidence: high, near-verbatim
        name match, only differing by a space: "Penn HOMES" vs
        "PennHOMES").
      * HEMAP loans -> HEMAP itself is explicitly one of the 5 named
        programs and Note 2 states HEMAP's revenues "are reported as a
        component of Program Income and Fees within the Agency's
        financial statements" (p.25) -- i.e. inside PHFA's own
        business-type activities. Confidence: high.
  - "off_balance_sheet": confirmed NOT to appear anywhere by name in
    PHFA's own 89-page financial statements (checked via full-text search
    for "PHARE", "Realty Transfer Tax", "Marcellus", "LIHTC", "Low-Income
    Housing Tax Credit", "PHTC", "PA Housing Tax Credit", "National
    Housing Trust Fund", "NHTF", "PENNVEST", "Health for Harrisburg" --
    zero matches for all of them except the one "Penn HOMES" hit above).
    This matches the same off_balance_sheet logic IHDA's build script
    documents for LIHTC/IAHTC: PHFA administers the award/allocation
    (multifamily federal/state tax credits go directly to developers and
    their investors; PHARE's Realty Transfer Tax and Marcellus Shale
    drilling-impact-fee revenue is Commonwealth money PHFA merely
    distributes to county/regional/statewide grantees; PENNVEST is a
    wholly separate Commonwealth authority -- the Pennsylvania
    Infrastructure Investment Authority -- that "teamed with" PHFA and DEP
    on well/septic loans, per PHFA's own program-description page, and
    never appears as a PHFA-carried balance) -- none of this money is ever
    booked as a PHFA fund asset.
Every subprogram below cites the exact page number backing its
classification in its inline comment.

Category-level methodology
------------------------------------------------------------------------
Multifamily (RAW_PROJECTS, Map Doc): the Map Doc's 41 rows carry NO
PDF-printed TOTALS/footer row of their own (unlike the Homeownership/
HEMAP/PHARE tables, which do), so this script verifies its own transcribed
column sums two ways: (1) internal consistency -- resumming
PROJECT_SOURCE_AMOUNTS by funding source must exactly reproduce the
independently-computed column totals in EXPECTED_SOURCE_TOTALS (each of
which was itself computed once, directly off the PDF's own table cells,
via pdfplumber, before any manual transcription happened) and (2) external
consistency -- project count, summed LI (affordable) units, summed total
units, and summed LIHTC dollars are checked against PHFA's own October 9,
2025 press release ("PHFA Announces $66.5 Million in Low-Income Housing
Tax Credits for Affordable Multifamily Developments in Pennsylvania",
PRNewswire release 302580249): "41 new developments will provide an
additional 1,946 rental housing units, including 1,900 affordable units"
and "$66.5 million in low-income housing tax credits". The Multifamily
category's subprograms are NOT additive (additive=False) -- 40 of the 41
projects draw on 2 or more of {PennHOMES, Health for Harrisburg, NHTF,
PHTC, LIHTC} simultaneously (LIHTC alone touches all 41 projects), so a
naive sum of subprogram unit counts would badly over-count actual physical
units -- same reasoning as IHDA's multifamily category.

Homeownership (Homeownership-2025-Fiscal-Year.pdf): the category headline
(6,643 loans / $1,458,750,346.00) is the table's own printed "TOTALS" row
for the "Purchased Loans" (first-mortgage) columns -- used verbatim, not
re-derived. K-FIT, Advantage and PENNVEST are down-payment/closing-cost
*assistance* loans that ride on top of a SUBSET of those 6,643 first
mortgages (a borrower can receive at most one of the three simultaneously
in practice -- PHFA's own program pages describe them as alternative,
not stackable, assistance products), so additive=True is correct for the
three of them *relative to each other*, but their combined count (4,389)
is intentionally smaller than the category headline (6,643) -- most
purchased loans close with no PHFA-sourced second-mortgage assistance at
all (e.g. a buyer using a non-PHFA down payment, or a lender-paid closing
cost credit). This is documented in the category's fy2025_source_quote and
mirrors IHDA's own pattern of a category headline that isn't purely a sum
of its subprograms' own figures.

HEMAP and PHARE: each table's own printed TOTALS ("211" loans /
"$2,758,612.00") and Grand Total ("$66,950,000" Realty Transfer Tax +
"$6,500,000" Marcellus Shale = "$73,450,000", plus separately-printed
"Regional $6,260,000" and "Statewide $2,080,000" line items below the
county rows) are used verbatim -- this script does NOT attempt to
independently re-derive either total by summing the 67 county rows itself,
because pdfplumber's cell extraction of a handful of county rows in the
PHARE table (at minimum "Washington") does not reconcile against that
row's own printed RTT+Marcellus=Total arithmetic (almost certainly a
source-PDF data-entry slip, e.g. Washington's printed Total of $1,012,500
is exactly its RTT column value, not the sum of RTT+Marcellus=$1,962,500)
-- since this script never builds county-level PHARE detail (no
household/unit count is disclosed for PHARE at all -- it is purely a
dollar-allocation program, so no unit count is invented for it, per this
project's "never fabricate a missing number" rule), that per-county
inconsistency doesn't affect anything this script outputs; only the
top-line printed totals are used.

Geocoding
------------------------------------------------------------------------
Same approach as IHDA's build script: Nominatim (OpenStreetMap), primary
query "{street address}, {city}, PA", falling back to "{city}, PA" (and
flagging geocode_status="city_center") when the street-level query fails
or the source table itself only gives "TBD"/"Scattered Sites"/"Multiple
Addresses" for a development's street address. Self-throttled to <=1
request/second with an identifying User-Agent per Nominatim's usage
policy.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "pa_program_activity.json"

SOURCE_URL = "https://annualreport.phfa.org/2025-report/"
SOURCE_FILE = "PA_PHFA_MapDoc_FY2025.pdf (+ 3 companion FY2025 program tables)"
RETRIEVED = "2026-08-12"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
GEOCODER_USER_AGENT = "us-hfa-data-map/1.0 (github.com/MD-ai-fin/us-hfa-data-map)"

# ---------------------------------------------------------------------------
# Category-level data
# ---------------------------------------------------------------------------
# fy2026 uniform shape: {value, amount, closed, note_key} -- see docstring.
_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "paFy26NotePending"}

CATEGORIES = [
    {
        "key": "multifamily_awards",
        "unit_type": "units",
        "fy2025_actual": 1900,
        "fy2025_source_quote": (
            "\"PHFA Announces $66.5 Million in Low-Income Housing Tax Credits for "
            "Affordable Multifamily Developments in Pennsylvania ... The Pennsylvania "
            "Housing Finance Agency has awarded $66.5 million in low-income housing tax "
            "credits to support the construction of 1,900 new and rehabilitated "
            "affordable multifamily housing units statewide ... 41 new developments will "
            "provide an additional 1,946 rental housing units, including 1,900 "
            "affordable units for Pennsylvania residents.\" (PHFA press release, "
            "PRNewswire release 302580249, October 9, 2025) -- cross-checked against "
            "the per-development \"2024 Low Income Housing Tax Credit, PennHOMES, "
            "National Housing Trust Fund and PA Housing Tax Credit Awards\" list (Map "
            "Doc, same date): 41 rows, LI Units column sums to 1,900, Total Units column "
            "sums to 1,946, Federal Tax Credit (LIHTC) column sums to $66,473,105."
        ),
        "fy2025_amounts": [
            {"label_key": "pa_amt_lihtc", "amount": 66473105},
            {"label_key": "pa_amt_pennhomes", "amount": 11114133},
            {"label_key": "pa_amt_nhtf", "amount": 21492957},
            {"label_key": "pa_amt_phtc", "amount": 19000000},
            {"label_key": "pa_amt_hfh", "amount": 1650000},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "lihtc", "fy2025_units": 1946, "fy2025_amount": 66473105,
             "color_group": "credit",
             # Never appears in PHFA's own FY2025 financial statements (checked
             # "LIHTC"/"Low-Income Housing Tax Credit"/"Federal Tax Credit" --
             # zero matches) -- federal tax credits are allocated directly to
             # developers/investors, not booked as a PHFA fund asset.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "phtc", "fy2025_units": 847, "fy2025_amount": 19000000,
             "color_group": "credit",
             # Never appears in PHFA's own FY2025 financial statements
             # (checked "PHTC"/"PA Housing Tax Credit" -- zero matches) --
             # a state tax-credit allocation, same off-balance-sheet logic as
             # LIHTC above.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "pennhomes", "fy2025_units": 264, "fy2025_amount": 11114133,
             "color_group": "trust",
             # PHFA's own MD&A "Designated Net Position" table (p.15) lists a
             # "Penn HOMES Program to lower development costs for apartments"
             # designation of $10.0M under "Multifamily Housing Program" --
             # PHFA's own business-type Multifamily program.
             "fund_type": "proprietary", "fund_name": "Multifamily Housing Program (Penn HOMES designation)",
             "fy2026": _FY26_PENDING},
            {"key": "nhtf", "fy2025_units": 1089, "fy2025_amount": 21492957,
             "color_group": "trust",
             # Never appears in PHFA's own FY2025 financial statements
             # (checked "National Housing Trust Fund"/"NHTF" -- zero matches)
             # -- a federal trust-fund allocation PHFA administers but does
             # not carry as its own fund asset.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "hfh", "fy2025_units": 109, "fy2025_amount": 1650000,
             "color_group": "capital",
             # Never appears in PHFA's own FY2025 financial statements
             # (checked "Health for Harrisburg" -- zero matches).
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "homeownership_loans",
        "unit_type": "households",
        "fy2025_actual": 6643,
        "fy2025_source_quote": (
            "\"Homeownership - 2025 Fiscal Year\" county table, TOTALS row: Total # "
            "Purchased Loans 6,643, Total $ Purchased Loans $1,458,750,346.00, Total # "
            "K-FIT 4,222, Total $ K-FIT $47,813,854.92, Total # Advantage 65, Total $ "
            "Advantage $353,623.00, Total # PENNVEST 102, Total $ PENNVEST $2,374,895.00. "
            "K-FIT/Advantage/PENNVEST are down-payment/closing-cost assistance loans "
            "layered on top of a SUBSET of the 6,643 purchase loans (a homebuyer "
            "receives at most one of the three), not a partition of the full 6,643 -- "
            "most purchase loans close with no PHFA-sourced second-mortgage assistance."
        ),
        "fy2025_amounts": [
            {"label_key": "pa_amt_purchase_loans", "amount": 1458750346},
            {"label_key": "pa_amt_downpayment_assist", "amount": 50542372.92},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "kfit", "fy2025_units": 4222, "fy2025_amount": 47813854.92,
             "color_group": "capital",
             # PHFA's own MD&A "Designated Net Position" table (p.15) lists a
             # "Closing Cost Assistance" designation of $3.0M under "Single
             # Family Mortgage Loan Program"; p.11 separately describes
             # "amortization of down payment assistance loans which are
             # forgiven over a period of time" as a Single Family Program
             # cost (matches K-FIT's forgivable-in-ten-years design). PHFA's
             # ACFR never uses the brand name "K-FIT" verbatim -- match is by
             # program description, confidence: medium.
             "fund_type": "proprietary", "fund_name": "Single Family Mortgage Loan Program (inferred)",
             "fy2026": _FY26_PENDING},
            {"key": "advantage", "fy2025_units": 65, "fy2025_amount": 353623,
             "color_group": "capital",
             # Same Single Family Mortgage Loan Program "Closing Cost
             # Assistance" designation as K-FIT above -- PHFA's ACFR never
             # names "Advantage" verbatim, confidence: medium.
             "fund_type": "proprietary", "fund_name": "Single Family Mortgage Loan Program (inferred)",
             "fy2026": _FY26_PENDING},
            {"key": "pennvest", "fy2025_units": 102, "fy2025_amount": 2374895,
             "color_group": "capital",
             # PENNVEST (the Pennsylvania Infrastructure Investment
             # Authority) is a wholly separate Commonwealth authority that
             # "teamed with" PHFA and the PA Dept. of Environmental
             # Protection on well/septic repair loans; it never appears
             # anywhere in PHFA's own FY2025 financial statements, so the
             # loan funds are treated as off PHFA's own balance sheet.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "hemap_foreclosure_prevention",
        "unit_type": "households",
        "fy2025_actual": 211,
        "fy2025_source_quote": (
            "\"HEMAP Loans - 2025 Fiscal Year\" county table, TOTALS row: 211 loans, "
            "$2,758,612.00 total loan amount, $13,074.00 average loan amount."
        ),
        "fy2025_amounts": [
            {"label_key": "pa_amt_hemap_loans", "amount": 2758612},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "hemap_loans", "fy2025_units": 211, "fy2025_amount": 2758612,
             "color_group": "capital",
             # HEMAP is explicitly one of PHFA's 5 named business-type
             # programs (Note 2, "Description of Programs", p.25): "HEMAP's
             # primary operating revenues ... are reported as a component of
             # Program Income and Fees within the Agency's financial
             # statements" -- i.e. inside PHFA's own business-type
             # (enterprise-style) reporting.
             "fund_type": "proprietary", "fund_name": "HEMAP",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "phare_funding",
        "unit_type": "dollars",
        "fy2025_actual": None,
        "fy2025_source_quote": (
            "\"PHARE Fund - 2025 Fiscal Year\" county table footer rows: Grand Total "
            "Realty Transfer Tax Funding $66,950,000 + Marcellus Shale Funding "
            "$6,500,000 = Total PHARE Funding $73,450,000; plus separately-printed "
            "Regional $6,260,000 and Statewide $2,080,000 allocations (not part of the "
            "county-level Grand Total row). No household/unit count is disclosed for "
            "PHARE anywhere in the source table -- it is purely a dollar-allocation "
            "program, so none is shown here."
        ),
        "fy2025_amounts": [
            {"label_key": "pa_amt_phare_total", "amount": 81790000},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "phare_rtt", "fy2025_units": None, "fy2025_amount": 75290000,
             "color_group": "capital",
             # PHARE (the Pennsylvania Housing Affordable and Rehabilitation
             # Enhancement Fund) is Commonwealth Realty Transfer Tax revenue
             # that PHFA distributes to county/regional/statewide grantees;
             # it never appears anywhere in PHFA's own FY2025 financial
             # statements (checked "PHARE"/"Realty Transfer Tax" -- zero
             # matches), so it is not a PHFA-carried fund balance.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "phare_marcellus", "fy2025_units": None, "fy2025_amount": 6500000,
             "color_group": "capital",
             # Same PHARE fund, its Marcellus Shale (natural-gas drilling
             # impact fee) revenue stream -- never appears in PHFA's own
             # financial statements (checked "Marcellus" -- zero matches).
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
]

# ---------------------------------------------------------------------------
# Multifamily project-level detail ("2024 Low Income Housing Tax Credit,
# PennHOMES, National Housing Trust Fund and PA Housing Tax Credit Awards",
# dated October 9, 2025 -- PHFA's "Map Doc"). Manually transcribed via
# pdfplumber table extraction, one row per development; "units" uses the
# "Total Units" column (the physical development's full size, which for 33
# of 41 rows equals "LI Units" -- the low-income/affordable-unit count --
# but is larger for 8 rows with some market-rate units mixed in).
# ---------------------------------------------------------------------------

# (name, address, city, total_units, [funding source keys])
# address=None marks developments whose own PDF row lists no street address
# (printed "TBD") -- these fall back to city-center geocoding.
RAW_PROJECTS = [
    ("421Seventh Ave Apts", "421 Seventh Avenue", "Pittsburgh", 40,
     ["nhtf", "phtc", "lihtc"]),
    ("Carrick Sr Apts", "2531 Brownsville Road", "Pittsburgh", 52,
     ["nhtf", "phtc", "lihtc"]),
    ("Chartiers Ave. Apts.", "704-708 Chartiers Avenue", "McKees Rocks", 44,
     ["pennhomes", "nhtf", "phtc", "lihtc"]),
    ("Gable Ridge", "8000 Beacon Hill Drive", "Wilkinsburg", 50,
     ["lihtc"]),
    ("HG Blair", "Blair Street at Eliza Street", "Pittsburgh", 46,
     ["nhtf", "phtc", "lihtc"]),
    ("Hill Top Villas", None, "Pittsburgh", 48,
     ["nhtf", "phtc", "lihtc"]),
    ("Riverview Manor", "1500 LeTort Street", "Pittsburgh", 98,
     ["lihtc"]),
    ("Ross Lofts", "100 Ross St.", "Pittsburgh", 46,
     ["phtc", "lihtc"]),
    ("Shannon Heights Sr. Living", "200 Penn Drive", "Verona", 48,
     ["nhtf", "lihtc"]),
    ("Legacy Bricks", "6 Parcels at the corner of Carroll St. and Temple St.", "Aliquippa", 40,
     ["nhtf", "phtc", "lihtc"]),
    ("St. Cecilia Senior", "303 Jackson Street", "Rochester", 45,
     ["nhtf", "lihtc"]),
    ("Cornerstone at 6th & Chestnut", "201 S. 6th Street", "Reading", 46,
     ["nhtf", "phtc", "lihtc"]),
    ("Bensalem Presbyterian Apts", "1900 Byberry Road", "Bensalem", 53,
     ["lihtc"]),
    ("Doylestown Senior Veterans", "280 N. Broad Street", "Doylestown", 60,
     ["nhtf", "lihtc"]),
    ("Nathaniel Hickman House", "400 N. Walnut St.", "West Chester", 32,
     ["nhtf", "phtc", "lihtc"]),
    ("Flemington Manor", "826 Linden St.", "Flemington Borough", 46,
     ["pennhomes", "lihtc"]),
    ("LeTort Lofts", "759 Hamilton Street", "Carlisle", 48,
     ["pennhomes", "phtc", "lihtc"]),
    ("TLC Capstone", None, "Harrisburg", 34,
     ["pennhomes", "nhtf", "lihtc"]),
    ("Greenhill Court", "1300 Clifton Avenue", "Sharon Hill", 45,
     ["lihtc"]),
    ("Carriage House", "1300 Oakland Avenue", "Indiana", 47,
     ["pennhomes", "nhtf", "lihtc"]),
    ("The Apartments at College Avenue", "210 College Avenue", "Lancaster", 49,
     ["hfh", "lihtc"]),
    ("Little Lehigh II", "Portion of 246 Lehigh St.", "Allentown", 35,
     ["phtc", "lihtc"]),
    ("Taylor Way", "Taylor Way", "Pittston", 40,
     ["lihtc"]),
    ("Laudenslager School Apts", "2600 Cowpath Road (aka 200 N. Main St.)", "Hatfield", 38,
     ["phtc", "lihtc"]),
    # PDF prints city as "Belthlehem" -- corrected to "Bethlehem" for
    # geocoding/display accuracy (Northampton County's well-known city;
    # not a fabrication, a typo fix).
    ("Gateway on 4th", "1400 E. 4th Street & 1414 E. 4th Street", "Bethlehem", 60,
     ["hfh", "phtc", "lihtc"]),
    ("Bretz Court", "Bretz Court", "Newport", 45,
     ["pennhomes", "nhtf", "lihtc"]),
    ("11th & Berks", "1915 N. 11th St.", "Philadelphia", 40,
     ["phtc", "lihtc"]),
    ("20th & CBM Sr. Housing", "2004-2034 Cecil B. Moore Avenue", "Philadelphia", 63,
     ["nhtf", "lihtc"]),
    ("4912 Griscom Street", "4912 Griscom Street", "Philadelphia", 44,
     ["nhtf", "lihtc"]),
    ("Camino De Oro II", "1802-25 North 8th Street", "Philadelphia", 38,
     ["nhtf", "phtc", "lihtc"]),
    ("Fairhill & St. Hugh Lofts", "Scattered Sites", "Philadelphia", 40,
     ["nhtf", "phtc", "lihtc"]),
    ("Help Philadelphia VII +", "2601-31 N. 28th Street", "Philadelphia", 50,
     ["nhtf", "phtc", "lihtc"]),
    ("Media Flats", "6435 Media Street", "Philadelphia", 33,
     ["lihtc"]),
    ("Nayda Cintron", "Various sites on W. Cumberland St., N. Resse St., and Fairhill St.", "Philadelphia", 40,
     ["nhtf", "lihtc"]),
    ("Pathways 17th Street Community Corridor", "Scattered Sites", "Philadelphia", 38,
     ["nhtf", "lihtc"]),
    ("Philly House Residences", "1310 Pearl Street", "Philadelphia", 70,
     ["nhtf", "phtc", "lihtc"]),
    ("West Philadelphia Preservation", "Scattered Sites", "Philadelphia", 45,
     ["nhtf", "lihtc"]),
    ("Westbrook Community Apartments", "3901 Germantown Ave.", "Philadelphia", 34,
     ["nhtf", "phtc", "lihtc"]),
    ("Westpark Redevelopment", "4401 Holden St.", "Philadelphia", 42,
     ["lihtc"]),
    ("The RidgeVue", "5000 Walker's Trail", "Greensburg", 84,
     ["lihtc"]),
    ("Willowbrook Commons", None, "Belle Vernon", 50,
     ["lihtc"]),
]

# Per-project "LI Units" (low-income/affordable-unit count) column, kept
# separate from RAW_PROJECTS' "Total Units" so both of the Map Doc's own
# unit columns can be independently verified (see verify_project_count_and_units).
# Not surfaced in the output JSON -- the bubble map uses Total Units (the
# physical development size) for marker sizing, matching IHDA's own
# "largest unit count = best estimate of physical size" convention.
LI_UNITS = {
    "421Seventh Ave Apts": 40, "Carrick Sr Apts": 52, "Chartiers Ave. Apts.": 44,
    "Gable Ridge": 49, "HG Blair": 44, "Hill Top Villas": 40, "Riverview Manor": 98,
    "Ross Lofts": 39, "Shannon Heights Sr. Living": 48, "Legacy Bricks": 40,
    "St. Cecilia Senior": 45, "Cornerstone at 6th & Chestnut": 46,
    "Bensalem Presbyterian Apts": 53, "Doylestown Senior Veterans": 60,
    "Nathaniel Hickman House": 32, "Flemington Manor": 46, "LeTort Lofts": 40,
    "TLC Capstone": 34, "Greenhill Court": 45, "Carriage House": 41,
    "The Apartments at College Avenue": 49, "Little Lehigh II": 35, "Taylor Way": 40,
    "Laudenslager School Apts": 38, "Gateway on 4th": 46, "Bretz Court": 45,
    "11th & Berks": 40, "20th & CBM Sr. Housing": 63, "4912 Griscom Street": 44,
    "Camino De Oro II": 38, "Fairhill & St. Hugh Lofts": 40,
    "Help Philadelphia VII +": 50, "Media Flats": 33, "Nayda Cintron": 40,
    "Pathways 17th Street Community Corridor": 38, "Philly House Residences": 70,
    "West Philadelphia Preservation": 45, "Westbrook Community Apartments": 34,
    "Westpark Redevelopment": 42, "The RidgeVue": 84, "Willowbrook Commons": 50,
}

# Per-project, per-funding-source dollar amount, transcribed from the Map
# Doc's own PennHOMES/Health for Harrisburg/NHTF/PHTC/LIHTC columns.
PROJECT_SOURCE_AMOUNTS = {
    "421Seventh Ave Apts": {"nhtf": 877141, "phtc": 1000000, "lihtc": 1136407},
    "Carrick Sr Apts": {"nhtf": 1000000, "phtc": 1000000, "lihtc": 1653863},
    "Chartiers Ave. Apts.": {"pennhomes": 2170000, "nhtf": 624147, "phtc": 1000000, "lihtc": 1850000},
    "Gable Ridge": {"lihtc": 992686},
    "HG Blair": {"nhtf": 1000000, "phtc": 1000000, "lihtc": 1850000},
    "Hill Top Villas": {"nhtf": 1000000, "phtc": 1000000, "lihtc": 1668218},
    "Riverview Manor": {"lihtc": 1662042},
    "Ross Lofts": {"phtc": 1000000, "lihtc": 1628804},
    "Shannon Heights Sr. Living": {"nhtf": 998944, "lihtc": 1700000},
    "Legacy Bricks": {"nhtf": 416098, "phtc": 1000000, "lihtc": 1700000},
    "St. Cecilia Senior": {"nhtf": 998944, "lihtc": 1684800},
    "Cornerstone at 6th & Chestnut": {"nhtf": 1000000, "phtc": 1000000, "lihtc": 1700000},
    "Bensalem Presbyterian Apts": {"lihtc": 1203272},
    "Doylestown Senior Veterans": {"nhtf": 1000000, "lihtc": 1850000},
    "Nathaniel Hickman House": {"nhtf": 815142, "phtc": 1000000, "lihtc": 1056137},
    "Flemington Manor": {"pennhomes": 1544133, "lihtc": 1700000},
    "LeTort Lofts": {"pennhomes": 2600000, "phtc": 1000000, "lihtc": 1530767},
    "TLC Capstone": {"pennhomes": 1000000, "nhtf": 660000, "lihtc": 1458756},
    "Greenhill Court": {"lihtc": 1680552},
    "Carriage House": {"pennhomes": 2300000, "nhtf": 777450, "lihtc": 1700000},
    "The Apartments at College Avenue": {"hfh": 1250000, "lihtc": 1408034},
    "Little Lehigh II": {"phtc": 1000000, "lihtc": 1561289},
    "Taylor Way": {"lihtc": 1700000},
    "Laudenslager School Apts": {"phtc": 1000000, "lihtc": 1622768},
    "Gateway on 4th": {"hfh": 400000, "phtc": 1000000, "lihtc": 1800000},
    "Bretz Court": {"pennhomes": 1500000, "nhtf": 917651, "lihtc": 1684800},
    "11th & Berks": {"phtc": 1000000, "lihtc": 1672008},
    "20th & CBM Sr. Housing": {"nhtf": 1000000, "lihtc": 1850000},
    "4912 Griscom Street": {"nhtf": 907440, "lihtc": 1850000},
    "Camino De Oro II": {"nhtf": 500000, "phtc": 1000000, "lihtc": 1622831},
    "Fairhill & St. Hugh Lofts": {"nhtf": 1000000, "phtc": 1000000, "lihtc": 1705860},
    "Help Philadelphia VII +": {"nhtf": 1000000, "phtc": 1000000, "lihtc": 1772076},
    "Media Flats": {"lihtc": 1414894},
    "Nayda Cintron": {"nhtf": 1000000, "lihtc": 1698675},
    "Pathways 17th Street Community Corridor": {"nhtf": 1000000, "lihtc": 1615597},
    "Philly House Residences": {"nhtf": 1000000, "phtc": 1000000, "lihtc": 1850000},
    "West Philadelphia Preservation": {"nhtf": 1000000, "lihtc": 1676177},
    "Westbrook Community Apartments": {"nhtf": 1000000, "phtc": 1000000, "lihtc": 1457808},
    "Westpark Redevelopment": {"lihtc": 1643053},
    "The RidgeVue": {"lihtc": 1760931},
    "Willowbrook Commons": {"lihtc": 1700000},
}

# Independently computed once (via pdfplumber, directly off the Map Doc's
# own table cells, before any manual RAW_PROJECTS transcription) sum of
# each funding-source column. Used as the "PDF-printed total" stand-in for
# this table (which prints no footer row of its own) -- see docstring.
EXPECTED_SOURCE_TOTALS = {
    "pennhomes": 11114133,
    "hfh": 1650000,
    "nhtf": 21492957,
    "phtc": 19000000,
    "lihtc": 66473105,
}

FUNDING_COLOR_GROUP = {
    "lihtc": "credit", "phtc": "credit",
    "pennhomes": "trust", "nhtf": "trust",
    "hfh": "capital",
}
# priority order for picking a project's single "primary" color when it has
# multiple funding sources (first match wins) -- LIHTC first since it is
# the universal anchor credit present on every one of the 41 awards.
FUNDING_PRIORITY = ["lihtc", "phtc", "pennhomes", "nhtf", "hfh"]


def verify_project_count_and_units():
    errors = []
    if len(RAW_PROJECTS) != 41:
        errors.append(f"project count: expected 41, got {len(RAW_PROJECTS)}")
    total_units_sum = sum(units for _n, _a, _c, units, _s in RAW_PROJECTS)
    if total_units_sum != 1946:
        errors.append(f"Total Units column sum: expected 1946, got {total_units_sum}")
    li_units_sum = sum(LI_UNITS.get(n, 0) for n, *_ in RAW_PROJECTS)
    if li_units_sum != 1900:
        errors.append(f"LI Units column sum: expected 1900, got {li_units_sum}")
    if set(LI_UNITS) != {n for n, *_ in RAW_PROJECTS}:
        errors.append("RAW_PROJECTS and LI_UNITS project-name sets differ")
    if set(PROJECT_SOURCE_AMOUNTS) != {n for n, *_ in RAW_PROJECTS}:
        errors.append("RAW_PROJECTS and PROJECT_SOURCE_AMOUNTS project-name sets differ")
    for name, _addr, _city, _units, sources in RAW_PROJECTS:
        amounts = PROJECT_SOURCE_AMOUNTS.get(name, {})
        missing = [s for s in sources if s not in amounts]
        extra = [s for s in amounts if s not in sources]
        if missing:
            errors.append(f"{name!r} is missing amounts for source(s) {missing}")
        if extra:
            errors.append(f"{name!r} has amounts for undeclared source(s) {extra}")
    if errors:
        raise SystemExit("Project count/unit mismatch(es):\n" + "\n".join(errors))
    print("Project count (41), Total Units sum (1,946) and LI Units sum (1,900) "
          "verified against PHFA's Oct 9, 2025 press release.")


def verify_source_amount_totals():
    sums = {}
    for _name, _addr, _city, _units, sources in RAW_PROJECTS:
        amounts = PROJECT_SOURCE_AMOUNTS.get(_name, {})
        for src in sources:
            sums[src] = sums.get(src, 0) + amounts[src]
    errors = []
    for key, expected in EXPECTED_SOURCE_TOTALS.items():
        got = sums.get(key, 0)
        if got != expected:
            errors.append(f"{key} (amount): expected {expected}, got {got}")
    lihtc_total = sums.get("lihtc", 0)
    if round(lihtc_total / 1e6, 1) != 66.5:
        errors.append(
            f"LIHTC total ${lihtc_total:,} does not round to $66.5M as stated in "
            f"PHFA's Oct 9, 2025 press release"
        )
    if errors:
        raise SystemExit("Funding-source amount mismatch(es):\n" + "\n".join(errors))
    print("All 5 funding-source dollar totals verified (self-consistent with Map Doc "
          "column sums); LIHTC total additionally verified as rounding to the "
          "press release's stated $66.5M.")


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
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, KeyError, ValueError, IndexError) as exc:
        print(f"  geocode failed for {query!r}: {exc}")
    cache[query] = result
    time.sleep(1.0)  # Nominatim usage policy: max 1 request/second
    return result


def build_projects():
    cache = {}
    projects = []
    for name, address, city, units, sources in RAW_PROJECTS:
        query = f"{address}, {city}, PA" if address else f"{city}, PA"
        coords = geocode(query, cache)
        status = "ok"
        if coords is None:
            coords = geocode(f"{city}, PA", cache)
            status = "city_center" if coords else "unresolved"
        primary = next((s for s in FUNDING_PRIORITY if s in sources), sources[0])
        source_amounts = PROJECT_SOURCE_AMOUNTS.get(name, {})
        projects.append({
            "id": name.lower().replace(" ", "-").replace("'", "").replace(".", "").replace("&", "and").replace("+", "plus"),
            "name": name,
            "address": address,
            "city": city,
            "lat": round(coords[0], 5) if coords else None,
            "lon": round(coords[1], 5) if coords else None,
            "units": units,
            "funding_sources": sources,
            "source_amounts": source_amounts,
            "total_amount": sum(source_amounts.values()) if source_amounts else None,
            "primary_color_group": FUNDING_COLOR_GROUP[primary],
            "overlaps": len(sources) > 1,
            "geocode_status": status,
        })
    return projects


def main():
    verify_project_count_and_units()
    verify_source_amount_totals()
    print("Geocoding project addresses via Nominatim...")
    projects = build_projects()
    unresolved = [p["name"] for p in projects if p["geocode_status"] == "unresolved"]
    if unresolved:
        print(f"  {len(unresolved)} project(s) could not be geocoded: {unresolved}")
    city_center = [p["name"] for p in projects if p["geocode_status"] == "city_center"]
    if city_center:
        print(f"  {len(city_center)} project(s) fell back to city-center geocoding: {city_center}")

    payload = {
        "PA": {
            "hfa_name": "Pennsylvania Housing Finance Agency",
            "hfa_abbr": "PHFA",
            "fiscal_year": "FY2025",
            "source_title": "PHFA 2025 Annual Report -- Homeownership, HEMAP, PHARE and Multifamily Award tables",
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
