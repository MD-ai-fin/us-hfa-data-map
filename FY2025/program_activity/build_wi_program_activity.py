"""
Builds docs/wi_program_activity.json from WHEDA's "Annual Report Fiscal Year
2024-2025" ("WHEDA By The Numbers" page) plus its own 2025 9% and 4% Housing
Tax Credit award lists (the per-development detail behind this script's
bubble map) and its own FY2025 audited financial statements (for GASB
fund-type classification).

Sources
------------------------------------------------------------------------
1. "WHEDA Annual Report Fiscal Year 2024-2025" (PDF, 10 pages):
     https://www.wheda.com/globalassets/documents/annual-reports-and-financials/2025/2025-annual-report.pdf
   Local copy: FY2025/program_activity/pdf/WI_WHEDA_AnnualReport_FY2025.pdf
   Web version: https://www.wheda.com/about-wheda/annual-report--financials/annual-report-2025
   -- "WHEDA BY THE NUMBERS" page (PDF p.6) supplies every category-level
   figure below.
2. "2025 9% Housing Tax Credit (HTC) Award List":
     https://www.wheda.com/developers-and-property-managers/tax-credits/htc/allocating/2025/9-percent-htc-awards
3. "2025 4% Housing Tax Credit Award List" (WHEDA's own page title is
   "2025 State and 4% Housing Tax Credit cycle" -- NOT the "2026" cycle page
   of the same name; that page covers a different, later award round and is
   deliberately NOT used here, see "HTC list vs headline" below):
     https://www.wheda.com/developers-and-property-managers/tax-credits/htc/allocating/2025/4-percent-htc-awards
   Both HTC pages render their award table via server-side HTML (a <table>
   with one <tr class="top-row"> per project plus a hidden expandable detail
   sub-row), not a PDF -- transcribed programmatically via BeautifulSoup off
   the raw page HTML (FY2025/program_activity/htc9_raw.html,
   htc4_raw.html), not by eye, to avoid transcription error.
4. WHEDA's own separately-issued FY2025 audited financial statements (used
   ONLY for GASB fund-type classification):
     FY2025/txt/WI_WHEDA_FY2025_ACFR.txt
   Confirmed to be the correct, WHEDA-scoped document -- title page reads
   "WISCONSIN HOUSING AND ECONOMIC DEVELOPMENT AUTHORITY Financial
   Statements For the Years Ended June 30, 2025 and 2024", and the
   auditor's opinion (p.3) is scoped to exactly "the Wisconsin Housing and
   Economic Development Authority's basic financial statements" -- no
   Commonwealth/state-wide-report mismatch of the kind flagged in this
   pilot series' PA build script.

Fiscal-year date verification
------------------------------------------------------------------------
The annual-report PDF is internally inconsistent about its own reporting
period: PDF p.6's "WHEDA BY THE NUMBERS" header prints "Fiscal Year 2024 -
2025 WHEDA Investments (June 1, 2024 - June 30, 2025)" (a "June 1" that
does not match any fiscal-year convention used elsewhere in WHEDA's own
reporting), while the live web version of the identical page
(annual-report-2025, fetched directly, not the PDF) prints the same
sentence as "July 1, 2024 through June 30, 2025". WHEDA's own audited
financial statements settle this: the Statements of Net Position, Revenues/
Expenses, and Cash Flows are all captioned "For the Year[s] Ended June 30,
2025" with no other period ever mentioned, and Note 1 describes a single
fiscal year ending June 30 with no mid-calendar-year start date anywhere.
"June 1, 2024" in the PDF is therefore treated as a typo (most likely a
dropped "Jul" -> "Jun" substitution) and this script uses the standard,
ACFR-confirmed **July 1, 2024 - June 30, 2025** fiscal year throughout.

Category-level methodology
------------------------------------------------------------------------
Single Family Homeownership (fy2025_actual = 2,323 households): PDF p.6's
own "Mortgages closed 2,323" figure, used verbatim. "Down payment
assistance $10,948,456" is a dollar amount only -- no separate loan count
is disclosed for it anywhere in the report, so none is invented
(fy2025_units=None on that subprogram) -- and it plausibly rides on a
SUBSET of the 2,323 first mortgages (a homebuyer either does or doesn't
take WHEDA down payment assistance on top of their first mortgage), so
additive=False, matching this pilot series' identical PA/OH "assistance
loan is a subset, not a partition" treatment. "Total loans serviced
29,245" (a cumulative *stock* figure, not a FY2025 *flow*) is deliberately
excluded, matching this project's existing practice of hiding cumulative
historical/stock metrics (see repo history: "隐藏'服务家庭数量'与'累计历史服务
家庭数量'两个指标").

Multifamily Housing (fy2025_actual = 1,410 units): PDF p.6's own "Housing
units created 1,410" figure, used verbatim, alongside "Developments
financed 28" and "Loans closed 83" (both cited in fy2025_source_quote as
context, not modeled as separate subprograms since no per-development list
discloses which of the 28 developments make up the 1,410 units -- WHEDA
publishes no per-project multifamily-lending detail the way it does for
HTC awards, so this category has NO RAW_PROJECTS entries and stays
KPI-card-only; inventing a development-by-development breakdown here would
violate this project's "never fabricate a missing number" rule).

Housing Tax Credits (fy2025_actual = 1,731 units -- see "HTC list vs
headline" below): built from the two live 2025 HTC award-list pages (9%
and 4%), each of which prints its own totals sentence used as an
independent verification gate (verify_htc_lists below): "The 2025 HTC
cycle has awarded $19,157,556 to 19 different projects. These projects
will provide assistance to 967 housing units, 957 of which are affordable
units" (9% page) and "The 2025 HTC cycle has awarded $10,591,203 Federal
Credits and $6,902,938 State Credits to fund 8 projects. These projects
will provide assistance to 774 housing units, all of which are affordable
units" (4% page). Both pages also list 1 additional row apiece
("Superior Townhomes"/"Lafayette County Housing Development, Phase 2,
LLC" on the 9% page; "Superior Golden" on the 4% page) with a BLANK
Federal/State Credit Award cell -- i.e. an application that was reviewed
but never actually funded. These 3 rows are excluded from RAW_PROJECTS
entirely (no dollar amount to show, and each page's own "N different
projects"/"fund N projects" language already excludes them from its
count), leaving exactly 19 + 8 = 27 funded developments.

HTC list vs headline
------------------------------------------------------------------------
19 (9%) + 8 (4%) = 27 developments, and 957 (9% affordable units) + 774
(4% affordable units, all of which are affordable) = 1,731 affordable
units -- BOTH exactly reproduce the annual report's own headline ("27
developments will provide 1,731 new affordable housing units in 23
communities across our state", PDF pp.4-5). This is a strong match: the
"27 developments"/"1,731 units" headline is confirmed to be exactly the
union of the two live 2025 award-list pages, not a different snapshot.

The dollar side does NOT fully reconcile, and this script does not force
it to: 9% Federal Credits $19,157,556 + 4% Federal Credits $10,591,203 +
4% State Credits $6,902,938 = $36,651,697 combined, versus the headline's
"$36,351,697" (PDF p.6, "Housing tax credits allocated"). The gap is
exactly $300,000 -- plausibly a single award adjusted/rescinded by that
amount between the headline's snapshot date and this script's retrieval
date, or a rounding/administrative-fee difference the annual report
applies that the raw award-list pages don't -- but nothing in either
source explains it, so it is reported here as-is rather than silently
forced to match (per this project's "never fabricate a missing number"
rule, which extends to never quietly editing a real number to make a
total reconcile). fy2025_actual uses the units figure (which DOES
reconcile exactly); fy2025_amounts shows the three components summing to
$36,651,697, and fy2025_source_quote documents the $300,000 gap
explicitly.

Per WHEDA's own award-list pages, no project appears on both the 9% and
4% lists (LIHTC rules do not allow the same building to draw both credit
types), so additive=False is used for a different reason than PA/OH's
"same project, multiple sources" overlap: here it is the 4% list's own
Federal+State credit pair on each of its 8 projects that overlaps (both
draw on the identical 774 units), not overlap between the 9% and 4% lists
themselves. Modeling federal/state as two subprograms lets the existing
overlap-detection logic (which operates on RAW_PROJECTS' funding_sources
lists) flag that pairing automatically.

Legislative Loans (fy2025_actual = 608 units) and More Like Home Repair &
Renew (fy2025_actual = 508 households): PDF p.6's "Legislative Loans"
box states "Infrastructure Access, Restore Main Street, and
Vacancy-to-Vitality ... Competitive lending 13 loans awarded ... Financing
$11,957,068 allocated ... Housing units 608 supported ... Communities 27
served", and the separate "More Like Home(R) Repair & Renew Loan" box
states "Loans Amount $20,791,757 ... Households 508 repaired". These are
modeled as two SEPARATE categories (not subprograms of one category)
because their disclosed unit types differ irreconcilably -- "Housing
units" (properties/apartments financed) for the competitive loan programs
versus "Households" (individual homeowners) for Repair & Renew -- and
this project's category schema carries a single unit_type per category.
No per-program breakdown of the 13 competitive loans across Infrastructure
Access/Restore Main Street/Vacancy-to-Vitality individually is disclosed
anywhere, so the Legislative Loans category has a single subprogram
carrying the combined figure, not three invented ones. Neither category
has a per-development list (no map-able detail is disclosed for either),
so both stay KPI-card-only, like Multifamily Housing above.

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
Unlike IL/PA/OH (each of which reports 2 or more discrete funds), WHEDA's
own Note 1 ("Summary of Significant Accounting Policies") states plainly:
"the Authority reports all activities within a single proprietary
enterprise fund using the accrual basis of accounting" (ACFR p.15) --
WHEDA carries no governmental funds and no multiple proprietary funds of
its own; everything that IS on WHEDA's balance sheet sits inside that one
enterprise fund. Note 1 ("Authority Programs", p.15) and Note 3
("Description of Programs", pp.18-19) further group that single fund's
internal activity by named "business segment":
  - "proprietary":
      * Single Family mortgage loans -> the "Home Ownership Mortgage Loan
        Program" / "Single Family Bond Programs" (MD&A, p.6: "The
        Authority's two largest programs are the Home Ownership Mortgage
        Loan Program (Single Family) and the Multifamily Mortgage Loan
        Program (Multifamily)"; Note 3, p.18, "Single Family Bond
        Programs: Home Ownership Revenue Bond (HORB) ... The funds are
        used to purchase mortgage loans on single family residential
        housing units"). Confidence: high, near-verbatim name match.
      * Down payment assistance -> inferred to be WHEDA's "Easy Close
        Advantage" product, a General Fund Program described in Note 3
        (p.18-19): "Easy Close Advantage is a statewide program offering
        loans ... to be used for down payment, closing costs and annual
        or single paid mortgage insurance premium" -- the ACFR's own
        outstanding-balance figures for this program ($12.2M/$14.3M) are
        in the same order of magnitude as, but not identical to, the
        annual report's $10,948,456 FY2025 fundings figure (a stock vs.
        flow difference is expected). The annual report never uses the
        brand name "Easy Close Advantage" verbatim, so this match is by
        program description, confidence: medium.
      * Multifamily lending -> the "Multifamily Mortgage Loan Program" /
        "Multifamily Bond Programs" + "Housing Revenue Bond Programs"
        (MD&A p.6, same sentence as Single Family above; Note 3, p.18,
        "Housing Revenue Bond Programs" + "Multifamily Bond Programs:
        Multifamily Housing Bonds (MHB) ... The funds are used to finance
        multifamily mortgage loans for certain eligible projects").
        Confidence: high.
      * Legislative Loans (Infrastructure Access/Restore Main Street/
        Vacancy-to-Vitality) and More Like Home Repair & Renew -> the
        "State of Wisconsin Programs" business segment's "Legislative
        Programs investment portfolio" (Note 3, p.18-19: "The affordable
        housing development program allocations include: $275.0 million
        to the Infrastructure Access Loan Program (Act 14) ... $100.0
        million to the Restore Main Street Program (Act 15) ... $100.0
        million to the Vacancy to Vitality Program (Act 18) ... and $50.0
        million to the More Like Home Program (Act 17)"; Note 4, p.20,
        "The Legislative Programs investment portfolio was created in
        fiscal year 2024 for the State of Wisconsin 2023-25 Biennial
        Budget allocation of $525.0 million ... to be administered by the
        Authority"). This $525.0 million allocation is one of WHEDA's own
        six named investment portfolios and is carried on WHEDA's own
        Statements of Net Position -- unlike PA's PHARE fund or OH's
        HDAP-adjacent grants, it is squarely inside WHEDA's own
        proprietary enterprise fund, not an off-balance-sheet pass
        through. Confidence: high, near-verbatim Act-number and dollar
        match.
  - "off_balance_sheet":
      * Both 9% and 4% Housing Tax Credits (federal and state) -- the
        credit VALUE itself is allocated directly to developers/investors
        and is confirmed never booked as a WHEDA fund asset or liability;
        the ACFR's only tax-credit-adjacent balance is *administrative
        fee* income for running the program ("Federal Tax Credit Program
        $4.9 million $6.0 million" under "Other Income", Note 1, p.16) --
        the fee revenue sits inside WHEDA's General Fund business segment,
        but the credits allocated to developers do not, matching this
        pilot series' identical IL/PA/OH LIHTC treatment. The ACFR
        confirms WHEDA administers, but does not itself fund, the state
        credit too (Note 2, p.17: "the Authority announced an award of
        $6.9 million in state housing tax credits to fund housing
        developments across Wisconsin").

Geocoding
------------------------------------------------------------------------
The HTC award-list pages give only City + County for each development (no
street address column at all). Query: "{City}, {County} County, WI" via
Nominatim (OpenStreetMap), falling back to "{City}, WI" if the
county-qualified query returns nothing. geocode_status is set to
"city_center" for every successfully-resolved project (this is the
highest precision this state's own disclosed data supports -- never "ok")
and "unresolved" for any that fail both attempts. Self-throttled to <=1
request/second with an identifying User-Agent, per Nominatim's usage
policy, matching this pilot series' IL/PA/OH build scripts.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "wi_program_activity.json"

SOURCE_URL = "https://www.wheda.com/about-wheda/annual-report--financials/annual-report-2025"
SOURCE_FILE = "WI_WHEDA_AnnualReport_FY2025.pdf (+ 2025 9%/4% HTC Award List pages)"
RETRIEVED = "2026-08-14"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
GEOCODER_USER_AGENT = "us-hfa-data-map/1.0 (github.com/MD-ai-fin/us-hfa-data-map)"

# fy2026 uniform shape: {value, amount, closed, note_key} -- see IL/PA/OH
# build scripts' identical convention. WHEDA's FY2024-2025 Annual Report
# contains no FY2026 projections anywhere (checked via full-text search of
# the 10-page PDF for "2026"/"projected"/"upcoming" -- the only "future
# fiscal years" language is a generic disclaimer that some already-awarded
# HTC/competitive loans "may close" in a later fiscal year, not a numeric
# forecast), so every fy2026 field below is the same all-pending
# placeholder; nothing is invented.
_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "wiFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "single_family_homeownership",
        "unit_type": "households",
        "fy2025_actual": 2323,
        "fy2025_source_quote": (
            "\"WHEDA BY THE NUMBERS ... Single Family Housing: Mortgage lending "
            "$481,116,311; Down payment assistance $10,948,456; Mortgages closed "
            "2,323.\" (Annual Report Fiscal Year 2024-2025, p.6). Down payment "
            "assistance is a dollar amount only -- no separate loan count is "
            "disclosed -- and rides on a subset of the 2,323 closed mortgages, not "
            "a partition of it."
        ),
        "fy2025_amounts": [
            {"label_key": "wi_amt_sf_mortgage_lending", "amount": 481116311},
            {"label_key": "wi_amt_sf_downpayment_assist", "amount": 10948456},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "sf_mortgage_loans", "fy2025_units": 2323, "fy2025_amount": 481116311,
             "color_group": "bond",
             # MD&A (p.6): "The Authority's two largest programs are the Home
             # Ownership Mortgage Loan Program (Single Family) ..."; Note 3
             # "Single Family Bond Programs" (p.18) describes the same
             # bond-funded mortgage-purchase activity.
             "fund_type": "proprietary", "fund_name": "Home Ownership Mortgage Loan Program (Single Family Bond Programs)",
             "fy2026": _FY26_PENDING},
            {"key": "sf_downpayment_assistance", "fy2025_units": None, "fy2025_amount": 10948456,
             "color_group": "capital",
             # Inferred to be WHEDA's "Easy Close Advantage" General Fund
             # Program (Note 3, p.18-19: "offering loans ... to be used for
             # down payment, closing costs and annual or single paid
             # mortgage insurance premium") -- the annual report never uses
             # the brand name verbatim, confidence: medium.
             "fund_type": "proprietary", "fund_name": "General Fund Programs (Easy Close Advantage, inferred)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "multifamily_housing",
        "unit_type": "units",
        "fy2025_actual": 1410,
        "fy2025_source_quote": (
            "\"WHEDA BY THE NUMBERS ... Multifamily Housing: Multifamily Lending "
            "$173,559,662.48; Developments financed 28; Loans closed 83; Housing "
            "units created 1,410.\" (Annual Report Fiscal Year 2024-2025, p.6). No "
            "per-development list is published for this category (unlike Housing "
            "Tax Credits below), so no project-level bubble-map detail is shown "
            "for it -- only the KPI card."
        ),
        "fy2025_amounts": [
            {"label_key": "wi_amt_mf_lending", "amount": 173559662.48},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "mf_lending", "fy2025_units": 1410, "fy2025_amount": 173559662.48,
             "color_group": "bond",
             # MD&A (p.6) + Note 3 "Housing Revenue Bond Programs"/
             # "Multifamily Bond Programs" (p.18): "The funds are used to
             # finance multifamily mortgage loans for certain eligible
             # projects."
             "fund_type": "proprietary", "fund_name": "Multifamily Mortgage Loan Program (Multifamily/Housing Revenue Bond Programs)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "housing_tax_credits",
        "unit_type": "units",
        "fy2025_actual": 1731,
        "fy2025_source_quote": (
            "\"In total, 27 developments will provide 1,731 new affordable "
            "housing units in 23 communities across our state.\" (Governor's and "
            "Executive Director's messages, pp.4-5); \"Housing tax credits "
            "allocated $36,351,697; Developments supported 27; Housing units "
            "supported 1,731\" (p.6). Cross-checked against the live 2025 9% and "
            "4% HTC Award List pages: 19 funded 9% projects (957 of 967 total "
            "units affordable, $19,157,556 Federal Credits) + 8 funded 4% "
            "projects (774 of 774 total units affordable, $10,591,203 Federal + "
            "$6,902,938 State Credits) = 27 developments, 1,731 affordable units "
            "-- both EXACTLY matching the headline. The combined dollar total of "
            "the two award lists ($36,651,697) is $300,000 higher than the "
            "headline's $36,351,697; neither source explains the gap, so it is "
            "reported here rather than forced to reconcile."
        ),
        "fy2025_amounts": [
            {"label_key": "wi_amt_htc_federal_9pct", "amount": 19157556},
            {"label_key": "wi_amt_htc_federal_4pct", "amount": 10591203},
            {"label_key": "wi_amt_htc_state_4pct", "amount": 6902938},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "htc_9pct", "fy2025_units": 957, "fy2025_amount": 19157556,
             "color_group": "credit",
             # Never appears as a WHEDA-carried balance in the ACFR (checked
             # "Housing Tax Credit"/"LIHTC"/"9%" -- the only match is
             # administrative fee income, "Federal Tax Credit Program
             # $4.9 million", Note 1 "Other Income", p.16) -- federal tax
             # credits are allocated directly to developers/investors.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "htc_4pct_federal", "fy2025_units": 774, "fy2025_amount": 10591203,
             "color_group": "credit",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "htc_4pct_state", "fy2025_units": 774, "fy2025_amount": 6902938,
             "color_group": "credit",
             # Note 2, "Authorizing Legislation and Funds" (p.17): "the
             # Authority announced an award of $6.9 million in state housing
             # tax credits to fund housing developments across Wisconsin" --
             # an administered award, not a WHEDA fund asset.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "legislative_loans",
        "unit_type": "units",
        "fy2025_actual": 608,
        "fy2025_source_quote": (
            "\"Legislative Loans: Infrastructure Access, Restore Main Street, and "
            "Vacancy-to-Vitality ... Competitive lending 13 loans awarded; "
            "Financing $11,957,068 allocated; Housing units 608 supported; "
            "Communities 27 served.\" (Annual Report Fiscal Year 2024-2025, p.6). "
            "No breakdown of the 13 loans across the three named programs is "
            "disclosed, so a single combined subprogram is shown rather than "
            "three invented ones."
        ),
        "fy2025_amounts": [
            {"label_key": "wi_amt_legislative_loans", "amount": 11957068},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "legislative_competitive_loans", "fy2025_units": 608, "fy2025_amount": 11957068,
             "color_group": "capital",
             # Note 3 (pp.18-19): "$275.0 million to the Infrastructure
             # Access Loan Program (Act 14) ... $100.0 million to the
             # Restore Main Street Program (Act 15) ... $100.0 million to
             # the Vacancy to Vitality Program (Act 18)"; Note 4 (p.20): the
             # "Legislative Programs investment portfolio was created in
             # fiscal year 2024 for the State of Wisconsin 2023-25 Biennial
             # Budget allocation of $525.0 million ... administered by the
             # Authority" -- carried inside WHEDA's own single proprietary
             # enterprise fund.
             "fund_type": "proprietary", "fund_name": "State of Wisconsin Programs (Legislative Programs investment portfolio -- Act 14/15/18)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "more_like_home_repair_renew",
        "unit_type": "households",
        "fy2025_actual": 508,
        "fy2025_source_quote": (
            "\"More Like Home(R) Repair & Renew Loan: Loans Amount $20,791,757; "
            "Households 508 repaired.\" (Annual Report Fiscal Year 2024-2025, "
            "p.6). Modeled as a category separate from Legislative Loans above "
            "because it discloses a household count, not a housing-unit count, "
            "and this project's category schema carries one unit_type per "
            "category."
        ),
        "fy2025_amounts": [
            {"label_key": "wi_amt_more_like_home", "amount": 20791757},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "more_like_home_loans", "fy2025_units": 508, "fy2025_amount": 20791757,
             "color_group": "capital",
             # Note 3 (p.18): "$50.0 million to the More Like Home Program
             # (Act 17) single family housing rehabilitation loans" -- same
             # Legislative Programs investment portfolio as legislative_loans
             # above, carried inside WHEDA's own single proprietary
             # enterprise fund.
             "fund_type": "proprietary", "fund_name": "State of Wisconsin Programs (Legislative Programs investment portfolio -- Act 17 More Like Home)",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# ---------------------------------------------------------------------------
# Housing Tax Credit project-level detail (2025 9% and 4% HTC Award List
# pages). One row per funded development; address is always None (both
# pages give only City + County, no street address column).
# (name, city, county, total_units, affordable_units, [(source_key, amount), ...])
# ---------------------------------------------------------------------------

RAW_PROJECTS = [
    # -- 2025 9% HTC Award List (19 funded projects; excludes 2 rows with a
    # blank award: "Superior Townhomes" and "Lafayette County Housing
    # Development, Phase 2, LLC") --
    ("Brillion Housing Redevelopment Phase 2, LLC", "Brillion", "Calumet", 47, 47,
     [("htc_9pct", 681655)]),
    ("Broadway Senior", "Monona", "Dane", 55, 55,
     [("htc_9pct", 1172800)]),
    ("Brookstone Townhomes", "Fitchburg", "Dane", 28, 24,
     [("htc_9pct", 399138)]),
    ("Corner View Cottages", "Kiel", "Manitowoc", 44, 44,
     [("htc_9pct", 1023373)]),
    ("Driftless Lofts", "Baraboo", "Sauk", 56, 56,
     [("htc_9pct", 1200000)]),
    ("Fairview Crossing Apartments", "Plymouth", "Sheboygan", 64, 64,
     [("htc_9pct", 999771)]),
    ("Hearthside Commons Apartments", "Neenah", "Winnebago", 60, 54,
     [("htc_9pct", 764462)]),
    ("Hilltop Apartments", "DeForest", "Dane", 50, 50,
     [("htc_9pct", 1077749)]),
    ("Oak Ridge Fitchburg", "Fitchburg", "Dane", 80, 80,
     [("htc_9pct", 1200000)]),
    ("Oregon Main Apartments", "Oregon", "Dane", 57, 57,
     [("htc_9pct", 1200000)]),
    ("Rivers Crossing Apartment Homes", "Portage", "Columbia", 52, 52,
     [("htc_9pct", 1200000)]),
    ("Riverside Apartments", "Beloit", "Rock", 55, 55,
     [("htc_9pct", 1200000)]),
    ("Riverview Senior Living", "Rhinelander", "Oneida", 48, 48,
     [("htc_9pct", 1126121)]),
    ("Somerset Eco-Cottages", "Somerset", "St. Croix", 40, 40,
     [("htc_9pct", 840535)]),
    ("Stageline Eco, LLC", "Hudson", "St. Croix", 38, 38,
     [("htc_9pct", 804960)]),
    ("The Avenue", "Sturgeon Bay", "Door", 39, 39,
     [("htc_9pct", 927244)]),
    ("Valley View", "River Falls", "St. Croix", 50, 50,
     [("htc_9pct", 1071800)]),
    ("Wauwatosa North Apartments", "Wauwatosa", "Milwaukee", 55, 55,
     [("htc_9pct", 1200000)]),
    ("White Label Lofts", "Oshkosh", "Winnebago", 49, 49,
     [("htc_9pct", 1067948)]),
    # -- 2025 4% HTC Award List (8 funded projects; excludes 1 row with a
    # blank award, "Superior Golden") --
    ("2711 W Wells", "Milwaukee", "Milwaukee", 124, 124,
     [("htc_4pct_federal", 1775029), ("htc_4pct_state", 874388)]),
    ("4220 35th", "Kenosha", "Kenosha", 94, 94,
     [("htc_4pct_federal", 1163827), ("htc_4pct_state", 851600)]),
    ("Austin Commons", "Milwaukee", "Milwaukee", 100, 100,
     [("htc_4pct_federal", 1064006), ("htc_4pct_state", 797851)]),
    ("Fox Meadowview", "Kenosha", "Kenosha", 144, 144,
     [("htc_4pct_federal", 1859920), ("htc_4pct_state", 1200000)]),
    ("Maritime Flats", "Manitowoc", "Manitowoc", 59, 59,
     [("htc_4pct_federal", 975873), ("htc_4pct_state", 541332)]),
    ("Midtown Commons", "Milwaukee", "Milwaukee", 100, 100,
     [("htc_4pct_federal", 1429173), ("htc_4pct_state", 915905)]),
    ("The Argus Apartments", "Verona", "Dane", 60, 60,
     [("htc_4pct_federal", 716109), ("htc_4pct_state", 537082)]),
    ("Timberline Terrace", "Madison", "Dane", 93, 93,
     [("htc_4pct_federal", 1607266), ("htc_4pct_state", 1184780)]),
]

FUNDING_COLOR_GROUP = {
    "htc_9pct": "credit", "htc_4pct_federal": "credit", "htc_4pct_state": "credit",
}
FUNDING_PRIORITY = ["htc_9pct", "htc_4pct_federal", "htc_4pct_state"]

# Independently-published totals (each award-list page's own printed totals
# sentence) used as verification gates -- see docstring "HTC list vs
# headline".
EXPECTED_TOTALS = {
    "htc_9pct":        {"count": 19, "amount": 19157556, "total_units": 967, "affordable_units": 957},
    "htc_4pct_federal": {"count": 8, "amount": 10591203, "total_units": 774, "affordable_units": 774},
    "htc_4pct_state":   {"count": 8, "amount": 6902938, "total_units": 774, "affordable_units": 774},
}


def verify_htc_lists():
    errors = []
    if len(RAW_PROJECTS) != 27:
        errors.append(f"project count: expected 27, got {len(RAW_PROJECTS)}")

    sums = {k: {"count": 0, "amount": 0, "total_units": 0, "affordable_units": 0} for k in EXPECTED_TOTALS}
    for name, _city, _county, total_units, aff_units, sources in RAW_PROJECTS:
        for key, amount in sources:
            sums[key]["count"] += 1
            sums[key]["amount"] += amount
            sums[key]["total_units"] += total_units
            sums[key]["affordable_units"] += aff_units

    for key, expected in EXPECTED_TOTALS.items():
        got = sums[key]
        for field, exp_val in expected.items():
            if got[field] != exp_val:
                errors.append(f"{key} {field}: expected {exp_val:,}, got {got[field]:,}")

    developments = len(RAW_PROJECTS)
    if developments != 27:
        errors.append(f"total developments: expected 27, got {developments}")

    affordable_total = sum(aff for _n, _c, _co, _t, aff, _s in RAW_PROJECTS)
    if affordable_total != 1731:
        errors.append(f"total affordable units: expected 1,731 (matches annual report headline), got {affordable_total:,}")

    combined_dollar_total = sums["htc_9pct"]["amount"] + sums["htc_4pct_federal"]["amount"] + sums["htc_4pct_state"]["amount"]
    if combined_dollar_total != 36651697:
        errors.append(f"combined HTC dollar total: expected 36,651,697 (9%+4%Fed+4%State), got {combined_dollar_total:,}")

    if errors:
        raise SystemExit("HTC award-list mismatch(es):\n" + "\n".join(errors))
    print(f"HTC award lists verified: {developments} developments, {affordable_total:,} affordable units "
          f"(both match the annual report's own \"27 developments / 1,731 units\" headline exactly); "
          f"combined dollar total ${combined_dollar_total:,} is $300,000 above the headline's $36,351,697 "
          f"(gap documented, not reconciled -- see module docstring).")


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
    for name, city, county, total_units, _aff_units, sources in RAW_PROJECTS:
        query = f"{city}, {county} County, WI"
        coords = geocode(query, cache)
        status = "city_center"
        if coords is None:
            coords = geocode(f"{city}, WI", cache)
            status = "city_center" if coords else "unresolved"
        funding_sources = [s for s, _amt in sources]
        primary = next((s for s in FUNDING_PRIORITY if s in funding_sources), funding_sources[0])
        source_amounts = {s: amt for s, amt in sources}
        projects.append({
            "id": name.lower().replace(" ", "-").replace(",", "").replace(".", "")
                        .replace("'", "").replace("&", "and"),
            "name": name,
            "address": None,
            "city": city,
            "lat": round(coords[0], 5) if coords else None,
            "lon": round(coords[1], 5) if coords else None,
            "units": total_units,
            "funding_sources": funding_sources,
            "source_amounts": source_amounts,
            "total_amount": sum(source_amounts.values()) if source_amounts else None,
            "primary_color_group": FUNDING_COLOR_GROUP[primary],
            "overlaps": len(funding_sources) > 1,
            "geocode_status": status,
        })
    return projects


def main():
    verify_htc_lists()
    print("Geocoding project city/county centers via Nominatim...")
    projects = build_projects()
    unresolved = [p["name"] for p in projects if p["geocode_status"] == "unresolved"]
    if unresolved:
        print(f"  {len(unresolved)} project(s) could not be geocoded: {unresolved}")
    print(f"  {sum(1 for p in projects if p['geocode_status'] == 'city_center')} "
          f"project(s) resolved to city/county-center coordinates.")

    payload = {
        "WI": {
            "hfa_name": "Wisconsin Housing and Economic Development Authority",
            "hfa_abbr": "WHEDA",
            "fiscal_year": "FY2025",
            "source_title": "WHEDA Annual Report Fiscal Year 2024-2025 -- \"WHEDA By The Numbers\" plus 2025 9%/4% HTC Award Lists",
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
