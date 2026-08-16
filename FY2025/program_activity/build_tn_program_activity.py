"""
Builds docs/tn_program_activity.json from the Tennessee Housing Development
Agency's (THDA) "2025 Investments and Impacts" report -- the agency's annual
comprehensive program/impact report -- plus THDA's own FY2025 audited
financial statements (used ONLY for GASB fund-type classification). This is a
KPI-layer-only build (RAW_PROJECTS = [], projects: []), mirroring VA/MA: THDA
publishes solid multi-category KPI figures (household/unit counts paired with
dollar amounts) but NO complete per-project cohort list -- only county-level
and congressional-district aggregation tables, not a full list of every
development/homebuyer.

Source
------------------------------------------------------------------------
"2025 Investments and Impacts", Tennessee Housing Development Agency (THDA),
authored by THDA research staff (Jessie Hu, Research Analyst; Hulya Arik, PhD,
Senior Economist), 147 pages. Landing page:
    https://thda.org/research-and-reports/investments-impacts/
Direct PDF (downloaded and archived per this build's task briefing; verified
live 2026-08-16: HTTP 200, 7,923,324 bytes, 147 pages, pypdf extracts the
"Tennessee Program Totals" table and the "Homeownership & Rental Summaries"
chapter):
    https://dogvxws799i6n.cloudfront.net/wp-content/uploads/2025-Investments-and-Impacts-Draft-Final.pdf
Local copy:
    FY2025/program_activity/pdf/TN_THDA_InvestmentsImpacts_2025.pdf

(Note: the task brief's catalog starting URL https://thda.org/about/financial-
reports/ returns HTTP 404 -- the report actually lives under
/research-and-reports/. The "Investments & Impacts" report is described by
THDA itself, on the /tn-program-reports-and-data/ page, as its "annual
comprehensive report about THDA's programs", so it is the correct primary
source for program-activity KPIs, not the audited ACFR.)

Fiscal-year discipline (title year is NOT proof of content year)
------------------------------------------------------------------------
The report is titled "2025" but that is a CALENDAR-year label, not THDA's
fiscal year. THDA's own ACFR has a June 30 fiscal year-end (FY2025 = July 1,
2024 - June 30, 2025), but this report's figures are explicitly CY2025
(calendar year 2025), confirmed by the report's own methodology text:
  - LIHEAP (p.135): "...the number of households served and the dollar amount
    of LIHEAP assistance provided in each county include both Crisis LIHEAP
    and Regular LIHEAP households served and payments made during the
    calendar year."
  - Section 8 (p.140): "...the number of families who lived in a project-based
    unit in 2025" / "...used a voucher ... in 2025."
  - Multi-Family Bond (p.137): "In 2025, several deals could not close due to
    the partial federal government shutdown that occurred for 43 days from
    October 1 to November 12, 2025."
  - Low Income Housing Credits (p.136): "Units are counted in the year in
    which the tax credits are allocated..."
So the honest fiscal_year field is "CY2025" (this script does not label it
"FY2025"). Every category below uses only the report's own CY2025 columns;
cumulative ("since inception"/"cumulative") figures are explicitly excluded.

Historical-cumulative figures explicitly excluded (NOT used anywhere)
------------------------------------------------------------------------
The report prints cumulative columns alongside each CY2025 figure. The
following are cumulative and are NEVER used as a fy2025_* value here:
140,441 home loans / $12.1B (Great Choice since 1974), 101,414 units /
$778.2M (LIHC since 1987), 109,599 renters / $304.2M (Emergency Rental
Assistance since 2021), 2,659 homeowners / $55.2M (Homeowner's Assistance
Fund), 55,295 units / $4.6B (Multi-Family Bond), 13,201 households / $454.7M
(HOME), 13,327 households / $133M (THTF), 1.2M households / $756.7M (LIHEAP),
and the $2.2B / 12,145 jobs "economic impact" headline (a derived IMPLAN
multiplier estimate, not a program-activity unit/dollar KPI, so it is not a
category either).

Why RAW_PROJECTS is empty ([])
------------------------------------------------------------------------
The report discloses NO complete per-project list. Its program detail is:
(a) the statewide "Tennessee Program Totals" table (PDF p.9), (b) per-county
program-totals tables (PDF pp.19-124, ~95 county tables), and (c) per-county
and per-congressional-district Homeownership/Rental summary totals (PDF
pp.126-129). The only "list" is the ESG/HOME-ARP CoC agency lists in the
Appendix (pp.143-145), which are homelessness-support-service agency awards,
not a housing-development/homebuyer cohort. Per this project's methodology
(see build_va_program_activity.py and build_ma_program_activity.py
docstrings), aggregating a county table into fake per-project rows would
misrepresent the source; RAW_PROJECTS is therefore [] and the output
`projects` array is empty -- an honest reflection of what THDA discloses at
project level. The frontend (docs/program_activity.js) renders the KPI cards
and shows the bubble map with 0 markers in this case.

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
Source: FY2025/txt/TN_THDA_FY2025_ACFR.txt. VERIFIED before use: title page
reads "Tennessee Housing Development Agency ... as of and for the year ended
June 30, 2025", the Independent Auditor's Report (lines 9-17) covers "the
financial statements of the Tennessee Housing Development Agency, a component
unit of the State of Tennessee", and the entity/purpose descriptions match
this report's own programs throughout (Great Choice, Section 8, Tennessee
Housing Trust Fund, bond programs). Correct document, no substitution.

THDA reports a SINGLE business-type/proprietary entity -- "Basis of
Presentation" (ACFR txt, Note 1) states the statements use "the accrual basis
of accounting and the flow of economic resources measurement focus" (the
proprietary-fund model) and that THDA "is a component unit of the State of
Tennessee ... discretely presented in Tennessee's Annual Comprehensive
Financial Report". There are NO governmental funds, and the 15 "fiduciary"
hits in the txt are all pension/OPEB (TCRS / OPEB Trust) measurement-note
text, not THDA funds of its own. So the default classification is
"proprietary" (THDA's own business-type activities), with the single
off-balance-sheet exception below.

  - "proprietary", HIGH confidence (THDA's own core business or a program the
    ACFR names and quantifies directly):
      * great_choice / new_start -- THDA's own single-family mortgage loan
        programs. The ACFR's whole balance sheet is these loans; the MD&A
        ("Financial Highlights") and Note 1 name the "Mortgage Finance
        Program, Single Family Program, Housing Finance Program, and General
        Residential Finance Program bond resolutions". New Start is a THDA
        loan program (report Methodology p.138). Confidence: high.
      * Section 8 subprograms (tenant_based_rental,
        tenant_based_homeownership, project_based) -- the ACFR MD&A states
        "Nonoperating grant revenues increased $47.5 million, and nonoperating
        grant expenses increased $45.7 million, primarily due to the HUD
        assignment of new Section 8 Project-Based Contract Administration
        properties to THDA's portfolio" (txt around char 18066), i.e. Section
        8 is recognized as grant revenue/expense INSIDE THDA's single
        proprietary fund. Confidence: high.
      * tn_housing_trust_fund -- the ACFR Note (txt around char 19016) names
        "Tennessee Housing Trust Fund" verbatim as a grant program THDA
        established, funded by "state appropriations, THDA funds,
        private-sector investment, and matching funds" (a funding table shows
        $9.7M THDA + $0 state in 2025). On THDA's own books. Confidence: high.
      * multifamily_bond -- THDA's own tax-exempt bond issuance (the ACFR
        shows "bonds outstanding ... $3,919,245" thousands and lists
        Multi-Family bond series). Bonds are THDA liabilities. Confidence:
        high.
  - "off_balance_sheet", HIGH confidence:
      * lihtc -- federal Low-Income Housing Tax Credits are allocated to
        developers/investors, never booked as a THDA asset. The ACFR contains
        ZERO occurrences of "low-income housing tax credit" / "tax credit"
        (verified by script grep), consistent with credits flowing off THDA's
        books -- same off-balance-sheet logic as every other pilot state's
        LIHTC subprogram. Confidence: high.
  - "proprietary", MEDIUM confidence (federal grant programs administered by
    THDA but not verbatim-named in the ACFR):
      * liheap_homeownership / liheap_rental -- LIHEAP is a federal formula
        grant THDA administers; it is recognized within THDA's single
        proprietary fund as nonoperating grant revenue/expense (the ACFR's
        MD&A confirms the grant revenue/expense lines exist, and its
        "unexpended grant money ... awarded to grantees" note covers such
        federal pass-through programs), but the word "LIHEAP" does not itself
        appear in the ACFR txt. Confidence: medium.
      * home (HOME Investment Partnerships) -- same reasoning: a federal
        formula grant administered by THDA within its proprietary fund; the
        ACFR does not name "HOME Investment Partnerships" verbatim (its
        "HOME" hits are all "homeownership"/"Homeownership" words).
        Confidence: medium.

Category-level methodology
------------------------------------------------------------------------
All five categories below are transcribed from the report's own statewide
"Tennessee Program Totals" table (PDF p.9), which pairs every program's
CY2025 Units/HHs with a CY2025 dollar figure, cross-checked against the
narrative chapters (pp.6-8) and the report's own Methodology chapter
(pp.130-141).

1. homeownership_loans (additive=True): the report's two first-mortgage
   programs, Great Choice Home Loans (1,802 households, $423.4M) and New
   Start (30 households, $5.7M). These are a true partition (a borrower is in
   one or the other), summed to 1,832 / $429.1M. IMPORTANT source-internal
   inconsistency, resolved in favor of the table + methodology: the narrative
   on p.6 says "The Great Choice and New Start Homeownership Loan Programs
   created 1,802 first time homeowners totaling $423.4M in home loans", but
   the table lists Great Choice (1,802/$423.4M) and New Start (30/$5.7M) as
   separate rows, and the Methodology (pp.133, 138) states "In previous
   years, New Start Program loans were reported under Great Choice Home
   Loans, but have been separated out since 2020." The p.6 sentence is a
   stale pre-2020 grouping; the table + methodology (which separate New Start
   out) are authoritative, so the combined homeownership-loan total is
   1,802 + 30 = 1,832 (this script's own sum, asserted once in
   verify_category_consistency()). Great Choice Plus DPA (1,766 borrowers /
   $17.4M) is a second-mortgage down-payment product "not included in the
   Homeownership Loan Program units and dollars" (p.133), so it is NOT a
   subprogram here (noted for context only).

2. rental_assistance (additive=True): Section 8 Rental Assistance =
   38,993 households / $377.4M, a perfect three-way partition:
   tenant_based_rental (5,991 / $60.8M) + tenant_based_homeownership (38 /
   $271,517) + project_based (32,964 / $316.3M). Units sum exactly
   (5,991+38+32,964 = 38,993); the three printed dollar parts sum to
   $377,371,517, which is the "$377.4M" headline rounded to $0.1M (the
   sub-parts "$60.8M" and "$316.3M" are themselves rounded). Verified in
   verify_category_consistency().

3. multifamily_lihtc (additive=False): Low Income Housing Credits = 4,197
   units / $71.6M, plus Multi-Family Bond Authority = 2,653 units / $399.2M.
   The bond units are a SUBSET of the LIHC units, not an additional
   population -- footnote 2 (p.9) and Methodology p.137: "Nearly all
   Multifamily Tax Exempt Bond transactions also utilize non-competitive Low
   Income Housing Credits (LIHC) for some or all of the units. The LIHC total
   unit reported is inclusive of these units." So additive=False (same
   non-additive pattern as AR's multifamily_lihtc). CRITICAL year-basis note:
   Methodology p.136 states "In prior years, THDA has reported the total
   value of tax credits, or those over 10 years. Starting in the 2025
   Investments and Impacts report, THDA will only report the one year value
   of tax credits." So $71.6M is the ONE-YEAR (annual) credit allocation, not
   a 10-year total -- the honest reading, cross-checked against THDA's own
   Sept 8, 2025 press release ("over $25 million in annual 9% ... LIHTC" for
   988 units → "$250 million over the next ten years"), which is the 9%
   competitive subset of this $71.6M total (the report's LIHC also includes
   4% non-competitive bond credits). $399.2M bond authority is bond
   financing, not a tax-credit value; Methodology p.137 notes only "$399M of
   its bond allocation" closed in 2025 due to the Oct 1-Nov 12, 2025 partial
   federal shutdown.

4. liheap_energy_assistance (additive=True): the Low Income Home Energy
   Assistance Program = 74,438 households / $54.3M, a perfect two-way
   partition: liheap_homeownership (24,314 / $17.7M) + liheap_rental (50,124
   / $36.6M) -- both sums are exact. Methodology p.135 notes 2025 households
   are "lower than they were in previous years" due to a vendor-change
   payment-records delay (documented, not resolved). The separate, small
   Weatherization Assistance Program (294 households / $3.8M, with 273
   homeownership / 21 rental) is deliberately NOT folded into this category
   because Methodology pp.135/141 explain THDA transfers part of its LIHEAP
   allocation into WAP and, in 2025, "removed the households that received
   LIHEAP Weatherization assistance funding from Weatherization Assistance
   Program households" -- a funding/overlap nuance that would blur a clean
   additive partition; it is documented here rather than silently omitted.

5. home_program_grants (additive=True): two distinct household-serving grant
   programs grouped for display (both are counted in households by the
   source): HOME Investment Partnerships = 142 households / $19.6M (131
   homeownership / $18.3M + 11 rental / $1.4M), and the Tennessee Housing
   Trust Fund = 335 households / $6.4M (Competitive Grants 44/$3.5M +
   Emergency Repair 150/$2.2M + Habitat 20/$500,000 + Home Modifications
   121/$175,037). Sum = 477 households / $26.0M. No overlap between the two
   programs is stated anywhere in the report. The National Housing Trust Fund
   (18 rental UNITS / $3.5M) is EXCLUDED from this household-counted category
   because the source counts it in rental units, not households -- mixing
   unit types in one additive category would be wrong; it is documented here,
   not silently merged.

External cross-check (press release)
------------------------------------------------------------------------
THDA's Sept 8, 2025 news release "THDA Awards Over $25 Million in Federal
Housing Credits" (https://thda.org/news/9057-2/) independently states the 2025
9% competitive LIHTC round was "over $25 million in annual 9% ... LIHTC"
supporting "988 affordable housing units" across 17 developments. This is the
9%-competitive SUBSET of the report's LIHC total (4,197 units / $71.6M, which
also includes 4% non-competitive credits). The two sources are consistent
(988 <= 4,197; ~$25M < $71.6M) but are not numerically equal, so this is
checked as a monotonic-consistency assertion in verify_category_consistency(),
not an equality -- per this project's standing rule against forced
reconciliation.

Honest gaps (documented, not fabricated)
------------------------------------------------------------------------
- Dollar-only / cumulative-only lines are not modeled: Emergency Rental
  Assistance (cumulative $304.2M/109,599 only -- "In 2025, the program
  ended"), Homeowner's Assistance Fund (cumulative $55.2M/2,659 only),
  Rebuild & Recover and Capacity Building (no 2025 units), Emergency
  Solutions Grant (reported as "--" in the 2025 columns; its CoC detail in
  the Appendix is 2024 activity, "In 2024, ESG funding assisted an estimated
  3,291 households"), and Community Investment Tax Credits ($600.9M / 2,504
  households is disclosed but Methodology p.131 says "it is not recommended
  that a per-unit cost calculation be derived from these data" and the
  dollars are below-market loan/contribution amounts, not actual tax-credit
  value, and are excluded from the report's own homeownership/rental dollar
  totals -- so CITC is left out of the KPI cards).
- The Homeownership & Rental Summary statewide totals (29,669 HH / $553.6M
  homeownership; 205,353 HH / $1.8B rental, PDF p.126) use deduplication
  rules (removing double-counted LIHC/MF-bond units, DPA second mortgages,
  and homebuyer-education participants -- see the "Note about these totals"
  on p.129) that make them non-additive with the program-level rows, so this
  script verifies categories against the program-level table only and does
  not force the two views to reconcile.

fy2026
------------------------------------------------------------------------
The 2025 Investments and Impacts report is backward-looking (CY2025 actuals)
with no forward-looking/projected-activity section; every fy2026 field below
is {value: None, amount: None, closed: False, note_key: "tnFy26NotePending"}.

Geocoding
------------------------------------------------------------------------
None needed: this is a KPI-only build with RAW_PROJECTS = [] (no projects to
geocode). The output JSON is fully deterministic (no network calls, no
timestamps), so re-runs are byte-identical.
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "tn_program_activity.json"

SOURCE_URL = "https://thda.org/research-and-reports/investments-impacts/"
SOURCE_FILE = (
    "TN_THDA_InvestmentsImpacts_2025.pdf (downloaded from "
    "https://dogvxws799i6n.cloudfront.net/wp-content/uploads/"
    "2025-Investments-and-Impacts-Draft-Final.pdf linked from the landing page "
    "above; verified live 2026-08-16, HTTP 200, 7,923,324 bytes, 147 pages)"
)
RETRIEVED = "2026-08-16"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                 "note_key": "tnFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data ("Tennessee Program Totals" table, PDF p.9, CY2025
# columns, cross-checked against the narrative chapters pp.6-8)
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "homeownership_loans",
        "unit_type": "households",
        "fy2025_actual": 1832,
        "fy2025_source_quote": (
            "\"The Great Choice and New Start Homeownership Loan Programs created "
            "1,802 first time homeowners totaling $423.4M in home loans.\" (2025 "
            "Investments and Impacts, 'Homeownership and Maintenance Programs', p.6). "
            "The 'Tennessee Program Totals' table (p.9) lists these as two separate "
            "rows: 'Great Choice Home Loans ... 1,802 $423.4M' and 'New Start Loan "
            "Program ... 30 $5.7M', and the Methodology (pp.133/138) states 'In "
            "previous years, New Start Program loans were reported under Great Choice "
            "Home Loans, but have been separated out since 2020.' The p.6 sentence's "
            "joint 'Great Choice and New Start ... 1,802' phrasing is a stale pre-2020 "
            "grouping; this script follows the table + methodology (New Start separated "
            "out), so the combined CY2025 homeownership-loan total is 1,802 + 30 = "
            "1,832 households / $423.4M + $5.7M = $429.1M (1,802 and 30 asserted as the "
            "source's own separate rows, summed once in verify_category_consistency()). "
            "Great Choice Plus DPA (1,766 borrowers / $17.4M) is a second-mortgage "
            "product 'not included in the Homeownership Loan Program units and dollars' "
            "(p.133) and is NOT a subprogram here."
        ),
        "fy2025_amounts": [
            {"label_key": "tn_amt_home_loans_total", "amount": 429100000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "great_choice", "fy2025_units": 1802, "fy2025_amount": 423400000,
             "color_group": "bond",
             # THDA's own single-family mortgage lending -- the agency's core
             # business-type activity (ACFR "Single Family Program" bond
             # resolutions; the whole balance sheet is these loans).
             "fund_type": "proprietary",
             "fund_name": "Single Family Program (first mortgage loans)",
             "fy2026": _FY26_PENDING},
            {"key": "new_start", "fy2025_units": 30, "fy2025_amount": 5700000,
             "color_group": "bond",
             # THDA's own loan program (report Methodology p.138); separated
             # out of Great Choice in the source since 2020.
             "fund_type": "proprietary",
             "fund_name": "New Start Loan Program (first mortgage loans)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "rental_assistance",
        "unit_type": "households",
        "fy2025_actual": 38993,
        "fy2025_source_quote": (
            "\"Section 8 Rental Assistance helped 38,993 households with $377.4M in rent "
            "and utility assistance. Of this: Tenant-based Housing Choice Voucher "
            "assistance of $60.8M aided 5,991 households living in privately owned rental "
            "housing. Through the Section 8 to Homeownership Program, 38 families received "
            "housing choice vouchers utilizing $271,517 in voucher assistance to make "
            "mortgage payments rather than rental payments. ... Project-based assistance "
            "of $316.3M helped 32,964 families pay an affordable rent in properties under "
            "contract with the U.S. Department of Housing and Urban Development (HUD).\" "
            "(2025 Investments and Impacts, 'Rental Development and Assistance Programs', "
            "p.7). 5,991 + 38 + 32,964 = 38,993 exactly (a perfect partition, verified in "
            "verify_category_consistency()). The three printed dollar parts sum to "
            "$377,371,517, which is the report's own '$377.4M' headline rounded to $0.1M "
            "(the '$60.8M' and '$316.3M' parts are themselves rounded)."
        ),
        "fy2025_amounts": [
            {"label_key": "tn_amt_section8_total", "amount": 377400000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "tenant_based_rental", "fy2025_units": 5991, "fy2025_amount": 60800000,
             "color_group": "trust",
             # ACFR MD&A: Section 8 PBCA is recognized inside THDA's single
             # proprietary fund as nonoperating grant revenue/expense.
             "fund_type": "proprietary",
             "fund_name": "Section 8 Housing Choice Voucher (federal pass-through grant revenue/expense)",
             "fy2026": _FY26_PENDING},
            {"key": "tenant_based_homeownership", "fy2025_units": 38, "fy2025_amount": 271517,
             "color_group": "trust",
             "fund_type": "proprietary",
             "fund_name": "Section 8 to Homeownership (federal pass-through grant revenue/expense)",
             "fy2026": _FY26_PENDING},
            {"key": "project_based", "fy2025_units": 32964, "fy2025_amount": 316300000,
             "color_group": "trust",
             "fund_type": "proprietary",
             "fund_name": "Section 8 Project-Based Contract Administration (federal pass-through grant revenue/expense)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "multifamily_lihtc",
        "unit_type": "units",
        "fy2025_actual": 4197,
        "fy2025_source_quote": (
            "\"Low Income Housing Credits in the amount of $71.6M were allocated to create "
            "or rehabilitate 4,197 affordable rental units. Of these, 2,653 units utilized "
            "$399.2M in Multi-Family Bond Authority to assist in financing the deal.\" "
            "(2025 Investments and Impacts, 'Rental Development and Assistance Programs', "
            "p.7). The Methodology (p.136) states 'Starting in the 2025 Investments and "
            "Impacts report, THDA will only report the one year value of tax credits' "
            "(previously the 10-year value) -- so $71.6M is the ONE-YEAR credit "
            "allocation, not a 10-year total. The 2,653 bond units are a SUBSET of the "
            "4,197 LIHC units (footnote 2, p.9: 'The LIHC total unit reported is inclusive "
            "of these units'), so this category is non-additive (additive=False). "
            "Methodology p.137 notes only $399M of the bond allocation closed in 2025 due "
            "to the Oct 1-Nov 12, 2025 partial federal shutdown. Externally cross-checked "
            "against THDA's Sept 8, 2025 press release ('over $25 million in annual 9% ... "
            "LIHTC' / 988 units / $250M over 10 years) -- the 9% competitive subset of "
            "this $71.6M total."
        ),
        "fy2025_amounts": [
            {"label_key": "tn_amt_lihtc", "amount": 71600000},
            {"label_key": "tn_amt_multifamily_bond", "amount": 399200000},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "lihtc", "fy2025_units": 4197, "fy2025_amount": 71600000,
             "color_group": "credit",
             # Federal low-income housing tax credits are allocated to
             # developers/investors, never booked as a THDA asset; the ACFR
             # contains zero occurrences of "low-income housing tax credit"/
             # "tax credit". $71.6M is the ONE-YEAR credit value (see quote).
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "multifamily_bond", "fy2025_units": 2653, "fy2025_amount": 399200000,
             "color_group": "bond",
             # THDA's own tax-exempt bond issuance; bonds payable are a THDA
             # liability on its balance sheet (ACFR MD&A "bonds outstanding").
             "fund_type": "proprietary",
             "fund_name": "Multi-Family Tax-Exempt Bond Authority",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "liheap_energy_assistance",
        "unit_type": "households",
        "fy2025_actual": 74438,
        "fy2025_source_quote": (
            "\"The Low Income Home Energy Assistance Program awarded $17.7M to non-profits "
            "serving Tennessee to assist 24,314 low-income homeowners with their heating "
            "and cooling expenses.\" (p.6) and \"...awarded $36.6M ... to assist 50,124 "
            "low-income renters with paying heating and cooling expenses.\" (p.7) -- "
            "'Tennessee Program Totals' table (p.9): 'Low-Income Home Energy Assistance "
            "Program ... 74,438 $54.3M'. 24,314 + 50,124 = 74,438 and $17.7M + $36.6M = "
            "$54.3M, an exact partition (verified in verify_category_consistency()). "
            "Methodology p.135: CY2025 households are 'lower than they were in previous "
            "years' because a vendor-change delayed some 2025 payment records (a "
            "documented source caveat, not a transcription issue). The separate, small "
            "Weatherization Assistance Program (294 households / $3.8M) is intentionally "
            "not folded in here: Methodology pp.135/141 explain THDA transfers part of its "
            "LIHEAP allocation into WAP and, in 2025, removed LIHEAP-weatherization "
            "households from the WAP count -- an overlap/funding nuance that would blur a "
            "clean additive partition."
        ),
        "fy2025_amounts": [
            {"label_key": "tn_amt_liheap_total", "amount": 54300000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "liheap_homeownership", "fy2025_units": 24314, "fy2025_amount": 17700000,
             "color_group": "trust",
             # Federal formula grant administered by THDA within its single
             # proprietary fund (recognized as nonoperating grant
             # revenue/expense); "LIHEAP" not verbatim-named in the ACFR.
             "fund_type": "proprietary",
             "fund_name": "LIHEAP (federal grant administered by THDA)",
             "fy2026": _FY26_PENDING},
            {"key": "liheap_rental", "fy2025_units": 50124, "fy2025_amount": 36600000,
             "color_group": "trust",
             "fund_type": "proprietary",
             "fund_name": "LIHEAP (federal grant administered by THDA)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "home_program_grants",
        "unit_type": "households",
        "fy2025_actual": 477,
        "fy2025_source_quote": (
            "\"The HOME Program awarded $19.6M to local governments and non-profit "
            "organizations to provide rehabilitation, homeownership, and rental services "
            "to 142 households.\" (p.6). \"Tennessee's Housing Trust Fund ... 335 $6.4M\" "
            "('Tennessee Program Totals', p.9) -- composed of Competitive Grants (44 "
            "households / $3.5M), Emergency Repair (150 / $2,239,293), Habitat for "
            "Humanity of Tennessee (20 / $500,000), and Home Modifications and Ramps (121 "
            "/ $175,037), per pp.6-7. 142 + 335 = 477 households and $19.6M + $6.4M = "
            "$26.0M (verified in verify_category_consistency()). No overlap between HOME "
            "and THTF is stated anywhere in the report, so this is treated as a true "
            "partition of the two grant programs. The National Housing Trust Fund (18 "
            "rental UNITS / $3.5M) is EXCLUDED because the source counts it in rental "
            "units, not households -- mixing unit types in one household-counted category "
            "would be wrong; it is documented, not silently merged."
        ),
        "fy2025_amounts": [
            {"label_key": "tn_amt_home_grants_total", "amount": 26000000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "home", "fy2025_units": 142, "fy2025_amount": 19600000,
             "color_group": "trust",
             # Federal HOME formula grant administered by THDA within its
             # proprietary fund; not verbatim-named in the ACFR (medium).
             "fund_type": "proprietary",
             "fund_name": "HOME Investment Partnerships Program (federal formula grant administered by THDA)",
             "fy2026": _FY26_PENDING},
            {"key": "tn_housing_trust_fund", "fy2025_units": 335, "fy2025_amount": 6400000,
             "color_group": "trust",
             # ACFR Note names "Tennessee Housing Trust Fund" verbatim as a
             # grant program THDA established (THDA funds + state appropriations).
             "fund_type": "proprietary",
             "fund_name": "Tennessee Housing Trust Fund (THDA funds + state appropriations)",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# KPI-only build: THDA discloses no complete per-project cohort list (only
# statewide/county/congressional-district aggregation tables). RAW_PROJECTS is
# therefore intentionally empty; see the module docstring "Why RAW_PROJECTS is
# empty" for the source-level evidence. The frontend renders the KPI cards and
# shows the bubble map with 0 markers when this is empty.
RAW_PROJECTS = []

# External cross-check constants (THDA Sept 8, 2025 press release -- the 9%
# competitive LIHTC subset of the report's LIHC total). Checked as monotonic
# consistency (subset <= total), not equality.
EXTERNAL_9PCT_LIHTC_UNITS = 988
EXTERNAL_9PCT_LIHTC_ANNUAL = 25000000  # "over $25 million in annual 9% LIHTC"


def verify_category_consistency():
    errors = []

    # homeownership_loans: great_choice + new_start must equal the combined
    # headline exactly (the two first-mortgage programs are a true partition).
    ho = next(c for c in CATEGORIES if c["key"] == "homeownership_loans")
    ho_units = sum(sp["fy2025_units"] for sp in ho["subprograms"])
    ho_dollars = sum(sp["fy2025_amount"] for sp in ho["subprograms"])
    if ho_units != ho["fy2025_actual"]:
        errors.append(f"homeownership_loans: subprogram units sum to {ho_units}, "
                      f"expected {ho['fy2025_actual']} (1,802 great_choice + 30 new_start)")
    if ho_dollars != 429100000:
        errors.append(f"homeownership_loans: subprogram dollars sum to {ho_dollars}, "
                      f"expected 429,100,000 ($423.4M + $5.7M)")

    # rental_assistance: 5,991 + 38 + 32,964 = 38,993 exactly; the three printed
    # dollar parts sum to $377,371,517, which is the "$377.4M" headline rounded
    # to $0.1M (allow a $100k rounding tolerance against the printed headline).
    ra = next(c for c in CATEGORIES if c["key"] == "rental_assistance")
    ra_units = sum(sp["fy2025_units"] for sp in ra["subprograms"])
    ra_dollars = sum(sp["fy2025_amount"] for sp in ra["subprograms"])
    if ra_units != ra["fy2025_actual"]:
        errors.append(f"rental_assistance: subprogram units sum to {ra_units}, "
                      f"expected {ra['fy2025_actual']} (5,991+38+32,964)")
    if ra_dollars != 377371517:
        errors.append(f"rental_assistance: subprogram dollars sum to {ra_dollars}, "
                      f"expected 377,371,517 ($60.8M+$271,517+$316.3M)")
    if abs(ra_dollars - 377400000) > 100000:
        errors.append(f"rental_assistance: subprogram dollar sum {ra_dollars} is not "
                      f"within $100k of the printed '$377.4M' headline")

    # multifamily_lihtc: the bond units (2,653) are a SUBSET of the LIHC units
    # (4,197) -- non-additive, so only assert the subset relationship, never a sum.
    ml = next(c for c in CATEGORIES if c["key"] == "multifamily_lihtc")
    lihtc_sp = next(sp for sp in ml["subprograms"] if sp["key"] == "lihtc")
    bond_sp = next(sp for sp in ml["subprograms"] if sp["key"] == "multifamily_bond")
    if bond_sp["fy2025_units"] > lihtc_sp["fy2025_units"]:
        errors.append(f"multifamily_lihtc: bond units {bond_sp['fy2025_units']} exceed "
                      f"LIHC units {lihtc_sp['fy2025_units']} (bond is a subset)")

    # liheap_energy_assistance: 24,314 + 50,124 = 74,438 and $17.7M + $36.6M =
    # $54.3M, both exact.
    le = next(c for c in CATEGORIES if c["key"] == "liheap_energy_assistance")
    le_units = sum(sp["fy2025_units"] for sp in le["subprograms"])
    le_dollars = sum(sp["fy2025_amount"] for sp in le["subprograms"])
    if le_units != le["fy2025_actual"]:
        errors.append(f"liheap_energy_assistance: subprogram units sum to {le_units}, "
                      f"expected {le['fy2025_actual']} (24,314+50,124)")
    if le_dollars != 54300000:
        errors.append(f"liheap_energy_assistance: subprogram dollars sum to {le_dollars}, "
                      f"expected 54,300,000 ($17.7M+$36.6M)")

    # home_program_grants: 142 + 335 = 477 and $19.6M + $6.4M = $26.0M, both exact.
    hg = next(c for c in CATEGORIES if c["key"] == "home_program_grants")
    hg_units = sum(sp["fy2025_units"] for sp in hg["subprograms"])
    hg_dollars = sum(sp["fy2025_amount"] for sp in hg["subprograms"])
    if hg_units != hg["fy2025_actual"]:
        errors.append(f"home_program_grants: subprogram units sum to {hg_units}, "
                      f"expected {hg['fy2025_actual']} (142 HOME + 335 THTF)")
    if hg_dollars != 26000000:
        errors.append(f"home_program_grants: subprogram dollars sum to {hg_dollars}, "
                      f"expected 26,000,000 ($19.6M + $6.4M)")

    # External cross-check (THDA Sept 8, 2025 press release): the 9% competitive
    # LIHTC round is a subset of the report's total LIHC allocation.
    if EXTERNAL_9PCT_LIHTC_UNITS > lihtc_sp["fy2025_units"]:
        errors.append(f"external: press-release 9% units {EXTERNAL_9PCT_LIHTC_UNITS} "
                      f"exceed the report's total LIHC units {lihtc_sp['fy2025_units']}")
    if EXTERNAL_9PCT_LIHTC_ANNUAL > lihtc_sp["fy2025_amount"]:
        errors.append(f"external: press-release 9% annual credits ${EXTERNAL_9PCT_LIHTC_ANNUAL:,} "
                      f"exceed the report's total one-year LIHC ${lihtc_sp['fy2025_amount']:,}")

    if RAW_PROJECTS:
        errors.append(
            "RAW_PROJECTS is expected to be empty for TN -- see module docstring; "
            "if a complete project-level list has since become available, update "
            "the docstring before populating this list."
        )

    if errors:
        raise SystemExit("Category consistency mismatch(es):\n" + "\n".join(errors))
    print("Category headline vs. subprogram consistency verified for all 5 categories:")
    print(f"  homeownership_loans: 1,802 + 30 = {ho_units} households / "
          f"${ho_dollars:,} (Great Choice + New Start).")
    print(f"  rental_assistance: 5,991 + 38 + 32,964 = {ra_units} households; "
          f"${ra_dollars:,} ~= $377.4M headline (rounding).")
    print(f"  multifamily_lihtc: bond units {bond_sp['fy2025_units']} <= LIHC units "
          f"{lihtc_sp['fy2025_units']} (subset, non-additive); LIHC = one-year $71.6M.")
    print(f"  liheap_energy_assistance: 24,314 + 50,124 = {le_units} households / "
          f"${le_dollars:,}.")
    print(f"  home_program_grants: 142 + 335 = {hg_units} households / "
          f"${hg_dollars:,} (HOME + THTF).")
    print(f"  external: press-release 9% LIHTC ({EXTERNAL_9PCT_LIHTC_UNITS} units / "
          f"${EXTERNAL_9PCT_LIHTC_ANNUAL:,}) is a consistent subset of the report's "
          f"total LIHC ({lihtc_sp['fy2025_units']} units / ${lihtc_sp['fy2025_amount']:,}).")
    print("  RAW_PROJECTS confirmed empty as expected (KPI-only build).")


def main():
    verify_category_consistency()
    payload = {
        "TN": {
            "hfa_name": "Tennessee Housing Development Agency",
            "hfa_abbr": "THDA",
            "fiscal_year": "CY2025",
            "source_title": "THDA 2025 Investments and Impacts Report -- 'Tennessee "
                             "Program Totals' (Homeownership and Maintenance, Rental "
                             "Development and Assistance, and Homelessness Assistance "
                             "and Prevention programs)",
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
