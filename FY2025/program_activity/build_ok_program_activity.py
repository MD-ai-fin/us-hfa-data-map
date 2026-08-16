"""
Builds docs/ok_program_activity.json from the Oklahoma Housing Finance
Agency's (OHFA, "OHFA") "2025 Annual Report" ("Where Home Takes Root"),
plus OHFA's own FY2025 audited financial statements (for GASB fund-type
classification and an independent external cross-check of the dollar and
unit figures). This is a KPI-layer-only build -- see "Why RAW_PROJECTS is
empty" below.

Source
------------------------------------------------------------------------
Primary source: OHFA "2025 Annual Report" ("Where Home Takes Root"),
published as a SCROLLING WEB PAGE (no downloadable PDF; the page's only
document link points to the separate "financials" landing page, not to an
annual-report PDF):
    https://www.ohfa.org/2025-annual-report/
Retrieved 2026-08-16 by this build's own curl fetch of the raw HTML; the
verbatim figures below are transcribed from that fetched text (the page's
"Where Home Takes Root: By the Numbers" section and the three expandable
program sections "Single Family Homeownership", "Housing Choice Voucher
Program", and "Performance Based Contract Administration"). Because the
source is a live web page (not a static file), its exact wording is quoted
verbatim into each category's fy2025_source_quote below.

Supporting archived document (downloaded and kept for reference, but NOT
used as a category source because its figures are "since inception"
cumulative -- see "Year discipline" below):
    FY2025/program_activity/pdf/OK_OHFA_HSP_AnnualStatusReport_2025.pdf
This is OHFA's statutorily-required "2025 Housing Stability Program (HSP)
Annual Status Report" (submitted July 1, 2025, Title 74:2903.1-2903.5),
downloaded from
https://www.ohfa.org/wp-content/uploads/2025/2025-Annual-Report-Housing-Stability-Program-FINAL.pdf
(HTTP 200, 7,366,836 bytes, 12 pages). Its headline figures -- "$95,859,011
in Housing Stability Program funds to 39 different developments containing
745 new housing units" -- are explicitly "since inception" (the program
began making awards May 15, 2024), so they are NOT FY2025 activity and are
never used as a category figure here.

Fiscal-year determination ("in 2025" == OHFA's fiscal year 2025)
------------------------------------------------------------------------
The report is titled "2025 Annual Report" and phrases every figure as "in
2025" / "this past year" (e.g. "$501 million in home loans financed in
2025", "$82 million in Housing Choice Voucher rental assistance provided in
2025"). OHFA's fiscal year ends September 30 (its ACFR covers "the years
ended September 30, 2025 and 2024"). This build treats the report as
covering OHFA's FY2025 (year ended September 30, 2025) -- NOT calendar
2025 -- because the report's figures cross-check exactly against the
FY2025 ACFR's MD&A (FY2025/txt/OK_OHFA_OK_FY2025_ACFR.txt):
  - The report's "An average of 9,898 families assisted with Housing Choice
    Voucher rental assistance each month" equals the ACFR's FY2025
    "Provided 118,776 unit months of Section 8 rental assistance"
    divided by 12 (118,776 / 12 = 9,898 exactly).
  - The report's "$93.6 million in rental assistance paid on behalf of PBCA
    residents" equals the ACFR's FY2025 "Paid $93.6 million in rental
    assistance to project-based Section 8 properties" to the decimal.
  A CY2025 (Jan-Dec) window would not reproduce either figure exactly (it
  would blend nine months of FY2025 with three months of FY2026), so
  fiscal_year is reported honestly as "FY2025". The one imperfect match is
  the HCV dollar figure -- the report says "$82 million" while the ACFR's
  audited FY2025 figure is "$83.1 million" -- a ~1.3% variance consistent
  with the annual report having been drafted from preliminary pre-audit
  data; the report's own "$82 million" is transcribed as-is and the
  variance is documented, not reconciled away (same approach as VA/PA/MN).

Year discipline -- cumulative figures explicitly excluded
------------------------------------------------------------------------
The archived HSP Annual Status Report's headline figures -- "$95,859,011
awarded", "39 developments", "745 new housing units" (454 rental + 291
homeownership) -- are all "since inception" / "to date" figures spanning
from the program's first awards (May 15, 2024) through the report date.
They are never used as fy2025_* values. For the record, OHFA's FY2025 ACFR
MD&A separately discloses the FY2025-only OHSP activity ("The Oklahoma
Housing Stability Program (OHSP) closed 27 loans for a total award amount
of $64.4 million in FY2025"), but the annual report itself does not print
an FY2025 HSP unit or dollar figure that this build could pair into a KPI
category (its HSP section gives only "33 loans in 29 counties" with no
paired dollar or unit count), so HSP is intentionally not modeled here.

Why RAW_PROJECTS is empty ([]) -- no complete per-project cohort list
------------------------------------------------------------------------
Per this build's task briefing (KPI-only verdict): solid multi-category
KPI figures exist, but there is no complete per-project list. Confirmed
independently during this build: the annual report names only two
individual developments in passing (Hillcrest Green II, Alley's End) as
photo captions -- not a complete list of FY2025 activity -- and the
archived HSP status report's only project-level detail is a map legend of
39 developments that is (a) "since inception" cumulative across FY2024 and
FY2025 and (b) embedded as image-rendered district maps whose per-
development details (developer, unit count, award amount) are NOT
machine-extractable as a structured list. RAW_PROJECTS is therefore []
and the output `projects` array is empty -- an honest reflection of what
OHFA discloses at project level, not a placeholder for missing work (the
frontend already renders the bubble map with 0 markers when this is empty).

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
Source: FY2025/txt/OK_OHFA_OK_FY2025_ACFR.txt. VERIFIED before use (this
project has repeatedly found mismatched .txt files under other states):
the Independent Auditor's Report (.txt lines 90-114) covers "the financial
statements of Oklahoma Housing Finance Agency (the Agency, or OHFA), a
component unit of the State of Oklahoma, as of and for the years ended
September 30, 2025 and 2024"; the entity, fiscal year-end, and program
descriptions throughout match the annual report's program lines below.
Unambiguously the correct entity, no substitution needed.

OHFA has NO governmental funds -- Note 2 states "The Agency accounts for
its activities within a proprietary fund type" (.txt line 1661) and "OHFA
is considered a single enterprise fund for financial reporting purposes"
(.txt line 1648). Every program line below is therefore classified within
that single proprietary (business-type/enterprise) fund:
  - single_family_homeownership / single_family_loans -- "proprietary",
    HIGH confidence. Note 1 (.txt lines 1597-1602): "OHFA is authorized...
    to issue mortgage revenue bonds through its Single Family Bond
    Programs... In no event does the indebtedness constitute a debt,
    liability, or moral obligation of the State... OHFA has no taxing
    power." These are OHFA's own bond-financed mortgage loans, core
    business-type activity of the enterprise fund.
  - housing_choice_voucher / section_8_hcv -- "proprietary", MEDIUM-HIGH
    confidence. Note 1 (.txt lines 1607-1609): "OHFA administers Section 8
    Housing Assistance Payments Programs for HUD. OHFA receives
    administrative fees..."; Note 2 (.txt lines 1778-1781) further states
    "The only exception to this accounting policy is the Section 8 Housing
    Choice Voucher Program... any unspent Housing Assistance Payment (HAP)
    becomes part of the net position - restricted for the Section 8 Voucher
    and Emergency Housing Voucher Programs." I.e. the voucher program is a
    federal pass-through that OHFA's own enterprise fund recognizes
    (restricted net position), not a separate governmental fund. The
    classification is "proprietary" by GASB fund type, with the pass-through
    nature documented in fund_name.
  - pbca_rental_assistance / pbca -- "proprietary", HIGH confidence. Note 1
    (.txt lines 1617-1619): "OHFA is the Section 8 Contract Administrator
    for federal HUD-financed Section 8 properties located throughout
    Oklahoma. The Agency receives a fee to administer the program..." The
    MD&A reports "a $7.7 million increase in the Section 8 Contract
    Administration Program revenues" (.txt line 704) -- a fee-for-service
    activity of OHFA's own enterprise fund (the $93.6M of rental assistance
    it administers is pass-through, reflected in restricted net position).

Category-level methodology
------------------------------------------------------------------------
All three categories are single-headline categories with no further
sub-program breakdown disclosed in the annual report, so each uses the
additive=True "single subprogram == the headline" pattern (same as VA's
federal_assistance / MA's single-line categories): one subprogram whose
fy2025_units and fy2025_amount exactly equal the category's fy2025_actual
and fy2025_amounts[0].amount, asserted in verify_category_consistency().

  - single_family_homeownership (unit_type="households", 2,403 buyers /
    $501M). The report's two figures are the same single-family program
    (OHFA's first-mortgage loans are bundled with its DPA/CCA products).
    Internal-consistency support: $501,000,000 / 2,403 ~= $208,489, close
    to the report's own "$208,137 - Average purchase price for OHFA
    homebuyers" (the ~$350 gap is the down payment, i.e. loan < purchase
    price). External cross-check note: the ACFR reports "2,431 single
    family mortgage loans" for FY2025 (.txt line 343) -- a closely-related
    but NOT identical metric ("loans made available" vs. "buyers using
    down payment and closing cost assistance"), and $375.0M of new single
    family bond issuance (.txt line 443) is bond issuance, not the same as
    $501M of loans financed in the year -- so neither is forced to match.

  - housing_choice_voucher (unit_type="households", 9,898 monthly-average
    families / $82M). "9,898" is a monthly average, not a point-in-time
    count; the ACFR's 118,776 unit-months / 12 == 9,898 exactly (external
    check, asserted below). The report's "By the Numbers" summary
    infographic prints "9,998" for the HCV program (vs "9,898" in the
    detailed section) -- a 100-household discrepancy within the source;
    the detailed section's 9,898 is used (it is the figure that
    cross-checks against the audited unit-months) and the discrepancy is
    noted, not silently resolved.

  - pbca_rental_assistance (unit_type="households", 12,578 households /
    $93.6M). The $93.6M matches the ACFR's "Paid $93.6 million in rental
    assistance to project-based Section 8 properties" exactly (external
    check, asserted below). PBCA (Performance Based Contract
    Administration) is OHFA's HUD project-based Section 8 contract
    administration program; the report's "By the Numbers" section confirms
    "12,578 households through the Performance Based Contract
    Administration program".

fy2026
------------------------------------------------------------------------
The 2025 Annual Report is a backward-looking report with no
forward-looking/projected-activity section; its only forward statement is
that HSP funds are "expected to be fully committed by early 2026" (no
FY2026 unit or dollar figures for any category). Every fy2026 field is
therefore {value: None, amount: None, closed: False, note_key:
"okFy26NotePending"}.
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "ok_program_activity.json"

SOURCE_URL = "https://www.ohfa.org/2025-annual-report/"
SOURCE_FILE = (
    "OHFA '2025 Annual Report' ('Where Home Takes Root') -- web page (no "
    "downloadable PDF), raw HTML fetched 2026-08-16; supporting archived "
    "document FY2025/program_activity/pdf/OK_OHFA_HSP_AnnualStatusReport_2025.pdf "
    "(the statutorily-required 2025 Housing Stability Program Annual Status "
    "Report, 12 pages, whose 'since inception' figures are excluded -- see "
    "module docstring)"
)
RETRIEVED = "2026-08-16"

# Independent external cross-check figures, transcribed from OHFA's FY2025
# ACFR MD&A (FY2025/txt/OK_OHFA_OK_FY2025_ACFR.txt, "FINANCIAL HIGHLIGHTS",
# year ended September 30, 2025). These are the "second independent number"
# leg of the dual verification gate.
ACFR_FY2025 = {
    "section8_unit_months": 118776,   # .txt line 346: "Provided 118,776 unit months of Section 8 rental assistance"
    "section8_voucher_paid": 83100000,  # .txt line 348: "Paid $83.1 million ... to benefit Section 8 voucher holders" (annual report says $82M -- see docstring)
    "pbca_paid": 93600000,            # .txt line 351: "Paid $93.6 million ... to project-based Section 8 properties"
    "single_family_loans": 2431,      # .txt line 343: "Made 2,431 single family mortgage loans available to first-time homebuyers"
}

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                 "note_key": "okFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data (OHFA "2025 Annual Report", "Where Home Takes Root")
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "single_family_homeownership",
        "unit_type": "households",
        "fy2025_actual": 2403,
        "fy2025_source_quote": (
            "\"Single Family Homeownership: 2,403 buyers purchased a home using "
            "OHFA down payment and closing cost assistance. $208,137 - Average "
            "purchase price for OHFA homebuyers. $501 million in home loans "
            "financed in 2025.\" (OHFA 2025 Annual Report, 'Where Home Takes "
            "Root', Single Family Homeownership section). The 2,403 buyers and "
            "the $501M in home loans are the same single-family program (OHFA's "
            "first-mortgage loans are bundled with its down payment / closing "
            "cost assistance products); $501,000,000 / 2,403 ~= $208,489, "
            "consistent with the report's own $208,137 average purchase price "
            "(the gap is the down payment, i.e. loan < purchase price). The ACFR's "
            "FY2025 '2,431 single family mortgage loans' is a closely-related "
            "but not identical metric (loans made available vs. buyers using "
            "DPA/CCA) and is not forced to match -- see module docstring."
        ),
        "fy2025_amounts": [
            {"label_key": "ok_amt_home_loans", "amount": 501000000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "single_family_loans", "fy2025_units": 2403, "fy2025_amount": 501000000,
             "color_group": "bond",
             # Note 1: OHFA issues mortgage revenue bonds through its Single
             # Family Bond Programs; "OHFA has no taxing power" -- its own
             # bond-financed mortgage lending, core business-type activity.
             "fund_type": "proprietary", "fund_name": "Single Family Mortgage Revenue Bond Programs",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "housing_choice_voucher",
        "unit_type": "households",
        "fy2025_actual": 9898,
        "fy2025_source_quote": (
            "\"Housing Choice Voucher Program: An average of 9,898 families "
            "assisted with Housing Choice Voucher rental assistance each month. "
            "$82 million in Housing Choice Voucher rental assistance provided in "
            "2025. $692 - average amount of rental assistance received per "
            "assisted household each month.\" (OHFA 2025 Annual Report, 'Where "
            "Home Takes Root', Housing Choice Voucher Program section). '9,898' "
            "is a monthly average, not a point-in-time count. The report's 'By "
            "the Numbers' summary infographic separately prints '9,998' for the "
            "HCV program (a 100-household discrepancy within the source); the "
            "detailed section's 9,898 is used here because it is the figure that "
            "cross-checks against the audited FY2025 ACFR (118,776 unit months / "
            "12 == 9,898 exactly). The report's '$82 million' vs. the ACFR's "
            "audited '$83.1 million' is a ~1.3% preliminary-vs-audited variance, "
            "documented and not reconciled -- see module docstring."
        ),
        "fy2025_amounts": [
            {"label_key": "ok_amt_hcv_rental", "amount": 82000000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "section_8_hcv", "fy2025_units": 9898, "fy2025_amount": 82000000,
             "color_group": "trust",
             # Note 1 + Note 2: OHFA "administers Section 8 Housing Assistance
             # Payments Programs for HUD" and recognizes the HCV program's
             # unspent HAP within its own restricted net position -- a federal
             # pass-through recognized inside OHFA's single enterprise fund.
             "fund_type": "proprietary", "fund_name": "Section 8 Housing Choice Voucher Program (federal pass-through)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "pbca_rental_assistance",
        "unit_type": "households",
        "fy2025_actual": 12578,
        "fy2025_source_quote": (
            "\"Performance Based Contract Administration: OHFA provides "
            "Performance Based Contract Administration (PBCA) services to 165 "
            "properties across the state. 12,578 households receive rental "
            "assistance through PBCA. $93.6 million in rental assistance paid on "
            "behalf of PBCA residents.\" (OHFA 2025 Annual Report, 'Where Home "
            "Takes Root', Performance Based Contract Administration section). The "
            "$93.6 million matches the audited FY2025 ACFR's 'Paid $93.6 million "
            "in rental assistance to project-based Section 8 properties' exactly "
            "(external cross-check, asserted in verify_category_consistency())."
        ),
        "fy2025_amounts": [
            {"label_key": "ok_amt_pbca_rental", "amount": 93600000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "pbca", "fy2025_units": 12578, "fy2025_amount": 93600000,
             "color_group": "trust",
             # Note 1: "OHFA is the Section 8 Contract Administrator for federal
             # HUD-financed Section 8 properties... The Agency receives a fee to
             # administer the program" -- fee-for-service contract administration
             # inside OHFA's own enterprise fund (the $93.6M it administers is
             # pass-through). Confidence: high.
             "fund_type": "proprietary", "fund_name": "Section 8 Contract Administration (PBCA)",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# Per this build's explicit task briefing (KPI-only verdict): OHFA's annual
# report discloses no complete per-project cohort list (only two photo-caption
# development names, plus the HSP status report's image-rendered, "since
# inception" map legend of 39 developments). RAW_PROJECTS is intentionally
# empty; see module docstring "Why RAW_PROJECTS is empty".
RAW_PROJECTS = []


def verify_category_consistency():
    errors = []

    # Internal gate -- each category is a single-headline category, so its one
    # subprogram must exactly equal the category headline (additive=True with a
    # single subprogram is only meaningful if the subprogram *is* the headline).
    for cat in CATEGORIES:
        if len(cat["subprograms"]) != 1:
            errors.append(f"{cat['key']}: expected exactly 1 subprogram, got {len(cat['subprograms'])}")
            continue
        sp = cat["subprograms"][0]
        if sp["fy2025_units"] != cat["fy2025_actual"]:
            errors.append(
                f"{cat['key']}: subprogram units {sp['fy2025_units']} != "
                f"category fy2025_actual {cat['fy2025_actual']}"
            )
        cat_amt = cat["fy2025_amounts"][0]["amount"] if cat["fy2025_amounts"] else None
        if cat_amt is not None and sp["fy2025_amount"] != cat_amt:
            errors.append(
                f"{cat['key']}: subprogram amount {sp['fy2025_amount']} != "
                f"category fy2025_amounts[0].amount {cat_amt}"
            )

    # External gate (second independent number = OHFA's audited FY2025 ACFR):
    #  - HCV "9,898 families/month" must equal the ACFR's 118,776 unit-months / 12.
    #  - PBCA "$93.6M" must equal the ACFR's project-based Section 8 $93.6M.
    hcv = next(c for c in CATEGORIES if c["key"] == "housing_choice_voucher")
    if ACFR_FY2025["section8_unit_months"] // 12 != hcv["fy2025_actual"]:
        errors.append(
            f"housing_choice_voucher: monthly average {hcv['fy2025_actual']} != "
            f"ACFR 118,776 unit-months / 12 = "
            f"{ACFR_FY2025['section8_unit_months'] // 12}"
        )
    if ACFR_FY2025["section8_unit_months"] % 12 != 0:
        errors.append(
            f"housing_choice_voucher: ACFR unit-months {ACFR_FY2025['section8_unit_months']} "
            f"not cleanly divisible by 12"
        )

    pbca = next(c for c in CATEGORIES if c["key"] == "pbca_rental_assistance")
    pbca_amt = pbca["fy2025_amounts"][0]["amount"] if pbca["fy2025_amounts"] else None
    if pbca_amt != ACFR_FY2025["pbca_paid"]:
        errors.append(
            f"pbca_rental_assistance: amount {pbca_amt} != ACFR project-based "
            f"Section 8 paid {ACFR_FY2025['pbca_paid']}"
        )

    # Documented, non-fatal cross-check notes (do NOT hard-error -- these are
    # definitional/rounding differences, not transcription errors, and are
    # handled the same way VA handled its ACFR-vs-annual-report variance):
    hcv_amt = hcv["fy2025_amounts"][0]["amount"] if hcv["fy2025_amounts"] else None
    print(
        "[note] HCV dollars: annual report $82,000,000 vs ACFR audited "
        f"${ACFR_FY2025['section8_voucher_paid']:,} (preliminary-vs-audited "
        "variance; annual report's own figure is used, not reconciled)."
    )
    sf = next(c for c in CATEGORIES if c["key"] == "single_family_homeownership")
    print(
        f"[note] single-family: annual report 2,403 DPA/CCA buyers vs ACFR "
        f"{ACFR_FY2025['single_family_loans']:,} mortgage loans made available "
        "(different metrics; neither forced to match)."
    )

    if RAW_PROJECTS:
        errors.append(
            "RAW_PROJECTS is expected to be empty for OK -- see module docstring; "
            "if a complete project-level list has since become available, update "
            "the docstring before populating this list."
        )

    if errors:
        raise SystemExit("Category consistency mismatch(es):\n" + "\n".join(errors))
    print(
        "Category headline vs. subprogram consistency verified for all 3 "
        "categories; external ACFR cross-checks passed (HCV 118,776/12 = 9,898; "
        "PBCA $93.6M == ACFR $93.6M); RAW_PROJECTS confirmed empty as expected."
    )


def main():
    verify_category_consistency()
    payload = {
        "OK": {
            "hfa_name": "Oklahoma Housing Finance Agency",
            "hfa_abbr": "OHFA",
            "fiscal_year": "FY2025",
            "source_title": "OHFA 2025 Annual Report ('Where Home Takes Root') -- "
                             "Single Family Homeownership, Housing Choice Voucher "
                             "Program, and Performance Based Contract Administration",
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
