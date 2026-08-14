"""
Builds docs/wa_program_activity.json from the Washington State Housing Finance
Commission's (WSHFC) FY2025 "2024-25 Data Report" plus its own separate 9%
Housing Tax Credit Program 2025 Allocation List (project-level detail) and its
FY2025 audited financial statements (fund-type classification only).

Sources (WSHFC's fiscal year = July 1, 2024 - June 30, 2025)
------------------------------------------------------------------------
1. "2024-25 Data Report" (a short highlights brochure, not a narrative report
   like IHDA's Report of Activities -- one infographic-style page per topic,
   pp.3-9 relevant here):
     https://wshfc.org/admin/WSHFCAR2025Updater12.pdf
   (source/landing page: https://wshfc.org/admin/publications.htm)
   Local copy: FY2025/program_activity/pdf/WA_WSHFC_DataReport_FY2025.pdf
2. "9% Housing Tax Credit Program -- 2025 Allocation List" (dated 1/17/2025,
   the November-2024-round competitive-allocation results; a NEWER 2026
   Allocation List already exists on the same page as of this build, but
   FY2025's own report period -- July 2024-June 2025 -- is covered by the
   2025 list, not the 2026 one):
     https://www.wshfc.org/mhcf/9percent/2025AllocationList.pdf
   (source/landing page: https://www.wshfc.org/mhcf/9percent/lists.htm)
   Local copy: FY2025/program_activity/pdf/WA_WSHFC_9pctHTC_AllocationList_2025.pdf
3. WSHFC's own FY2025 audited financial statements (used ONLY for fund-type
   classification, see below):
     FY2025/txt/WA_WSHFC_FY2025_ACFR.txt (verified below to be the correctly
     scoped source -- no substitution needed, unlike PA's build).

Data-provenance check on the checked-in ACFR text
------------------------------------------------------------------------
FY2025/txt/WA_WSHFC_FY2025_ACFR.txt WAS verified to be WSHFC's own financial
statements before use: its title page reads "Financial Statements June 30,
2025 and 2024, Washington State Housing Finance Commission (A Component Unit
of the State of Washington)", the Independent Auditor's Report is addressed
"To the Board of Commissioners, Washington State Housing Finance Commission,
Seattle, Washington", and Note 1 ("Principal Business Activity and
Significant Accounting Policies") describes exactly one reporting entity
(WSHFC itself, created in 1983) with no discretely-presented component-unit
summary of a different agency -- i.e. this is the real, correctly-scoped
source, unlike PA's build (which caught FY2025/txt/PA_PHFA_FY2025_ACFR.txt
pointing at the Commonwealth-wide ACFR instead of PHFA's own statements).

Category-level methodology
------------------------------------------------------------------------
Homeownership Loans (p.4, "2025 HOMEOWNERSHIP HIGHLIGHTS"): "5,247 households
served (4,638 Home Advantage loans and 609 House Key loans)" and "$2.04B in
first-mortgage loans". 4,638 + 609 = 5,247 exactly -- additive=True, the two
first-mortgage products are mutually exclusive per household. The $2.04B
total is not broken out by product in the Data Report, so both subprograms'
fy2025_amount is None (not invented) and $2.04B is shown only as a
category-level fy2025_amounts chip.

Down Payment and Closing-Cost Loans (p.4): "5,124 ... homebuyers served
(buyers using our home loans) ... $126M". This is a SEPARATE metric from the
5,247 first-mortgage households above (a downpayment/closing-cost assistance
loan that may or may not accompany one of those first mortgages -- the Data
Report never states the two figures nest or sum), so it is kept as its own
category, not folded into Homeownership Loans, matching PHFA's build-script
precedent of a category headline that is not simply another category's
subset without explicit agency confirmation that it is.

Covenant Homeownership (p.5, "COVENANT HOMEOWNERSHIP PROGRAM"): "547
Homebuyers served, 1,236 Total household members, $60.2M Total downpayment
loans." A brand-new program (launched July 1, 2024, per HB 1474 as amended
by HB 1696) with its own dedicated funding source (a new document recording
fee) and its own headline figures -- kept as its own category rather than a
Homeownership Loans subprogram, since the Data Report never states whether
a Covenant Homeownership borrower is also counted in the 5,247/5,124
figures above. The "1,236 total household members" figure is a person-count,
not a homebuyer/loan count or a dollar figure, so it is not surfaced as
fy2025_actual (which uses "547 Homebuyers served," the unit_type="households"
-- i.e. borrower households -- headline) nor as an fy2025_amounts chip
(which is dollars-only); it is preserved here in this docstring for context
only, per this project's "never fabricate/misrepresent a number's units"
rule.

Multifamily Housing (pp.6-7, "2025 MULTIFAMILY HOUSING HIGHLIGHTS") -- the
one case here requiring real reconciliation work:
  Overview (p.6): "2,952 affordable apartments created or preserved," "36
  affordable apartment projects financed statewide in 13 counties," "$395.6
  million total bonds issued," "$543.5 million in equity generated from Low
  Income Housing Tax Credits."
  Subcategory breakdown (p.7, "2025 MULTIFAMILY HOUSING HIGHLIGHTS"):
    - Combined Bonds and 4% Tax Credits: 23 projects, 9 counties, 2,292
      units, $395.6M tax-exempt bonds, $375M tax-credit equity.
    - 9% Housing Tax Credits: 13 projects, 9 counties, 660 units, $168M
      tax-credit equity.
    - Nonprofit Senior Housing: 3 senior projects, King and Pierce counties,
      522 units or beds financed, $167M bonds issued.
  Arithmetic check: 23 + 13 = 36 projects (matches the overview's "36"
  exactly); 2,292 + 660 = 2,952 units (matches the overview's "2,952"
  exactly); $395.6M (Combined Bonds bucket alone) matches the overview's
  "$395.6 million total bonds issued" exactly; $375M + $168M = $543M, which
  rounds to the overview's "$543.5 million" equity figure. All four overview
  numbers reconcile to Combined-Bonds-and-4%-Credits + 9%-Credits ONLY --
  Nonprofit Senior Housing's own 3 projects / 522 units / $167M bonds are
  NOT included in the overview totals (3 fewer projects, 522 fewer units,
  and $167M of bonds the overview's "$395.6 million total" does not count).
  This category therefore uses fy2025_actual=2,952 (the overview headline,
  which itself is the exact, verified sum of only 2 of the 3 subcategories)
  with additive=False, because a naive sum of all three subprograms'
  fy2025_units (2,292+660+522=3,474) would silently imply a total WSHFC
  itself never published and does not match its own headline -- the same
  "headline is not a naive full sum of subprograms" pattern documented in
  IHDA's, PHFA's, and Florida Housing's own build scripts, here caused by
  Nonprofit Senior Housing sitting entirely outside the "2,952 apartments"
  count rather than by unit-level double-counting across programs.

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
Like PHFA and Florida Housing (and unlike IHDA), WSHFC's own FY2025 audited
financial statements report ONLY business-type activities: the Independent
Auditor's Report opinion covers "the financial statements of the
business-type activities of the Washington State Housing Finance
Commission" -- WSHFC carries no GASB governmental funds of its own, so the
"governmental" value of fund_type is never used anywhere in this file. Note
1, "Principal Business Activity and Significant Accounting Policies" ->
"Program Funds" (pp.17-18), names three internal fund groupings: the General
Operating Fund, Program-Related Investments (PRI), and the Bond Fund (itself
split into the Single-Family Homeownership Program and Conduit Financing
Programs).
  - "proprietary" (on WSHFC's own balance sheet):
      * home_advantage -- Note 1, p.17-18: the Bond Fund's "Single-Family
        Homeownership Program" finances "first-time homebuyers ... Assets
        of the indentures are pledged as collateral for the debt ... $1,023.5
        million" as of June 30, 2025. MD&A (p.5) confirms Home Advantage
        loans are "supplement[ed] ... by issuing taxable bonds" under this
        same program (in addition to loans sold into the TBA/MBS secondary
        market), and Note 4 (p.29) reports "Single Family Homeownership
        Program" MBS fair-value gains by name. Confidence: high.
      * house_key -- Note 1's same "Single-Family Homeownership Program"
        Bond Fund entry; MD&A (p.5) states WSHFC "generated approximately
        $170.1 million in lendable proceeds for our House Key Opportunity
        program through the issuance of tax-exempt bonds in fiscal year
        2025." Confidence: high.
      * downpayment_closing_cost -- Note 5, "Mortgage Loans" (p.29-30):
        "Down Payment Assistance and Other Loans Supporting Homeownership
        $449,499,316" is WSHFC's own carried mortgage-loan-receivable
        balance (funded via Program-Related Investments, per Note 1's PRI
        description: "resources provided by other funders for use in
        established down payment assistance ... programs"). Confidence:
        high on proprietary, medium on the exact PRI-vs-other-fund
        attribution (Note 5 does not itself name PRI as the funding source
        for this specific balance).
      * covenant_downpayment_loans -- Note 5 (p.30) states explicitly:
        "in FY 2025, the Commission began issuing forgivable downpayment
        assistance loans through the Covenant Homeownership Program
        (authorized by HB 1474 and amended by HB 1696) ... The mortgage
        receivable for these loans is offset by an allowance for forgivable
        loans" -- i.e. these loans sit directly on WSHFC's own balance sheet
        (inside the same "Down Payment Assistance and Other Loans" Note 5
        line, netted by a new $27,780,379 "Allowance for Forgivable Loans"
        that appeared for the first time in FY2025). Confidence: high.
  - "off_balance_sheet" (confirmed structurally external to WSHFC's own
    balance sheet):
      * combined_bonds_4pct, nonprofit_senior_housing -- Note 1 (p.18)
        states plainly that Multifamily Housing and Nonprofit Housing and
        Facilities bonds are "Conduit Financing Programs ... conduit debt,
        i.e., limited-obligation bonds issued for the express purpose of
        providing financing for a specific third party that is not a part
        of the financial reporting entity ... as of fiscal years ending
        June 30, 2025 and 2024, all bonds under these programs meet the
        accounting standard definition of conduit bonds and, as such, are
        NOT included in our financial statements." The 4% tax credits
        layered on top of combined_bonds_4pct are, additionally, a tax
        credit allocation issued directly to developers/investors -- the
        same off-balance-sheet logic used for every other state's 4%/9%
        LIHTC subprograms in this project.
      * pct9_credits -- same LIHTC-allocation logic as combined_bonds_4pct's
        4% credits: WSHFC allocates the federal 9% credit to developers/
        investors, never carrying the credit value or syndication equity as
        its own asset. "9%"/"Housing Tax Credit"/"LIHTC" never appears
        anywhere in the ACFR's Note 1-13 program/fund descriptions as a
        WSHFC-carried balance (only as MD&A market-conditions commentary).

Multifamily project-level detail (9% Housing Tax Credit Program, 2025
Allocation List) -- what "above the line" means and the King County anomaly
------------------------------------------------------------------------
The 2025 Allocation List covers ONE competitive round (the November 2024
application round) split into 4 geographic pools (King County, Metro,
Non-Metro New Production, Non-Metro Preservation/Rehab -- the last had zero
allocations this round). Each pool lists its "Application" rows in ranked
order, followed by a printed "Credit Allocated: $X" subtotal (the
competitively ranked, funded/"above the line" projects) and then a separate
"... Unranked (Noncompetitive or Awaiting Other Funding Commitments)"
section for projects that applied but did not receive an allocation this
round. The list's own statewide footer distinguishes both populations:
"Total Project Applications: 17 Total Credit Requested: $27,919,667 [1,026
total low-income units]" (ALL 17 applications, funded and unfunded) vs.
"Total Projects Above Line: 11 ... Total LIHTC Allocation for 2025:
$17,668,367 [668 total low-income units]" (only the 11 that actually
received an allocation). This script includes ONLY the 11 "above the line"
projects (the rows preceding each pool's own "Credit Allocated:" subtotal
line, i.e. King County's 2 + Metro's 4 + Non-Metro New Production's 5 = 11),
NOT the 6 "Unranked" applicants -- matching the task brief's "只取实际获配
(above the line/awarded)的项目" instruction. The 1,026-unit/$27.9M
all-applicant figures are quoted above for context only and never used as an
output number, the same treatment Florida's build gives its own two
non-reconciling headline totals.

Double-verification gate and a documented PDF-internal anomaly: summing this
script's own 11 RAW_PROJECTS rows' Credit Request dollar amounts gives
EXACTLY $17,668,367 (3,823,640 King + 6,403,164 Metro + 7,441,563 Non-Metro
= 17,668,367), matching the list's own printed "Total LIHTC Allocation for
2025" line exactly -- the primary double-verification gate for this table.
However, summing the same 11 rows' "Total Low-Income Units" column gives
637 (136 King + 232 Metro + 269 Non-Metro), NOT the list's own printed
statewide total of 668. The discrepancy traces to exactly one pool: King
County's two listed rows (Skyway Mixed Use, 53 units; Lexington & Concord,
83 units) sum to 136, but the King County pool's own printed subtotal line
reads "King County Credit Allocated: $3,823,640 167" -- 167, not 136, a
31-unit gap with no corresponding row anywhere on the page. Both King County
rows independently check out against their own Credit/Unit x Total
Low-Income Units arithmetic ($28,859 x 53 = $1,529,527 ~ $1,529,520 printed;
$27,640 x 83 = $2,294,120 printed exactly) and the pool's own dollar subtotal
reconciles exactly (1,529,520 + 2,294,120 = 3,823,640), so the two
transcribed project rows are correct; the pool's own printed "167" unit
subtotal is the one number on this page that does not reconcile with
anything else on it -- almost certainly a source-PDF data-entry slip (e.g. a
project's unit count carried over from an earlier draft of this pool before
a project was pulled), the same kind of isolated printed-subtotal
inconsistency PHFA's own PHARE table documents for its Washington County
row. Metro (232) and Non-Metro (269) both reconcile exactly against their
own listed rows. Because the dollar gate -- the figure this project's other
builds treat as the authoritative double-verification total whenever a
unit-level anomaly and a dollar-level total disagree on which number is
trustworthy -- reconciles perfectly, this script verifies project count
(11), the row-summed Credit Request total ($17,668,367, matching the
printed total exactly) and the row-summed Total Low-Income Units total
(637, explicitly NOT expected to equal the PDF's own printed 668, with the
mismatch asserted and explained rather than silently allowed) as its gate.

Geocoding
------------------------------------------------------------------------
Unlike IL/PA (street address) or FL (county only, no city), WSHFC's 9%
Allocation List gives City + County but no street address for any project.
Per this build's task brief, every project is therefore geocoded to city
precision: primary query "{City}, {County} County, WA", falling back to
"{City}, WA" if the county-qualified query fails, with geocode_status
uniformly recorded as "city_center" regardless of which of the two queries
succeeded (this state's best available precision -- not "ok", which this
project's convention reserves for a resolved street address). Self-throttled
to <=1 request/second with an identifying User-Agent per Nominatim's usage
policy.

fy2026
------------------------------------------------------------------------
The 2024-25 Data Report is a highlights brochure with no forward-looking/
projected-activity section anywhere in it (unlike IHDA's Report of
Activities) -- every fy2026 field below is {value: None, amount: None,
closed: False, note_key: "waFy26NotePending"}.
"""

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "wa_program_activity.json"

