"""
Builds docs/nh_program_activity.json from New Hampshire Housing's
"Annual Report for Fiscal Year 2025" (the HFA's own program-activity
report) plus its own audited financial statements (for GASB fund-type
classification).

Sources
------------------------------------------------------------------------
1. New Hampshire Housing, "Annual Report for Fiscal Year 2025"
   (PDF, 16 pages, "JULY 1, 2024 - JUNE 30, 2025" per its back page):
     https://www.nhhousing.org/wp-content/uploads/2026/06/NH-Housing-FY25-Annual-Report.pdf
   Local copy: FY2025/program_activity/pdf/NH_NHHousing_AnnualReport_FY2025.pdf
   -- Supplies every category-level figure below (Multifamily p.4-5,
   Homeownership p.9, Assisted Housing p.12) and the two complete
   per-development project tables (p.7 "FY25 Multifamily Housing:
   Commitments & Under Construction" -- 20 developments / 1,193 units;
   p.8 "FY25 Multifamily Housing: Completed Developments" -- 15
   developments / 722 units).
2. NH Housing's own audited financial statements (used ONLY for fund-type
   classification):
     FY2024/txt/NH_NHHousing_FY2024_ACFR.txt
   This is the FY2024 edition -- the corpus has NO FY2025 txt for NH (the
   only NH-scoped txt is FY2024). NH Housing's separately-published FY2025
   audited financial statements (fiscal year ended June 30, 2025, dated
   September 29, 2025) are referenced at NHHousing.org and confirm the
   identical fund structure (see below), so the FY2024 txt is a stable,
   high-confidence cross-reference for the FY2025 fund-type mapping.

Fiscal-year verification
------------------------------------------------------------------------
The report's back page (p.16) states "FISCAL YEAR 2025 ANNUAL REPORT ...
JULY 1, 2024 - JUNE 30, 2025", so fiscal_year = "FY2025" (standard
Jul-Jun HFA fiscal year, unlike several of this pilot series' CY2025
states). Every figure used below is FY2025 (Jul 1, 2024 - Jun 30, 2025).

Category-level methodology
------------------------------------------------------------------------
Multifamily Housing (fy2025_actual = 1,915 units): p.4's own "1,915
MULTIFAMILY HOUSING UNITS IN FY25", broken down by occupancy type on the
same page into "1,636 GENERAL OCCUPANCY UNITS", "184 AGE-RESTRICTED
UNITS" and "95 SUPPORTIVE HOUSING UNITS" -- a true partition
(1,636+184+95 = 1,915), so additive=True. The occupancy breakdown is
independently re-derived from the two project tables (see
verify_project_tables) and reconciles EXACTLY against p.4's printed
1,636/184/95, so the occupancy subprograms are not merely restated --
they are verified against the underlying development rows.

Multifamily Financing (fy2025_actual = 1,152 units = LIHTC): p.5's own
"IN FY25, 15 PROJECTS WERE FUNDED WITH LIHTC RESULTING IN 1152 UNITS
(NEW AND REHABILITATED)" and "WE PROVIDED $35.8 MILLION IN TAX-EXEMPT
BOND FUNDING IN FY25". The 15 LIHTC projects are exactly the 15 LIHTC
rows in the COMMITMENTS table (5 x 9% LIHTC = 168 units + 10 x 4% LIHTC
= 984 units = 1,152 units), verified in verify_project_tables -- the
completed-development LIHTC rows (funded in prior years) are correctly
excluded, matching the report's "in FY25 ... funded with LIHTC" wording.
The 9%/4% unit split (168/984) is DERIVED from the tables (the report
prints only the combined "15 projects / 1,152 units"); it is asserted
against the printed combined figure, never against a fabricated total.
The remaining funding sources in the tables' "Funding Sources & PBVs"
column (AHF, HOME, HOME-ARP, HTF, InvestNH, ARPA, ERAP, Participation
Loan, Construction, PBV) disclose NO aggregate unit/dollar figure
anywhere in the report, so they are modeled as subprograms with null
units/amount -- a faithful taxonomy, not a fabricated number. The
category is additive=False because the funding sources heavily overlap
on individual developments (the same project routinely draws 3-7
sources; the 1,152-unit headline is the de-duplicated LIHTC count, not a
sum of the subprograms).

Single-Family Homeownership (fy2025_actual = 1,078 households): p.9's
own "Single-Family Mortgage Program: $348M TOTAL MORTGAGE LOANS, 1,078
MORTGAGE LOANS, 941 LOANS TO FIRST-TIME HOMEBUYERS" (and "we helped more
than 1,078 households purchase a home in the last year"). "941 first-
time homebuyers" is a SUBSET of the 1,078 mortgage loans (first-time
buyers are a sub-population of all buyers), not a partition, so
additive=False.

Downpayment Assistance (fy2025_actual = 584 loans): p.9's own
"Downpayment Assistance (DPA) ... $5.4M TOTAL DPA IN FY25, 584 LOANS
WITH DPA" and p.10's "1st Generation Homebuyer Program ... assisted 51
new first-generation homeowners in FY25" (a subset/overlap of the 584,
since the report notes the 1st-Gen program "can be combined with other
downpayment assistance programs"), so additive=False. NOTE: p.9 also
prints "$12.5K AVERAGE DPA PER HOMEOWNER" -- $5.4M / 584 = $9,247 per
loan, which does NOT reconcile with the printed $12.5K average (and
$12.5K x 584 = $7.3M, not $5.4M); this is a source-internal
inconsistency that is documented here rather than forced to reconcile,
per this project's "never quietly edit a real number" rule.

Housing Choice Vouchers (fy2025_actual = 4,251 households): p.12's own
"4,251 HOUSING VOUCHER HOLDERS IN FY25" / "4,251 VOUCHERS ALLOCATED TO
NH HOUSING AND ISSUED TO HOUSEHOLDS" and "$58M PROVIDED IN RENTAL
ASSISTANCE". This is the persistent per-household operating rental
subsidy (Section 8/HCV) this pilot series now tracks as a distinct
category from one-time multifamily capital. The "8,900 applications on
waiting list", "8% attrition", and "$19,806 average income" figures are
contextual, not KPIs, and are not surfaced as categories.

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
NH Housing reports under a SINGLE accounting basis: the proprietary-fund
concept, full accrual -- NOT governmental funds. FY2024 ACFR Note 2
("Basis of Presentation", p.14): "NH Housing's financial statements have
been prepared on the basis of the proprietary-fund concept ... NH Housing
follows the accrual basis of accounting." The same note: "The financial
statements encompass NH Housing's general funds and both single family
and multi-family bond programs." Because NH Housing carries no
governmental funds, everything that appears on its balance sheet is, by
GASB definition, proprietary -- with one exception (LIHTC credits):
  - "off_balance_sheet": LIHTC (9% and 4%). The ACFR's only LIHTC
    mention describes it as an administered program -- "NH Housing offers
    and administers a variety of programs ... Low Income Housing Tax
    Credits and the HOME Investment Partnership Program" (FY2024 ACFR,
    MD&A p.4) -- the federal credits are allocated directly to
    developers/investors and are never booked as an NH Housing fund
    asset, matching this pilot series' identical IL/PA/WI LIHTC
    treatment. Confidence: high.
  - "proprietary":
      * Tax-Exempt Bonds -> the "multi-family bond programs" (FY2024
        ACFR Note 2). Confidence: high.
      * Participation Loan / Construction -> NH Housing's own
        multi-family lending, carried in the general funds / bond
        programs. Confidence: high (near-verbatim "multi-family bond
        programs ... finance multifamily mortgage loans" language).
      * Single-Family mortgages -> the "single family bond programs"
        (FY2024 ACFR Note 2; the FY2025 ACFR's MD&A confirms NH Housing
        "continued issuing tax-exempt bonds ... to fund single family
        loans"). Confidence: high.
      * Downpayment assistance (DPA) + 1st-Generation -> NH Housing's own
        single-family assistance lending in the general funds. Confidence:
        medium (the annual report never names a specific fund for DPA;
        classified by program description).
      * AHF / HOME / HOME-ARP / HTF / InvestNH / ARPA / ERAP -> federal/
        state PASS-THROUGH grants. FY2024 ACFR MD&A (p.5) reports "escrow
        funds held in federal and state grant programs awaiting
        disbursement", and the notes state "NH Housing receives various
        other pass-through grants to support housing programs" -- these
        grant funds sit on NH Housing's balance sheet (as restricted/
        escrow cash in the general funds), not off it, so they are
        proprietary (pass-through) rather than off_balance_sheet.
        Confidence: medium-high (FY2024 ACFR language is clear; the
        FY2025 ACFR's "Grants and subsidies $32.9M revenue / $40.8M
        expense" confirms the same on-book pass-through treatment).
      * PBV (project-based vouchers) and the HCV voucher category -> the
        "Federal rental assistance programs" that NH Housing administers
        for HUD. FY2024 ACFR Note on operations (p.16): "The financial
        assistance received and disbursed on behalf of program
        participants is reflected as both an operating revenue and
        expense" -- i.e. pass-through HUD money carried on NH Housing's
        proprietary books as operating revenue/expense, not a separate
        governmental fund. Confidence: high.

Geocoding
------------------------------------------------------------------------
The two project tables give only "Location" (city/town), not street
addresses, so every project is geocoded at city-center precision:
query "{city}, NH" (falling back to "{city}, New Hampshire"), with
geocode_status="city_center" for every successful resolve -- never "ok"
(the source discloses no street-level data). Self-throttled to <=1
request/second with an identifying User-Agent, per Nominatim's usage
policy, matching this pilot series' other build scripts.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "nh_program_activity.json"

SOURCE_URL = "https://www.nhhousing.org/wp-content/uploads/2026/06/NH-Housing-FY25-Annual-Report.pdf"
SOURCE_FILE = "NH_NHHousing_AnnualReport_FY2025.pdf"
RETRIEVED = "2026-08-16"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
GEOCODER_USER_AGENT = "us-hfa-data-map/1.0 (github.com/MD-ai-fin/us-hfa-data-map)"
# Persisted geocode cache: Nominatim is rate-limited (1 req/sec) and, when
# several states of this batch geocode concurrently against the shared public
# instance, a bare re-run can trip HTTP 429 and drop coordinates. The first
# run populates this file; every later run reads it and never touches the
# network, guaranteeing a byte-identical, deterministic output (same
# convention as this batch's other build scripts, e.g. GA/UT).
GEOCODE_CACHE_PATH = Path(__file__).resolve().parent / "nh_geocode_cache.json"

# fy2026 uniform shape. NH Housing's FY2025 annual report contains no
# FY2026 projections anywhere (no forward-looking unit/dollar figure is
# disclosed), so every fy2026 field below is the same all-pending
# placeholder; nothing is invented.
_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "nhFy26NotePending"}


# ---------------------------------------------------------------------------
# Category-level data
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "multifamily_housing",
        "unit_type": "units",
        "fy2025_actual": 1915,
        "fy2025_source_quote": (
            "\"1,915 MULTIFAMILY HOUSING UNITS IN FY25\" ... \"1,636 GENERAL "
            "OCCUPANCY UNITS\" ... \"184 AGE-RESTRICTED UNITS\" ... \"95 "
            "SUPPORTIVE HOUSING UNITS\" (Annual Report for Fiscal Year 2025, "
            "p.4), plus \"In FY 2025, the Multifamily Housing Division supported "
            "20 projects across the state.\" The occupancy breakdown is a true "
            "partition (1,636 + 184 + 95 = 1,915) and is independently re-derived "
            "from the two project tables (p.7 Commitments & Under Construction: "
            "20 developments / 1,193 units; p.8 Completed Developments: 15 "
            "developments / 722 units) -- 35 developments / 1,915 units total, "
            "which by occupancy type reconcile to exactly 1,636 general / 184 "
            "age-restricted / 95 supportive."
        ),
        "fy2025_amounts": [],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            # Occupancy-type subprograms: a true partition of the 1,915-unit
            # headline (the report's own primary breakdown). "mixed" because an
            # occupancy type is not a GASB fund -- each spans multiple funding
            # sources (LIHTC credits [off_balance_sheet] + bonds/grants/loans
            # [proprietary]), matching IL's "mixed" convention.
            {"key": "general_occupancy", "fy2025_units": 1636, "fy2025_amount": None,
             "color_group": "bond", "fund_type": "mixed", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "age_restricted", "fy2025_units": 184, "fy2025_amount": None,
             "color_group": "bond", "fund_type": "mixed", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "supportive_housing", "fy2025_units": 95, "fy2025_amount": None,
             "color_group": "trust", "fund_type": "mixed", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "multifamily_financing",
        "unit_type": "units",
        "fy2025_actual": 1152,
        "fy2025_source_quote": (
            "\"IN FY25, 15 PROJECTS WERE FUNDED WITH LIHTC RESULTING IN 1152 "
            "UNITS (NEW AND REHABILITATED)\" and \"WE PROVIDED $35.8 MILLION IN "
            "TAX-EXEMPT BOND FUNDING IN FY25\" (Annual Report for Fiscal Year "
            "2025, p.5). The 15 LIHTC projects are exactly the 15 LIHTC rows in "
            "the p.7 Commitments table (5 x 9% LIHTC = 168 units + 10 x 4% LIHTC "
            "= 984 units = 1,152 units; the 9%/4% split is derived from the "
            "table's funding-source column and asserted against the printed "
            "combined 15/1,152). The other funding sources (AHF/HOME/HOME-ARP/"
            "HTF/InvestNH/ARPA/ERAP/Participation Loan/Construction/PBV) disclose "
            "no aggregate unit or dollar figure anywhere in the report, so their "
            "unit/amount fields are null (an honest taxonomy, not a fabricated "
            "number)."
        ),
        "fy2025_amounts": [
            {"label_key": "nh_amt_tax_exempt_bonds", "amount": 35800000},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            # LIHTC credits are allocated directly to developers/investors and
            # never booked as an NH Housing fund asset (FY2024 ACFR MD&A p.4:
            # "NH Housing offers and administers ... Low Income Housing Tax
            # Credits ..." -- an administered program, not a fund balance).
            {"key": "lihtc_9", "fy2025_units": 168, "fy2025_amount": None,
             "color_group": "credit", "fund_type": "off_balance_sheet",
             "fund_name": None, "fy2026": _FY26_PENDING},
            {"key": "lihtc_4", "fy2025_units": 984, "fy2025_amount": None,
             "color_group": "credit", "fund_type": "off_balance_sheet",
             "fund_name": None, "fy2026": _FY26_PENDING},
            # NH Housing's own multi-family bond programs (FY2024 ACFR Note 2,
            # "multi-family bond programs").
            {"key": "texb", "fy2025_units": None, "fy2025_amount": 35800000,
             "color_group": "bond", "fund_type": "proprietary",
             "fund_name": "Multi-family Bond Programs", "fy2026": _FY26_PENDING},
            # Federal/state pass-through grants held in NH Housing's general
            # funds as restricted/escrow cash (FY2024 ACFR MD&A p.5: "escrow
            # funds held in federal and state grant programs awaiting
            # disbursement"; notes: "NH Housing receives various other
            # pass-through grants"). On-book, so proprietary (pass-through).
            {"key": "ahf", "fy2025_units": None, "fy2025_amount": None,
             "color_group": "trust", "fund_type": "proprietary",
             "fund_name": "General Funds (state Affordable Housing Fund pass-through)",
             "fy2026": _FY26_PENDING},
            {"key": "home", "fy2025_units": None, "fy2025_amount": None,
             "color_group": "trust", "fund_type": "proprietary",
             "fund_name": "General Funds (HOME pass-through)", "fy2026": _FY26_PENDING},
            {"key": "home_arp", "fy2025_units": None, "fy2025_amount": None,
             "color_group": "trust", "fund_type": "proprietary",
             "fund_name": "General Funds (HOME-ARP pass-through)", "fy2026": _FY26_PENDING},
            {"key": "htf", "fy2025_units": None, "fy2025_amount": None,
             "color_group": "trust", "fund_type": "proprietary",
             "fund_name": "General Funds (Housing Trust Fund pass-through)",
             "fy2026": _FY26_PENDING},
            {"key": "investnh", "fy2025_units": None, "fy2025_amount": None,
             "color_group": "capital", "fund_type": "proprietary",
             "fund_name": "General Funds (InvestNH ARPA SLFRF pass-through)",
             "fy2026": _FY26_PENDING},
            {"key": "arpa", "fy2025_units": None, "fy2025_amount": None,
             "color_group": "capital", "fund_type": "proprietary",
             "fund_name": "General Funds (ARPA pass-through)", "fy2026": _FY26_PENDING},
            {"key": "erap", "fy2025_units": None, "fy2025_amount": None,
             "color_group": "capital", "fund_type": "proprietary",
             "fund_name": "General Funds (Emergency Rental Assistance pass-through)",
             "fy2026": _FY26_PENDING},
            # NH Housing's own multi-family lending (carried in the general
            # funds / bond programs).
            {"key": "participation_loan", "fy2025_units": None, "fy2025_amount": None,
             "color_group": "capital", "fund_type": "proprietary",
             "fund_name": "General Funds (participation lending)", "fy2026": _FY26_PENDING},
            {"key": "construction", "fy2025_units": None, "fy2025_amount": None,
             "color_group": "capital", "fund_type": "proprietary",
             "fund_name": "General Funds (construction financing)", "fy2026": _FY26_PENDING},
            # HUD project-based vouchers administered for HUD -- pass-through
            # subsidy reflected as operating revenue/expense on NH Housing's
            # proprietary books (FY2024 ACFR p.16).
            {"key": "pbv", "fy2025_units": None, "fy2025_amount": None,
             "color_group": "trust", "fund_type": "proprietary",
             "fund_name": "Federal rental assistance programs (administered for HUD)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "single_family_homeownership",
        "unit_type": "households",
        "fy2025_actual": 1078,
        "fy2025_source_quote": (
            "\"Single-Family Mortgage Program: $348M TOTAL MORTGAGE LOANS, 1,078 "
            "MORTGAGE LOANS, 941 LOANS TO FIRST-TIME HOMEBUYERS\" (Annual Report "
            "for Fiscal Year 2025, p.9); \"we helped more than 1,078 households "
            "purchase a home in the last year.\" The 941 first-time-homebuyer "
            "loans are a SUBSET of the 1,078 total mortgage loans (first-time "
            "buyers are a sub-population of all borrowers), not a partition, so "
            "additive=False."
        ),
        "fy2025_amounts": [
            {"label_key": "nh_amt_mortgage_loans", "amount": 348000000},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            # NH Housing's single family bond programs (FY2024 ACFR Note 2,
            # "single family bond programs"; the FY2025 ACFR MD&A confirms NH
            # Housing "continued issuing tax-exempt bonds ... to fund single
            # family loans").
            {"key": "first_mortgages", "fy2025_units": 1078, "fy2025_amount": 348000000,
             "color_group": "bond", "fund_type": "proprietary",
             "fund_name": "Single Family Bond Programs", "fy2026": _FY26_PENDING},
            {"key": "first_time_homebuyers", "fy2025_units": 941, "fy2025_amount": None,
             "color_group": "bond", "fund_type": "proprietary",
             "fund_name": "Single Family Bond Programs (first-time subset)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "downpayment_assistance",
        "unit_type": "households",
        "fy2025_actual": 584,
        "fy2025_source_quote": (
            "\"Downpayment Assistance (DPA) ... $5.4M TOTAL DPA IN FY25, 584 "
            "LOANS WITH DPA, $12.5K AVERAGE DPA PER HOMEOWNER\" (Annual Report "
            "for Fiscal Year 2025, p.9); \"we provided over $5.4 million in "
            "self-generated downpayment assistance.\" The 1st Generation "
            "Homebuyer Program \"assisted 51 new first-generation homeowners in "
            "FY25\" (p.10) and \"can be combined with other downpayment "
            "assistance programs\", so additive=False. NOTE: $5.4M / 584 = "
            "$9,247 per loan, which does not reconcile with the printed $12.5K "
            "average (and $12.5K x 584 = $7.3M); this source-internal "
            "inconsistency is documented here, not reconciled."
        ),
        "fy2025_amounts": [
            {"label_key": "nh_amt_dpa", "amount": 5400000},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            # NH Housing's own down-payment/closing-cost assistance lending
            # (the "Home First" MRB program), carried in the general funds /
            # single family programs. No single named fund is disclosed for DPA
            # in the annual report -- classified by program description,
            # confidence: medium.
            {"key": "dpa_loans", "fy2025_units": 584, "fy2025_amount": 5400000,
             "color_group": "capital", "fund_type": "proprietary",
             "fund_name": "General Funds (Home First DPA, inferred)",
             "fy2026": _FY26_PENDING},
            {"key": "first_generation", "fy2025_units": 51, "fy2025_amount": None,
             "color_group": "capital", "fund_type": "proprietary",
             "fund_name": "General Funds (1st Generation Homebuyer Program, inferred)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "housing_choice_voucher",
        "unit_type": "households",
        "fy2025_actual": 4251,
        "fy2025_source_quote": (
            "\"4,251 HOUSING VOUCHER HOLDERS IN FY25\" / \"4,251 VOUCHERS "
            "ALLOCATED TO NH HOUSING AND ISSUED TO HOUSEHOLDS\" and \"$58M "
            "PROVIDED IN RENTAL ASSISTANCE\" (Annual Report for Fiscal Year "
            "2025, p.12). This is the persistent per-household Section 8/HCV "
            "operating rental subsidy -- a categorically different population "
            "from the one-time multifamily capital programs, kept as its own "
            "category per this project's rental-assistance convention."
        ),
        "fy2025_amounts": [
            {"label_key": "nh_amt_rental_assistance", "amount": 58000000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            # HUD Housing Choice Voucher subsidies administered for HUD and
            # reflected as operating revenue/expense on NH Housing's
            # proprietary books (FY2024 ACFR p.16: "The financial assistance
            # received and disbursed on behalf of program participants is
            # reflected as both an operating revenue and expense").
            {"key": "vouchers", "fy2025_units": 4251, "fy2025_amount": 58000000,
             "color_group": "trust", "fund_type": "proprietary",
             "fund_name": "Federal rental assistance programs (administered for HUD)",
             "fy2026": _FY26_PENDING},
        ],
    },
]


# ---------------------------------------------------------------------------
# Multifamily project-level detail (the two complete project tables, p.7 and
# p.8). One row per development: (name, city, units, occupancy_type, status,
# [funding source keys]). "occupancy_type" is "general" | "age_restricted" |
# "supportive" (the two "Supportive Housing/ Veteran Housing" rows in the
# completed table are classified supportive); "status" is "commitment"
# (p.7 Commitments & Under Construction) | "completed" (p.8 Completed
# Developments). Funding sources preserve the table's own printed order
# (the first source is the "lead" source and drives the bubble-marker color
# via the frontend's primaryColorGroup -> funding_sources[0] lookup). No
# per-development dollar amount is disclosed anywhere in the report, so
# source_amounts/total_amount are left empty/None rather than invented.
#
# NOTE on two rows where the PDF's text layer concatenates "Tax-Exempt Bonds"
# and "Construction" without a comma ("Tax-Exempt Bonds Construction" --
# Roosevelt West and Elms Farms Housing): "Construction" is a distinct NH
# Housing funding source (it appears standalone in "Construction, AHF, PBV"
# for 6 South State Street and "9% LIHTC, Construction, Participation Loan"
# for Hillsborough Heights), so both are transcribed as separate sources.
# ---------------------------------------------------------------------------

RAW_PROJECTS = [
    # -- FY25 Commitments & Under Construction (p.7): 20 developments / 1,193 units --
    ("106 Roxbury Street", "Keene", 16, "supportive", "commitment", ["ahf"]),
    ("6 South State Street", "Concord", 8, "supportive", "commitment",
     ["construction", "ahf", "pbv"]),
    ("Avery Lane Apartments Phase I", "Nashua", 32, "general", "commitment",
     ["lihtc_9", "participation_loan", "investnh"]),
    ("Avery Lane Apartments Phase II", "Nashua", 63, "general", "commitment",
     ["texb", "lihtc_4", "home_arp", "ahf", "pbv"]),
    ("Concord & Royal Gardens", "Concord", 300, "general", "commitment",
     ["texb", "lihtc_4", "ahf"]),
    ("Ernie Clark Senior Housing", "Newmarket", 30, "age_restricted", "commitment",
     ["lihtc_9", "participation_loan", "home", "htf"]),
    ("Harriman Hill Phase III", "Wolfeboro", 30, "general", "commitment",
     ["lihtc_9", "participation_loan", "ahf", "investnh"]),
    ("Haven at the Falls", "Dover", 6, "supportive", "commitment",
     ["construction", "participation_loan", "ahf"]),
    ("Jameson Street Apartments", "Laconia", 3, "supportive", "commitment", ["ahf"]),
    ("Maynard Homes Redevelopment Phase I 4%", "Nashua", 133, "general", "commitment",
     ["texb", "lihtc_4", "ahf", "home_arp", "investnh", "pbv"]),
    ("Maynard Homes Redevelopment Phase I 9%", "Nashua", 46, "general", "commitment",
     ["lihtc_9", "participation_loan", "ahf"]),
    ("McIntosh West Apartments", "Dover", 78, "general", "commitment",
     ["texb", "lihtc_4", "ahf"]),
    ("Province Street Apartments", "Laconia", 90, "general", "commitment",
     ["texb", "lihtc_4", "ahf", "home_arp", "htf", "pbv"]),
    ("Redberry Farm Apartments Phase II", "Epping", 8, "supportive", "commitment",
     ["ahf"]),
    ("Roosevelt East", "Keene", 30, "general", "commitment",
     ["lihtc_9", "participation_loan", "htf"]),
    ("Roosevelt West", "Keene", 30, "general", "commitment",
     ["texb", "construction", "lihtc_4", "participation_loan"]),
    ("The Rapids on Cocheco", "Rochester", 52, "general", "commitment",
     ["texb", "lihtc_4", "ahf", "home", "htf", "pbv"]),
    ("The Residences at Chestnut - 4%", "Manchester", 142, "general", "commitment",
     ["texb", "lihtc_4", "ahf", "home", "home_arp", "erap", "pbv"]),
    ("Vose Farm Residences Phase I", "Peterborough", 64, "general", "commitment",
     ["texb", "lihtc_4", "ahf", "home_arp", "pbv"]),
    ("Woodland Village Phase II", "Goffstown", 32, "general", "commitment",
     ["texb", "lihtc_4", "home", "ahf", "arpa"]),
    # -- FY25 Completed Developments (p.8): 15 developments / 722 units --
    ("Bay Street Supportive Housing", "Laconia", 12, "supportive", "completed",
     ["ahf", "htf", "pbv"]),
    ("Coliseum Senior Residence Phase III", "Nashua", 133, "age_restricted", "completed",
     ["texb", "lihtc_4"]),
    ("Davis Ridge (FKA Sheep Davis)", "Concord", 48, "general", "completed",
     ["lihtc_9", "investnh"]),
    ("Dexter Richards & Sons Woolen Mill", "Newport", 70, "general", "completed",
     ["texb", "lihtc_4", "investnh", "home_arp", "pbv"]),
    ("Elms Farms Housing", "Franklin", 29, "supportive", "completed",
     ["texb", "construction", "lihtc_4", "participation_loan", "pbv"]),
    ("Gafney Home", "Rochester", 21, "age_restricted", "completed",
     ["lihtc_9", "home"]),
    ("Hillsborough Heights", "Hillsborough", 42, "general", "completed",
     ["lihtc_9", "construction", "participation_loan"]),
    ("Kingston Veterans Housing", "Kingston", 6, "supportive", "completed",
     ["ahf", "htf", "pbv"]),
    ("Pembroke Road Phase I", "Concord", 39, "general", "completed",
     ["lihtc_9", "participation_loan", "investnh"]),
    ("Pembroke Road Phase II", "Concord", 84, "general", "completed",
     ["texb", "lihtc_4", "ahf"]),
    ("Rail Yard Phase I", "Concord", 96, "general", "completed",
     ["texb", "lihtc_4", "ahf", "htf", "pbv"]),
    ("Redberry Farm Phase I", "Epping", 7, "supportive", "completed", ["ahf"]),
    ("The Apartments at 249 Main", "Nashua", 45, "general", "completed",
     ["lihtc_9", "home", "htf"]),
    ("Twin Bridge Apartments", "Merrimack", 48, "general", "completed",
     ["texb", "lihtc_4"]),
    ("Woodland Phase I", "Goffstown", 42, "general", "completed",
     ["lihtc_9", "participation_loan", "home", "arpa"]),
]

# Color group for each funding source (drives both the subprogram reference
# chips and the bubble-map marker color via funding_sources[0]).
FUNDING_COLOR_GROUP = {
    "lihtc_9": "credit", "lihtc_4": "credit",
    "texb": "bond",
    "ahf": "trust", "home": "trust", "home_arp": "trust", "htf": "trust",
    "pbv": "trust",
    "investnh": "capital", "arpa": "capital", "erap": "capital",
    "participation_loan": "capital", "construction": "capital",
}

# Every funding source that may appear in RAW_PROJECTS must be a subprogram
# of the multifamily_financing category (so each has an nhSub_* i18n key and
# a color_group for the bubble map). Verified in verify_funding_coverage.
ALL_FUNDING_SOURCES = set(FUNDING_COLOR_GROUP)


def verify_project_tables():
    """Dual gate: (1) both tables' own printed totals (20/1,193 and 15/722),
    (2) the occupancy-type breakdown re-derived from the rows must match the
    report's own printed 1,636/184/95, and (3) the LIHTC commitments must
    match the report's printed "15 projects / 1,152 units" (with the 9%/4%
    split summing to it)."""
    errors = []
    commitments = [r for r in RAW_PROJECTS if r[4] == "commitment"]
    completed = [r for r in RAW_PROJECTS if r[4] == "completed"]

    if len(commitments) != 20:
        errors.append(f"commitment count: expected 20, got {len(commitments)}")
    if len(completed) != 15:
        errors.append(f"completed count: expected 15, got {len(completed)}")

    commitment_units = sum(r[2] for r in commitments)
    if commitment_units != 1193:
        errors.append(f"commitment units: expected 1,193, got {commitment_units}")
    completed_units = sum(r[2] for r in completed)
    if completed_units != 722:
        errors.append(f"completed units: expected 722, got {completed_units}")

    total_units = commitment_units + completed_units
    if total_units != 1915:
        errors.append(f"total units: expected 1,915, got {total_units}")

    # Occupancy breakdown re-derived from the rows -> must match p.4's printed
    # 1,636 general / 184 age-restricted / 95 supportive.
    occ = {"general": 0, "age_restricted": 0, "supportive": 0}
    for _n, _c, units, occupancy, _s, _src in RAW_PROJECTS:
        occ[occupancy] += units
    for key, expected in (("general", 1636), ("age_restricted", 184), ("supportive", 95)):
        if occ[key] != expected:
            errors.append(f"{key} occupancy units: expected {expected}, got {occ[key]}")

    # LIHTC commitments: the report prints "15 projects / 1,152 units" for
    # "funded with LIHTC in FY25" -- these are exactly the LIHTC rows in the
    # COMMITMENTS table (completed LIHTC rows were funded in prior years).
    lihtc = [r for r in commitments if any(s in ("lihtc_9", "lihtc_4") for s in r[5])]
    lihtc_9 = [r for r in commitments if "lihtc_9" in r[5]]
    lihtc_4 = [r for r in commitments if "lihtc_4" in r[5]]
    lihtc_units = sum(r[2] for r in lihtc)
    lihtc_9_units = sum(r[2] for r in lihtc_9)
    lihtc_4_units = sum(r[2] for r in lihtc_4)
    if len(lihtc) != 15:
        errors.append(f"LIHTC commitments: expected 15, got {len(lihtc)}")
    if lihtc_units != 1152:
        errors.append(f"LIHTC commitment units: expected 1,152, got {lihtc_units}")
    if len(lihtc_9) != 5 or lihtc_9_units != 168:
        errors.append(f"9% LIHTC: expected 5 projects / 168 units, got "
                      f"{len(lihtc_9)} / {lihtc_9_units}")
    if len(lihtc_4) != 10 or lihtc_4_units != 984:
        errors.append(f"4% LIHTC: expected 10 projects / 984 units, got "
                      f"{len(lihtc_4)} / {lihtc_4_units}")

    if errors:
        raise SystemExit("Project-table mismatch(es):\n" + "\n".join(errors))
    print("Project tables verified: 20 commitments / 1,193 units + 15 completed / "
          "722 units = 35 developments / 1,915 units; occupancy breakdown "
          "reconciles to exactly 1,636 general / 184 age-restricted / 95 "
          "supportive; LIHTC commitments reconcile to exactly 15 projects / "
          "1,152 units (9%: 5/168, 4%: 10/984).")


def verify_funding_coverage():
    """Every funding source used in RAW_PROJECTS must be a known subprogram key
    (so it has an nhSub_* i18n string and a color_group), and every declared
    funding source must actually be used by at least one project (no orphans)."""
    errors = []
    used = set()
    for name, _c, _u, _o, _s, sources in RAW_PROJECTS:
        unknown = [s for s in sources if s not in ALL_FUNDING_SOURCES]
        if unknown:
            errors.append(f"{name!r} uses undeclared funding source(s) {unknown}")
        used.update(sources)
    orphans = ALL_FUNDING_SOURCES - used
    if orphans:
        errors.append(f"declared funding sources never used: {sorted(orphans)}")
    if errors:
        raise SystemExit("Funding-source coverage mismatch(es):\n" + "\n".join(errors))
    print(f"Funding-source coverage verified: {len(used)} source keys all used "
          f"and declared.")


def verify_category_consistency():
    """The subprogram unit/dollar figures must match the independently-verified
    transcription (the multifamily_financing LIHTC 9%/4% split, and the
    category headline values already cross-checked in the docstring)."""
    errors = []
    by_key = {sp["key"]: sp for cat in CATEGORIES for sp in cat["subprograms"]}
    expect = {
        "general_occupancy": (1636, None), "age_restricted": (184, None),
        "supportive_housing": (95, None),
        "lihtc_9": (168, None), "lihtc_4": (984, None), "texb": (None, 35800000),
        "first_mortgages": (1078, 348000000), "first_time_homebuyers": (941, None),
        "dpa_loans": (584, 5400000), "first_generation": (51, None),
        "vouchers": (4251, 58000000),
    }
    for key, (units, amount) in expect.items():
        sp = by_key.get(key)
        if sp is None:
            errors.append(f"missing subprogram {key!r}")
            continue
        if sp["fy2025_units"] != units:
            errors.append(f"{key} units: expected {units}, got {sp['fy2025_units']}")
        if sp["fy2025_amount"] != amount:
            errors.append(f"{key} amount: expected {amount}, got {sp['fy2025_amount']}")

    occ = {"general_occupancy": 0, "age_restricted": 0, "supportive_housing": 0}
    for cat in CATEGORIES:
        if cat["key"] == "multifamily_housing":
            if cat["fy2025_actual"] != 1915:
                errors.append(f"multifamily_housing headline: expected 1915, got {cat['fy2025_actual']}")
            for sp in cat["subprograms"]:
                if sp["fy2025_units"] is not None:
                    occ[sp["key"]] = sp["fy2025_units"]
    occ_sum = sum(occ.values())
    if occ_sum != 1915:
        errors.append(f"multifamily occupancy partition sums to {occ_sum}, expected 1915")
    if occ != {"general_occupancy": 1636, "age_restricted": 184, "supportive_housing": 95}:
        errors.append(f"multifamily occupancy partition mismatch: {occ}")

    if errors:
        raise SystemExit("Category-consistency mismatch(es):\n" + "\n".join(errors))
    print("Category consistency verified (occupancy partition 1,636/184/95 = 1,915; "
          "LIHTC 9%/4% = 168/984 = 1,152; single-family/dpa/voucher figures match).")


def geocode(query, cache):
    if query in cache:
        return cache[query]
    params = urllib.parse.urlencode({"q": query, "format": "json", "limit": 1})
    url = f"{NOMINATIM_URL}?{params}"
    result = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": GEOCODER_USER_AGENT})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.load(resp)
            if data:
                result = (float(data[0]["lat"]), float(data[0]["lon"]))
            break
        except urllib.error.HTTPError as exc:
            # 429 = Nominatim rate limit (also hit when several state builds
            # geocode concurrently against the shared public instance).
            # Back off and retry rather than giving up.
            if exc.code == 429:
                wait = 5 * (attempt + 1)
                print(f"  rate-limited ({exc.code}) for {query!r}; retrying in "
                      f"{wait}s (attempt {attempt + 1}/4)")
                time.sleep(wait)
                continue
            print(f"  geocode failed for {query!r}: {exc}")
            break
        except (urllib.error.URLError, TimeoutError, KeyError, ValueError, IndexError) as exc:
            print(f"  geocode failed for {query!r}: {exc}")
            break
    cache[query] = result
    time.sleep(1.2)  # Nominatim usage policy: max 1 request/second (small buffer)
    return result


def make_id(name):
    return (name.lower()
            .replace("&", "and")
            .replace("%", "pct")
            .replace("(", "").replace(")", "")
            .replace("-", " ")
            .replace(".", "").replace("'", "").replace(",", "")
            .replace("  ", " ")
            .strip()
            .replace(" ", "-"))


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
    for name, city, units, _occupancy, _status, sources in RAW_PROJECTS:
        query = f"{city}, NH"
        coords = geocode(query, cache)
        status = "city_center"
        if coords is None:
            coords = geocode(f"{city}, New Hampshire", cache)
            status = "city_center" if coords else "unresolved"
        primary = sources[0]  # table's own "lead" source drives the marker color
        projects.append({
            "id": make_id(name),
            "name": name,
            "address": None,
            "city": city,
            "lat": round(coords[0], 5) if coords else None,
            "lon": round(coords[1], 5) if coords else None,
            "units": units,
            "funding_sources": sources,
            "source_amounts": {},   # no per-development dollar figure disclosed
            "total_amount": None,
            "primary_color_group": FUNDING_COLOR_GROUP[primary],
            "overlaps": len(sources) > 1,
            "geocode_status": status,
        })
    save_geocode_cache(cache)
    return projects


def main():
    verify_project_tables()
    verify_funding_coverage()
    verify_category_consistency()
    print("Geocoding project city/town centers via Nominatim...")
    projects = build_projects()
    unresolved = [p["name"] for p in projects if p["geocode_status"] == "unresolved"]
    if unresolved:
        print(f"  {len(unresolved)} project(s) could not be geocoded: {unresolved}")
    print(f"  {sum(1 for p in projects if p['geocode_status'] == 'city_center')} "
          f"project(s) resolved to city/town-center coordinates.")

    payload = {
        "NH": {
            "hfa_name": "New Hampshire Housing Finance Authority",
            "hfa_abbr": "NH Housing",
            "fiscal_year": "FY2025",
            "source_title": "New Hampshire Housing Annual Report for Fiscal Year 2025 -- Multifamily, Homeownership and Assisted Housing sections",
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
