"""
Builds docs/ny_program_activity.json for New York State Homes and Community
Renewal (HCR) -- the umbrella under which THREE separate statutory housing
entities operate, each with its OWN reporting cadence and fiscal-year
convention. Unlike IL/PA/FL/OH/WA/TX (one HFA, one ACFR, one fiscal year),
NY's housing activity is legally fragmented, so this script deliberately
does NOT force the three entities' numbers into one reconciled total -- see
"Why three entities, two time windows" below. (Four CATEGORIES are modeled
in total -- HFA Multifamily, SONYMA Homebuyer, and two separate HTFC
categories, Multifamily Awards and Rental Assistance, covering HTFC's two
distinct offices -- but only two fiscal-year windows, since both HTFC
categories share the same SFY2025-26 source document.)

Sources
---------------------------------------------------------------------------
1. New York State Housing Finance Agency (HFA) and State of New York
   Mortgage Agency (SONYMA) -- "List of Measurements for Calendar Year
   2025" (the PARIS annual self-evaluation filing covering HFA, SONYMA, the
   Mortgage Insurance Fund (MIF, a SONYMA component), the Affordable
   Housing Corporation (AHC), the Municipal Bond Bank Agency (MBBA, inactive
   in CY2025) and the Tobacco Settlement Financing Corporation (TSFC,
   inactive in CY2025)):
     https://hcr.ny.gov/system/files/documents/2026/01/list-of-measurements-for-cy-2025-final_1.pdf
   Local copy: FY2025/program_activity/pdf/NY_HCR_ListOfMeasurements_CY2025.pdf
   Reporting period: CALENDAR YEAR 2025 (Jan-Dec).
2. Housing Trust Fund Corporation (HTFC, a subsidiary public benefit
   corporation of HFA) -- "Operations and Accomplishments Fiscal Year
   April 1, 2025 to March 31, 2026":
     https://hcr.ny.gov/system/files/documents/2026/07/fy-25-26-htfc-operations-and-accomplishments-final-no-watermark.pdf
   Local copy: FY2025/program_activity/pdf/NY_HTFC_OperationsAccomplishments_FY2025-26.pdf
   Reporting period: NEW YORK STATE FISCAL YEAR 2025-26 (April 2025-March
   2026) -- NOT a calendar year, and NOT the same window as source #1.
3. "New York State Homes and Community Renewal Legislative Report on
   Appropriated Housing Program Funds" (per-development address/funding
   appendices) -- INVESTIGATED, NOT USED. See "Why RAW_PROJECTS is empty"
   below.

Why three entities, two time windows -- not one reconciled total
---------------------------------------------------------------------------
HFA, SONYMA and HTFC are three separate legal public-benefit corporations
(HTFC is technically an HFA subsidiary, but reports on its own fiscal-year
cycle and its own set of financing programs). Their own self-published
numbers cover different calendar windows and cannot be summed into a
single "NY housing activity" figure without fabricating a reconciliation
none of the three agencies themselves publish:
  - HFA + SONYMA (source #1): calendar year 2025 (Jan 1 - Dec 31, 2025).
  - HTFC (source #2): NYS fiscal year 2025-26 (Apr 1, 2025 - Mar 31, 2026)
    -- a window that OVERLAPS but does not equal CY2025 (9 of its 12
    months fall in CY2025, 3 fall in CY2026).
This script's fiscal_year field is therefore the compound string
"CY2025 (HFA/SONYMA) / SFY2025-26 (HTFC)", each category states its own
window in fy2025_source_quote, and no script-computed number ever adds
HFA+SONYMA+HTFC together.

Category 1 -- HFA Multifamily (hfa_multifamily, unit_type=units)
---------------------------------------------------------------------------
Source #1, HFA section, p.1: "HFA created and preserved 9,382 affordable
housing units in 2025 compared to 5,554 in 2024; 4,970 in 2023; 5,073 in
2022 and 4,577 units in 2021. HFA financed a total of 41 projects,
including 15 new construction projects that created 2,744 affordable
units, 25 preservation projects that preserved 6,542 affordable units and
one project that included both the new construction of 54 units and the
preservation of 42 units."
This is an unusually clean case for a 41-state pilot: unlike IL/PA/FL,
where a category headline routinely does NOT equal the sum of its own
subprogram figures, HFA's own numbers reconcile EXACTLY once the one mixed
project's two halves are folded into each activity type: new construction
= 2,744 + 54 = 2,798 units; preservation = 6,542 + 42 = 6,584 units;
2,798 + 6,584 = 9,382, matching the headline to the unit. additive=True is
therefore used here (verify_hfa_reconciliation() checks this arithmetic at
build time), even though the 41 PROJECT count itself does not partition
cleanly into "15 + 25" (the 41st project is split across both buckets).
fy2025_amounts includes one disclosed dollar figure, a SUBSET, not a
category total (source #1, p.3): "In 2025, HFA issued $1.23 billion of
Sustainability Bonds to fund 23 projects for the creation of 4,369 units"
-- 23 of the 41 projects, 4,369 of the 9,382 units; no total-dollars-
financed figure for all 41 projects is disclosed anywhere in source #1
(a PARIS self-evaluation filing focused on units/counts, not agency-wide
bond volume), so none is invented here.
fund_type: NY_NYHFA.pdf (FY2025/pdf/NY_NYHFA.pdf, HFA's own "Fiscal Year
Statutory Report... Financial Statements for the fiscal years ended
October 31, 2025 and 2024" -- confirmed by its own title page and running
headers "NEW YORK STATE HOUSING FINANCE AGENCY (A COMPONENT UNIT OF THE
STATE OF NEW YORK)" to be HFA's own financial statements, not a
substituted/mismatched document) describes the Agency on an accrual basis
with "operating revenues" / "non-operating" revenue classification (Note
2.A, p.29) and shows mortgage loans receivable carried directly on its own
books ($16.943 billion at 10/31/2025, Note 3, p.32) -- i.e. a single
business-type (enterprise-style) reporting entity with no separate
GASB governmental funds of its own, the same "single enterprise/business-
type umbrella" pattern PHFA and Florida Housing use. Both HFA subprograms
are therefore "proprietary", fund_name "New York State Housing Finance
Agency (single business-type reporting entity)".

Category 2 -- SONYMA Homebuyer Loans (sonyma_homebuyer, unit_type=households)
---------------------------------------------------------------------------
Source #1, SONYMA section, p.6: "The Agency purchased 1,384 mortgages in
2025, compared to 1,694 in 2024, and 1,701 in 2023." fy2025_amounts uses
the MIF section's own total dollar figure for those same 1,384 mortgages
(source #1, MIF section, p.12): "The MIF provided pool insurance for 1,384
single family loans purchased by SONYMA with a loan amount of
$358,285,339" -- the loan-count matches exactly (1,384 = 1,384), so this is
treated as the total purchase volume for the category headline, not an
independently-sourced subset.
Unlike IL/PA/FL/HFA-above, SONYMA's own report gives no funding-SOURCE
breakdown of its 1,384 purchases (there is no "these mortgages were
financed via bond series X / program Y" table) -- what it discloses
instead are three overlapping BORROWER-ELIGIBILITY subsets of that same
1,384-mortgage pool (p.6-7,9): "1,129 of the Agency's mortgages were
originated through [the Achieving the Dream Program, its lower-income-
focused product]"; "998 of the mortgages purchased were made to low-income
homebuyers (80% of area median income or less)"; "In 2025, the Agency
funded 619 loans totaling $187.6 million in first liens with $9.19 million
in down payment assistance to minority households." These three categories
overlap by construction (a single mortgage is very often both "Achieving
the Dream" AND "<=80% AMI" AND "minority"), summing to 2,746 -- nearly
double the 1,384 total -- so additive=False is used, and the three appear
as non-additive reference chips rather than a stacked bar. Because these
are borrower characteristics, not distinct financing vehicles, the usual
bond/credit/trust/capital color_group semantic doesn't map cleanly onto
them; "capital" is used uniformly for all three as a neutral placeholder
(documented here rather than silently reusing a category that doesn't
apply). fund_type is None for every SONYMA subprogram: SONYMA is a
separate legal agency from HFA, and no SONYMA-specific audited financial
statements are present in this project's FY2025 corpus (FY2025/pdf/ and
FY2025/txt/ contain only NY_NYHFA.pdf, HFA's own statements) -- per this
project's "don't guess a fund classification without a source" rule,
fund_type is left unclassified rather than assumed.
Two DPA-specific programs (eDPAL: "$8.3 million...371 mortgages totaling
$149.2 million," and DPAL Plus: "$26.4 million...951 mortgages totaling
$90.8 million") are explicitly EXCLUDED from subprograms: both are quoted
in source #1 as "As of December 31, 2025" LIFE-OF-PROGRAM-TO-DATE
cumulative figures (since each program's own launch date, Sept. 2023 for
DPAL Plus / a more recent launch for eDPAL), not CY2025-only originations
-- mixing a multi-year cumulative figure into a calendar-year category
would misrepresent the time window, the same problem this project's other
build scripts avoid for cumulative/rolling totals (e.g. FL's SHIP
footnote-driven exclusion, PA's Map Doc non-reconciliation).

Category 3 -- HTFC Multifamily Awards (htfc_multifamily_awards, unit_type=units)
---------------------------------------------------------------------------
Source #2, p.9 (Financing and Development of Multifamily Housing section):
"In the past fiscal year, through the Office of Finance and Development,
HTFC has made multifamily development awards totaling over $217 million
which have leveraged approximately $70 million in private and public
investment... and assisted in the creation or rehabilitation of 1,935
units of affordable housing." This category's fy2025_actual (1,935) and
fy2025_amounts ($217M awarded / $70M leveraged) are used VERBATIM from
that sentence -- note the source itself only commits to "over"/
"approximately", not exact-to-the-dollar figures, unlike HFA/SONYMA's
whole-number counts above; that imprecision is inherent to the source, not
introduced by this script.
Source #2 also prints an "ACCOMPLISHMENTS OVERVIEW: CHART OF HTFC
FINANCING PROGRAMS" table (pp.10-14, 26 rows, extracted via pdfplumber
find_tables()) giving Amount Awarded / Amount Leveraged / Proposed Units
for every HTFC program for the same April 2025-March 2026 fiscal year.
This table's own footnote (p.14) states: "The amount leveraged and
assistance reported reflects estimated numbers PROPOSED for assistance in
awarded projects... Accomplishments are estimated and confirmed at
project/contract completion" -- i.e. the table is a different accounting
vintage (proposed-at-award) from the p.9 narrative sentence (which reads
as a completed-to-date summary), so, following this project's IL/FL
precedent of not force-reconciling two differently-scoped totals, this
script does NOT attempt to make the table's own program-level figures sum
to 1,935/$217M (a brute-force search over combinations of the table's 26
rows found no subset landing on 1,935 units, confirming the two are not a
simple partition of each other). additive=False; subprograms are a
CONSERVATIVE 4-row subset of that table -- ONLY the rows whose program
name is explicitly named in source #2's own p.9 prose describing the
"Financing and Development of Multifamily Housing" office ("the Low-
Income Housing Trust Fund Program, Senior Housing Program, ... Rural and
Urban Community Investment Fund, ... Supportive Housing Opportunities
Program"): lihtf, senior_housing, rucif, shop. Three other programs named
in that same sentence (Public Housing Preservation Program, Middle Income
Housing Program, Federal Housing Trust Fund Program) have NO matching row
in the table (no award that fiscal year, or a name this script could not
confidently match) and are omitted rather than guessed at. The table's
$326M/295-unit "New Construction Program" row is deliberately EXCLUDED
even though its own one-line description ("Funds the new construction or
adaptive reuse of affordable rental housing") reads as multifamily
development -- it is not one of the programs p.9's own prose names for
this office, and guessing it in would nearly quadruple the subprogram
total's distance from the 1,935/$217M headline with no source-anchored
justification either way. fund_type is None for all four HTFC
subprograms, matching SONYMA's above: HTFC is again a legally distinct
entity (a subsidiary corporation, not HFA itself) with no HTFC-specific
audited financial statements in this project's FY2025 corpus.

Category 4 -- HTFC Rental Assistance (htfc_rental_assistance, unit_type=units)
---------------------------------------------------------------------------
Per user request (2026-08-14): a fourth category, structurally separate from
Category 3's construction/rehabilitation awards (Office of Finance and
Development), covering HTFC's Office of Housing Preservation ("OHP")
programs that pay ONGOING, per-unit rental assistance to tenants/landlords
at ALREADY-EXISTING developments -- not one-time construction financing.
Source #2, p.4 (Housing Preservation section): "HTFC administers both
tenant-based and project-based rental assistance through federal contracts
for Section 8 Performance-Based Contract Administration ('PBCA') and
Housing Choice Vouchers ('HCVs'). Furthermore, HTFC utilizes State funding
to provide rental assistance to federally-financed rural properties through
New York State's Rural Rental Assistance Program ('RRAP')... Together,
these three programs provide over $3 billion annually in Housing Assistance
Payments." This headline sentence is the category's own dual-verification
anchor (see verify_htfc_rental_assistance_totals()): the three subprograms'
own dollar figures, each independently disclosed elsewhere in the same
report, sum to $3,008,331,349 -- reconciling almost exactly to the
narrative's own "over $3 billion" statement, the same reconciliation
discipline IHDA's Exhibit XX/XXI totals are held to.
  - pbca (fy2025_units=101,958, fy2025_amount=$2,202,699,905): p.4, "Section
    8 Performance-Based Contract Administration" -- "HTFC is the only Public
    Housing Authority in New York with a state-wide portfolio. Through a
    PBCA contract with HUD, HTFC administers rental assistance and provides
    oversight for the country's largest Section 8 multi-family, project-
    based portfolio, which includes 974 contracts with 101,958 units."
    Units from the narrative; the $2,202,699,905 dollar figure is the
    "Section 8 Project Based Contract Administration" row of the
    ACCOMPLISHMENTS OVERVIEW table (p.12) -- the table gives no unit count
    of its own for this row (N/A), so narrative and table are complementary,
    not contradictory, here.
  - hcv (fy2025_units=43,540, fy2025_amount=$783,921,444): p.5, "HTFC
    administers approximately 43,000 Section 8 HCVs that can be used to
    lease apartments in the private sector" -- narrative's rounded "~43,000"
    is consistent with the ACCOMPLISHMENTS OVERVIEW table's own precise
    "Section 8 Housing Choice Voucher" row (p.12): "$783,921,444 ... 43,540
    Vouchers", which this script uses for both figures (more precise than
    the narrative's own rounding).
  - rrap (fy2025_units=5,046, fy2025_amount=$21,710,000): p.5, "Rural Rental
    Assistance Program" -- "HTFC works closely with the U.S. Department of
    Agriculture's Rural Development Office to provide State-funded rental
    assistance through RRAP to 247 properties with 5,046 units located
    across rural regions of the State ... New York is the only state that
    provides rental assistance to these federally-assisted properties."
    Units from the narrative; the $21,710,000 dollar figure is the "Rural
    Rental Assistance Program" row of the same table (p.12): "Provides
    direct rent subsidies to project owner for low-income elderly and
    family tenants living in Rural Development-financed projects" -- the
    single closest structural analog in this project's FY2025 corpus to
    IHDA's own RHS-LAA subprogram (a state-funded, ongoing, per-unit rental
    operating subsidy to already-built developments).
additive=True: PBCA (HUD project-based Section 8 contracts at specific
developments), HCV (tenant-based vouchers usable at any qualifying private
unit), and RRAP (USDA Rural Development-financed rural properties) are
three legally and programmatically distinct populations with no unit-level
overlap by construction (a household cannot simultaneously be a PBCA-
covered unit, a mobile HCV holder, and an RRAP-subsidized rural tenant for
the same subsidy). fund_type is None for all three subprograms, matching
Category 3's HTFC subprograms above: HTFC is a subsidiary legally distinct
from HFA with no HTFC-specific audited financial statements in this
project's FY2025 corpus, so fund_type is intentionally left unclassified.
Two related items were investigated and deliberately EXCLUDED:
  - HAVP (Housing Access Voucher Program, p.4: "$50 million... of which
    HTFC will receive $17.5 million to serve approximately 700 unhoused
    families"): brand-new this fiscal year, correctly not part of the
    "over $3 billion" figure (source #2's own three-programs sentence
    predates/excludes it), and has no ACCOMPLISHMENTS OVERVIEW table row to
    cross-check its own $17.5M/~700-family figures against -- so it is left
    out rather than added on unverified single-source numbers.
  - The HOME Investment Partnership -- Local Programs table row (p.11:
    "$32,881,699 ... 271 Residential Units / 558 Households - Rent
    Assistance") blends new-construction units and rent-assistance
    households into ONE undivided dollar figure with no way to split how
    much of the $32.9M is rent assistance versus construction financing --
    guessing a split would fabricate a number this table does not itself
    provide, so this row is excluded entirely (neither Category 3 nor
    Category 4 uses it).

Why RAW_PROJECTS is empty -- no per-development bubble map for NY
---------------------------------------------------------------------------
Neither source #1 nor source #2 names any individual development (both are
program/agency-level roll-ups only). The one document that DOES name
individual developments with street addresses -- the "Legislative Report
on Appropriated Housing Program Funds" (source #3, investigated at
https://hcr.ny.gov/system/files/documents/2026/06/2025_26_legislative_report_final.pdf,
95 pages) -- was fetched and inspected, and rejected for two independent
reasons, either one of which alone would be disqualifying:
  1. WRONG TIME WINDOW: source #3 covers appropriated-fund activity across
     TWO five-year Housing Plans at once (p.1-2): "the entirety of the
     first Housing Plan which ran from SFY 2017-18 through SFY 2021-22...
     A total of 33,630 affordable multifamily homes across 297 projects...
     Governor Hochul's Housing Plan is delivering 27,096 affordable homes
     in 187 projects (and counting)" -- a multi-year, still-open-ended
     cumulative count, not a single-year CY2025 figure comparable to HFA's
     41-project/9,382-unit CY2025 total. There is no reliable way to filter
     this list down to "only the 41 HFA projects financed specifically in
     calendar 2025" -- source #3's own project table gives award dates and
     construction-status flags, not the CY2025 activity classification
     source #1 uses.
  2. EXTRACTION COST/RELIABILITY: the underlying data (pp.3 onward) is
     printed as a wide, multi-column crosstab (funding-source columns
     across a two-page spread, dozens of programs) that pdfplumber's table
     extraction cannot cleanly recover -- unlike PA's Map Doc or FL's
     Rental Properties table (both single, well-bounded tables this
     project's other build scripts DID successfully extract), a raw-text
     dump of this table interleaves digit fragments from adjacent columns
     into single garbled strings (e.g. one probe row of digits/column-
     header fragments came back as literal "2 2 2 2 2 2 2 2 2 2 2 2 2 2 2
     2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 0 0
     0 0 0..." with no reliable way to reconstruct which digits belong to
     which project/column). Manually transcribing several hundred rows
     from that presentation, on a document whose own headline figures
     don't even correspond to the CY2025 window this pilot needs, is
     exactly the "transcription cost too high" case this project's task
     brief explicitly permits abandoning -- so RAW_PROJECTS = [] is the
     honest result here, not a shortcut taken to save time on a document
     that would otherwise have worked cleanly.
As a consequence, NY's bubble map renders empty (0 markers) -- this is a
known, intentional limitation of the source documents, not a bug.

fy2026
---------------------------------------------------------------------------
Neither source #1 (a backward-looking annual self-evaluation) nor source
#2 (itself the current, not-yet-complete SFY2025-26 report) discloses any
forward-looking FY2026/SFY2026-27 projection. Every fy2026 field below is
{value: None, amount: None, closed: False, note_key: "nyFy26NotePending"}.
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "ny_program_activity.json"

SOURCE_URL = "https://hcr.ny.gov/system/files/documents/2026/01/list-of-measurements-for-cy-2025-final_1.pdf"
SOURCE_FILE = (
    "NY_HCR_ListOfMeasurements_CY2025.pdf (HFA/SONYMA/MIF, CY2025) + "
    "NY_HTFC_OperationsAccomplishments_FY2025-26.pdf (HTFC, SFY2025-26; "
    "https://hcr.ny.gov/system/files/documents/2026/07/fy-25-26-htfc-operations-and-accomplishments-final-no-watermark.pdf)"
)
RETRIEVED = "2026-08-13"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "nyFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "hfa_multifamily",
        "unit_type": "units",
        "fy2025_actual": 9382,
        "fy2025_source_quote": (
            "\"List of Measurements for Calendar Year 2025\" (HFA section, p.1): "
            "\"HFA created and preserved 9,382 affordable housing units in 2025 "
            "compared to 5,554 in 2024; 4,970 in 2023; 5,073 in 2022 and 4,577 units "
            "in 2021. HFA financed a total of 41 projects, including 15 new "
            "construction projects that created 2,744 affordable units, 25 "
            "preservation projects that preserved 6,542 affordable units and one "
            "project that included both the new construction of 54 units and the "
            "preservation of 42 units.\" Reporting period: calendar year 2025 "
            "(Jan-Dec). New construction (2,744 + 54 = 2,798) + preservation "
            "(6,542 + 42 = 6,584) = 9,382, matching the headline exactly -- see "
            "verify_hfa_reconciliation()."
        ),
        "fy2025_amounts": [
            {"label_key": "ny_amt_sustainability_bonds", "amount": 1230000000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "new_construction", "fy2025_units": 2798, "fy2025_amount": None,
             "color_group": "bond",
             # NY_NYHFA.pdf (HFA's own FYE 10/31/2025 statutory financial
             # statements), Note 1 (p.28): "The Agency finances most of its
             # activities through the issuance of bonds"; Note 2.A (p.29)
             # describes accrual-basis operating/non-operating revenue
             # classification typical of a single business-type reporting
             # entity, with no separate governmental funds of its own.
             "fund_type": "proprietary",
             "fund_name": "New York State Housing Finance Agency (single business-type reporting entity)",
             "fy2026": _FY26_PENDING},
            {"key": "preservation", "fy2025_units": 6584, "fy2025_amount": None,
             "color_group": "bond",
             "fund_type": "proprietary",
             "fund_name": "New York State Housing Finance Agency (single business-type reporting entity)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "sonyma_homebuyer",
        "unit_type": "households",
        "fy2025_actual": 1384,
        "fy2025_source_quote": (
            "\"List of Measurements for Calendar Year 2025\" (SONYMA section, p.6): "
            "\"The Agency purchased 1,384 mortgages in 2025, compared to 1,694 in "
            "2024, and 1,701 in 2023.\" Total loan volume from the MIF section (p.12): "
            "\"The MIF provided pool insurance for 1,384 single family loans "
            "purchased by SONYMA with a loan amount of $358,285,339.\" Reporting "
            "period: calendar year 2025. Subprograms below are OVERLAPPING "
            "borrower-eligibility subsets of this same 1,384-loan pool (not "
            "distinct funding sources), so this category is not additive -- see "
            "module docstring."
        ),
        "fy2025_amounts": [
            {"label_key": "ny_amt_sonyma_loan_volume", "amount": 358285339},
            {"label_key": "ny_amt_sonyma_minority_volume", "amount": 187600000},
            {"label_key": "ny_amt_sonyma_minority_dpa", "amount": 9190000},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "achieving_dream", "fy2025_units": 1129, "fy2025_amount": None,
             "color_group": "capital",
             # SONYMA is a separate legal agency from HFA; no SONYMA-specific
             # audited financial statements are present in this project's
             # FY2025 corpus (only HFA's own NY_NYHFA.pdf is available), so
             # fund_type is intentionally left unclassified rather than
             # guessed -- see module docstring.
             "fund_type": None, "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "low_income", "fy2025_units": 998, "fy2025_amount": None,
             "color_group": "capital",
             "fund_type": None, "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "minority", "fy2025_units": 619, "fy2025_amount": 187600000,
             "color_group": "capital",
             "fund_type": None, "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "htfc_multifamily_awards",
        "unit_type": "units",
        "fy2025_actual": 1935,
        "fy2025_source_quote": (
            "\"Housing Trust Fund Corporation -- Operations and Accomplishments "
            "Fiscal Year April 1, 2025 to March 31, 2026\" (p.9): \"HTFC has made "
            "multifamily development awards totaling over $217 million which have "
            "leveraged approximately $70 million in private and public "
            "investment... and assisted in the creation or rehabilitation of 1,935 "
            "units of affordable housing.\" Reporting period: NYS fiscal year "
            "2025-26 (Apr 2025-Mar 2026) -- NOT the same calendar window as HFA/"
            "SONYMA above, and NOT summed with them. The \"over\"/\"approximately\" "
            "wording is the source's own imprecision, not introduced here."
        ),
        "fy2025_amounts": [
            {"label_key": "ny_amt_htfc_awards", "amount": 217000000},
            {"label_key": "ny_amt_htfc_leveraged", "amount": 70000000},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "lihtf", "fy2025_units": 622, "fy2025_amount": 43000000,
             "color_group": "trust",
             # HTFC is a subsidiary corporation legally distinct from HFA;
             # no HTFC-specific audited financial statements are present in
             # this project's FY2025 corpus, so fund_type is left
             # unclassified -- see module docstring.
             "fund_type": None, "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "senior_housing", "fy2025_units": 204, "fy2025_amount": 12252462,
             "color_group": "capital",
             "fund_type": None, "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "rucif", "fy2025_units": 584, "fy2025_amount": 10514342,
             "color_group": "capital",
             "fund_type": None, "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "shop", "fy2025_units": 796, "fy2025_amount": 65000000,
             "color_group": "capital",
             "fund_type": None, "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        # Source #2, p.4-5, "Housing Preservation" / Office of Housing
        # Preservation -- ongoing, per-unit/per-voucher rental assistance to
        # ALREADY-EXISTING developments and tenants, structurally distinct
        # from Category 3's one-time construction/rehabilitation awards
        # (Office of Finance and Development) -- see module docstring.
        "key": "htfc_rental_assistance",
        "unit_type": "units",
        "fy2025_actual": 150544,
        "fy2025_source_quote": (
            "\"Housing Trust Fund Corporation -- Operations and Accomplishments "
            "Fiscal Year April 1, 2025 to March 31, 2026\" (p.4): \"HTFC administers "
            "both tenant-based and project-based rental assistance through federal "
            "contracts for Section 8 Performance-Based Contract Administration "
            "('PBCA') and Housing Choice Vouchers ('HCVs'). Furthermore, HTFC "
            "utilizes State funding to provide rental assistance to federally-"
            "financed rural properties through New York State's Rural Rental "
            "Assistance Program ('RRAP')... Together, these three programs provide "
            "over $3 billion annually in Housing Assistance Payments.\" (p.4) PBCA: "
            "\"974 contracts with 101,958 units.\" (p.5) HCV: \"approximately 43,000 "
            "Section 8 HCVs\" (narrative) / \"43,540 Vouchers\", \"$783,921,444\" "
            "(ACCOMPLISHMENTS OVERVIEW table, p.12). (p.5) RRAP: \"247 properties "
            "with 5,046 units... New York is the only state that provides rental "
            "assistance to these federally-assisted properties\" (narrative) / "
            "\"$21,710,000\" (same table, p.12). Reporting period: NYS fiscal year "
            "2025-26 (Apr 2025-Mar 2026), same window as Category 3. Subprogram "
            "dollar figures sum to $3,008,331,349, reconciling to the narrative's "
            "own \"over $3 billion\" -- see verify_htfc_rental_assistance_totals()."
        ),
        "fy2025_amounts": [
            {"label_key": "ny_amt_hap_total", "amount": 3008331349},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "pbca", "fy2025_units": 101958, "fy2025_amount": 2202699905,
             "color_group": "capital",
             # HTFC is a subsidiary corporation legally distinct from HFA;
             # no HTFC-specific audited financial statements are present in
             # this project's FY2025 corpus, so fund_type is left
             # unclassified -- see module docstring.
             "fund_type": None, "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "hcv", "fy2025_units": 43540, "fy2025_amount": 783921444,
             "color_group": "capital",
             "fund_type": None, "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "rrap", "fy2025_units": 5046, "fy2025_amount": 21710000,
             "color_group": "trust",
             "fund_type": None, "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
]

# No per-development detail -- see module docstring, "Why RAW_PROJECTS is
# empty". Deliberately empty, not a placeholder awaiting future work.
RAW_PROJECTS = []


def verify_hfa_reconciliation():
    errors = []
    hfa_cat = next(c for c in CATEGORIES if c["key"] == "hfa_multifamily")
    new_c = next(s for s in hfa_cat["subprograms"] if s["key"] == "new_construction")
    preserve = next(s for s in hfa_cat["subprograms"] if s["key"] == "preservation")
    if new_c["fy2025_units"] != 2744 + 54:
        errors.append(f"new_construction: expected 2744+54=2798, got {new_c['fy2025_units']}")
    if preserve["fy2025_units"] != 6542 + 42:
        errors.append(f"preservation: expected 6542+42=6584, got {preserve['fy2025_units']}")
    total = new_c["fy2025_units"] + preserve["fy2025_units"]
    if total != hfa_cat["fy2025_actual"]:
        errors.append(
            f"new_construction + preservation = {total:,}, does not match "
            f"category headline {hfa_cat['fy2025_actual']:,}"
        )
    if errors:
        raise SystemExit("HFA reconciliation mismatch(es):\n" + "\n".join(errors))
    print("HFA new_construction (2,798) + preservation (6,584) = 9,382 verified "
          "against the CY2025 List of Measurements headline.")


def verify_sonyma_totals():
    sonyma_cat = next(c for c in CATEGORIES if c["key"] == "sonyma_homebuyer")
    if sonyma_cat["fy2025_actual"] != 1384:
        raise SystemExit(f"SONYMA headline: expected 1384, got {sonyma_cat['fy2025_actual']}")
    loan_volume = next(a for a in sonyma_cat["fy2025_amounts"]
                        if a["label_key"] == "ny_amt_sonyma_loan_volume")
    if loan_volume["amount"] != 358285339:
        raise SystemExit(f"SONYMA loan volume: expected $358,285,339, got ${loan_volume['amount']:,}")
    minority = next(s for s in sonyma_cat["subprograms"] if s["key"] == "minority")
    if minority["fy2025_units"] != 619 or minority["fy2025_amount"] != 187600000:
        raise SystemExit("SONYMA minority subprogram figures do not match the "
                          "MIF/SONYMA section's own quoted 619 loans / $187.6M.")
    print("SONYMA 1,384 mortgages / $358,285,339 pool-insured loan volume and the "
          "619-loan / $187.6M minority-household subset verified against source "
          "quotes.")


def verify_htfc_table_subset():
    htfc_cat = next(c for c in CATEGORIES if c["key"] == "htfc_multifamily_awards")
    expected = {
        "lihtf": (622, 43000000),
        "senior_housing": (204, 12252462),
        "rucif": (584, 10514342),
        "shop": (796, 65000000),
    }
    errors = []
    for sp in htfc_cat["subprograms"]:
        exp_units, exp_amount = expected[sp["key"]]
        if sp["fy2025_units"] != exp_units or sp["fy2025_amount"] != exp_amount:
            errors.append(
                f"{sp['key']}: expected {exp_units:,} units / ${exp_amount:,}, "
                f"got {sp['fy2025_units']:,} units / ${sp['fy2025_amount']:,}"
            )
    if set(s["key"] for s in htfc_cat["subprograms"]) != set(expected):
        errors.append("HTFC subprogram key set does not match the expected 4-row subset")
    if errors:
        raise SystemExit("HTFC subprogram mismatch(es):\n" + "\n".join(errors))
    print("HTFC lihtf/senior_housing/rucif/shop rows verified against the "
          "ACCOMPLISHMENTS OVERVIEW table's own printed Amount Awarded/Units cells "
          "(pp.10-14 of the FY2025-26 Operations and Accomplishments report).")


def verify_htfc_rental_assistance_totals():
    cat = next(c for c in CATEGORIES if c["key"] == "htfc_rental_assistance")
    subs = cat["subprograms"]
    units_sum = sum(sp["fy2025_units"] for sp in subs)
    amount_sum = sum(sp["fy2025_amount"] for sp in subs)
    errors = []
    if units_sum != cat["fy2025_actual"]:
        errors.append(f"htfc_rental_assistance units: expected {cat['fy2025_actual']}, got {units_sum}")
    headline_amount = cat["fy2025_amounts"][0]["amount"]
    if amount_sum != headline_amount:
        errors.append(f"htfc_rental_assistance amount: expected {headline_amount}, got {amount_sum}")
    # Cross-check against the source's own independently-stated "over $3
    # billion annually" sentence (p.4) -- the dollar sum must be >= $3.0B
    # (matching "over") and not implausibly far past it (sanity bound, not
    # a second precise figure to match exactly, since the source itself
    # only commits to "over").
    if not (3_000_000_000 <= amount_sum < 3_100_000_000):
        errors.append(
            f"htfc_rental_assistance amount sum (${amount_sum:,}) does not fall in the "
            f"expected 'over $3 billion' range implied by the source's own headline sentence"
        )
    # HCV cross-check: table's precise 43,540 vouchers vs. narrative's own
    # rounded "approximately 43,000" -- must be within a few hundred of each
    # other to count as the same figure restated at different precision.
    hcv = next(sp for sp in subs if sp["key"] == "hcv")
    if abs(hcv["fy2025_units"] - 43000) > 1000:
        errors.append(
            f"hcv units ({hcv['fy2025_units']}) is not close to the narrative's own "
            f"'approximately 43,000' restatement"
        )
    if errors:
        raise SystemExit("HTFC rental assistance total mismatch(es):\n" + "\n".join(errors))
    print(
        "HTFC rental assistance subprogram totals verified: PBCA (101,958 units/"
        "$2,202,699,905) + HCV (43,540 vouchers/$783,921,444) + RRAP (5,046 units/"
        f"$21,710,000) = {units_sum:,} units / ${amount_sum:,} -- reconciles to the "
        "report's own \"over $3 billion annually in Housing Assistance Payments\" "
        "sentence."
    )


def main():
    verify_hfa_reconciliation()
    verify_sonyma_totals()
    verify_htfc_table_subset()
    verify_htfc_rental_assistance_totals()

    payload = {
        "NY": {
            "hfa_name": "New York State Homes and Community Renewal",
            "hfa_abbr": "HCR",
            "fiscal_year": "CY2025 (HFA/SONYMA) / SFY2025-26 (HTFC)",
            "source_title": (
                "List of Measurements for Calendar Year 2025 (HFA/SONYMA/MIF) + "
                "HTFC Operations and Accomplishments Fiscal Year 2025-26"
            ),
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
