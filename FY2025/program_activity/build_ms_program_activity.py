"""
Builds docs/ms_program_activity.json from the Mississippi Home Corporation's
(MHC) "2025 Annual Report" -- a KPI-layer-only build (no per-project cohort),
like VA, MA, and LA. See "Why RAW_PROJECTS is empty" below.

Source
------------------------------------------------------------------------
"2025 Annual Report", Mississippi Home Corporation (MHC), published as a
Visme-hosted interactive report:
    https://my.visme.co/view/op6gwkz1-2025-mhc-annual-report
The report has no PDF; its text was extracted to a local archive file
(ms_text.txt) and every figure below is transcribed from that extraction, not
from memory. The extraction opens with the cover "ANNUAL REPORT 2025 / OUR
PURPOSE OUR PROMISE OUR PEOPLE" and the Executive Director's "OUR PROMISE"
message, followed by the MHC PROGRAMS tiles.

Fiscal-year discipline
------------------------------------------------------------------------
The report's Executive Director message is dated "2026-07-01" and narrates
"in 2025", and its own "OUR PROMISE" prose says "50% of our loans for FY 2025
took place..." -- MHC's audited combined financial statements (FY2025/txt/
MS_MHC_FY2025_ACFR.txt, an audit by Forvis Mazars, LLP) cover "June 30, 2025
and 2024". So "2025" / "FY 2025" = FY2025 (July 1, 2024 - June 30, 2025).
Every KPI used below is the report's own FY2025 program total; no "since
inception"/cumulative figure is modeled (there are none in the KPI tiles).

Every figure below is transcribed from this build's own text extraction
(ms_text.txt), not from memory or a secondary source:
  - Single Family (opening prose + KPI tiles): "MHC continued its mission to
    provide affordable housing across the state in 2025. 1,836 homes were
    financed through our Single Family Programs in 76 counties. MHC issued
    $361 million in mortgage revenue bonds to provide loans and down payment
    assistance for homebuyers." The KPI tiles read "Homes Purchased 1836" and
    "Homeowner Spending $23.2 million". "50% of our loans for FY 2025 took
    place in the 5 counties... our single family products were used in 76 of
    the 82 counties" is outreach/geographic context, not a KPI.
  - LIHTC / Housing Tax Credits (KPI tile + prose): the KPI tile reads
    "LIHTC Units 670", and the prose reads "Additionally, MHC's Housing Tax
    Credit Program proved to be a boost to Mississippi's economy producing
    634 jobs and $34.4 million in wages for working families." The report's
    Housing Tax Credit economic-impact tiles further print "Jobs 275",
    "Wages $16.5 million", and a "$35.5 million" tile (extraction order:
    Jobs/275, Tax Revenue/Total Developments, Wages/$16.5 million, then the
    three tiles 634 / $34.4 / $35.5 million -- several of these sit in image
    charts whose labels do not extract cleanly, so only the prose figures are
    asserted verbatim). Those jobs/wages figures are economic-impact
    estimates, NOT a dollar amount that corresponds to the 670 LIHTC units.

Why RAW_PROJECTS is empty ([]) -- no complete per-project cohort list
------------------------------------------------------------------------
Per this build's task briefing (already investigated, not re-litigated, but
independently confirmed during this build): MHC's Visme annual report has NO
complete per-project FY2025 cohort list. The report presents KPI tiles only
(some figures live in image charts whose text does not extract), and lists a
menu of program names (HOPWA, CHOICE, ESG, HTF, HOME Rental, HTC, AMI, HOME
Homeowner Rehabilitation, Home4All, MAHDF, RLF, HAT, MCC, MRB Products,
Smart6, Smart7) without a per-development name/address/unit/dollar cohort.
RAW_PROJECTS is therefore [] and the output `projects` array is empty -- the
honest KPI-only result, not a placeholder. The frontend (docs/program_activity.js)
renders the KPI cards normally and the bubble map with 0 markers.

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
Source: FY2025/txt/MS_MHC_FY2025_ACFR.txt. VERIFIED before use: title page
reads "Mississippi Home Corporation ... Combined Financial Statements ...
June 30, 2025 and 2024"; the Independent Auditor's Report covers MHC's
combined financial statements as of and for the year ended June 30, 2025.
Unambiguously the correct entity, no substitution needed.

MHC reports its accounts "as a separate set of self-balancing accounts that
comprise the assets, deferred outflows, liabilities, net position, revenues,
and expenses of the Mortgage Revenue Bond Program, the Down Payment
Assistance Program, the Mississippi Affordable Housing Development Program,
the House Bill 530 Program, and the General Corporate Fund" and states "The
measurement focus is on determining operating income and capital maintenance"
(.txt lines 692-696) -- i.e. a single combined enterprise/proprietary fund.
Classification below follows from this:
  - "proprietary" (HIGH confidence) -- single_family_loans. Note 8 "Mortgage
    Revenue Bond Program" (.txt lines 1252-1260): "The Corporation's Mortgage
    Revenue Bond (MRB) Program provides loans to qualified borrowers for
    purchases of the borrower's primary residence." The MRB Program is one of
    the funds combined into MHC's own self-balancing accounts -- MHC's core
    lending business. fund_name "Mortgage Revenue Bond Program".
  - "off_balance_sheet" (HIGH confidence) -- multifamily_lihtc. Note 11 "Low
    Income Housing Tax Credit Program" (.txt lines 1287-1294): "The
    Corporation has been designated as the allocating agency for the Low
    Income Housing Tax Credit Program (Tax Credit Program)." and "Receipts
    under the Tax Credit Program represent fees earned for administering the
    Tax Credit Program and are not restricted under the terms of the Plan or
    the Tax Credit Program." The credits themselves flow to developers/
    investors, not to MHC's own balance sheet; MHC recognizes only the
    administration fees as revenue. fund_name "Low Income Housing Tax Credit
    Program (fee-administered)".
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "ms_program_activity.json"

SOURCE_URL = "https://my.visme.co/view/op6gwkz1-2025-mhc-annual-report"
SOURCE_FILE = (
    "MHC 2025 Annual Report (Visme-hosted interactive report; no PDF -- text "
    "extracted and archived locally as ms_text.txt for this build)"
)
RETRIEVED = "2026-08-16"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "msFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data (MHC 2025 Annual Report KPI tiles)
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "single_family_loans",
        "unit_type": "households",
        "fy2025_actual": 1836,
        "fy2025_source_quote": (
            "\"MHC continued its mission to provide affordable housing across the "
            "state in 2025. 1,836 homes were financed through our Single Family "
            "Programs in 76 counties. MHC issued $361 million in mortgage revenue "
            "bonds to provide loans and down payment assistance for homebuyers.\" "
            "(MHC 2025 Annual Report, Executive Director 'OUR PROMISE' message). "
            "The accompanying KPI tiles read \"Homes Purchased 1836\" and "
            "\"Homeowner Spending $23.2 million\". The 1,836-home / $361M-MRB pair "
            "is the single-family homeownership KPI; the $23.2M \"Homeowner "
            "Spending\" tile is a separate economic/spending metric with no "
            "per-loan partition, so it is quoted here for completeness but not "
            "modeled as a separate amount (the $361M MRB issuance is the amount "
            "that corresponds to the 1,836 financed homes). The \"50% of our "
            "loans for FY 2025 took place in the 5 counties... single family "
            "products were used in 76 of the 82 counties\" line is geographic/"
            "outreach context, not a KPI."
        ),
        "fy2025_amounts": [
            {"label_key": "ms_amt_mrb", "amount": 361000000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "single_family_mrb", "fy2025_units": 1836, "fy2025_amount": 361000000,
             "color_group": "bond",
             # ACFR Note 8: the MRB Program is one of the funds combined into
             # MHC's own self-balancing accounts (single enterprise/proprietary
             # fund). See module docstring.
             "fund_type": "proprietary",
             "fund_name": "Mortgage Revenue Bond Program",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "multifamily_lihtc",
        "unit_type": "units",
        "fy2025_actual": 670,
        "fy2025_source_quote": (
            "KPI tile \"LIHTC Units 670\"; prose: \"Additionally, MHC's Housing "
            "Tax Credit Program proved to be a boost to Mississippi's economy "
            "producing 634 jobs and $34.4 million in wages for working "
            "families.\" (MHC 2025 Annual Report, Executive Director 'OUR PROMISE' "
            "message + 'HOUSING TAX CREDITS' tiles). The report's Housing Tax "
            "Credit economic-impact tiles further print \"Jobs 275\", \"Wages "
            "$16.5 million\", and a \"$35.5 million\" tax-revenue/economy tile "
            "(several of these sit in image charts whose labels do not extract "
            "cleanly, so only the prose figures are asserted verbatim). Those "
            "jobs/wages figures are economic-impact estimates, NOT a dollar "
            "amount that corresponds to the 670 LIHTC units, so this category "
            "carries no fy2025 amount (fy2025_amounts is empty; the economic-"
            "impact numbers are quoted here for completeness but not modeled as "
            "a housing-unit amount). The 670-unit figure is the housing-unit KPI."
        ),
        "fy2025_amounts": [],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "lihtc_units", "fy2025_units": 670, "fy2025_amount": None,
             "color_group": "credit",
             # ACFR Note 11: MHC is only the *allocating agency* for the Tax
             # Credit Program and recognizes only the administration fees as
             # revenue; the credits flow to developers/investors
             # (off-balance-sheet). See module docstring.
             "fund_type": "off_balance_sheet",
             "fund_name": "Low Income Housing Tax Credit Program (fee-administered)",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# Per this build's explicit task briefing: MHC's Visme report has NO complete
# per-project FY2025 cohort list (KPI tiles only; some figures live in image
# charts that don't extract). RAW_PROJECTS is intentionally empty; see module
# docstring.
RAW_PROJECTS = []


def verify_category_consistency():
    errors = []
    warnings = []

    # single_family_loans: single subprogram must equal the 1,836-home /
    # $361,000,000 headline (additive=True with 1 subprogram = the headline).
    sf = next(c for c in CATEGORIES if c["key"] == "single_family_loans")
    if len(sf["subprograms"]) != 1:
        errors.append(f"single_family_loans: expected 1 subprogram, got {len(sf['subprograms'])}")
    else:
        sp = sf["subprograms"][0]
        if sp["fy2025_units"] != sf["fy2025_actual"]:
            errors.append(f"single_family_loans: subprogram units {sp['fy2025_units']} "
                          f"!= headline {sf['fy2025_actual']}")
        if sp["fy2025_amount"] != sf["fy2025_amounts"][0]["amount"]:
            errors.append(f"single_family_loans: subprogram amount {sp['fy2025_amount']} "
                          f"!= headline amount {sf['fy2025_amounts'][0]['amount']}")

    # multifamily_lihtc: single subprogram must equal the 670-unit headline, and
    # must carry no dollar amount (the report's $34.4M/634-jobs figures are
    # economic-impact, not a per-unit credit amount).
    mf = next(c for c in CATEGORIES if c["key"] == "multifamily_lihtc")
    if len(mf["subprograms"]) != 1:
        errors.append(f"multifamily_lihtc: expected 1 subprogram, got {len(mf['subprograms'])}")
    else:
        sp = mf["subprograms"][0]
        if sp["fy2025_units"] != mf["fy2025_actual"]:
            errors.append(f"multifamily_lihtc: subprogram units {sp['fy2025_units']} "
                          f"!= headline {mf['fy2025_actual']}")
        if sp["fy2025_amount"] is not None:
            errors.append(f"multifamily_lihtc: subprogram amount should be null, "
                          f"got {sp['fy2025_amount']} (no per-unit credit amount is disclosed)")
    if mf["fy2025_amounts"]:
        errors.append("multifamily_lihtc: fy2025_amounts should be empty "
                      "(economic-impact wages/jobs figures are not a credit amount)")

    if RAW_PROJECTS:
        errors.append(
            "RAW_PROJECTS is expected to be empty for MS -- see module docstring; "
            "if a complete per-project cohort list has since become available, "
            "update the docstring before populating this list."
        )

    for w in warnings:
        print(f"WARNING: {w}")
    if errors:
        raise SystemExit("Category consistency mismatch(es):\n" + "\n".join(errors))
    print("Category headline vs. subprogram consistency verified: "
          "single_family_loans (1,836 homes / $361,000,000 MRB), "
          "multifamily_lihtc (670 units, no amount). "
          "RAW_PROJECTS confirmed empty as expected.")


def main():
    verify_category_consistency()
    payload = {
        "MS": {
            "hfa_name": "Mississippi Home Corporation",
            "hfa_abbr": "MHC",
            "fiscal_year": "FY2025",
            "source_title": "Mississippi Home Corporation 2025 Annual Report -- "
                             "Single Family Programs & Housing Tax Credits KPI tiles",
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
