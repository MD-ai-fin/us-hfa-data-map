"""
Builds docs/va_program_activity.json from Virginia Housing's (Virginia Housing
Development Authority, "VHDA") "2025 Annual Report", "By the Numbers" chapter,
plus Virginia Housing's own FY2025 audited financial statements (for GASB
fund-type classification). This is a KPI-layer-only build, like MA -- see
"Why RAW_PROJECTS is empty" below.

Source
------------------------------------------------------------------------
"2025 Annual Report", Virginia Housing, landing page:
    https://www.virginiahousing.com/en/about/strategic-direction-annual-reports
Actual PDF is served from a CMS dynamic content endpoint (not a static file
URL):
    https://virginiahousing.stylelabs.cloud/api/public/content/Annual-Report_FY25
Local copy, downloaded and archived per this build's task briefing (verified
live 2026-08-14: HTTP 200, 31,694,457 bytes, 44 pages, extracted text
confirms "BY THE NUMBERS" chapter and "REACH VIRGINIA IMPACT" chapter
headings):
    FY2025/program_activity/pdf/VA_VirginiaHousing_AnnualReport_FY2025.pdf
FY2025 = Virginia Housing's fiscal year, July 1, 2024 - June 30, 2025 ("In
FY25, we allocated..." per the REACH Virginia section; the report itself
does not print an explicit "July 2024-June 2025" span, but this matches
Virginia Housing's ACFR fiscal year end of June 30, 2025).

"By the Numbers" chapter (PDF pages 29-34, i.e. pypdf 0-indexed pages 28-33)
------------------------------------------------------------------------
Every figure below is transcribed directly from this build's own local PDF
extraction (pypdf, page-by-page), not from memory or a secondary source:
  - HOMEOWNERSHIP REPORT (PDF page 30): "4,852 home loans for a total of
    $1.4B. Since our beginning, we have provided 255,272 home loans."
    "$11.5M Down Payment Assistance grants to 1,758 homebuyers." "$2.7M
    Closing Cost Assistance grants to 491 homebuyers." "45.94% of our home
    loans were for minorities."
  - FEDERAL ASSISTANCE PROGRAMS REPORT (PDF page 31): "$105.8M federally
    allocated funding." "9,220 households served." "26 local program
    agencies across the Commonwealth."
  - RENTAL HOUSING REPORT (PDF page 32): "4,599 rental units financed for a
    total of $834.7M. Since our beginning, we have financed 153,048 rental
    units." "574 units are in mixed-income developments." "4,025 are for
    low- to moderate-income and hard-to-serve populations." "$60M allocated
    in annual state and federal tax credits." (574 + 4,025 = 4,599 -- an
    exact partition of the headline, confirmed by this script's own
    verify_category_consistency().)
  - REACH VIRGINIA PROGRAM (PDF page 28, chapter "REACH VIRGINIA IMPACT"):
    "In FY25, we allocated $144,401,518 from REACH Virginia: $53,115,000
    Making communities more stable[;] $63,461,518 Making rentals more
    affordable[;] $27,825,000 Making homeownership more attainable[.]
    $1,027,661,399 In allocations since its inception." (53,115,000 +
    63,461,518 + 27,825,000 = 144,401,518 exactly, confirmed by this
    script's own verify_category_consistency().) The PDF's raw text
    extraction prints two of these figures with a stray internal space
    ("$63,461 ,518", "$27 ,825,000") -- an extraction/kerning artifact of
    the source PDF's own number formatting, not a transcription choice by
    this script; the arithmetic check above confirms the intended values.

IMPORTANT -- historical-cumulative figures explicitly excluded
------------------------------------------------------------------------
Per this build's task briefing, the following "since our beginning" /
"since its inception" figures appear adjacent to the FY2025 figures above
but are NOT FY2025 activity and are never used as a fy2025_actual/
fy2025_amount/fy2025_amounts value anywhere in this script: 255,272 home
loans (cumulative since Virginia Housing's founding), 153,048 rental units
(cumulative), and $1,027,661,399 in REACH Virginia allocations "since its
inception" (cumulative). Only figures the source document itself frames as
"In FY25"/this fiscal year's own chapter total are used.

Why RAW_PROJECTS is empty ([]) -- VA's only project-level detail is 6
editorially-selected, image-rendered case studies, not a full-year list
------------------------------------------------------------------------
Per this build's task briefing (already investigated, not re-litigated
here, but independently confirmed during this build): the report's Appendix
(PDF pages 38-43, immediately following an "Appendix" divider page 37 and a
"Home Helps Everyone." closing page 36) contains 6 project profiles
(Fairfax Crest, Telestar Court, Legacy Landing, Goodson Hills, Fusion at
NEON, The Rise II). This build independently re-verified, via pypdf
per-page text extraction, that all 6 of these pages extract to essentially
nothing (each page's extracted text is the single line "< GO BACK", 9
characters, i.e. only a navigation UI element -- the project profile
content itself is image-rendered, not machine-readable text). Separately,
per the task briefing, these 6 are the report's own editorially-curated
"case study" selections, not a complete list of every multifamily
development Virginia Housing financed or preserved in FY2025 (the Rental
Housing Report's own 4,599-unit/$834.7M headline above implies a much
larger population of individual developments than 6). Transcribing these 6
profiles as if they were RAW_PROJECTS would therefore both (a) require
manually reading numbers off inaccessible image content and (b) misrepresent
6 hand-picked examples as a complete per-development dataset, which this
project's methodology (see build_ma_program_activity.py's docstring for the
same reasoning applied to MassHousing) explicitly prohibits. RAW_PROJECTS is
therefore [] and the `projects` array in the output JSON is empty -- an
honest reflection of what Virginia Housing's Annual Report discloses at
project level, not a placeholder for missing work. The frontend
(docs/program_activity.js) already handles this: the KPI cards render
normally and the bubble map renders with 0 markers ("0 projects" in its own
count legend).

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
Source: FY2025/txt/VA_VirginiaHousing_FY2025_ACFR.txt. VERIFIED before use
(this project has repeatedly found mismatched .txt files under other
states): title page reads "VIRGINIA HOUSING DEVELOPMENT AUTHORITY (A
Component Unit of the Commonwealth of Virginia) ... Basic Financial
Statements ... June 30, 2025 and 2024"; the Independent Auditors' Report
(.txt lines 441-448) covers "the business-type activities and fiduciary
activities of the Virginia Housing Development Authority (the Authority), a
component unit of the Commonwealth"; the "By the Numbers" totals above (a
different document) match this ACFR's own entity, fiscal year-end, and
program descriptions throughout (Homeownership/Single-Family, Rental
Housing/Multifamily, REACH Virginia, HCV/federal pass-through -- see below).
Unambiguously the correct entity, no substitution needed.

Like MassHousing and PHFA (and unlike IHDA's mixed governmental+proprietary
structure), Virginia Housing has NO governmental funds of its own -- the
Independent Auditors' Report covers only "business-type activities and
fiduciary activities" (.txt line 441-442). The MD&A's "Organization
Overview" (.txt lines 60-108) and Note 1 name several internal program
lines used for classification below:
  - "proprietary", HIGH confidence (Virginia Housing's own core lending
    business, or a program named and quantified in a dedicated ACFR Note):
      * homeownership_loans' own core (the 4,852/$1.4B headline itself,
        not modeled as a subprogram -- see below) and rental_housing's
        mixed_income/low_mod_hard_to_serve subprograms -- the MD&A states
        "Authority revenues are generated primarily from interest on
        mortgage loans..." and separately: "In addition to its major
        mortgage loan programs, the Authority also administers, on a fee
        basis, various other programs..." (.txt lines 60-83) -- i.e.
        homeownership and rental/multifamily mortgage lending ARE the
        Authority's own "major mortgage loan programs" (as opposed to the
        fee-basis-administered programs listed next to that sentence:
        HCV and LIHTC). The MD&A separately states "In its rental housing
        program, ... utilize federal Low-Income Housing Tax Credits and
        Commonwealth Housing Opportunity Tax Credit..." (.txt line 169-172,
        naming "rental housing program" directly) and the Statements of
        Revenues show the Authority's own asset line "Deferred fees and
        points on multifamily loans" (.txt line 614, Note 1(z), a
        proprietary-fund asset). Confidence: high.
      * homeownership_loans' down_payment_assistance subprogram -- Note
        1(bb) "REACH and Grant Expenses" (.txt lines 1150-1168) states
        REACH Virginia uses "internally generated funds" and explicitly
        lists "down payment assistance grants" as one of the grant types
        it funds ("The Authority provides several different types of
        grants, which are reflected on the financial statements as
        operating expenses and include but are not limited to, down
        payment assistance grants, accessibility grants, network capacity
        support grants, and community market support grants" -- .txt lines
        1162-1164). Verbatim name match. Confidence: high.
      * reach_virginia's 3 subprograms (community_stability,
        rental_affordability, homeownership_access) -- same Note 1(bb):
        REACH Virginia grants are funded from "internally generated funds"
        and recognized "on the financial statements as operating expenses"
        -- i.e. inside the Authority's own business-type activities, not a
        pass-through of someone else's money. Confidence: high.
  - "proprietary", MEDIUM confidence (inferred by program description, not
    a literal, dedicated ACFR line item):
      * homeownership_loans' closing_cost_assistance subprogram -- not
        itself named verbatim in the ACFR (only "down payment assistance
        grants" is explicitly listed as an example in Note 1(bb)'s "include
        but are not limited to" list), but structurally identical to down
        payment assistance (both are Homeownership Report loan-closing
        grants disclosed together on the same "By the Numbers" page), so
        classified the same way by description, not literal name match.
        Confidence: medium.
      * federal_assistance's single subprogram -- Note 1(s) "Pass-Through
        Revenues and Expenses" (.txt lines 1041-1059) discloses "U.S.
        Department of Housing and Urban Development - Tenant Based Section
        8": the Authority "requisitions Section 8 funds, makes
        disbursements of funds to eligible participants, and recognizes
        administrative fee income. Program income and program expenses
        that are recognized as pass-through grants...totaled $109,963,261
        and $98,168,014 during the years ended June 30, 2025, and 2024,
        respectively." This confirms Virginia Housing's own financial
        statements DO recognize a federally-funded, pass-through-structured
        assistance program as its own operating revenue/expense (unlike
        PA's PHARE/LIHTC, which never appear in PHFA's ACFR at all) -- but
        the ACFR's own $109,963,261 FY2025 Section 8 figure does NOT
        exactly match the Annual Report's separately-disclosed Federal
        Assistance Programs Report headline ($105.8M/9,220 households/26
        local program agencies), and the ACFR's Note 1(s) does not mention
        "26 local program agencies" or a household count at all -- so this
        script does NOT assume the two are the identical program (VA's
        "Federal Assistance Programs Report" may aggregate Section 8 HCV
        plus other federally-funded programs the ACFR doesn't separately
        itemize, or use a different measurement convention). No forced
        reconciliation is attempted, per this project's standing rule (same
        approach as PA's Map-Doc-vs-press-release and MN's awards-vs-
        disbursed handling) -- the fund-type classification is based only
        on the ACFR's general confirmation that this CATEGORY of activity
        (federal pass-through funds serving households via program
        administration) is recognized within Virginia Housing's own
        proprietary-fund financial statements. Confidence: medium.
  - "off_balance_sheet" (confirmed fee-basis-administered, not carried as
    the Authority's own fund asset) -- relevant only to a reference amount,
    not a modeled subprogram: rental_housing's "$60M allocated in annual
    state and federal tax credits" (LIHTC/HOTC) fy2025_amounts entry. The
    MD&A states the Authority "also administers, on a fee basis" the
    federal LIHTC program and Virginia's own Housing Opportunity Tax Credit
    (HOTC) program (.txt lines 82-87), and the Statements of Revenues show
    a distinct "Tax credit program fees earned" line (.txt line 644,
    $12,034,028 for FY2025) -- i.e. Virginia Housing earns an
    ADMINISTRATION FEE for allocating these tax credits, but the $60M of
    credits themselves are not the Authority's own asset (the credits flow
    to developers/investors, same off-balance-sheet logic as every other
    pilot state's LIHTC treatment). This $60M figure is therefore shown
    only as an fy2025_amounts reference chip on the rental_housing
    category, is NOT part of the $834.7M mortgage-financing total, and is
    NOT modeled as its own subprogram (no fund_type is attached to it,
    since it is not a subprogram at all).

Category-level methodology
------------------------------------------------------------------------
homeownership_loans: additive=False. The $1.4B/4,852-loan headline (used
verbatim -- Virginia Housing's own report prints only the rounded "$1.4B",
no more precise figure appears anywhere in the document) is NOT the sum of
its two disclosed grant subprograms (down_payment_assistance 1,758/$11.5M,
closing_cost_assistance 491/$2.7M) -- those are second-position assistance
products layered on top of a SUBSET of the 4,852 first mortgages, not a
partition of it (1,758 + 491 = 2,249 is well under 4,852, consistent with
most purchase loans closing without either grant). Unlike PA's K-FIT/
Advantage/PENNVEST, Virginia Housing's own report does not state whether a
single borrower can receive BOTH Down Payment Assistance and Closing Cost
Assistance on the same loan (PA's own program pages explicitly confirmed
its three assistance products were mutually exclusive, which is why PA used
additive=True "relative to each other"); absent that same explicit
confirmation for VA, this script conservatively treats the two as
non-additive reference chips rather than assuming either full overlap or
full exclusivity.

rental_housing: additive=True. Its two subprograms (mixed_income 574 units,
low_mod_hard_to_serve 4,025 units) sum to exactly 4,599 -- the report's own
population breakdown of the full headline, not an assistance layer, so a
stacked bar is the correct display (verified in
verify_category_consistency()). Neither subprogram discloses its own dollar
amount (only the $834.7M category total is given), so fy2025_amount is None
on both.

federal_assistance: additive=True with a single subprogram exactly equal to
the category headline (same pattern as MA's two categories) -- the report
discloses only one federal-assistance total, no further breakdown by source
or program.

reach_virginia: additive=False (unit_type="dollars", fy2025_actual=None --
same shape as PA's phare_funding category). REACH Virginia's own 3
allocation buckets (community_stability $53,115,000, rental_affordability
$63,461,518, homeownership_access $27,825,000) sum to exactly
$144,401,518, verified in verify_category_consistency(), but additive=False
is used anyway (not a stacked bar) because none of the three discloses a
household/unit count (fy2025_units is None on all three) -- the frontend's
stacked-bar renderer divides by summed fy2025_units, which would be
undefined here, so a dollar-only category always uses the chip/reference
display, exactly like PA's PHARE.

fy2026
------------------------------------------------------------------------
The 2025 Annual Report is a backward-looking annual report with no
forward-looking/projected-activity section anywhere in its 44 pages
(checked: the string "2026" does not appear even once in this build's own
full-document pypdf text extraction). Every fy2026 field below is therefore
{value: None, amount: None, closed: False, note_key: "vaFy26NotePending"}.
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "va_program_activity.json"

SOURCE_URL = "https://www.virginiahousing.com/en/about/strategic-direction-annual-reports"
SOURCE_FILE = (
    "VA_VirginiaHousing_AnnualReport_FY2025.pdf (downloaded from the CMS "
    "endpoint https://virginiahousing.stylelabs.cloud/api/public/content/"
    "Annual-Report_FY25 linked from the landing page above; verified live "
    "2026-08-14, HTTP 200, 31,694,457 bytes, 44 pages)"
)
RETRIEVED = "2026-08-14"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "vaFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data ("By the Numbers" chapter, PDF pages 28-32)
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "homeownership_loans",
        "unit_type": "households",
        "fy2025_actual": 4852,
        "fy2025_source_quote": (
            "\"HOMEOWNERSHIP REPORT: 4,852 home loans for a total of $1.4B. Since our "
            "beginning, we have provided 255,272 home loans [historical cumulative, not "
            "used as a FY2025 figure]. $11.5M Down Payment Assistance grants to 1,758 "
            "homebuyers. $2.7M Closing Cost Assistance grants to 491 homebuyers. 45.94% "
            "of our home loans were for minorities.\" (Virginia Housing 2025 Annual "
            "Report, \"By the Numbers\", p.30). \"$1.4B\" is Virginia Housing's own "
            "rounded phrasing -- no more precise figure is disclosed anywhere in the "
            "document -- and is used as-is, not re-derived."
        ),
        "fy2025_amounts": [
            {"label_key": "va_amt_home_loans_total", "amount": 1400000000},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "down_payment_assistance", "fy2025_units": 1758, "fy2025_amount": 11500000,
             "color_group": "capital",
             # ACFR Note 1(bb) "REACH and Grant Expenses" names "down payment
             # assistance grants" verbatim as a REACH Virginia grant type,
             # funded from the Authority's own "internally generated funds".
             "fund_type": "proprietary", "fund_name": "REACH Virginia (internally generated funds)",
             "fy2026": _FY26_PENDING},
            {"key": "closing_cost_assistance", "fy2025_units": 491, "fy2025_amount": 2700000,
             "color_group": "capital",
             # Not itself named verbatim in the ACFR (only "down payment
             # assistance grants" is an explicit example in Note 1(bb)'s
             # non-exhaustive list) -- classified the same way by structural
             # description (a loan-closing grant reported alongside DPA on
             # the same Homeownership Report page). Confidence: medium.
             "fund_type": "proprietary", "fund_name": "REACH Virginia (internally generated funds, inferred -- not verbatim named in the ACFR)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "rental_housing",
        "unit_type": "units",
        "fy2025_actual": 4599,
        "fy2025_source_quote": (
            "\"RENTAL HOUSING REPORT: 4,599 rental units financed for a total of "
            "$834.7M. Since our beginning, we have financed 153,048 rental units "
            "[historical cumulative, not used]. 574 units are in mixed-income "
            "developments. 4,025 are for low- to moderate-income and hard-to-serve "
            "populations. $60M allocated in annual state and federal tax credits.\" "
            "(Virginia Housing 2025 Annual Report, \"By the Numbers\", p.32). 574 + "
            "4,025 = 4,599, an exact partition of the headline (verified in "
            "verify_category_consistency()). The $60M tax-credit figure is shown only "
            "as a reference amount below -- it is a separate, fee-administered "
            "(LIHTC/HOTC) program, not part of the $834.7M mortgage-financing total "
            "and not modeled as its own subprogram -- see module docstring."
        ),
        "fy2025_amounts": [
            {"label_key": "va_amt_rental_total", "amount": 834700000},
            {"label_key": "va_amt_rental_tax_credits", "amount": 60000000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "mixed_income", "fy2025_units": 574, "fy2025_amount": None,
             "color_group": "bond",
             # MD&A: "In its rental housing program..." (Authority's own
             # named program) and Statements of Revenues line "Deferred fees
             # and points on multifamily loans" (Note 1(z)) -- one of the
             # Authority's own "major mortgage loan programs" (as
             # distinguished from its fee-basis-administered programs).
             "fund_type": "proprietary", "fund_name": "Rental Housing Program (multifamily mortgage loans)",
             "fy2026": _FY26_PENDING},
            {"key": "low_mod_hard_to_serve", "fy2025_units": 4025, "fy2025_amount": None,
             "color_group": "bond",
             "fund_type": "proprietary", "fund_name": "Rental Housing Program (multifamily mortgage loans)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "federal_assistance",
        "unit_type": "households",
        "fy2025_actual": 9220,
        "fy2025_source_quote": (
            "\"FEDERAL ASSISTANCE PROGRAMS REPORT: $105.8M federally allocated "
            "funding. 9,220 households served. 26 local program agencies across the "
            "Commonwealth.\" (Virginia Housing 2025 Annual Report, \"By the Numbers\", "
            "p.31). No further breakdown by funding source or sub-program is disclosed "
            "in this report. Cross-referenced against the ACFR's Note 1(s) \"Pass-"
            "Through Revenues and Expenses\", which separately discloses a FY2025 "
            "U.S. HUD Tenant Based Section 8 Housing Choice Voucher pass-through "
            "figure of $109,963,261 -- a similarly-scoped but not numerically "
            "identical federal pass-through program; the two are not assumed to be "
            "the same figure and are never reconciled or added together, per this "
            "project's standing rule -- see module docstring."
        ),
        "fy2025_amounts": [
            {"label_key": "va_amt_federal_grants", "amount": 105800000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "federal_assistance_total", "fy2025_units": 9220, "fy2025_amount": 105800000,
             "color_group": "trust",
             # ACFR Note 1(s) "Pass-Through Revenues and Expenses" confirms
             # Virginia Housing's own financial statements recognize
             # federally-funded, locally-administered assistance programs
             # (e.g. Section 8 HCV) as pass-through operating revenue/
             # expense -- unlike PA's PHARE/LIHTC, which never appear in
             # PHFA's ACFR at all -- but the exact scope of "Federal
             # Assistance Programs Report" is not confirmed to be identical
             # to the ACFR's own Section 8 HCV figure (see module
             # docstring). Confidence: medium.
             "fund_type": "proprietary", "fund_name": "Pass-Through Revenues and Expenses (ACFR Note 1(s); scope not exactly reconciled to this report's own figure)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "reach_virginia",
        "unit_type": "dollars",
        "fy2025_actual": None,
        "fy2025_source_quote": (
            "\"REACH VIRGINIA PROGRAM: In FY25, we allocated $144,401,518 from REACH "
            "Virginia: $53,115,000 Making communities more stable. $63,461,518 Making "
            "rentals more affordable. $27,825,000 Making homeownership more "
            "attainable. $1,027,661,399 In allocations since its inception "
            "[historical cumulative, NOT used as a FY2025 figure].\" (Virginia "
            "Housing 2025 Annual Report, \"REACH Virginia Impact\", p.28). "
            "53,115,000 + 63,461,518 + 27,825,000 = 144,401,518 exactly (verified in "
            "verify_category_consistency()). No household/unit count is disclosed for "
            "any of the three allocation buckets -- REACH Virginia is purely a "
            "dollar-allocation program at this level of disclosure, so none is shown "
            "here (fy2025_actual is None, matching PA's phare_funding category "
            "pattern)."
        ),
        "fy2025_amounts": [
            {"label_key": "va_amt_reach_total", "amount": 144401518},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "community_stability", "fy2025_units": None, "fy2025_amount": 53115000,
             "color_group": "capital",
             # ACFR Note 1(bb): REACH Virginia grants are funded from the
             # Authority's own "internally generated funds" and recognized
             # as its own operating expenses.
             "fund_type": "proprietary", "fund_name": "REACH Virginia (internally generated funds)",
             "fy2026": _FY26_PENDING},
            {"key": "rental_affordability", "fy2025_units": None, "fy2025_amount": 63461518,
             "color_group": "capital",
             "fund_type": "proprietary", "fund_name": "REACH Virginia (internally generated funds)",
             "fy2026": _FY26_PENDING},
            {"key": "homeownership_access", "fy2025_units": None, "fy2025_amount": 27825000,
             "color_group": "capital",
             "fund_type": "proprietary", "fund_name": "REACH Virginia (internally generated funds)",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# Per this build's explicit task briefing: VA's only project-level detail is
# 6 editorially-selected, image-rendered case-study pages (Fairfax Crest,
# Telestar Court, Legacy Landing, Goodson Hills, Fusion at NEON, The Rise
# II) -- not a full-year, extractable, complete list of FY2025 multifamily
# activity. RAW_PROJECTS is therefore intentionally empty; see module
# docstring "Why RAW_PROJECTS is empty" for the independent re-verification
# performed during this build. This is the allowed, honest outcome (not a
# placeholder for missing work): the frontend renders the bubble map with 0
# markers when this is empty.
RAW_PROJECTS = []


def verify_category_consistency():
    errors = []

    # rental_housing: mixed_income + low_mod_hard_to_serve must equal the
    # 4,599-unit headline exactly (an exact partition, not an overlapping
    # assistance layer).
    rh = next(c for c in CATEGORIES if c["key"] == "rental_housing")
    rh_sum = sum(sp["fy2025_units"] for sp in rh["subprograms"])
    if rh_sum != rh["fy2025_actual"]:
        errors.append(
            f"rental_housing: subprogram units sum to {rh_sum}, expected "
            f"{rh['fy2025_actual']} (574 mixed_income + 4,025 low_mod_hard_to_serve)"
        )

    # federal_assistance: single subprogram must exactly equal the category
    # headline (additive=True with 1 subprogram is only meaningful if the
    # subprogram *is* the headline).
    fa = next(c for c in CATEGORIES if c["key"] == "federal_assistance")
    if len(fa["subprograms"]) != 1:
        errors.append(f"federal_assistance: expected exactly 1 subprogram, got {len(fa['subprograms'])}")
    else:
        sp = fa["subprograms"][0]
        if sp["fy2025_units"] != fa["fy2025_actual"]:
            errors.append(f"federal_assistance: subprogram units {sp['fy2025_units']} != category fy2025_actual {fa['fy2025_actual']}")
        cat_amt = fa["fy2025_amounts"][0]["amount"] if fa["fy2025_amounts"] else None
        if cat_amt is not None and sp["fy2025_amount"] != cat_amt:
            errors.append(f"federal_assistance: subprogram amount {sp['fy2025_amount']} != category fy2025_amounts[0].amount {cat_amt}")

    # homeownership_loans: sanity check only (non-additive) -- the two grant
    # subprograms must each be <= the 4,852-loan headline, since they are a
    # subset layered on top of it, never a partition or an over-count.
    ho = next(c for c in CATEGORIES if c["key"] == "homeownership_loans")
    for sp in ho["subprograms"]:
        if sp["fy2025_units"] > ho["fy2025_actual"]:
            errors.append(
                f"homeownership_loans: subprogram {sp['key']!r} units "
                f"{sp['fy2025_units']} exceeds category headline {ho['fy2025_actual']}"
            )

    # reach_virginia: 3 subprograms must sum to the $144,401,518 headline
    # exactly, even though additive=False (dollar-only category, see
    # docstring) -- this is an internal-consistency check, not a display
    # decision.
    rv = next(c for c in CATEGORIES if c["key"] == "reach_virginia")
    rv_sum = sum(sp["fy2025_amount"] for sp in rv["subprograms"])
    rv_headline = rv["fy2025_amounts"][0]["amount"] if rv["fy2025_amounts"] else None
    if rv_headline is not None and rv_sum != rv_headline:
        errors.append(f"reach_virginia: subprogram amounts sum to {rv_sum}, expected {rv_headline}")

    if RAW_PROJECTS:
        errors.append(
            "RAW_PROJECTS is expected to be empty for VA -- see module docstring; "
            "if a complete project-level list has since become available, update "
            "the docstring before populating this list."
        )

    if errors:
        raise SystemExit("Category consistency mismatch(es):\n" + "\n".join(errors))
    print("Category headline vs. subprogram consistency verified for all 4 categories "
          "(rental_housing: 574+4,025=4,599 units; federal_assistance: single "
          "subprogram = 9,220 households/$105,800,000; reach_virginia: "
          "53,115,000+63,461,518+27,825,000=$144,401,518); RAW_PROJECTS confirmed "
          "empty as expected.")


def main():
    verify_category_consistency()
    payload = {
        "VA": {
            "hfa_name": "Virginia Housing",
            "hfa_abbr": "Virginia Housing",
            "fiscal_year": "FY2025",
            "source_title": "Virginia Housing 2025 Annual Report -- \"By the Numbers\" "
                             "(Homeownership, Rental Housing, Federal Assistance Programs "
                             "Reports) and REACH Virginia Impact",
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
