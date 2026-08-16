"""
Builds docs/ut_program_activity.json from Utah Housing Corporation's (UHC)
FY2025 Annual Report (fiscal year July 1, 2024 - June 30, 2025) plus UHC's
own separately-issued FY2025 audited financial statements (for GASB fund-type
classification).

Sources (all FY2025 = UHC's fiscal year July 1, 2024 - June 30, 2025)
------------------------------------------------------------------------
1. UHC FY2025 Annual Report ("Annual Report Fiscal Year 2025"), 26 pages:
     https://utahhousingcorp.org/about/2025-annual-report/
     PDF: https://utahhousingcorp.org/wp-content/uploads/2025_Annual_Report.pdf
     Local copy: FY2025/program_activity/pdf/UT_UtahHousing_AnnualReport_2025.pdf
   - Homeownership KPIs (p.5, p.8): 3,684 families / $1.44B first mortgages;
     p.9: Down Payment Assistance funded in FY25 $52.7M, plus three named
     assistance sub-programs (FTHB 1,244 loans / $24,811,427; Law Enforcement &
     Correctional Officer Assistance 158 loans / $3,034,858; Veteran Grant 213
     grants / $532,500).
   - Multifamily KPIs (p.12): 1,666 affordable rental units financed;
     $303,177,309 total net proceeds from 4%/9% federal LIHTC; $43,454,343
     total net proceeds from State Tax Credit; $196,335,000 tax-exempt PAB.
   - Appendix B (p.24-25): the complete per-project list ("data on all projects
     awarded LIHTC during FY25"), 23 rows with PROJECT NAME / LOCATION /
     # OF UNITS / FEDERAL LIHTC AWARDED (with 9% or 4% type) / STATE TAX CREDIT
     AWARDED / BONDS ISSUED, and a printed Totals row: 1,666 units,
     $33,424,483 federal LIHTC (annual credits), $7,634,695 state tax credit
     (annual credits), $196,335,000 bonds.
2. UHC FY2025 audited financial statements (67 pages, "business-type activities
   ... June 30, 2025", auditor's report dated September 19, 2025) -- used ONLY
   for fund-type classification:
     https://utahhousingcorp.org/pdf/auditfs2025.pdf
     Local copy: FY2025/program_activity/pdf/UT_UtahHousing_AuditFS_2025.pdf

IMPORTANT data-provenance note on the checked-in ACFR text
------------------------------------------------------------------------
FY2025/txt/UT_UtahHousing_FY2025_ACFR.txt (the file this build's task briefing
pointed at) is NOT UHC's ACFR -- it is a text dump of a 2025-10-23 board
meeting package (single audit letter + bond resolutions + a mortgage
dashboard), not an audited financial report. The correctly-scoped source for
fund-type classification is the *PDF* above (UT_UtahHousing_AuditFS_2025.pdf),
downloaded from UHC's own financial-statements page
(https://utahhousingcorp.org/investors/auditfinancialstatements/), which this
script cites below. The .txt/.pdf mismatch is flagged here for awareness, not
fixed by this script.

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
UHC's own audited financial statements report ONLY business-type activities:
the auditor's opinion covers "the financial statements of the business-type
activities of Utah Housing Corporation" and Note 1 states the Corporation "is
self-supporting, and follows enterprise fund reporting" -- a single
enterprise fund, no governmental funds. Financial activities are recorded in
funds established under various bond resolutions (the "SINGLE-FAMILY MORTGAGE
PROGRAM FUNDS" combining statements name Single Family Mortgage Loans / 2000
Indenture / 2009 Indenture / General Obligation) plus a general operating fund
that carries administrative/operational expenses and an internal net-position
designation "Down payment assistance $45,000 (thousand)".
  - "proprietary" (UHC's own enterprise-fund lending/disbursement):
      * single-family first mortgages -> "Single-Family Mortgage Program Funds"
        (the $5.99B serviced portfolio, p.11 of the annual report).
      * FTHB / Law Enforcement & Correctional Officer / Veteran assistance ->
        inside UHC's own funds. The audit's Note "Prior Period Adjustment"
        explicitly names the "First-Time Home Buyer and Law Enforcement
        programs" as holding liabilities ($24,467,528) ON UHC's balance sheet
        -- near-verbatim confirmation these are UHC-carried activities, not
        pass-throughs. The Veteran Grant is classified by program description
        (UHC disburses the grants from its own resources, same as the other
        two) -- confidence: high. fund_name = "Operating Fund (down payment
        assistance designation)".
  - "off_balance_sheet" (administered but never booked as UHC fund assets):
      * Federal LIHTC and Utah State Tax Credit: full-text search of the 67-page
        audit returns ZERO matches for "low-income housing tax credit", "LIHTC",
        "State Tax Credit", "private activity bond" -- the credits are allocated
        directly to developers/investors, not carried as UHC assets (same
        off-balance-sheet logic PA/IHDA document).
      * Tax-exempt PAB: Note 12 "CONDUIT DEBT" states "The Corporation has
        issued Multi-Family Mortgage Purchase Bonds as conduit debt obligations
        for the purpose of providing capital financing for third party
        affordable housing projects that are not a part of the Corporation. The
        Corporation is not obligated in any manner for repayment of the conduit
        debt. The Corporation has not included the activity of these bonds in
        the financial statements for the current year." -> off_balance_sheet.

Category-level methodology
------------------------------------------------------------------------
Homeownership: the headline (3,684 households / $1.44B) is the p.8 infographic
"3,684 families assisted in achieving homeownership" / "$1.44 billion in loans
funded" (p.5 gives the same "helping 3,684 low- and moderate-income Utah
families to buy their homes"). DPA is p.9's "Down Payment Assistance funded in
FY25 $52.7M" (p.5 rounds it "nearly $53 million"). The three assistance
subprograms (FTHB 1,244 / Law Enforcement 158 / Veteran 213) are three distinct,
separately-appropriated programs presented as parallel counts on p.9; their sum
(1,615) is intentionally smaller than the 3,684 headline because most purchase
loans close with no UHC-sourced second-mortgage assistance (mirrors PHFA's
homeownership pattern). additive=True for the three relative to each other.

Multifamily: the headline (1,666 units) and the three dollar KPIs use the
annual report's NET PROCEEDS figures ($303,177,309 federal LIHTC net proceeds,
$43,454,343 State Tax Credit net proceeds, $196,335,000 PAB issued). The
per-project layer (Appendix B) instead discloses ANNUAL credit allocations
(federal column sums to $33,424,483, state column sums to $7,634,695) -- a
different, smaller measure than net proceeds (the ~10-year net-equity value);
bonds are the same $196,335,000 measure in both places. This is documented, not
paper-ed over: subprogram dollar figures = net proceeds (the p.12 headline),
project source_amounts = annual credits (the p.24 columns).

Appendix B's printed "Totals: 1,666" is a SUBSET of its own 23 rows (which sum
to 2,554 units), because the printed total counts only developments whose
FEDERAL LIHTC award took place in FY2025 (footnote 1 "Where the federal award
took place in FY2025"). 5 rows are prior-year federal awards (Valley West, 44 N
PSH, Silos on 500, 9Ten West = FY24; New City Plaza = FY21) and 1 row (Alta
Fairpark, 147 units) "was awarded and then relinquished volume cap during
FY25" (footnote *). 2,554 - (20+67+180+175+299) - 147 = 1,666. This script
surfaces ALL 23 Appendix B rows as the bubble-map cohort (2,554 physical units)
and verifies BOTH sums.

The federal LIHTC annual-credit total ($33,424,483) is likewise the sum of the
FY25-awarded federal column EXCLUDING Alta Fairpark's relinquished $1,390,000
(34,814,483 - 1,390,000 = 33,424,483, per footnote 2 "9% credits removed from
total where the award date was not during FY25"). The state-tax-credit total
($7,634,695) sums the FY25-awarded state column (14 rows; Lotus Riverwalk III
and Silos on 500 print "Awarded in FY24" and are excluded, per footnote 3).
Bonds sum the FY25-issued column (9 rows; Liberty Corner / Waymark at Folsom
Trail / Daybreak print "Issuance in FY26" and are excluded).

Geocoding
------------------------------------------------------------------------
Appendix B gives only a city/town-level LOCATION (no street addresses), so this
is a city-level list: query "{location}, UT", expect geocode_status
"city_center" (honest precision; never "ok"). Self-throttled <=1 request/second
with an identifying User-Agent per Nominatim's usage policy.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "ut_program_activity.json"

SOURCE_URL = "https://utahhousingcorp.org/about/2025-annual-report/"
SOURCE_FILE = ("UT_UtahHousing_AnnualReport_2025.pdf (+ UT_UtahHousing_AuditFS_2025.pdf "
               "for fund-type classification)")
RETRIEVED = "2026-08-16"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
# OSM-based fallback used only when Nominatim rate-limits (HTTP 429) or fails;
# same underlying OpenStreetMap data, so city-level results are equivalent.
PHOTON_URL = "https://photon.komoot.io/api/"
GEOCODER_USER_AGENT = "us-hfa-data-map/1.0 (github.com/MD-ai-fin/us-hfa-data-map)"

# Persistent on-disk geocode cache so re-runs are byte-identical and do not
# re-hit the geocoders (the shared IP is often Nominatim-rate-limited).
GEOCODE_CACHE_PATH = Path(__file__).resolve().parent / "ut_geocode_cache.json"

# ---------------------------------------------------------------------------
# Category-level data
# ---------------------------------------------------------------------------
# fy2026 uniform shape: {value, amount, closed, note_key} -- the FY2025 annual
# report discloses no forward-looking FY2026 figure, so none is invented.
_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                 "note_key": "utFy26NotePending"}

CATEGORIES = [
    {
        "key": "homeownership",
        "unit_type": "households",
        "fy2025_actual": 3684,
        "fy2025_source_quote": (
            "\"Utah Housing's Direct Investment in Down Payment Assistance -- FY25, "
            "UHC invested nearly $53 million of its resources into down payment "
            "assistance and raised $1.44 billion in capital from all sources for the "
            "acquisition of single family first mortgages, helping 3,684 low- and "
            "moderate-income Utah families to buy their homes.\" (Annual Report, p.5) "
            "-- p.8 infographic: \"3,684 families assisted in achieving homeownership\" "
            "and \"$1.44 billion in loans funded\"; p.9: \"Down Payment Assistance "
            "funded in FY25 $52.7M\". p.9 also lists three named assistance "
            "sub-programs -- \"FTHB Assistance 1,244 loans funded, totaling $24,811,427\", "
            "\"Law Enforcement & Correctional Officer Assistance 158 loans funded, "
            "totaling $3,034,858\", \"Veteran Grant 213 grants funded, totaling "
            "$532,500\" -- which are a SUBSET of the 3,684 purchasers (most purchase "
            "loans close with no UHC-sourced assistance); their sum (1,615) is "
            "therefore smaller than the 3,684 headline. The source does not disclose "
            "whether any single household received more than one assistance type; the "
            "three are treated as distinct programs."
        ),
        "fy2025_amounts": [
            {"label_key": "ut_amt_purchase_loans", "amount": 1440000000},
            {"label_key": "ut_amt_dpa", "amount": 52700000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "fthb", "fy2025_units": 1244, "fy2025_amount": 24811427,
             "color_group": "capital",
             # Audit's "Prior Period Adjustment" note names the "First-Time Home
             # Buyer ... programs" as holding liabilities ON UHC's balance sheet
             # -> inside UHC's own enterprise fund. Confidence: high.
             "fund_type": "proprietary",
             "fund_name": "Operating Fund (down payment assistance designation)",
             "fy2026": _FY26_PENDING},
            {"key": "law_enforcement", "fy2025_units": 158, "fy2025_amount": 3034858,
             "color_group": "capital",
             # Same "Prior Period Adjustment" note names the "Law Enforcement"
             # program alongside FTHB as a UHC-carried liability. Confidence: high.
             "fund_type": "proprietary",
             "fund_name": "Operating Fund (down payment assistance designation)",
             "fy2026": _FY26_PENDING},
            {"key": "veteran", "fy2025_units": 213, "fy2025_amount": 532500,
             "color_group": "capital",
             # Not named in the audit, but UHC disburses the grants from its own
             # resources (same as FTHB/Law Enforcement); classified proprietary
             # by program description. Confidence: high.
             "fund_type": "proprietary",
             "fund_name": "Operating Fund (down payment assistance designation)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "multifamily_lihtc",
        "unit_type": "units",
        "fy2025_actual": 1666,
        "fy2025_source_quote": (
            "\"$303,177,309 total net proceeds from 4% and 9% federal tax credits "
            "awarded ... $196,335,000 in tax-exempt private activity bonds (PAB) "
            "issued ... $43,454,343 Total net proceeds from State Tax Credit awarded "
            "... 1,666 affordable rental units financed.\" (Annual Report, p.12, "
            "\"Multifamily Finance & Development\"). Cross-checked against Appendix B "
            "(p.24): 23 project rows whose printed \"Totals\" row reads \"1,666\" units "
            "(footnote 1: counts only developments whose FEDERAL LIHTC award took place "
            "in FY2025), \"$33,424,483\" federal LIHTC (annual credits, footnote 2), "
            "\"$7,634,695\" state tax credit (annual credits, footnote 3), and "
            "\"$196,335,000\" bonds. NOTE the two LIHTC/STC measures: the subprogram "
            "dollar figures below use the report's headline NET PROCEEDS ($303,177,309 / "
            "$43,454,343, the p.12/p.24 'net proceeds (approx.)' figures), while each "
            "project's source_amounts below use Appendix B's per-project ANNUAL credit "
            "allocations ($33,424,483 / $7,634,695 column sums) -- a different, smaller "
            "measure (annual credit vs ~10-year net equity)."
        ),
        "fy2025_amounts": [
            {"label_key": "ut_amt_lihtc", "amount": 303177309},
            {"label_key": "ut_amt_stc", "amount": 43454343},
            {"label_key": "ut_amt_pab", "amount": 196335000},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "lihtc", "fy2025_units": 1666, "fy2025_amount": 303177309,
             "color_group": "credit",
             # ZERO matches for LIHTC / "low-income housing tax credit" in UHC's
             # 67-page audit -> credits flow directly to developers/investors.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "stc", "fy2025_units": None, "fy2025_amount": 43454343,
             "color_group": "credit",
             # ZERO matches for "State Tax Credit" in UHC's audit -> same
             # off-balance-sheet logic as federal LIHTC.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "pab", "fy2025_units": None, "fy2025_amount": 196335000,
             "color_group": "bond",
             # Audit Note 12 "CONDUIT DEBT": UHC "is not obligated in any manner
             # for repayment of the conduit debt" and "has not included the
             # activity of these bonds in the financial statements".
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
]

# ---------------------------------------------------------------------------
# Multifamily project-level detail (Annual Report, Appendix B, p.24-25).
# Manually transcribed via pdfplumber table extraction -- 23 rows: PROJECT NAME,
# LOCATION, # OF UNITS, FEDERAL LIHTC AWARDED (amount or "Awarded in FYXX"),
# type (9% = competitive; 4% = bond-financed), STATE TAX CREDIT AWARDED, BONDS
# ISSUED. "units" uses the "# OF UNITS" column (physical development size).
#
# funding_sources lists only a project's FY2025 activity (a source with a
# FY2025 dollar amount in its column); a source whose column prints "Awarded in
# FY24/FY21" (prior-year award), "Issuance in FY26" (future bonds), or "-" is
# NOT a FY2025 source and is omitted. Alta Fairpark's federal LIHTC
# ($1,390,000) was "awarded and then relinquished volume cap during FY25"
# (footnote *) so it is excluded from its funding_sources; its State Tax Credit
# ($700,000) was awarded in FY25 (recaptured in FY26, outside this window) and
# is kept.
# ---------------------------------------------------------------------------

# (name, city, units, [FY2025 funding source keys])
RAW_PROJECTS = [
    ("Valley West Apartments", "Gunnison", 20, ["stc"]),
    ("44 N PSH", "Salt Lake City", 67, ["stc"]),
    ("Iron Falcon CROWN", "Enoch", 9, ["lihtc"]),
    ("CROWN at Pleasant Creek", "Mt. Pleasant", 7, ["lihtc"]),
    ("Amasa Apartments", "Moab", 50, ["lihtc", "stc"]),
    ("Fairmont Heights", "Salt Lake City", 55, ["lihtc"]),
    ("Switchpoint Fairpark", "Salt Lake City", 76, ["lihtc", "stc"]),
    ("Saltair Lofts", "Salt Lake City", 68, ["lihtc", "stc"]),
    ("Dominguez Park III", "Millcreek", 60, ["lihtc", "stc"]),
    ("Sage Meadow Townhomes", "Fillmore", 39, ["lihtc", "stc"]),
    ("Promontory Place", "Salt Lake City", 175, ["lihtc", "stc", "pab"]),
    ("Latitude / 2nd South Apartments", "Salt Lake City", 104, ["lihtc", "stc", "pab"]),
    ("Liberty Ranch", "Park City", 40, ["lihtc", "pab"]),
    ("Lotus Riverwalk III", "Ogden", 137, ["lihtc", "pab"]),
    ("Moda Griffin", "Salt Lake City", 110, ["lihtc", "stc", "pab"]),
    ("Liberty Corner", "Salt Lake City", 200, ["lihtc", "stc"]),
    ("Waymark at Folsom Trail", "Salt Lake City", 108, ["lihtc", "stc"]),
    ("Lotus Fluence", "Salt Lake City", 225, ["lihtc", "stc", "pab"]),
    ("Daybreak Affordable Phase I", "Daybreak", 203, ["lihtc"]),
    ("Alta Fairpark", "Salt Lake City", 147, ["stc"]),
    ("Silos on 500", "Salt Lake City", 180, ["pab"]),
    ("New City Plaza", "Salt Lake City", 299, ["pab"]),
    ("9Ten West", "Salt Lake City", 175, ["pab"]),
]

# Per-project FY2025 dollar amounts from Appendix B's own columns. Federal LIHTC
# and State Tax Credit amounts are the ANNUAL credit allocations; bond amounts
# are the FY2025 issuance. A source that prints "Awarded in FY24/FY21",
# "Issuance in FY26", or "-" has no entry here (see RAW_PROJECTS comment).
PROJECT_SOURCE_AMOUNTS = {
    "Valley West Apartments": {"stc": 150000},
    "44 N PSH": {"stc": 260000},
    "Iron Falcon CROWN": {"lihtc": 327607},
    "CROWN at Pleasant Creek": {"lihtc": 216207},
    "Amasa Apartments": {"lihtc": 1801816, "stc": 700000},
    "Fairmont Heights": {"lihtc": 2375000},
    "Switchpoint Fairpark": {"lihtc": 963496, "stc": 1000000},
    "Saltair Lofts": {"lihtc": 2500000, "stc": 1000000},
    "Dominguez Park III": {"lihtc": 1144762, "stc": 350000},
    "Sage Meadow Townhomes": {"lihtc": 1259292, "stc": 474085},
    "Promontory Place": {"lihtc": 3209014, "stc": 700000, "pab": 38500000},
    "Latitude / 2nd South Apartments": {"lihtc": 1561374, "stc": 575000, "pab": 20000000},
    "Liberty Ranch": {"lihtc": 675721, "pab": 11000000},
    "Lotus Riverwalk III": {"lihtc": 2127408, "pab": 24700000},
    "Moda Griffin": {"lihtc": 1715611, "stc": 450000, "pab": 21500000},
    "Liberty Corner": {"lihtc": 5327737, "stc": 350000},
    "Waymark at Folsom Trail": {"lihtc": 2113030, "stc": 350000},
    "Lotus Fluence": {"lihtc": 2836408, "stc": 575610, "pab": 32500000},
    "Daybreak Affordable Phase I": {"lihtc": 3270000},
    "Alta Fairpark": {"stc": 700000},
    "Silos on 500": {"pab": 21335000},
    "New City Plaza": {"pab": 5500000},
    "9Ten West": {"pab": 21300000},
}

# The 6 Appendix B rows excluded from the printed "Totals: 1,666" unit total:
# 5 prior-year federal-LIHTC awards (Valley West, 44 N PSH, Silos on 500,
# 9Ten West = FY24; New City Plaza = FY21) plus Alta Fairpark (awarded then
# relinquished volume cap during FY25).
NON_FY25_COHORT = {
    "Valley West Apartments", "44 N PSH", "Silos on 500", "9Ten West",
    "New City Plaza", "Alta Fairpark",
}

EXPECTED_TOTAL_UNITS = 2554         # sum of all 23 rows' "# OF UNITS"
EXPECTED_FY25_COHORT_UNITS = 1666   # Appendix B printed "Totals: 1,666" (footnote 1)
EXPECTED_SOURCE_TOTALS = {          # Appendix B printed column totals (p.24)
    "lihtc": 33424483,              # annual federal credits, FY25-awarded (footnote 2)
    "stc": 7634695,                 # annual state credits, FY25-awarded (footnote 3)
    "pab": 196335000,               # bonds issued FY25
}

FUNDING_COLOR_GROUP = {
    "lihtc": "credit", "stc": "credit", "pab": "bond",
}
# priority order for picking a project's single "primary" color when it has
# multiple funding sources (first match wins) -- LIHTC first (the anchor credit).
FUNDING_PRIORITY = ["lihtc", "stc", "pab"]


def verify_project_count_and_units():
    errors = []
    if len(RAW_PROJECTS) != 23:
        errors.append(f"project count: expected 23, got {len(RAW_PROJECTS)}")
    total_units_sum = sum(units for _n, _c, units, _s in RAW_PROJECTS)
    if total_units_sum != EXPECTED_TOTAL_UNITS:
        errors.append(f"all-23 units sum: expected {EXPECTED_TOTAL_UNITS}, got {total_units_sum}")
    cohort_units = sum(units for n, _c, units, _s in RAW_PROJECTS if n not in NON_FY25_COHORT)
    if cohort_units != EXPECTED_FY25_COHORT_UNITS:
        errors.append(f"FY25-cohort units (Totals row): expected {EXPECTED_FY25_COHORT_UNITS}, got {cohort_units}")
    if set(PROJECT_SOURCE_AMOUNTS) != {n for n, *_ in RAW_PROJECTS}:
        errors.append("RAW_PROJECTS and PROJECT_SOURCE_AMOUNTS project-name sets differ")
    for name, _city, _units, sources in RAW_PROJECTS:
        amounts = PROJECT_SOURCE_AMOUNTS.get(name, {})
        missing = [s for s in sources if s not in amounts]
        extra = [s for s in amounts if s not in sources]
        if missing:
            errors.append(f"{name!r} is missing amounts for source(s) {missing}")
        if extra:
            errors.append(f"{name!r} has amounts for undeclared source(s) {extra}")
    if errors:
        raise SystemExit("Project count/unit mismatch(es):\n" + "\n".join(errors))
    print("Project count (23), all-23 unit sum (2,554) and FY25-cohort unit total "
          "(1,666) verified against Appendix B's own rows + printed Totals row.")


def verify_source_amount_totals():
    sums = {}
    for _name, _city, _units, sources in RAW_PROJECTS:
        amounts = PROJECT_SOURCE_AMOUNTS.get(_name, {})
        for src in sources:
            sums[src] = sums.get(src, 0) + amounts[src]
    errors = []
    for key, expected in EXPECTED_SOURCE_TOTALS.items():
        got = sums.get(key, 0)
        if got != expected:
            errors.append(f"{key} (amount): expected {expected}, got {got}")
    if errors:
        raise SystemExit("Funding-source amount mismatch(es):\n" + "\n".join(errors))
    print("Federal LIHTC annual-credit sum ($33,424,483), State Tax Credit sum "
          "($7,634,695) and bond sum ($196,335,000) verified against Appendix B's "
          "printed column totals.")


def verify_kpi_headlines():
    # External/secondary check: the category headline figures against the
    # annual report's own prose (p.5/p.8/p.9/p.12), independent of Appendix B.
    errors = []
    home = CATEGORIES[0]
    if home["fy2025_actual"] != 3684:
        errors.append(f"homeownership units: expected 3684, got {home['fy2025_actual']}")
    home_amounts = {a["label_key"]: a["amount"] for a in home["fy2025_amounts"]}
    if home_amounts.get("ut_amt_purchase_loans") != 1440000000:
        errors.append("homeownership purchase-loan amount != $1.44B")
    if home_amounts.get("ut_amt_dpa") != 52700000:
        errors.append("homeownership DPA amount != $52.7M")
    if sum(s["fy2025_units"] for s in home["subprograms"]) != 1615:
        errors.append("assistance subprogram units do not sum to 1,615")
    mf = CATEGORIES[1]
    if mf["fy2025_actual"] != 1666:
        errors.append(f"multifamily units: expected 1666, got {mf['fy2025_actual']}")
    mf_amounts = {a["label_key"]: a["amount"] for a in mf["fy2025_amounts"]}
    if mf_amounts.get("ut_amt_lihtc") != 303177309:
        errors.append("multifamily LIHTC net proceeds != $303,177,309")
    if mf_amounts.get("ut_amt_stc") != 43454343:
        errors.append("multifamily STC net proceeds != $43,454,343")
    if mf_amounts.get("ut_amt_pab") != 196335000:
        errors.append("multifamily PAB != $196,335,000")
    if errors:
        raise SystemExit("KPI headline mismatch(es):\n" + "\n".join(errors))
    print("Category headlines (3,684 households / $1.44B / $52.7M DPA; 1,666 units / "
          "$303.2M LIHTC net / $43.5M STC net / $196.3M PAB; 1,615 assistance "
          "recipients) verified against the annual report's prose.")


def _load_cache():
    if GEOCODE_CACHE_PATH.exists():
        try:
            return json.loads(GEOCODE_CACHE_PATH.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            return {}
    return {}


def _nominatim(query):
    params = urllib.parse.urlencode({"q": query, "format": "json", "limit": 1})
    url = f"{NOMINATIM_URL}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": GEOCODER_USER_AGENT})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.load(resp)
    if data:
        return (float(data[0]["lat"]), float(data[0]["lon"]))
    return None


def _photon(query):
    params = urllib.parse.urlencode({"q": query, "limit": 1})
    url = f"{PHOTON_URL}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": GEOCODER_USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.load(resp)
    features = data.get("features") or []
    if features:
        lon, lat = features[0]["geometry"]["coordinates"]
        return (float(lat), float(lon))
    return None


def geocode(query, cache):
    if query in cache:
        return cache[query]
    result = None
    # 1) Nominatim (primary), with a single retry on transient HTTP 429.
    for attempt in (1, 2):
        try:
            result = _nominatim(query)
            break
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError,
                KeyError, ValueError, IndexError) as exc:
            if attempt == 1:
                print(f"  Nominatim failed for {query!r}: {exc} -- retrying once")
                time.sleep(1.0)
            else:
                print(f"  Nominatim failed again for {query!r}: {exc}")
    # 2) OSM-based Photon fallback (only if Nominatim did not resolve).
    if result is None:
        try:
            result = _photon(query)
            print(f"  Photon fallback resolved {query!r}")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError,
                KeyError, ValueError, IndexError) as exc:
            print(f"  geocode failed for {query!r}: {exc}")
    cache[query] = result
    time.sleep(1.0)  # Nominatim usage policy: max 1 request/second
    return result


def build_projects():
    cache = _load_cache()
    dirty = False
    projects = []
    for name, city, units, sources in RAW_PROJECTS:
        query = f"{city}, UT"
        before = query in cache
        coords = geocode(query, cache)
        if not before and query in cache:
            dirty = True
        # City-level source list -> always city_center (never claim "ok").
        status = "city_center" if coords else "unresolved"
        primary = next((s for s in FUNDING_PRIORITY if s in sources), sources[0])
        source_amounts = PROJECT_SOURCE_AMOUNTS.get(name, {})
        projects.append({
            "id": (name.lower().replace(" ", "-").replace("/", "-").replace("*", "")
                   .replace("'", "").replace(".", "").replace("&", "and")),
            "name": name,
            "address": None,
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
    if dirty:
        GEOCODE_CACHE_PATH.write_text(
            json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")
    return projects


def main():
    verify_project_count_and_units()
    verify_source_amount_totals()
    verify_kpi_headlines()
    print("Geocoding project cities via Nominatim...")
    projects = build_projects()
    unresolved = [p["name"] for p in projects if p["geocode_status"] == "unresolved"]
    if unresolved:
        print(f"  {len(unresolved)} project(s) could not be geocoded: {unresolved}")
    city_center = [p["name"] for p in projects if p["geocode_status"] == "city_center"]
    if city_center:
        print(f"  {len(city_center)} project(s) geocoded to city center (source is city-level): {len(city_center)}")

    payload = {
        "UT": {
            "hfa_name": "Utah Housing Corporation",
            "hfa_abbr": "Utah Housing",
            "fiscal_year": "FY2025",
            "source_title": "Utah Housing Corporation FY2025 Annual Report -- Homeownership, Multifamily LIHTC and Appendix B project list",
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
