"""
Builds docs/ca_program_activity.json from CalHFA's FY2024-25 Popular Annual
Financial Report (PAFR), its FY2024-25 California Dream For All Annual
Report, and CalHFA's own FY2025 Annual Comprehensive Financial Report (ACFR)
Statistical Section.

Sources
------------------------------------------------------------------------
1. "2024/25 Popular Annual Financial Report" (PAFR), Statistical Snapshot
   pages (Multifamily Highlights / Single Family Highlights) and the Chief
   Deputy Director's transmittal letter:
     https://www.calhfa.ca.gov/about/financials/reports/24-25/2024-2025-pafr.pdf
   Local copy: FY2025/program_activity/pdf/CA_CalHFA_PAFR_2024-2025.pdf
2. "California Dream For All Annual Report, Fiscal Year 2024-2025" (to the
   Legislature, pursuant to Health and Safety Code Section 51526):
     https://www.calhfa.ca.gov/about/press/reports/DFA-Report-2026-01.pdf
   Local copy: FY2025/program_activity/pdf/CA_CalHFA_DFA_Report_FY2025.pdf
3. CalHFA's own FY2025 ACFR (checked-in text extraction), used for (a) GASB
   fund-type classification and (b) the Statistical Section's per-project
   "Multifamily Programs" table (see "Project-level detail" below):
     FY2025/txt/CA_CalHFA_FY2025_ACFR.txt

Data-provenance check on the checked-in ACFR text
------------------------------------------------------------------------
FY2025/txt/CA_CalHFA_FY2025_ACFR.txt WAS verified to be CalHFA's own audited
financial statements before use (the PA build's own docstring flagged this
exact failure mode -- a mismatched, wrongly-scoped ACFR -- as something to
check for every state). The file's own title page reads "ANNUAL
COMPREHENSIVE FINANCIAL REPORT of the California Housing Finance Fund for
the fiscal years ended June 30, 2024 and June 30, 2025 / CALIFORNIA HOUSING
FINANCE AGENCY / A Component Unit of the State of California", its Letter of
Transmittal (dated December 22, 2025) is signed in CalHFA's own voice ("The
California Housing Finance Agency (CalHFA or Agency) is pleased to present
the Annual Comprehensive Financial Report (ACFR) of the California Housing
Finance Fund..."), and its Notes describe exactly CalHFA's own single
enterprise fund with no discretely-presented summary of a different agency.
This is the correctly-scoped source -- no substitution was needed.

$1.1 billion vs. $1.4 billion -- which Multifamily dollar figure this script uses
------------------------------------------------------------------------
The PAFR states TWO different dollar figures for FY2024-25 multifamily
lending/bond issuance activity, and they do not match:
  - "Multifamily Highlights" Statistical Snapshot page (p.8 of the PAFR,
    the page directly captioned with the 2,779-units figure and its own
    AMI-tier chart): "2,779 units* ... $1.1 billion IN LENDING AND BOND
    ISSUANCE" (* "Represents all units in CalHFA-financed affordable
    housing developments").
  - Chief Deputy Director's transmittal letter (p.1): "...the Agency used
    more than $1.4 billion in lending and bond issuance to create and
    preserve more than 2,700 affordable rental units for California
    families."
This script uses the Multifamily Highlights snapshot's $1.1 billion, cross-
checked against (and refined by) the ACFR's own Statistical Section "Net
Lending and Unit Production Total" line (p.189 of the ACFR): "$1,115,923,982
... 2,779 ... 1,120" -- i.e. the ACFR's own audited total reconciles to
2,779 units and $1,115,923,982, which rounds to exactly "$1.1 billion" and
matches the *exact* unit count printed on the snapshot page. The letter's
"more than $1.4 billion" is a rounder, broader framing not tied to any
single named statistic elsewhere in either document (and its own paired
unit figure, "more than 2,700", is itself a looser rounding of 2,779) --
since $1.1B/2,779 has two independent, mutually-reconciling, precisely-
matching sources (the snapshot page AND the ACFR's own audited total) and
$1.4B has none, $1.1B ($1,115,923,982) is the figure this script treats as
authoritative. The letter's $1.4B is quoted in fy2025_source_quote for
transparency but is not used as an output number anywhere.
(By contrast the Single Family side has no such conflict: the letter's
"$3.14 billion in first mortgage loans" is simply a more precise version of
the snapshot page's rounded "$3.1 billion", and "6,955" homebuyers is
identical in both places.)

Category-level methodology
------------------------------------------------------------------------
Category 1 -- Multifamily (fy2025_actual=2,779 units, unit_type=units):
headline and $1.1B lending/bond figure both per the discussion above. This
category's TWO subprograms (Conduit Projects and SNHP -- see "Project-level
detail" below) are additive=True (they are two distinct, non-overlapping
CalHFA program lines -- no development appears in both), matching the same
convention PHFA's build script uses for its own non-overlapping
Homeownership subprograms: additive=True does NOT require the subprograms'
own sum to equal the category headline, only that the subprograms do not
double-count each other. Here Conduit (2,554 units) + SNHP (99 units) =
2,653 of the category's 2,779-unit headline (95.5%) -- the remaining 126
units are real ACFR-disclosed activity (Permanent Conversion Projects and
Mixed Income Program Conversion Projects, per the ACFR's own "Net
Production" reconciliation table, p.188-189) that this script deliberately
leaves OUT of both RAW_PROJECTS and the subprograms list -- see "Why the
2,779 total is not fully decomposed" below.

Category 2 -- Homeownership (fy2025_actual=6,955 households, unit_type=
households): headline is the PAFR's own "6,955 homebuyers helped" (Single
Family Highlights snapshot, cross-checked against the CDD letter's "more
than $3.14 billion in first mortgage loans" for 6,955 families -- both
documents give the identical 6,955 figure). additive=False, with exactly one
subprogram, dream_for_all (fy2025_units=1,732, fy2025_amount=$200,000,000):
per this build's task brief, Dream For All's 1,732 borrowers are a SUBSET of
the 6,955 total homebuyers, not a parallel/additional category -- confirmed
structurally by the DFA Annual Report itself ("The shared appreciation loan
must be paired with a CalHFA first mortgage", p.6), i.e. every DFA borrower
is necessarily also one of the 6,955 CalHFA first-mortgage borrowers counted
in the category headline. additive=False (a reference chip, not a stacked
bar) correctly signals "this subprogram's count is not additional to the
headline", matching this project's established convention for subset-not-
partition subprograms (e.g. IHDA/PHFA's own non-additive categories).
fy2025_amounts on the category itself list BOTH the $3.14B first-mortgage
total (letter, more precise than the snapshot's rounded $3.1B) and the
snapshot's own $278M "down payment & closing cost assistance" total; DFA's
$200M is a portion of that $278M (not shown as a separate category amount,
to avoid implying DFA's $200M is additive on top of the $278M -- it is the
same dollars viewed from the DFA program's own report).

Project-level detail: why CalHFA's ACFR Statistical Section was used instead of TCAC/CDLAC
------------------------------------------------------------------------
This build first attempted, per the task brief, to find a ready-made
per-project multifamily list the way PHFA's "Map Doc" or IHDA's Appendix
provide one:
  - CalHFA's own website has no published "closed loans" or "funded
    developments" list for multifamily (checked calhfa.ca.gov's Multifamily
    Programs pages and press releases; only found preliminary,
    forward-looking award lists for specific NOFA rounds, e.g. the 2025
    Mixed-Income Program's "top 12 eligible developments" -- a different,
    smaller, and not-yet-closed population, not FY2025's actual closed
    activity).
  - CalHFA Board of Directors meeting packages do contain individual loan
    commitment items (e.g. "Final Loan Commitment for Holt & Main
    Project... 160-unit"), but only as items scattered across ~6 bi-monthly
    board packages with no single aggregated table or Board-approved total
    to check a transcription against -- exactly the "large amount of manual
    work, unverifiable" pattern this project's methodology says to avoid.
  - CTCAC (California Tax Credit Allocation Committee)'s 2025 awards (37
    projects, 2,162 units, per its own 2025 Annual Report) and CDLAC
    (California Debt Limit Allocation Committee)'s bond allocations are
    real, well-documented, per-project lists with their own official
    totals -- but neither is CalHFA-specific: TCAC and CDLAC allocate
    credits/bonds to any qualified sponsor statewide, most of which never
    involve a CalHFA loan at all. Confirming which of TCAC's 37 or CDLAC's
    awardees also received a CalHFA loan in FY2025 would require manually
    cross-referencing sponsor/address across three separate agencies'
    documents with no shared identifier -- again the kind of unverifiable
    manual reconciliation this project avoids, so neither was used.
Instead, CalHFA's OWN FY2025 ACFR Statistical Section (a document already
confirmed to be CalHFA's own audited report, not a third party's) turned out
to contain a genuine per-project table: "Multifamily Programs, Fiscal Year
Ended June 30, 2025" (ACFR pp.185-186) lists, for the "Conduit Projects"
program, 18 named developments with County, Loan Amount, Total Units, and
Very Low Income Units, followed by the table's own printed "Total $962,358
[thousand] 2,554 1,009" row -- and a second, one-row "Special Needs Housing
Program (SNHP)" table for "SNHP Flor 401 Lofts" with its own printed
"Total $500,000 99 98" row. Both tables' own dollar/unit/VLI-unit columns
were independently re-summed from the row data during this build and
verified to match their own printed totals exactly (Conduit's dollar column
needs the table's own separately-listed "Supplemental CDLAC Allocated Bonds
Issued" line, $40,784 thousand -- itself a refinancing top-up to
PRIOR-year projects, not a new development, and correctly excluded from
RAW_PROJECTS -- added back in: $921,575K [18 named projects] + $40,784K
[supplemental bonds] = $962,359K, a $1,000 (0.0001%) rounding difference
from the table's own printed $962,358K, consistent with each row being
independently rounded to the nearest $1,000 for display; see
verify_conduit_totals()). This is the same double-verification-gate standard
(own printed total, independently re-summed) used throughout PHFA's and
Florida Housing's build scripts -- it just happens to live inside CalHFA's
ACFR rather than a separate annual-report table.

Why the 2,779 total is not fully decomposed / why RAW_PROJECTS is a documented subset
------------------------------------------------------------------------
The ACFR's own "Net Production" reconciliation table (p.188-189) shows how
Conduit (2,554) + SNHP (99) + Permanent Only (~0) + several
construction-to-permanent conversion line items nets to the category's
2,779-unit headline. However, that specific reconciliation table's text
extraction shows visible column-interleaving/OCR artifacts (e.g. one row
literally reads "PMrioxjeedc tIsncome Program Conversion" -- overlapping
text streams from "Mixed Income Program Conversion" and an adjacent "Prior
[Fiscal Years]" label bleeding into each other), unlike the clean,
artifact-free Conduit Projects and SNHP tables this script actually uses.
Because that reconciliation table cannot be trusted cell-by-cell, this
script does NOT attempt to re-derive named projects or dollar/unit
subtotals for "Permanent Conversion Projects" or "Mixed Income Program
Conversion Projects" (together the remaining ~126 units of the 2,779
headline) -- doing so from unreliable OCR would risk exactly the kind of
fabricated-looking number this project's methodology forbids. The named
projects that DO appear inside those reconciliation rows in the ACFR text
(e.g. the same 6 Mixed Income Program developments -- St. Luke's Affordable,
Holt & Main, North City Affordable, Monarch, BUSD Workforce Housing,
Maison's Village Phase II -- also appear, with different, larger dollar
figures, as "Projects Construction Loan Closed, Waiting for Permanent Loan
Conversion") are deliberately EXCLUDED from RAW_PROJECTS: per the ACFR's own
"Net Production" table, that entire 2,008-unit "Construction Loan Closed"
line is offset by an equal-and-opposite "Unit Adjustment for Construction to
Permanent Financing" line (net effect: zero net units counted toward
FY2025's 2,779 production this year -- they are still under construction,
not yet "permanent", and will only count in a future fiscal year's totals
when converted), so including them in this year's bubble map would
double-count/misrepresent activity that the ACFR itself says nets to zero
this year. The same is true of the "Permanent Conversion Projects Counted in
Prior Fiscal Years" (7 named projects) and "Mixed Income Program Conversion
Projects Counted in Prior Fiscal Years" (10 named projects) rows -- both
explicitly labeled by the ACFR as reversals of amounts ALREADY counted in a
prior year's total, not new FY2025 production.
Net result: RAW_PROJECTS covers 19 named developments / 2,653 of the
category's 2,779 headline units (95.5%) -- a real, ACFR-sourced, doubly-
verified subset, not the full headline. This is disclosed here and in the
category's own fy2025_source_quote, not glossed over.

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
Like Florida Housing (and unlike IHDA's 7 governmental + 4 proprietary funds
or PHFA's 5 named business-type programs), CalHFA's ACFR states plainly:
"The Fund is accounted for as an enterprise fund" (singular) and "The Agency
follows the business-type accounting requirements of GASB Statement 34"
(Note 2, Basis of Presentation and Accounting). CalHFA has no governmental
funds at all, so "governmental" is never used below -- only "proprietary"
(carried inside CalHFA's own enterprise Fund) vs. "off_balance_sheet"
(explicitly or structurally outside the Fund's own financial statements).
  - conduit -- "proprietary", high confidence. Note 2's "Programs and
    Accounts" section (c) names "Multifamily Rental Housing Programs" --
    Special Obligation Multifamily Housing Revenue Bonds (SOMHRB),
    Multifamily Housing Revenue Bonds (MHRB), and Affordable Housing
    Revenue Bonds (AHRB) -- as accounts of the Fund itself; Conduit
    Projects' own loans are part of this same multifamily bond-financing
    business.
  - snhp -- "proprietary", high confidence, near-verbatim quote. Note 2
    explicitly places the Special Needs Housing Program among the
    "Contract Administration Programs" and states: "All monies transferred
    in accordance with the agreements and for the purposes of the program
    are considered assets of the Fund." -- i.e. SNHP funds ARE carried on
    CalHFA's own books, unlike a pure pass-through.
  - dream_for_all -- "off_balance_sheet", high confidence, verbatim quote.
    Note 2 states, in its own dedicated paragraph: "The Agency is the
    administrator of the Dream for All Program (DFA) fund, established in
    2022 by Section 51520 of the Health and Safety Code et seq. which is a
    shared appreciation down payment loan program, the funds of which are
    neither generated nor held within the Fund, and therefore, not
    included in the accompanying financial statements." This is the most
    explicit fund-type disclosure found across any of this project's state
    builds to date -- CalHFA administers DFA, but DFA's own money is
    structurally never part of the audited Fund this ACFR reports on, the
    same way IHDA's LIHTC/PHFA's PHARE money never becomes a fund asset
    even though the agency administers the program.

Geocoding
------------------------------------------------------------------------
The Conduit Projects / SNHP table gives only a COUNTY for each development
(no street address, no city) -- the same disclosure limit Florida Housing's
"RENTAL PROPERTIES AWARDED FUNDING IN 2025" table has. This script therefore
follows FL's build script exactly: one Nominatim query per unique county
("{County} County, California"), geocode_status="county_center" for every
project, self-throttled to <=1 request/second with an identifying
User-Agent per Nominatim's usage policy.

fy2026
------------------------------------------------------------------------
Neither the PAFR nor the DFA Annual Report contains a forward-looking
FY2026 activity projection (units or households). The DFA report's "Current
Status" section does note "The 2025-26 State Budget allocated an additional
$300 million to continue implementation" -- but this is a budget
appropriation for the program's revolving fund, not a projected FY2026
count of homeowners or dollars actually deployed, so it is NOT used as a
fy2026.amount (which would misleadingly suggest CalHFA disclosed a FY2026
activity forecast). Every fy2026 field below is therefore {value: None,
amount: None, closed: False, note_key: "caFy26NotePending"}.
"""

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "ca_program_activity.json"

