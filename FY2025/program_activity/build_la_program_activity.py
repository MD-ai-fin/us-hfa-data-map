"""
Builds docs/la_program_activity.json from the Louisiana Housing Corporation's
(LHC) "2025 Annual Report" -- a KPI-layer-only build (no per-project cohort),
like VA and MA. See "Why RAW_PROJECTS is empty" below.

Source
------------------------------------------------------------------------
"2025 Annual Report", Louisiana Housing Corporation (LHC), "A Year of Growth,
Stability, and Hope Across Louisiana":
    https://www.lhc.la.gov/hubfs/Annual%20Report%20Edits%20II.pdf
The report is referenced (and linked) from LHC's press release
"LHC Reflects on Affordable Housing Progress" (dated May 5, 2026):
    https://www.lhc.la.gov/press-releases/lhc-reflects-on-affordable-housing-progress
The catalog's own "financial-reports" landing URL
(https://www.lhc.la.gov/about/financial-reports) returned HTTP 404 at build
time, so the hubfs PDF (the actual report file) is recorded as source_url.

Local copy, downloaded and archived for this build:
    FY2025/program_activity/pdf/LA_LHC_AnnualReport_2025.pdf
Verified live 2026-08-16: HTTP 200, 62,875,511 bytes, 46 pages; pypdf text
extraction confirms the BUILD / BLOOM / BELIEVE chapter headings and the
"GRAND TOTAL 24 1,312 $17,568,669" LIHTC table.

Fiscal-year discipline
------------------------------------------------------------------------
The report's Executive Director message states it "summarizes the agency's
activities, accomplishments, and financial position during the 2025 fiscal
year" (PDF page 3). LHC's audited financial statements (FY2025/txt/
LA_LHC_FY2025_ACFR.txt, an audit by the Louisiana Legislative Auditor) cover
"the year ended June 30, 2025" -- so "the 2025 fiscal year" = FY2025 (July 1,
2024 - June 30, 2025). The report never prints an explicit "July 2024 - June
2025" span, and a few items reach into late calendar 2025 (e.g. the CENLA
Blue Tarp round launched November 17, 2025, PDF page 14), so the report is a
loose "2025" narrative rather than a strictly-bounded FY2025 document; the
KPI figures used below are all the report's own "In 2025"/"2025" program
totals. federal fiscal-year nuance: LIHEAP and Weatherization are
federally-funded programs that the report labels "2025" without specifying a
state-FY vs federal-FY boundary; this build reports them as the report prints
them, under the report's own "2025 fiscal year" framing (fiscal_year "FY2025").
No "since inception"/cumulative figures appear in the KPI sections; the only
historical figures in the report (e.g. Appendix A's "pending" LIHTC pipeline)
are not FY2025 activity and are excluded.

Every figure below is transcribed from this build's own local PDF extraction
(pypdf, page-by-page), not from memory or a secondary source:
  - BUILD / LIHTC (PDF page 9): "In 2025, LHC invested $17.5 million through
    the Low-Income Housing Tax Credit Program to fund affordable multifamily
    rental units..." with table "LIHTC (4%) 3 268 $2,785,183; LIHTC (9%) 21
    1,044 $14,783,486; GRAND TOTAL 24 1,312 $17,568,669." and the KPI tiles
    "2025 NEW UNITS 557 / 2025 LIHTC UNITS 1,312 / 2025 REHABILITATED UNITS
    755" (557 + 755 = 1,312, a second exact partition).
  - BUILD / HOME & NHTF (PDF page 11): "In 2025, LHC awarded $6,371,00
    [sic -- the prose prints $6,371,00, a typo for the table's $6,371,000]
    through the HOME program and $2,750,000 through the National Housing
    Trust Fund Program (NHTF)." Table total row prints "38 [HOME/NHTF units]
    $6,371,000 [HOME] $2,750,000 [NHTF]".
  - BLOOM / Rental Assistance (PDF page 17): "Project Based Vouchers 1,397;
    Tenant Based Vouchers 357; Non-Elderly Housing Voucher 135; Emergency
    Housing Voucher 101; Veterans Affairs Supportive Housing 19; Rental
    Assistance Vouchers Statewide 2,009." (1,397 + 357 + 135 + 101 + 19 =
    2,009 exactly.)
  - BLOOM / Energy (PDF page 19): "2025 Weatherization Assistance Program:
    Funding $5,356,647; Recipients 652 recipients. 2025 Low Income Home Energy
    Assistance Program: Funding $48,394,446; Recipients 72,685. Funding
    Combined: $53,751,113." (See the $20 discrepancy note below.)
  - BELIEVE / Homeownership (PDF page 22): "805 Homeownership Loans; $144,003,900
    Amount of Loan Production; $66,402 Homeownership Counseling Awarded; 993
    Homebuyer Education Graduates; 2,457 people attended LHC's Homebuyer
    Education courses...; 1,400+ Real Estate Professionals...; 2,345 Loan
    Officers & Bank Office Closing Personnel...".

External cross-check (press release)
------------------------------------------------------------------------
LHC's "LHC Reflects on Affordable Housing Progress" press release (the same
figures, published independently of the PDF's layout) confirms: LIHTC $17.5M;
HOME $6,371,000; NHTF $2,750,000; Rural Rental Rehab $10,614,264 / 236 units;
Middle Market Loan $47,655,129 / 288 units; PRIME 2 $313,432,935 / 2,628
units; PRIME 3 $141,442,607 / 1,489 units; LIHEAP $48,394,446 / 72,685;
Weatherization $5,356,647 / 652. These all match the PDF figures used here.

Two honest source-side inconsistencies (flagged, not resolved)
------------------------------------------------------------------------
1. Energy "Funding Combined" is $20 off: the PDF prints LIHEAP funding
   $48,394,446 and Weatherization funding $5,356,647, whose arithmetic sum is
   $53,751,093 -- but the PDF's own "Funding Combined" line prints $53,751,113
   (exactly $20 more; consistent with one of the two components carrying a
   $20 typo, e.g. $48,394,466 or $5,356,667). Both component figures are
   independently corroborated by the press release, so each is used as
   printed; the combined line is NOT reproduced as a category total, and the
   mismatch is documented here rather than hard-erroring the build (it is the
   source's inconsistency, not a transcription error by this script).
2. HOME/NHTF project table does not reconcile to its own printed total: the
   PDF's per-project table (PDF page 11) shows 10 HOME rows summing to
   $5,371,000 / 27 units and 2 NHTF rows summing to $2,750,000 / 12 units,
   i.e. 39 units and $5,371,000 HOME -- while the table's own total row (and
   the prose and the press release) print 38 units and $6,371,000 HOME. The
   NHTF side reconciles exactly ($2,750,000 / 12 units). The HOME side is off
   by exactly 1 unit and exactly $1,000,000, indicating a likely
   missing/misprinted HOME row in the PDF's table rendering. Because the
   headline ($6,371,000 HOME / $2,750,000 NHTF / 38 units) is corroborated in
   three places (prose, table total, press release), this build uses the
   printed headline and does NOT re-derive a unit split or dollar total from
   the inconsistent rows. subprogram fy2025_units are therefore null (the
   report does not cleanly partition the 38 units between HOME and NHTF), and
   the category is additive=False.

Why RAW_PROJECTS is empty ([]) -- no complete per-project cohort list
------------------------------------------------------------------------
Per this build's task briefing (already investigated, not re-litigated, but
independently confirmed during this build): LHC's report has NO complete
per-project FY2025 cohort list. Appendix A ("List of Pending LIHTC
Developments", PDF pages 25-32) is a PENDING LIHTC *pipeline* (GRAND TOTALS
"2,251 new + 4,619 rehab = 6,870 units, $102,558,287 LIHTC, $1,995,480,676
TDC"), not the 24 projects actually awarded in FY2025 (the page-9 table);
Appendix B ("2025 Homeowner Loan Amounts", PDF pages 34-46) is a list of
individual single-family mortgage loans (parish/city level), not affordable-
housing developments; Appendix C is a certified-CHDO directory. None of these
is a complete, extractable per-development cohort of FY2025 production, and
the award-level table (page 9) is summarized at 24 projects/1,312 units with
no per-project name/address/unit detail. RAW_PROJECTS is therefore [] and the
output `projects` array is empty -- the honest KPI-only result, not a
placeholder. The frontend (docs/program_activity.js) renders the KPI cards
normally and the bubble map with 0 markers.

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
Source: FY2025/txt/LA_LHC_FY2025_ACFR.txt. VERIFIED before use: title page
reads "LOUISIANA HOUSING CORPORATION FINANCIAL STATEMENTS JUNE 30, 2025"; the
Independent Auditor's Report covers "the Louisiana Housing Corporation, a
component unit of the State of Louisiana, as of and for the year ended June
30, 2025". Note 1 "Organization of the Corporation" (.txt lines 515-521) lists
LHC's programs -- "Mortgage Revenue Bond Programs, the Low-Income Housing Tax
Credit Program, the Louisiana Housing Trust Fund Program, the Neighborhood
Stabilization Program, and various federal award programs including the
Low-Income Housing Energy Assistance Program, the Weatherization Assistance
Program, HOME Investment Partnerships, Housing Choice Vouchers Program,
Emergency Solutions Grant Program, Continuum of Care Program, Section 811
Program, Comprehensive Housing Counseling Program, and Section 8 Contract
Administration." Unambiguously the correct entity, no substitution needed.

LHC has NO governmental funds of its own: "The Corporation's Funds have been
presented on a combined basis, as the Corporation is considered a single
enterprise fund for financial reporting purposes" (.txt lines 578-580), and
"the Corporation's financial statements include the activity of the General
Fund and the Single Family Mortgage Revenue Bond Program" (.txt lines
545-546). Classification below follows from this:
  - "off_balance_sheet" (HIGH confidence) -- the LIHTC credit awards
    (lihtc_9pct / lihtc_4pct). Tax credits flow to developers/investors, not
    to LHC's own balance sheet; the ACFR instead recognizes "Low income
    housing tax credit program fees" ($3,035,280, .txt lines 383/2445) as
    fee revenue. Same treatment as every other pilot state's LIHTC.
  - "proprietary" (HIGH confidence) -- single_family_loans. The Single Family
    Mortgage Revenue Bond Program is one of the two funds combined into LHC's
    single enterprise fund (.txt lines 545-546, 574-577), i.e. LHC's own
    core lending business. fund_name "Single Family Mortgage Revenue Bond
    Program".
  - "proprietary" (MEDIUM confidence) -- rental_assistance (HCV/vouchers),
    energy_assistance (LIHEAP/Weatherization), and home_program (HOME/NHTF).
    These are federal award/pass-through programs. The ACFR's accounting
    policy states "Federal grant pass-through revenues and expenses... are
    classified as non-operating" (.txt lines 674-676) -- i.e. LHC DOES
    recognize these federal pass-through flows within its own single
    enterprise fund (unlike PA's PHARE/LIHTC, which never appear in PHFA's
    ACFR at all). The exact FY2025 dollar amounts are not reconciled to a
    specific ACFR line item here (no forced reconciliation, per this project's
    standing rule), so confidence is medium; the classification rests on the
    ACFR's confirmation that this CATEGORY of activity is recognized within
    LHC's proprietary (enterprise) fund.
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "la_program_activity.json"

SOURCE_URL = "https://www.lhc.la.gov/hubfs/Annual%20Report%20Edits%20II.pdf"
SOURCE_FILE = (
    "LA_LHC_AnnualReport_2025.pdf (downloaded from the hubfs URL above, linked "
    "from LHC's 'LHC Reflects on Affordable Housing Progress' press release; "
    "verified live 2026-08-16, HTTP 200, 62,875,511 bytes, 46 pages)"
)
RETRIEVED = "2026-08-16"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "laFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data (2025 Annual Report, BUILD/BLOOM/BELIEVE chapters)
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "multifamily_lihtc",
        "unit_type": "units",
        "fy2025_actual": 1312,
        "fy2025_source_quote": (
            "\"In 2025, LHC invested $17.5 million through the Low-Income Housing "
            "Tax Credit Program to fund affordable multifamily rental units...\" "
            "(LHC 2025 Annual Report, BUILD, PDF p.9). Accompanying table: "
            "\"LIHTC (4%) 3 [projects] 268 [units] $2,785,183; LIHTC (9%) 21 "
            "[projects] 1,044 [units] $14,783,486; GRAND TOTAL 24 1,312 "
            "$17,568,669.\" The 4% and 9% rows are an exact partition of the grand "
            "total (268 + 1,044 = 1,312 units; $2,785,183 + $14,783,486 = "
            "$17,568,669; 3 + 21 = 24 projects), verified in "
            "verify_category_consistency(). The page also prints a second, "
            "independent partition -- \"2025 NEW UNITS 557 / 2025 REHABILITATED "
            "UNITS 755\" = 1,312 -- verified there too. The dollar column is the "
            "report's own \"LIHTC AWARDED\" figure; the report does not state "
            "whether it is an annual or 10-year credit total, so it is reported "
            "as-printed without that qualifier. \"$17.5 million\" is LHC's own "
            "rounded phrasing of the $17,568,669 grand total (also confirmed by "
            "the press release)."
        ),
        "fy2025_amounts": [
            {"label_key": "la_amt_lihtc", "amount": 17568669},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "lihtc_9pct", "fy2025_units": 1044, "fy2025_amount": 14783486,
             "color_group": "credit",
             # ACFR: LIHTC is fee-administered; LHC recognizes "Low income
             # housing tax credit program fees" as revenue, not the credits
             # themselves (off-balance-sheet). See module docstring.
             "fund_type": "off_balance_sheet",
             "fund_name": "Low-Income Housing Tax Credit Program (fee-administered)",
             "fy2026": _FY26_PENDING},
            {"key": "lihtc_4pct", "fy2025_units": 268, "fy2025_amount": 2785183,
             "color_group": "credit",
             "fund_type": "off_balance_sheet",
             "fund_name": "Low-Income Housing Tax Credit Program (fee-administered)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "homeownership_loans",
        "unit_type": "households",
        "fy2025_actual": 805,
        "fy2025_source_quote": (
            "\"805 Homeownership Loans. $144,003,900 Amount of Loan Production. "
            "$66,402 Homeownership Counseling Awarded. 993 Homebuyer Education "
            "Graduates. 2,457 people attended LHC's Homebuyer Education courses "
            "either in-person or virtually. Over 1,400 Real Estate Professionals "
            "participated in LHC's Continuing Education Curriculum Course. 2,345 "
            "Loan Officers & Bank Office Closing Personnel participated in LHC's "
            "Lender Training Courses.\" (LHC 2025 Annual Report, BELIEVE, PDF "
            "p.22). The 805-loan / $144,003,900 loan-production pair is the "
            "homeownership KPI; the counseling/education/lender-training figures "
            "are outreach metrics with no per-loan partition and are quoted here "
            "for completeness but not modeled as subprograms. No per-loan dollar "
            "or per-loan subprogram breakdown is disclosed on this page (the "
            "Appendix B loan list is parish/city level, not a program split)."
        ),
        "fy2025_amounts": [
            {"label_key": "la_amt_loan_production", "amount": 144003900},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "single_family_loans", "fy2025_units": 805, "fy2025_amount": 144003900,
             "color_group": "bond",
             # ACFR: the Single Family Mortgage Revenue Bond Program is one of
             # the two funds combined into LHC's single enterprise fund.
             "fund_type": "proprietary",
             "fund_name": "Single Family Mortgage Revenue Bond Program",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "rental_assistance",
        "unit_type": "households",
        "fy2025_actual": 2009,
        "fy2025_source_quote": (
            "\"Project Based Vouchers 1,397. Tenant Based Vouchers 357. "
            "Non-Elderly Housing Voucher 135. Emergency Housing Voucher 101. "
            "Veterans Affairs Supportive Housing 19. Rental Assistance Vouchers "
            "Statewide 2,009.\" (LHC 2025 Annual Report, BLOOM, PDF p.17). The "
            "five voucher types sum to exactly 2,009 (1,397 + 357 + 135 + 101 + "
            "19 = 2,009), the report's own statewide total -- an exact partition, "
            "verified in verify_category_consistency(). No dollar amount is "
            "disclosed for these vouchers on this page, so all subprogram "
            "amounts are null. (The report's separately-disclosed PBCA / Section 8 "
            "contract-administration figures -- 179 contracts, 15,376 PBCA units, "
            "$134M payments to owners, PDF p.19 -- are a monitoring/"
            "administration function, not part of the voucher award cohort, and "
            "are not modeled here.)"
        ),
        "fy2025_amounts": [],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "project_based", "fy2025_units": 1397, "fy2025_amount": None,
             "color_group": "trust",
             # ACFR: "Housing Choice Vouchers Program" is a listed federal award
             # program; federal pass-through flows are recognized in LHC's own
             # single enterprise fund. Confidence: medium (scope not reconciled
             # to a specific ACFR line).
             "fund_type": "proprietary",
             "fund_name": "Federal Housing Choice Voucher pass-through (recognized in LHC's single enterprise fund)",
             "fy2026": _FY26_PENDING},
            {"key": "tenant_based", "fy2025_units": 357, "fy2025_amount": None,
             "color_group": "trust",
             "fund_type": "proprietary",
             "fund_name": "Federal Housing Choice Voucher pass-through (recognized in LHC's single enterprise fund)",
             "fy2026": _FY26_PENDING},
            {"key": "non_elderly_housing", "fy2025_units": 135, "fy2025_amount": None,
             "color_group": "trust",
             "fund_type": "proprietary",
             "fund_name": "Federal Housing Choice Voucher pass-through (recognized in LHC's single enterprise fund)",
             "fy2026": _FY26_PENDING},
            {"key": "emergency_housing", "fy2025_units": 101, "fy2025_amount": None,
             "color_group": "trust",
             "fund_type": "proprietary",
             "fund_name": "Federal Housing Choice Voucher pass-through (recognized in LHC's single enterprise fund)",
             "fy2026": _FY26_PENDING},
            {"key": "vash", "fy2025_units": 19, "fy2025_amount": None,
             "color_group": "trust",
             "fund_type": "proprietary",
             "fund_name": "Federal Housing Choice Voucher pass-through (recognized in LHC's single enterprise fund)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "energy_assistance",
        "unit_type": "households",
        "fy2025_actual": 73337,
        "fy2025_source_quote": (
            "\"2025 Weatherization Assistance Program: Funding $5,356,647; "
            "Recipients 652 recipients. 2025 Low Income Home Energy Assistance "
            "Program: Funding $48,394,446; Recipients 72,685. Funding Combined: "
            "$53,751,113.\" (LHC 2025 Annual Report, BLOOM, PDF p.19). Recipient "
            "counts sum cleanly to 73,337 (72,685 + 652) -- the report prints no "
            "combined-recipient total, so there is nothing to conflict with. "
            "Dollar note: the two printed funding figures sum to $53,751,093, but "
            "the report's own \"Funding Combined\" line prints $53,751,113 (a $20 "
            "source-side discrepancy, consistent with a $20 typo in one of the "
            "two components). Both component figures are independently confirmed "
            "by the press release, so each is used as printed and NO combined "
            "dollar total is asserted here -- see module docstring."
        ),
        "fy2025_amounts": [],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "liheap", "fy2025_units": 72685, "fy2025_amount": 48394446,
             "color_group": "trust",
             # ACFR: LIHEAP is a listed federal award program; federal
             # pass-through flows are recognized in LHC's single enterprise
             # fund. Confidence: medium.
             "fund_type": "proprietary",
             "fund_name": "Federal LIHEAP pass-through (recognized in LHC's single enterprise fund)",
             "fy2026": _FY26_PENDING},
            {"key": "weatherization", "fy2025_units": 652, "fy2025_amount": 5356647,
             "color_group": "trust",
             "fund_type": "proprietary",
             "fund_name": "Federal Weatherization Assistance pass-through (recognized in LHC's single enterprise fund)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "home_program",
        "unit_type": "units",
        "fy2025_actual": 38,
        "fy2025_source_quote": (
            "\"In 2025, LHC awarded $6,371,00 [sic] through the HOME program and "
            "$2,750,000 through the National Housing Trust Fund Program (NHTF).\" "
            "(LHC 2025 Annual Report, BUILD, PDF p.11). The accompanying "
            "\"PROJECTS FUNDED THROUGH HOME & NATIONAL HOUSING TRUST FUND\" table "
            "prints a total row of 38 HOME/NHTF units, $6,371,000 HOME awards, "
            "$2,750,000 NHTF awards. The prose's \"$6,371,00\" is a typo for the "
            "table's and press release's \"$6,371,000\". IMPORTANT source-side "
            "inconsistency: the table's own visible rows sum to $5,371,000 HOME "
            "/ 39 units (10 HOME rows: 27 units, $5,371,000; 2 NHTF rows: 12 "
            "units, $2,750,000 -- the NHTF side reconciles exactly) rather than "
            "the printed $6,371,000 / 38 -- a $1,000,000 / 1-unit gap indicating "
            "a likely missing or misprinted HOME row. Because the headline is "
            "corroborated in three places (prose, table total, press release), "
            "the printed headline is used as-is and no per-program unit split or "
            "re-derived total is asserted (subprogram units are null, "
            "additive=False). See module docstring."
        ),
        "fy2025_amounts": [
            {"label_key": "la_amt_home", "amount": 6371000},
            {"label_key": "la_amt_nhtf", "amount": 2750000},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "home", "fy2025_units": None, "fy2025_amount": 6371000,
             "color_group": "trust",
             # ACFR: "HOME Investment Partnerships" is a listed federal award
             # program; federal pass-through flows are recognized in LHC's
             # single enterprise fund. Confidence: medium.
             "fund_type": "proprietary",
             "fund_name": "Federal HOME Investment Partnerships pass-through (recognized in LHC's single enterprise fund)",
             "fy2026": _FY26_PENDING},
            {"key": "nhtf", "fy2025_units": None, "fy2025_amount": 2750000,
             "color_group": "trust",
             # ACFR note: the federal National Housing Trust Fund is distinct
             # from LHC's state-level "Louisiana Housing Trust Fund Program";
             # the report's "NHTF" is the federal program. Confidence: medium.
             "fund_type": "proprietary",
             "fund_name": "Federal National Housing Trust Fund pass-through (recognized in LHC's single enterprise fund)",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# Per this build's explicit task briefing: LHC's report has NO complete
# per-project FY2025 cohort list (Appendix A is a *pending* LIHTC pipeline,
# Appendix B is a parish/city homeowner-loan list, Appendix C is a CHDO
# directory). RAW_PROJECTS is intentionally empty; see module docstring.
RAW_PROJECTS = []


def verify_category_consistency():
    errors = []
    warnings = []

    # multifamily_lihtc: 9% + 4% must exactly equal the 1,312-unit / $17,568,669
    # grand total (an exact partition), and projects 21 + 3 = 24.
    mf = next(c for c in CATEGORIES if c["key"] == "multifamily_lihtc")
    mf_units = sum(sp["fy2025_units"] for sp in mf["subprograms"])
    mf_amt = sum(sp["fy2025_amount"] for sp in mf["subprograms"])
    if mf_units != mf["fy2025_actual"]:
        errors.append(f"multifamily_lihtc: subprogram units sum to {mf_units}, "
                      f"expected {mf['fy2025_actual']} (1,044 + 268)")
    if mf_amt != mf["fy2025_amounts"][0]["amount"]:
        errors.append(f"multifamily_lihtc: subprogram amounts sum to {mf_amt}, "
                      f"expected {mf['fy2025_amounts'][0]['amount']} ($17,568,669)")
    # Second printed partition: NEW 557 + REHAB 755 = 1,312 (assert the constant).
    if 557 + 755 != mf["fy2025_actual"]:
        errors.append("multifamily_lihtc: 557 new + 755 rehab != 1,312 (unexpected)")

    # homeownership_loans: single subprogram must equal the 805-loan / $144,003,900
    # headline (additive=True with 1 subprogram = the headline).
    ho = next(c for c in CATEGORIES if c["key"] == "homeownership_loans")
    if len(ho["subprograms"]) != 1:
        errors.append(f"homeownership_loans: expected 1 subprogram, got {len(ho['subprograms'])}")
    else:
        sp = ho["subprograms"][0]
        if sp["fy2025_units"] != ho["fy2025_actual"]:
            errors.append(f"homeownership_loans: subprogram units {sp['fy2025_units']} "
                          f"!= headline {ho['fy2025_actual']}")
        if sp["fy2025_amount"] != ho["fy2025_amounts"][0]["amount"]:
            errors.append(f"homeownership_loans: subprogram amount {sp['fy2025_amount']} "
                          f"!= headline amount {ho['fy2025_amounts'][0]['amount']}")

    # rental_assistance: the 5 voucher types must sum to exactly 2,009.
    ra = next(c for c in CATEGORIES if c["key"] == "rental_assistance")
    ra_sum = sum(sp["fy2025_units"] for sp in ra["subprograms"])
    if ra_sum != ra["fy2025_actual"]:
        errors.append(f"rental_assistance: subprogram units sum to {ra_sum}, "
                      f"expected {ra['fy2025_actual']} (1,397+357+135+101+19=2,009)")

    # energy_assistance: recipient counts must sum to 73,337 (clean partition; the
    # report prints no combined-recipient total). Dollar: the two printed funding
    # figures sum to $53,751,093 but the report prints "Funding Combined:
    # $53,751,113" -- a $20 source-side discrepancy, documented (WARNING, not an
    # error: both components are independently corroborated by the press release).
    ea = next(c for c in CATEGORIES if c["key"] == "energy_assistance")
    ea_units = sum(sp["fy2025_units"] for sp in ea["subprograms"])
    if ea_units != ea["fy2025_actual"]:
        errors.append(f"energy_assistance: subprogram units sum to {ea_units}, "
                      f"expected {ea['fy2025_actual']} (72,685 + 652)")
    ea_amt = sum(sp["fy2025_amount"] for sp in ea["subprograms"])
    if ea_amt != 53751113:
        warnings.append(
            f"energy_assistance: printed 'Funding Combined' is $53,751,113, but the "
            f"two printed components sum to ${ea_amt:,} (a $20 source-side "
            f"discrepancy -- see module docstring); components used as-printed."
        )

    # home_program: dollar figures are the printed, triple-corroborated headline;
    # the table's own rows do NOT reconcile (documented -- WARNING, not an error).
    hp = next(c for c in CATEGORIES if c["key"] == "home_program")
    if [a["amount"] for a in hp["fy2025_amounts"]] != [6371000, 2750000]:
        errors.append("home_program: fy2025_amounts do not match the printed HOME/NHTF headline")
    warnings.append(
        "home_program: the source's own project-table rows sum to $5,371,000 HOME / "
        "39 units, while the printed total row (and prose, and press release) print "
        "$6,371,000 HOME / 38 units -- a $1,000,000 / 1-unit source-side gap (likely "
        "a missing/misprinted row); the corroborated printed headline is used and no "
        "per-program unit split is asserted. See module docstring."
    )

    if RAW_PROJECTS:
        errors.append(
            "RAW_PROJECTS is expected to be empty for LA -- see module docstring; "
            "if a complete per-project cohort list has since become available, "
            "update the docstring before populating this list."
        )

    for w in warnings:
        print(f"WARNING: {w}")
    if errors:
        raise SystemExit("Category consistency mismatch(es):\n" + "\n".join(errors))
    print("Category headline vs. subprogram consistency verified: "
          "multifamily_lihtc (1,044+268=1,312 units; $14,783,486+$2,785,183=$17,568,669; "
          "557+755=1,312), homeownership_loans (805/$144,003,900), rental_assistance "
          "(1,397+357+135+101+19=2,009), energy_assistance (72,685+652=73,337). "
          "RAW_PROJECTS confirmed empty as expected.")


def main():
    verify_category_consistency()
    payload = {
        "LA": {
            "hfa_name": "Louisiana Housing Corporation",
            "hfa_abbr": "LHC",
            "fiscal_year": "FY2025",
            "source_title": "Louisiana Housing Corporation 2025 Annual Report -- "
                             "BUILD/BLOOM/BELIEVE chapters (LIHTC, HOME & NHTF, "
                             "Rental Assistance, Energy Assistance, Homeownership)",
            "source_url": SOURCE_URL,
            "source_file": SOURCE_FILE,
            "retrieved": RETRIEVED,
            "categories": CATEGORIES,
            "projects": RAW_PROJECTS,
        }
    }
    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT_PATH} ({len(RAW_PROJECTS)} projects, {len(CATEGORIES)} categories)")


if __name__ == "__main__":
    main()