SOURCE_URL = "https://wshfc.org/admin/WSHFCAR2025Updater12.pdf"
SOURCE_FILE = "WA_WSHFC_DataReport_FY2025.pdf (+ WA_WSHFC_9pctHTC_AllocationList_2025.pdf)"
RETRIEVED = "2026-08-13"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
GEOCODER_USER_AGENT = "us-hfa-data-map/1.0 (github.com/MD-ai-fin/us-hfa-data-map)"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "waFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "multifamily_housing",
        "unit_type": "units",
        "fy2025_actual": 2952,
        "fy2025_source_quote": (
            "\"2025 MULTIFAMILY HOUSING HIGHLIGHTS\" (Data Report p.6): \"2,952 "
            "affordable apartments created or preserved ... 36 affordable apartment "
            "projects financed statewide in 13 counties ... $395.6 million total bonds "
            "issued ... $543.5 million in equity generated from Low Income Housing Tax "
            "Credits.\" Subcategory breakdown (p.7): Combined Bonds and 4% Tax Credits -- "
            "23 projects, 2,292 units, $395.6M bonds, $375M equity; 9% Housing Tax "
            "Credits -- 13 projects, 660 units, $168M equity; Nonprofit Senior Housing -- "
            "3 projects, 522 units/beds, $167M bonds. 23+13=36 projects, 2,292+660=2,952 "
            "units and 375+168=543(.5)M equity all reconcile exactly to the overview -- "
            "Nonprofit Senior Housing's 3 projects/522 units/$167M bonds sit OUTSIDE the "
            "overview totals entirely (see module docstring)."
        ),
        "fy2025_amounts": [
            {"label_key": "wa_amt_total_bonds", "amount": 395600000},
            {"label_key": "wa_amt_total_lihtc_equity", "amount": 543500000},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "combined_bonds_4pct", "fy2025_units": 2292, "fy2025_amount": 395600000,
             "color_group": "bond",
             # Note 1 (p.18): Multifamily Housing bonds are "Conduit Financing
             # Programs" -- conduit debt "not included in our financial
             # statements"; the accompanying 4% credits are a federal
             # tax-credit allocation, never a WSHFC-carried asset.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "pct9_credits", "fy2025_units": 660, "fy2025_amount": 168000000,
             "color_group": "credit",
             # 9% LIHTC is a federal tax-credit allocation issued directly to
             # developers/investors -- never appears as a WSHFC-carried
             # balance anywhere in the ACFR.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "nonprofit_senior_housing", "fy2025_units": 522, "fy2025_amount": 167000000,
             "color_group": "bond",
             # Note 1 (p.18): "Nonprofit Housing and Facilities" bonds are
             # explicitly named among the Conduit Financing Programs --
             # conduit debt not included in WSHFC's financial statements.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "homeownership_loans",
        "unit_type": "households",
        "fy2025_actual": 5247,
        "fy2025_source_quote": (
            "\"2025 HOMEOWNERSHIP HIGHLIGHTS\" (Data Report p.4): \"5,247 households "
            "served (4,638 Home Advantage loans and 609 House Key loans) ... $2.04B in "
            "first-mortgage loans.\" 4,638 + 609 = 5,247 exactly; the $2.04B total is not "
            "broken out by product in the source, so it is shown only as a "
            "category-level amount, not split between the two subprograms."
        ),
        "fy2025_amounts": [
            {"label_key": "wa_amt_first_mortgage_total", "amount": 2040000000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "home_advantage", "fy2025_units": 4638, "fy2025_amount": None,
             "color_group": "bond",
             # Note 1 (p.17-18): Bond Fund's Single-Family Homeownership
             # Program; MD&A (p.5) confirms Home Advantage is "supplement[ed]
             # ... by issuing taxable bonds" under this program, plus loans
             # sold into the TBA/MBS market; Note 4 (p.29) names "Single
             # Family Homeownership Program" MBS gains by program.
             "fund_type": "proprietary", "fund_name": "Single-Family Homeownership Program (Bond Fund)",
             "fy2026": _FY26_PENDING},
            {"key": "house_key", "fy2025_units": 609, "fy2025_amount": None,
             "color_group": "bond",
             # Same Bond Fund Single-Family Homeownership Program; MD&A
             # (p.5): "$170.1 million in lendable proceeds for our House Key
             # Opportunity program through the issuance of tax-exempt bonds
             # in fiscal year 2025."
             "fund_type": "proprietary", "fund_name": "Single-Family Homeownership Program (Bond Fund) — House Key Opportunity",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "downpayment_closing_cost_assistance",
        "unit_type": "households",
        "fy2025_actual": 5124,
        "fy2025_source_quote": (
            "\"2025 HOMEOWNERSHIP HIGHLIGHTS\" (Data Report p.4), \"Down Payment and "
            "Closing-cost Loans\" panel: \"5,124 homebuyers served (buyers using our home "
            "loans) ... $126M.\" A separate metric from the 5,247-household first-mortgage "
            "figure above -- the Data Report never states the two nest or sum, so this is "
            "kept as its own category rather than folded into Homeownership Loans."
        ),
        "fy2025_amounts": [
            {"label_key": "wa_amt_dpa_closing_cost_total", "amount": 126000000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "downpayment_closing_cost", "fy2025_units": 5124, "fy2025_amount": 126000000,
             "color_group": "capital",
             # Note 5, "Mortgage Loans" (p.29-30): "Down Payment Assistance
             # and Other Loans Supporting Homeownership $449,499,316" is
             # WSHFC's own carried loan-receivable balance; Note 1's
             # Program-Related Investments description names "established
             # down payment assistance ... programs" as a PRI use, though
             # Note 5 itself does not re-name PRI as this balance's specific
             # funding source (confidence: medium on the PRI attribution).
             "fund_type": "proprietary", "fund_name": "Down Payment Assistance and Other Loans Supporting Homeownership (Note 5)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "covenant_homeownership",
        "unit_type": "households",
        "fy2025_actual": 547,
        "fy2025_source_quote": (
            "\"COVENANT HOMEOWNERSHIP PROGRAM\" (Data Report p.5): \"This groundbreaking "
            "program launched July 1, 2024 ... Funded by a new document recording fee ... "
            "547 Homebuyers served, 1,236 Total household members, $60.2M Total "
            "downpayment loans.\" (The 1,236 total-household-members figure is a "
            "person-count, not a homebuyer/loan count, and is not otherwise surfaced in "
            "this file's numeric fields.)"
        ),
        "fy2025_amounts": [
            {"label_key": "wa_amt_covenant_downpayment_loans", "amount": 60200000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "covenant_downpayment_loans", "fy2025_units": 547, "fy2025_amount": 60200000,
             "color_group": "capital",
             # Note 5 (p.30): "in FY 2025, the Commission began issuing
             # forgivable downpayment assistance loans through the Covenant
             # Homeownership Program (authorized by HB 1474 and amended by
             # HB 1696) ... offset by an allowance for forgivable loans" --
             # carried directly on WSHFC's own balance sheet.
             "fund_type": "proprietary", "fund_name": "Covenant Homeownership Program forgivable down payment loans (Note 5)",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# ---------------------------------------------------------------------------
# Multifamily project-level detail (9% Housing Tax Credit Program, 2025
# Allocation List -- the 11 "above the line"/awarded projects only; see
# module docstring for the King County pool's printed-subtotal anomaly).
# (name, city, county, total_low_income_units, credit_request_dollars)
# ---------------------------------------------------------------------------

RAW_PROJECTS = [
    ("Skyway Mixed Use", "Seattle", "King", 53, 1529520),
    ("Lexington & Concord", "Seattle", "King", 83, 2294120),
    ("Housing Hope - EUCC (AKA Rainbow Terrace)", "Everett", "Snohomish", 66, 1824058),
    ("South Yakima Senior Housing", "Tacoma", "Pierce", 62, 1712360),
    ("Bellis Fair Senior Housing", "Bellingham", "Whatcom", 64, 1768960),
    ("Claudia's Place", "Vancouver", "Clark", 40, 1097786),
    ("Lewis, Spruce, & Sixth", "Yakima", "Yakima", 50, 1378777),
    ("Pathways Place", "Ellensburg", "Kittitas", 78, 2155920),
    ("Catlin and Main", "Kelso", "Cowlitz", 40, 1105600),
    ("Franz Anderson PSH", "Olympia", "Thurston", 71, 1928539),
    ("Farmview Family Housing", "Burlington", "Skagit", 30, 872727),
]

EXPECTED_PROJECT_COUNT = 11
EXPECTED_CREDIT_TOTAL = 17668367     # PDF's own printed "Total LIHTC Allocation for 2025"
EXPECTED_UNITS_ROWSUM = 637          # this script's own row sum -- see docstring: the
                                      # PDF's own printed statewide total (668) does NOT
                                      # reconcile, solely due to a King County pool
                                      # subtotal-line anomaly documented above.

FUNDING_COLOR_GROUP = {"pct9_credits": "credit"}
FUNDING_PRIORITY = ["pct9_credits"]


def verify_totals():
    errors = []
    if len(RAW_PROJECTS) != EXPECTED_PROJECT_COUNT:
        errors.append(f"project count: expected {EXPECTED_PROJECT_COUNT}, got {len(RAW_PROJECTS)}")
    credit_sum = sum(r[4] for r in RAW_PROJECTS)
    if credit_sum != EXPECTED_CREDIT_TOTAL:
        errors.append(f"Credit Request total: expected ${EXPECTED_CREDIT_TOTAL:,}, got ${credit_sum:,}")
    units_sum = sum(r[3] for r in RAW_PROJECTS)
    if units_sum != EXPECTED_UNITS_ROWSUM:
        errors.append(f"Total Low-Income Units row-sum: expected {EXPECTED_UNITS_ROWSUM:,}, got {units_sum:,}")
    if errors:
        raise SystemExit("Project count/total mismatch(es):\n" + "\n".join(errors))
    print(f"Project count ({EXPECTED_PROJECT_COUNT}) and Credit Request total "
          f"(${EXPECTED_CREDIT_TOTAL:,}) verified exactly against the 2025 Allocation "
          f"List's own printed \"Total LIHTC Allocation for 2025\" line. Row-summed Total "
          f"Low-Income Units ({EXPECTED_UNITS_ROWSUM:,}) intentionally does NOT match the "
          f"PDF's own printed statewide total (668) -- a documented King County pool "
          f"subtotal anomaly, see module docstring; the dollar gate above is this "
          f"script's authoritative double-verification total.")


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


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
    for name, city, county, units, credit_request in RAW_PROJECTS:
        coords = geocode(f"{city}, {county} County, WA", cache)
        if coords is None:
            coords = geocode(f"{city}, WA", cache)
        status = "city_center" if coords else "unresolved"
        source_amounts = {"pct9_credits": credit_request}
        projects.append({
            "id": slugify(name),
            "name": name,
            "address": None,
            "city": city,
            "lat": round(coords[0], 5) if coords else None,
            "lon": round(coords[1], 5) if coords else None,
            "units": units,
            "funding_sources": ["pct9_credits"],
            "source_amounts": source_amounts,
            "total_amount": credit_request,
            "primary_color_group": FUNDING_COLOR_GROUP["pct9_credits"],
            "overlaps": False,
            "geocode_status": status,
        })
    return projects


def main():
    verify_totals()
    print("Geocoding project cities via Nominatim (city-center precision)...")
    projects = build_projects()
    unresolved = [p["name"] for p in projects if p["geocode_status"] == "unresolved"]
    if unresolved:
        print(f"  {len(unresolved)} project(s) could not be geocoded: {unresolved}")

    payload = {
        "WA": {
            "hfa_name": "Washington State Housing Finance Commission",
            "hfa_abbr": "WSHFC",
            "fiscal_year": "FY2025",
            "source_title": "2024-25 Data Report (+ 9% Housing Tax Credit Program 2025 Allocation List)",
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