SOURCE_URL = "https://www.calhfa.ca.gov/about/financials/reports/24-25/2024-2025-pafr.pdf"
SOURCE_FILE = (
    "CA_CalHFA_PAFR_2024-2025.pdf (+ CA_CalHFA_DFA_Report_FY2025.pdf, + "
    "CA_CalHFA_FY2025_ACFR.txt Statistical Section \"Multifamily Programs\")"
)
RETRIEVED = "2026-08-13"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
GEOCODER_USER_AGENT = "us-hfa-data-map/1.0 (github.com/MD-ai-fin/us-hfa-data-map)"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "caFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "multifamily_rental",
        "unit_type": "units",
        "fy2025_actual": 2779,
        "fy2025_source_quote": (
            "PAFR \"Multifamily Highlights\" Statistical Snapshot: \"2,779 units* ... "
            "$1.1 billion IN LENDING AND BOND ISSUANCE\" (* \"Represents all units in "
            "CalHFA-financed affordable housing developments\"); AMI tiers 10% 80 AMI+ / "
            "19% 70 AMI / 31% 60 AMI / 15% 50 AMI / 2% 40 AMI / 23% 30 AMI or below. "
            "Cross-checked against the FY2025 ACFR Statistical Section's own \"Net "
            "Lending and Unit Production Total\": \"$1,115,923,982 ... 2,779 ... 1,120\" "
            "(p.189) -- rounds to the identical $1.1B and matches 2,779 exactly. (The "
            "CDD transmittal letter separately states \"more than $1.4 billion in "
            "lending and bond issuance to create and preserve more than 2,700 "
            "affordable rental units\" -- a rounder figure not used here; see module "
            "docstring for why $1.1B/2,779 is treated as authoritative.)"
        ),
        "fy2025_amounts": [
            {"label_key": "ca_amt_multifamily_lending", "amount": 1115923982},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "conduit", "fy2025_units": 2554, "fy2025_amount": 962358000,
             "color_group": "bond",
             # ACFR Note 2(c) "Programs and Accounts": Multifamily Rental
             # Housing Programs (SOMHRB/MHRB/AHRB) are accounts of the Fund
             # itself; Conduit Projects' loans are part of this business.
             "fund_type": "proprietary",
             "fund_name": "Multifamily Rental Housing Programs (Conduit — SOMHRB/MHRB/AHRB)",
             "fy2026": _FY26_PENDING},
            {"key": "snhp", "fy2025_units": 99, "fy2025_amount": 500000,
             "color_group": "capital",
             # ACFR Note 2(c): "All monies transferred in accordance with
             # the agreements and for the purposes of the [Contract
             # Administration] program are considered assets of the Fund" --
             # SNHP is explicitly named among those programs.
             "fund_type": "proprietary",
             "fund_name": "Contract Administration Programs — Special Needs Housing Program (SNHP)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "homeownership_loans",
        "unit_type": "households",
        "fy2025_actual": 6955,
        "fy2025_source_quote": (
            "PAFR \"Single Family Highlights\" Statistical Snapshot: \"6,955 homebuyers "
            "helped ... $3.1 billion IN FIRST MORTGAGE LENDING ... $278 million IN DOWN "
            "PAYMENT & CLOSING COST ASSISTANCE\"; loan types 46% FHA / 53% Conventional / "
            "0.4% VA / 0.2% USDA. CDD transmittal letter: \"CalHFA helped 6,955 low- and "
            "moderate-income families achieve the dream of homeownership with more than "
            "$3.14 billion in first mortgage loans.\" California Dream For All Annual "
            "Report, FY2024-25: \"From July 1, 2024 through June 30, 2025, the Dream For "
            "All program helped 1,732 new homeowners purchase a home. This corresponds "
            "to $200 million in down payment assistance, leveraging nearly $1 billion in "
            "first mortgage secondary market capital.\" Every Dream For All loan is "
            "paired with a CalHFA first mortgage (DFA Annual Report, \"Overview of "
            "Shared Appreciation Loans\": \"The shared appreciation loan must be paired "
            "with a CalHFA first mortgage\"), so DFA's 1,732 borrowers are a SUBSET of "
            "the 6,955 total homebuyers helped, not an additional/parallel population."
        ),
        "fy2025_amounts": [
            {"label_key": "ca_amt_first_mortgage", "amount": 3140000000},
            {"label_key": "ca_amt_dpa_total", "amount": 278000000},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "dream_for_all", "fy2025_units": 1732, "fy2025_amount": 200000000,
             "color_group": "capital",
             # ACFR Note 2: "The Agency is the administrator of the Dream
             # for All Program (DFA) fund ... the funds of which are
             # neither generated nor held within the Fund, and therefore,
             # not included in the accompanying financial statements." --
             # CalHFA administers DFA but its money is structurally never a
             # Fund asset.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
]

# ---------------------------------------------------------------------------
# Multifamily project-level detail: FY2025 ACFR Statistical Section,
# "Multifamily Programs, Fiscal Year Ended June 30, 2025" (pp.185-186).
# (name, county, source_key, loan_amount_dollars, total_units, vli_units)
# Amounts transcribed from the table (printed "dollars in thousands") x1000.
# ---------------------------------------------------------------------------

RAW_PROJECTS = [
    ("All Hallows Apartments", "San Francisco", "conduit", 76500000, 157, 80),
    ("La Salle Apartments", "San Francisco", "conduit", 68000000, 145, 72),
    ("U.S. VETS-WLAVA Building 210", "Los Angeles", "conduit", 19562000, 38, 37),
    ("Bayview Apartments", "San Francisco", "conduit", 63000000, 146, 72),
    ("Sisal Apartments", "San Diego", "conduit", 32100000, 120, 12),
    ("The Pardes 2", "Sacramento", "conduit", 59169000, 140, 42),
    ("The Trails at Carmel Mountain Ranch", "San Diego", "conduit", 50233000, 125, 26),
    ("St. Luke's Affordable", "San Diego", "conduit", 20000000, 78, 44),
    ("Holt & Main", "Los Angeles", "conduit", 70858000, 160, 52),
    ("Kindred Apartments", "San Diego", "conduit", 71958000, 126, 97),
    ("6018 Brynhurst", "Los Angeles", "conduit", 11887000, 50, 10),
    ("121 N. Mathews", "Los Angeles", "conduit", 9540000, 40, 8),
    ("North City Affordable", "San Diego", "conduit", 62130000, 224, 124),
    ("Monarch", "Sacramento", "conduit", 73272000, 241, 99),
    ("BUSD Workforce Housing", "Alameda", "conduit", 44549000, 110, 50),
    ("Maison's Village Phase II", "Los Angeles", "conduit", 40020000, 191, 58),
    ("Westside Village", "Santa Cruz", "conduit", 30747000, 38, 25),
    ("300 De Haro", "San Francisco", "conduit", 118050000, 425, 101),
    ("SNHP Flor 401 Lofts", "Los Angeles", "snhp", 500000, 99, 98),
]

# The Conduit Projects table's own printed Total row also includes a
# "Supplemental CDLAC Allocated Bonds Issued" line -- a refinancing top-up
# to projects funded in a PRIOR fiscal year, not a new FY2025 development,
# and therefore correctly excluded from RAW_PROJECTS -- but it IS part of
# the table's own $ total, so it is added back in only for verification.
CONDUIT_SUPPLEMENTAL_BONDS_AMOUNT = 40784000  # "$40,784" (thousands) x1000

CONDUIT_EXPECTED_TOTAL_AMOUNT = 962358000  # table's own printed "Total $962,358" (thousands) x1000
CONDUIT_EXPECTED_TOTAL_UNITS = 2554
CONDUIT_EXPECTED_TOTAL_VLI = 1009
SNHP_EXPECTED_TOTAL_AMOUNT = 500000
SNHP_EXPECTED_TOTAL_UNITS = 99
SNHP_EXPECTED_TOTAL_VLI = 98

FUNDING_COLOR_GROUP = {"conduit": "bond", "snhp": "capital"}
FUNDING_PRIORITY = ["conduit", "snhp"]


def verify_conduit_totals():
    conduit = [r for r in RAW_PROJECTS if r[2] == "conduit"]
    errors = []
    if len(conduit) != 18:
        errors.append(f"Conduit project count: expected 18, got {len(conduit)}")
    amt = sum(r[3] for r in conduit)
    units = sum(r[4] for r in conduit)
    vli = sum(r[5] for r in conduit)
    amt_with_supplemental = amt + CONDUIT_SUPPLEMENTAL_BONDS_AMOUNT
    # Table's own printed total vs. re-summed named rows + the supplemental
    # bonds line item -- allow the table's own <=$1,000 rounding artifact
    # (see module docstring), no more.
    if abs(amt_with_supplemental - CONDUIT_EXPECTED_TOTAL_AMOUNT) > 1000:
        errors.append(
            f"Conduit amount (+ supplemental bonds): expected ~{CONDUIT_EXPECTED_TOTAL_AMOUNT:,}, "
            f"got {amt_with_supplemental:,} (diff {amt_with_supplemental - CONDUIT_EXPECTED_TOTAL_AMOUNT:,})"
        )
    if units != CONDUIT_EXPECTED_TOTAL_UNITS:
        errors.append(f"Conduit Total Units: expected {CONDUIT_EXPECTED_TOTAL_UNITS}, got {units}")
    if vli != CONDUIT_EXPECTED_TOTAL_VLI:
        errors.append(f"Conduit Very Low Income Units: expected {CONDUIT_EXPECTED_TOTAL_VLI}, got {vli}")
    if errors:
        raise SystemExit("Conduit Projects total mismatch(es):\n" + "\n".join(errors))
    print(f"Conduit Projects verified: 18 projects, {units:,} units, {vli:,} VLI units, "
          f"${amt_with_supplemental:,} (incl. supplemental bonds) vs. printed "
          f"${CONDUIT_EXPECTED_TOTAL_AMOUNT:,}.")


def verify_snhp_totals():
    snhp = [r for r in RAW_PROJECTS if r[2] == "snhp"]
    errors = []
    if len(snhp) != 1:
        errors.append(f"SNHP project count: expected 1, got {len(snhp)}")
    amt = sum(r[3] for r in snhp)
    units = sum(r[4] for r in snhp)
    vli = sum(r[5] for r in snhp)
    if amt != SNHP_EXPECTED_TOTAL_AMOUNT:
        errors.append(f"SNHP amount: expected {SNHP_EXPECTED_TOTAL_AMOUNT:,}, got {amt:,}")
    if units != SNHP_EXPECTED_TOTAL_UNITS:
        errors.append(f"SNHP units: expected {SNHP_EXPECTED_TOTAL_UNITS}, got {units}")
    if vli != SNHP_EXPECTED_TOTAL_VLI:
        errors.append(f"SNHP VLI units: expected {SNHP_EXPECTED_TOTAL_VLI}, got {vli}")
    if errors:
        raise SystemExit("SNHP total mismatch(es):\n" + "\n".join(errors))
    print(f"SNHP verified: 1 project, {units} units, {vli} VLI units, ${amt:,}.")


def verify_category_and_subprogram_consistency():
    mf_cat = next(c for c in CATEGORIES if c["key"] == "multifamily_rental")
    conduit_sub = next(s for s in mf_cat["subprograms"] if s["key"] == "conduit")
    snhp_sub = next(s for s in mf_cat["subprograms"] if s["key"] == "snhp")
    errors = []
    if conduit_sub["fy2025_units"] != CONDUIT_EXPECTED_TOTAL_UNITS:
        errors.append("multifamily_rental.conduit subprogram units do not match Conduit table total")
    if snhp_sub["fy2025_units"] != SNHP_EXPECTED_TOTAL_UNITS:
        errors.append("multifamily_rental.snhp subprogram units do not match SNHP table total")
    subs_total = conduit_sub["fy2025_units"] + snhp_sub["fy2025_units"]
    if subs_total >= mf_cat["fy2025_actual"]:
        errors.append(
            f"Conduit+SNHP subprogram total ({subs_total}) should be LESS than the "
            f"category headline ({mf_cat['fy2025_actual']}) -- this category is a "
            f"documented partial subset, not a full decomposition; if this ever flips "
            f"the docstring's coverage-gap explanation needs updating too"
        )
    ho_cat = next(c for c in CATEGORIES if c["key"] == "homeownership_loans")
    dfa_sub = next(s for s in ho_cat["subprograms"] if s["key"] == "dream_for_all")
    if dfa_sub["fy2025_units"] >= ho_cat["fy2025_actual"]:
        errors.append("dream_for_all subprogram units should be a strict SUBSET of the Homeownership headline")
    if errors:
        raise SystemExit("Category/subprogram consistency mismatch(es):\n" + "\n".join(errors))
    print("Category headline vs. subprogram consistency verified (Multifamily: 2,653/2,779 "
          "documented subset; Homeownership: 1,732/6,955 documented subset).")


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
    for name, county, source_key, amount, units, _vli in RAW_PROJECTS:
        query = f"{county} County, California"
        coords = geocode(query, cache)
        status = "county_center" if coords else "unresolved"
        sources = [source_key]
        source_amounts = {source_key: amount}
        projects.append({
            "id": slugify(name),
            "name": name,
            "address": None,
            "city": f"{county} County",
            "lat": round(coords[0], 5) if coords else None,
            "lon": round(coords[1], 5) if coords else None,
            "units": units,
            "funding_sources": sources,
            "source_amounts": source_amounts,
            "total_amount": amount,
            "primary_color_group": FUNDING_COLOR_GROUP[source_key],
            "overlaps": False,
            "geocode_status": status,
        })
    return projects


def main():
    verify_conduit_totals()
    verify_snhp_totals()
    verify_category_and_subprogram_consistency()
    print("Geocoding project counties via Nominatim (county-center precision)...")
    projects = build_projects()
    unresolved = [p["name"] for p in projects if p["geocode_status"] == "unresolved"]
    if unresolved:
        print(f"  {len(unresolved)} project(s) could not be geocoded: {unresolved}")
    unique_counties = len({p["city"] for p in projects})
    print(f"  {len(projects)} projects across {unique_counties} unique counties.")

    payload = {
        "CA": {
            "hfa_name": "California Housing Finance Agency",
            "hfa_abbr": "CalHFA",
            "fiscal_year": "FY2025",
            "source_title": (
                "2024-25 Popular Annual Financial Report (PAFR); California Dream For "
                "All Annual Report FY2024-25; FY2025 ACFR Statistical Section "
                "(Multifamily Programs)"
            ),
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
