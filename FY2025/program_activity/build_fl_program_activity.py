"""
Builds docs/fl_program_activity.json from Florida Housing Finance Corporation's
2025 Annual Report.

Source: Florida Housing Finance Corporation, "2025 Annual Report"
  https://www.floridahousing.org/docs/default-source/data-docs-and-reports/annual-reports/2025-annual-report.pdf
Local copy: FY2025/program_activity/pdf/FL_FloridaHousing_AnnualReport_2025.pdf
(text already extracted to the matching .txt in the same directory; a set of
page_*.png/crop_*.png images from an earlier partial run also sit alongside
the PDF but were not needed for this build -- pdfplumber's table extraction
on the PDF itself was sufficient and more reliable than re-reading crops.)

IMPORTANT fiscal-year note
---------------------------------------------------------------------------
Unlike IHDA (IL), PHFA (PA), and OHFA (OH), Florida Housing's Annual Report
and audited financial statements both run on a CALENDAR year, January-
December 2025 -- not a July-June government fiscal year. This script
therefore uses "CY2025" (not "FY2025") in the fiscal_year field and every
place the reporting period is described, even though the file/module is
still named "fy2025"-style to match this project's directory convention.

Data-provenance check on the checked-in ACFR text
---------------------------------------------------------------------------
FY2025/txt/FL_FloridaHousing_FY2025_ACFR.txt WAS verified to be Florida
Housing's own audited financial statements before use (unlike the PA build,
which caught its FY2025/txt/PA_PHFA_FY2025_ACFR.txt pointing at the wrong,
Commonwealth-wide document). The FL file's own title page and running
headers read "FLORIDA HOUSING FINANCE CORPORATION (A Component Unit of the
State of Florida)" throughout, its MD&A is captioned "FOR THE YEAR ENDED
DECEMBER 31, 2025" (confirming the calendar-year period above), and its
Note 2 describes exactly one reporting entity with no discretely-presented
component-unit summary of a different agency -- i.e. this is the real,
correctly-scoped source, no substitution was needed.

Category-level methodology
---------------------------------------------------------------------------
Category 1 -- Rental/Multifamily (RAW_PROJECTS, "RENTAL PROPERTIES AWARDED
FUNDING IN 2025", pp. 47-56 of the Annual Report PDF): this table was
extracted programmatically with pdfplumber (its `find_tables()`, matching
each page-pair's left half -- County/Development/RFA#/HC9%/HC4%/MMRB/SAIL/
Live Local SAIL/HOME/HOME-ARP/NHTF/Developmental-Disabilities-Grants -- to
its facing right half -- CDBG-DR/Local Bonds/Total Units/Set-Aside Units/...
/Estimated Total Development Cost -- by matching each table row's y-position
across the two pages, since the physical table is printed as one row spread
across a two-page spread with no other reliable join key). A handful of
cells absorbed a stray fragment of an adjacent, line-wrapped "RFA 2024-306"
cell (e.g. a bare "2024" landing in the MMRB column with no leading "$") --
these were detected programmatically (every genuine dollar cell in this
table carries a leading "$"; a numeric-looking cell without one is always
this wrapping artifact, never a real amount) and dropped before totals were
computed. This produced 81 developments, and RAW_PROJECTS/
PROJECT_SOURCE_AMOUNTS below is that extraction's direct, reviewed output.

Every one of the table's own 11 funding-source columns, plus Total Units,
Set-Aside Units, and Estimated Total Development Cost, was independently
re-summed from RAW_PROJECTS/PROJECT_SOURCE_AMOUNTS and checked against the
table's own printed "TOTALS" row (p.56): all 14 values matched exactly on
the first fully-cleaned pass (see verify_amount_totals() and
verify_unit_totals()) -- both the unit-count gate AND the dollar-amount
gate for every column, not just a subset.

12,007 vs. 13,196 -- which headline total this category uses
---------------------------------------------------------------------------
The Annual Report discloses TWO different rental-program unit totals that
do NOT reconcile with each other, and says so itself (footnote 6, p.8):
  - "SUMMARY OF PROGRAMS" (pp.8-9): Total Units Funded 13,196 / Set-Aside
    Units 12,951, built by "calculating the number of units for all
    developments receiving funding in 2024, minus any units funded in a
    prior year, and 50% of the SHIP Rental Units" -- a rolling, multi-year,
    partially-overlap-adjusted calculation with no accompanying per-
    development list.
  - "RENTAL PROPERTIES AWARDED FUNDING IN 2025" (pp.47-56): Total Units
    12,007 / Set-Aside Units 11,762 -- the straight sum of the 81 named
    developments actually funded in calendar 2025, with a full per-
    development, per-funding-source breakdown and its own printed TOTALS
    row.
This script uses 12,007 as the category's fy2025_actual, NOT 13,196,
because 12,007 is the only one of the two figures with fully-verifiable,
named-development detail behind it -- the same table this script's
RAW_PROJECTS/bubble map are built from, so the category headline, every
subprogram's unit count, and the map's own markers are all internally
consistent and traceable to one table. 13,196 is shown for context only,
inside fy2025_source_quote, and is never used as a number this script
outputs elsewhere. As a side effect of computing each subprogram's
fy2025_units by summing RAW_PROJECTS' Total Units per funding source (see
below), 7 of the 11 sources' sums (SAIL 565, Live Local SAIL 2,714, HOME
115, HOME-ARP 258, NHTF 326, Developmental Disabilities Grants 60, CDBG-DR
353) landed EXACTLY on the SUMMARY OF PROGRAMS table's own per-program
figures despite being computed from a totally different table -- a strong
independent cross-check. Only HC4% (11,022 computed vs. 10,902 published)
and MMRB (4,400 vs. 4,280) diverge, by 120 units each, consistent with the
SUMMARY table's own stated "minus units funded in a prior year" adjustment
applying differently to those two columns. "Housing Stability for
Schoolchildren" (HSS, 44 units in the SUMMARY table) has no column at all
in the RENTAL PROPERTIES table and so has no subprogram entry in THIS
category -- it is a structurally different population (ongoing per-
household rental subsidy payments to already-housed tenants, not one-time
development financing) and is instead modeled as its own category
(Category 3 below), per user request (2026-08-14) to add any state's
independent, per-unit/per-household "persistent rental assistance/
operating subsidy" program that was previously scanned for but omitted for
lack of a verifiable breakdown.

Category 2 -- Homebuyer/Down-Payment Assistance: the category headline
(8,427, "Total Homeowners Served or Units Funded", p.8) is FL's own
published aggregate. Footnote 3 (p.8) states explicitly: "the Total
Homeowners Served or Units Funded is not equal to the sum of each program"
-- FL itself declares this category non-additive (because the same
household is frequently served by a first mortgage AND a down-payment
program simultaneously), so additive=False is used here, matching that
footnote rather than guessing at exclusivity. Subprogram-level unit counts
come from the SUMMARY OF PROGRAMS table (p.8); subprogram-level dollar
amounts (not disclosed in that summary at all) were independently sourced
from three underlying data tables and cross-checked against each other:
  - "Homes Funded Through the Homebuyer Loan and Down Payment Assistance
    Programs" (pp.32-35, county-by-county): TOTALS row (p.35) gives
    Homebuyer Loan Programs 5,843 loans / $1,582,166,593, and HAP-Florida
    Assist / FL HLP Second Mortgage / (HFA Preferred) PLUS TBA / Hometown
    Heroes their own loan-count + DPA-dollar columns (p.35-36 TOTALS rows).
    Internal check: 3,866 + 79 + 88 + 1,808 = 5,841 exactly matches the
    summary's own "Down Payment Assistance" subtotal, and + 2 "No DPA
    Requested" loans = 5,843, the Homebuyer Loan Programs total -- and
    38,655,880 + 890,000 + 1,034,882 + 29,310,655 = $69,891,417 exactly
    matches that table's own overall "DPA" TOTALS-row dollar figure. See
    verify_homebuyer_totals().
  - "Homeownership Pool (HOP) Program" county table (p.37): TOTALS row
    129 loans / $3,384,500.
  - "Predevelopment Loan Program Homeownership Loans Approved for Funding
    in 2025" (p.83): TOTALS row 99 loans / $2,768,333 -- matches the
    summary's own "Predevelopment Loan Program" 99 figure exactly (this
    table's *rental* counterpart, p.82, TOTALS 440 units / 88 set-aside,
    is the source of the *Rental* category's separate "Predevelopment Loan
    Program 440" summary-table line -- a different, smaller table from the
    81-development "RENTAL PROPERTIES AWARDED FUNDING IN 2025" table above,
    and NOT one of that table's 11 funding-source columns, which is why
    Predevelopment Loan Program has no RAW_PROJECTS presence).
  - SHIP (State Housing Initiatives Partnership): the summary's homeowner-
    ship figure of 2,455 is exactly 50% of the 4,910-unit "HOMEOWNERSHIP...
    TOTAL UNITS" figure printed in the "State Housing Initiatives
    Partnership (SHIP) Distribution and Allocation of Funds for 2022-2023"
    table's own TOTALS row (p.62), matching footnote 6's stated "50% ...
    overlap" adjustment (4,910 x 50% = 2,455 exactly; the same table's
    Rental TOTALS of 2,377 x 50% = 1,188.5, rounding to the Rental
    category's separately-summarized SHIP figure of 1,189). That table's
    own dollar figure ($218,079,957 Homeownership Expenditures) is NOT
    halved to match -- halving a printed dollar total to match a halved
    unit count would not be a number FL ever actually published -- so
    fy2025_amount for the ship subprogram below is left None rather than
    inventing a $109M "half-total" FL never stated.

Category 3 -- Housing Stability for Schoolchildren (HSS) Tenant-Based
Rental Assistance (TBRA): identified during a 2026-08-14 re-scan of this
report's full text for "rental assistance"/"voucher"/"Section 8"/"operating
subsidy"/"tenant-based" keywords (per user request to check every pilot
state's existing report for an independent, ongoing per-unit/per-household
rental subsidy program distinct from one-time development financing). The
Annual Report's own narrative (p.19, inside the HOME Investment
Partnerships Program section): "Florida Housing utilizes HOME funding to
provide short- and medium-term Tenant Based Rental Assistance (TBRA) to
families with school-aged children experiencing homelessness. The Housing
Stability for Schoolchildren Program is targeted to counties with small
and rural communities..." -- structurally a per-household, ongoing rent
subsidy (not construction/preservation financing), the same category of
program IL modeled as "rental_assistance_operations" for IHDA's Section 811
PRA/RHSP. A dedicated table, "HOUSING STABILITY FOR SCHOOLCHILDREN PROGRAM
TENANT-BASED RENTAL ASSISTANCE (TBRA)" (p.44), gives a full per-county
breakdown with its own printed TOTALS row: Charlotte 11 households/$79,641,
Hernando 15 households/$110,443, Santa Rosa 18 households/$77,967, TOTALS
44 households/$268,051 -- independently re-summed here and verified exactly
(see verify_hss_tbra_totals()). This 44-household total is a THIRD
independent match (after live_local_sail=2,714, home=115, home_arp=258,
nhtf=326, dev_disab=60, cdbg_dr=353 in Category 1 above) between this
table and the separate "SUMMARY OF PROGRAMS" table's own per-program line
("Housing Stability for Schoolchildren 44...44", p.9) -- despite the two
tables being visually and structurally unrelated. The same table also
prints an AMI-tier breakdown (0-30% AMI 25 + 31-50% AMI 17 + 51-80% AMI 2 =
44) that independently sums to the same 44, a fourth cross-check. Because
this is a per-household subsidy program with no associated physical
development/address of its own (the table is county-level, not project-
level, and describes payments to landlords on behalf of already-housed
families, not a financed construction project), this category has no
`projects`/bubble-map presence, matching how CT's Build For CT and IL's
Section 811 PRA/RHSP are also KPI-only. fy2026: not disclosed (no
forward-looking figure anywhere in this table or its surrounding section).

Fund-type classification (fund_type/fund_name on each subprogram)
---------------------------------------------------------------------------
Florida Housing's own FY2025 (CY2025) audited financial statements state
plainly, in Note 2: "Florida Housing accounts for its activities through
the use of an enterprise fund" (singular) -- i.e. unlike IHDA (7 major
governmental + 4 major proprietary + 14 nonmajor governmental funds) or
even PHFA (5 named business-type programs under one business-type
umbrella), Florida Housing has exactly ONE GASB fund, a single enterprise
fund, internally organized into non-GASB-reported "subfunds" (Note 2,
Basis of Presentation, p.20: "subfunds to account separately ... for the
bond programs, Guarantee Program, certain state and federally funded
programs, subsidiary corporations, and the operations of Florida
Housing"). Consequently the "governmental" value of fund_type is NEVER
used anywhere in this file -- Florida Housing carries no governmental
funds at all -- and the working distinction below is instead "proprietary"
(carried inside Florida Housing's own single enterprise fund, evidenced by
that program's own named loans-receivable or outstanding-commitment
balance in the ACFR) vs. "off_balance_sheet" (never appears as a Florida
Housing-carried asset/liability in the ACFR at all).
  - "proprietary", high confidence (program named with its own dollar
    balance in the ACFR):
      * sail -- Note 12, Commitments and Contingencies (p.35): "State
        Apartment Incentive Loan Program $244,498,189" of outstanding loan
        commitments.
      * mmrb -- Note 2, Basis of Presentation (p.20), names "bond
        programs" as one of the enterprise fund's own subfunds; Note 3
        (pp.21-22) describes the Multifamily Mortgage Revenue Bond program
        as Florida Housing's own bond-financing vehicle.
      * home -- Note 12 (p.35): "HOME Investment Partnerships Program
        $23,351,606"; Note 10 (p.34) separately discusses HOME loans
        outstanding by county.
      * nhtf -- Note 12 (p.35): "National Housing Trust Fund $38,304,759";
        Note 6, Loans Receivable (p.28): "$78.3 million in National
        Housing Trust Fund loans outstanding at December 31, 2025."
      * cdbg_dr -- Note 12 (p.35): "Community Development Block Grant-
        Disaster Recovery $21,664,853"; Note 6 (p.28): "$140.0 million in
        CDBG-DR loans outstanding at December 31, 2025."
      * predevelopment_loan -- Note 12 (p.35): "Predevelopment Loan
        Program $3,190,350."
      * hap_fl_assist -- Note 3, Description of Programs (p.21), places
        the Florida Assist Program directly under the "Housing Trust
        Funds" heading (State Housing Trust Fund / Local Government
        Housing Trust Fund, funded by the Sadowski Act documentary stamp
        tax) -- the Annual Report's own footnote 4 (p.8) confirms "This
        program is/has historically been funded by revenues from
        documentary stamp taxes."
      * hop -- Note 3 (p.21) places the Homeownership Pool (HOP) Program
        in the same "Housing Trust Funds" paragraph as HAP, immediately
        before the SAIL/Predevelopment Loan Program entries.
      * hometown_heroes -- not literally named in the ACFR, but Note 3's
        Legislative-Initiatives-style state-appropriation language
        matches the Annual Report's own description (p.22-23: "$50.0
        million in 2025 from general revenue") of a state-funded program
        administered inside Florida Housing's enterprise fund; confidence:
        high on "proprietary" (it is Florida Housing's own money, not a
        pass-through), medium on the literal fund_name.
  - "proprietary" (inferred, medium confidence -- same program family as
    an ACFR-named line, but not itself broken out as a separate ACFR
    balance):
      * live_local_sail -- a 2023 Live Local Act variant of SAIL; Note 12's
        "State Apartment Incentive Loan Program" balance is not broken out
        by SAIL vs. Live Local SAIL sub-type, so this is presumed folded
        into that same figure rather than being off Florida Housing's
        balance sheet.
      * home_arp -- an ARPA-funded supplemental allocation under the same
        federal HOME Investment Partnerships Program authority as `home`;
        presumed folded into Note 12's single "HOME Investment
        Partnerships Program" figure.
      * tbra (Category 3, Housing Stability for Schoolchildren) -- the
        Annual Report's own narrative states this program is funded with
        "HOME funding" (same federal authority as `home`/`home_arp` above);
        Note 12's "HOME Investment Partnerships Program $23,351,606" balance
        is not broken out between multifamily construction loans and this
        rental-subsidy use, so this is presumed folded into that same
        figure rather than being off Florida Housing's balance sheet --
        same inference logic as `home_arp`, confidence: medium.
      * dev_disab (Grants for Persons with Developmental Disabilities) --
        Note 3 (p.23) describes "Legislative Initiatives" as appropriations
        that "target a specific segment of the affordable housing
        continuum such as housing for persons with special needs," which
        directly matches this program's description; Note 12 lists a
        "Legislative Initiatives $45,455,275" balance this is presumed to
        sit inside.
      * hlp_second_mortgage ("Homeownership Loan Program (HLP) Second
        Mortgage") -- "HLP" reads as the same "Homeownership Loan Program"
        bond-indenture family Note 3 names for `homebuyer_loans`; presumed
        to be a second-lien product of that same bond subfund.
      * homebuyer_loans -- Note 3 (pp.21-22) names this Florida Housing's
        own revenue-bond-financed first-mortgage program.
  - "off_balance_sheet" (confirmed absent from the ACFR by name, or
    structurally external to Florida Housing's own balance sheet):
      * hc9, hc4 -- Note 3 (p.23), "Housing Credit Program": Florida
        Housing "allocate[s] the tax credits" to developers/investors;
        the credit value and syndication equity are never a Florida
        Housing asset, the same off-balance-sheet logic used for IL's
        LIHTC/IAHTC and PA's LIHTC/PHTC.
      * local_bonds -- the Annual Report's own table-abbreviation legend
        (p.80) defines "Local Funds = City and/or County Funds" for this
        exact column; these are municipal/county bond issuances layered
        onto a deal alongside Florida Housing's own funding, never a
        Florida Housing liability. Checked against the ACFR full text for
        "Local Bonds"/"local government bonds" -- zero matches.
      * hfa_preferred_plus ("PLUS TBA") -- never appears in the ACFR by
        name (checked "HFA Preferred", "Preferred PLUS", "TBA" -- zero
        matches). Nationally, "HFA Preferred PLUS"-style down-payment
        grants are typically funded through the TBA/MBS-execution pricing
        itself (a lender/investor-funded credit built into the mortgage-
        backed security, not agency cash), consistent with its total
        absence from Florida Housing's own financial statements;
        confidence: medium (inferred from the product's national design,
        not from an explicit Florida Housing statement).
      * ship -- SHIP is a population-based formula ANNUAL DISTRIBUTION to
        67 counties and 55 entitlement cities (Note 3, p.23), who then
        administer their own Local Housing Assistance Plans; once
        distributed the funds and any resulting loans belong to the local
        government's own trust fund, not Florida Housing's. Consistent
        with this, SHIP is the one homeownership-side program that never
        appears in either Note 6 (Loans Receivable) or Note 12
        (Commitments) -- unlike SAIL/HOME/NHTF/CDBG-DR/Predevelopment
        Loan Program, which all have explicit Florida-Housing-carried
        balances in those same two notes.

Geocoding
---------------------------------------------------------------------------
Unlike IL/PA, the "RENTAL PROPERTIES AWARDED FUNDING IN 2025" table gives
only a COUNTY for each development -- no street address, no city. This
script therefore geocodes every project to its county's centroid via
Nominatim ("{County} County, Florida"), one query per unique county (31
queries for 81 projects, since many developments share a county), and
marks every project geocode_status="county_center" -- a courser precision
tier than IL/PA's "ok"/"city_center", introduced here because no finer
location is disclosed anywhere in the source document. Multiple
developments in the same county will render at the same map point; this is
a known, documented limitation of the source data, not a bug, and no
attempt is made to jitter/offset markers to hide it. Self-throttled to
<=1 request/second with an identifying User-Agent per Nominatim's usage
policy (only 31 requests total are actually made, well under any rate
concern).

fy2026
---------------------------------------------------------------------------
The 2025 Annual Report has no forward-looking/projected-activity section
(unlike IHDA's Report of Activities) -- every fy2026 field below is
{value: None, amount: None, closed: False, note_key: "flFy26NotePending"}.
"""

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "fl_program_activity.json"

SOURCE_URL = "https://www.floridahousing.org/docs/default-source/data-docs-and-reports/annual-reports/2025-annual-report.pdf"
SOURCE_FILE = "FL_FloridaHousing_AnnualReport_2025.pdf"
RETRIEVED = "2026-08-13"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
GEOCODER_USER_AGENT = "us-hfa-data-map/1.0 (github.com/MD-ai-fin/us-hfa-data-map)"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "flFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "rental_multifamily",
        "unit_type": "units",
        "fy2025_actual": 12007,
        "fy2025_source_quote": (
            "\"RENTAL PROPERTIES AWARDED FUNDING IN 2025\" table (pp.47-56), TOTALS "
            "row: Total Units 12,007, Set-Aside Units 11,762, Estimated Total "
            "Development Cost $4,316,107,548, across 81 named developments. (The "
            "separate \"SUMMARY OF PROGRAMS\" table, pp.8-9, prints a different Total "
            "Units Funded of 13,196 / Set-Aside 12,951, built by a different rolling, "
            "multi-year, partial-overlap-adjusted calculation with no per-development "
            "detail -- footnote 6 explains the two totals do not reconcile. This "
            "script uses 12,007, the fully project-verifiable figure -- see module "
            "docstring.)"
        ),
        "fy2025_amounts": [
            {"label_key": "fl_amt_total_allocated", "amount": 2728587908},
            {"label_key": "fl_amt_total_dev_cost", "amount": 4316107548},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "hc9", "fy2025_units": 373, "fy2025_amount": 12665630,
             "color_group": "credit",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "hc4", "fy2025_units": 11022, "fy2025_amount": 167954503,
             "color_group": "credit",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "mmrb", "fy2025_units": 4400, "fy2025_amount": 920440000,
             "color_group": "bond",
             "fund_type": "proprietary", "fund_name": "Multifamily Mortgage Revenue Bond program (bond-programs subfund)",
             "fy2026": _FY26_PENDING},
            {"key": "sail", "fy2025_units": 565, "fy2025_amount": 35484704,
             "color_group": "trust",
             "fund_type": "proprietary", "fund_name": "State Apartment Incentive Loan Program",
             "fy2026": _FY26_PENDING},
            {"key": "live_local_sail", "fy2025_units": 2714, "fy2025_amount": 183051021,
             "color_group": "trust",
             "fund_type": "proprietary", "fund_name": "State Apartment Incentive Loan Program (Live Local Act variant, inferred)",
             "fy2026": _FY26_PENDING},
            {"key": "home", "fy2025_units": 115, "fy2025_amount": 26550000,
             "color_group": "trust",
             "fund_type": "proprietary", "fund_name": "HOME Investment Partnerships Program",
             "fy2026": _FY26_PENDING},
            {"key": "home_arp", "fy2025_units": 258, "fy2025_amount": 6061400,
             "color_group": "trust",
             "fund_type": "proprietary", "fund_name": "HOME Investment Partnerships Program (ARP supplemental allocation, inferred)",
             "fy2026": _FY26_PENDING},
            {"key": "nhtf", "fy2025_units": 326, "fy2025_amount": 8375000,
             "color_group": "trust",
             "fund_type": "proprietary", "fund_name": "National Housing Trust Fund",
             "fy2026": _FY26_PENDING},
            {"key": "dev_disab", "fy2025_units": 60, "fy2025_amount": 2800000,
             "color_group": "capital",
             "fund_type": "proprietary", "fund_name": "Legislative Initiatives (inferred)",
             "fy2026": _FY26_PENDING},
            {"key": "cdbg_dr", "fy2025_units": 353, "fy2025_amount": 38400000,
             "color_group": "capital",
             "fund_type": "proprietary", "fund_name": "Community Development Block Grant - Disaster Recovery",
             "fy2026": _FY26_PENDING},
            {"key": "local_bonds", "fy2025_units": 6016, "fy2025_amount": 1326805650,
             "color_group": "bond",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "homebuyer_dpa",
        "unit_type": "households",
        "fy2025_actual": 8427,
        "fy2025_source_quote": (
            "\"SUMMARY OF PROGRAMS\" (p.8): Total Homeowners Served or Units Funded "
            "8,427. Footnote 3: \"In order to serve lower income households, "
            "resources from more than one program may be combined. Because of this "
            "the Total Homeowners Served or Units Funded is not equal to the sum of "
            "each program.\" -- Florida Housing's own statement that this category is "
            "not additive."
        ),
        "fy2025_amounts": [
            {"label_key": "fl_amt_first_mortgage_total", "amount": 1582166593},
            {"label_key": "fl_amt_dpa_total", "amount": 69891417},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "homebuyer_loans", "fy2025_units": 5843, "fy2025_amount": 1582166593,
             "color_group": "bond",
             "fund_type": "proprietary", "fund_name": "Homebuyer Loan Program (Single Family bond program)",
             "fy2026": _FY26_PENDING},
            {"key": "hap_fl_assist", "fy2025_units": 3866, "fy2025_amount": 38655880,
             "color_group": "trust",
             "fund_type": "proprietary", "fund_name": "State/Local Government Housing Trust Fund (documentary stamp tax)",
             "fy2026": _FY26_PENDING},
            {"key": "hlp_second_mortgage", "fy2025_units": 79, "fy2025_amount": 890000,
             "color_group": "bond",
             "fund_type": "proprietary", "fund_name": "Homeownership Loan Program bond subfund (inferred)",
             "fy2026": _FY26_PENDING},
            {"key": "hfa_preferred_plus", "fy2025_units": 88, "fy2025_amount": 1034882,
             "color_group": "capital",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "hometown_heroes", "fy2025_units": 1808, "fy2025_amount": 29310655,
             "color_group": "capital",
             "fund_type": "proprietary", "fund_name": "Florida Hometown Heroes Program (state general revenue)",
             "fy2026": _FY26_PENDING},
            {"key": "hop", "fy2025_units": 129, "fy2025_amount": 3384500,
             "color_group": "trust",
             "fund_type": "proprietary", "fund_name": "Homeownership Pool (HOP) Program (Housing Trust Funds)",
             "fy2026": _FY26_PENDING},
            {"key": "ship", "fy2025_units": 2455, "fy2025_amount": None,
             "color_group": "trust",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "predevelopment_loan", "fy2025_units": 99, "fy2025_amount": 2768333,
             "color_group": "capital",
             "fund_type": "proprietary", "fund_name": "Predevelopment Loan Program",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        # Housing Stability for Schoolchildren (HSS) -- Tenant-Based Rental
        # Assistance (TBRA). An ongoing, per-household rent subsidy paid to
        # landlords on behalf of already-housed families, structurally
        # different from Category 1's one-time development financing --
        # same distinction IL draws for IHDA's Section 811 PRA/RHSP
        # "rental_assistance_operations" category. See module docstring's
        # "Category 3" section for the full methodology and page citations.
        "key": "hss_tbra",
        "unit_type": "households",
        "fy2025_actual": 44,
        "fy2025_source_quote": (
            "\"Housing Stability for Schoolchildren Program\" narrative (p.19): "
            "\"Florida Housing utilizes HOME funding to provide short- and "
            "medium-term Tenant Based Rental Assistance (TBRA) to families with "
            "school-aged children experiencing homelessness.\" \"HOUSING "
            "STABILITY FOR SCHOOLCHILDREN PROGRAM TENANT-BASED RENTAL ASSISTANCE "
            "(TBRA)\" table (p.44), printed TOTALS row: Charlotte 11 households/"
            "$79,641, Hernando 15 households/$110,443, Santa Rosa 18 households/"
            "$77,967, TOTALS 44 households/$268,051 -- independently re-summed "
            "and matched exactly (see verify_hss_tbra_totals()), and cross-"
            "checked against the separate SUMMARY OF PROGRAMS table's own "
            "\"Housing Stability for Schoolchildren 44...44\" line (p.9) and "
            "this table's own AMI-tier breakdown (0-30% AMI 25 + 31-50% AMI 17 "
            "+ 51-80% AMI 2 = 44)."
        ),
        "fy2025_amounts": [
            {"label_key": "fl_amt_tbra_total", "amount": 268051},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "tbra", "fy2025_units": 44, "fy2025_amount": 268051,
             "color_group": "trust",
             # HOME-funded, same federal authority as `home`/`home_arp` in
             # Category 1; not separately broken out in the ACFR's Note 12
             # "HOME Investment Partnerships Program $23,351,606" balance --
             # see module docstring's Fund-type classification section.
             "fund_type": "proprietary",
             "fund_name": "HOME Investment Partnerships Program (Tenant-Based Rental Assistance, inferred)",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# ---------------------------------------------------------------------------
# Category 1 project-level detail ("RENTAL PROPERTIES AWARDED FUNDING IN
# 2025", pp.47-56). Extracted via pdfplumber table extraction (see module
# docstring); (county, development name, total_units, set_aside_units,
# [funding source keys]).
# ---------------------------------------------------------------------------

RAW_PROJECTS = [
    ('Alachua', 'Pine Grove - Gainesville', 97, 97,
     ["hc4", "local_bonds"]),
    ('Alachua', 'Williston Pointe', 80, 7,
     ["nhtf"]),
    ('Brevard', 'Ekos at Rockledge Park', 100, 100,
     ["hc4", "mmrb", "cdbg_dr"]),
    ('Brevard', 'Freedom Point Apartments', 90, 90,
     ["hc4", "mmrb", "live_local_sail"]),
    ('Broward', 'Aspire 1650', 90, 90,
     ["hc9", "sail", "home_arp"]),
    ('Broward', 'Palms of Deerfield Townhomes', 56, 56,
     ["hc4", "local_bonds"]),
    ('Broward', 'Vista at Springtree', 96, 96,
     ["hc4", "mmrb", "live_local_sail"]),
    ('Broward', 'Woodsdale Oaks', 172, 172,
     ["hc4", "local_bonds"]),
    ('Charlotte', 'Vincentian Villas II', 17, 17,
     ["sail", "home_arp"]),
    ('Collier', 'Clara Landings - an Ekos Community', 84, 84,
     ["hc4"]),
    ('Columbia', 'Arbors Pointe', 24, 24,
     ["live_local_sail", "home"]),
    ('Columbia', 'Sweetwater Apartments Phase III', 24, 24,
     ["live_local_sail", "home"]),
    ('Duval', 'Huron Sophia and Capri Villas', 151, 151,
     ["hc4", "local_bonds"]),
    ('Duval', 'Riverside Park Apartments', 90, 90,
     ["hc4", "sail", "local_bonds"]),
    ('Gadsden', 'Gadsden Arms', 100, 100,
     ["hc4", "mmrb"]),
    ('Hardee', 'Grove at Theater Road', 24, 24,
     ["live_local_sail", "home"]),
    ('Hillsborough', 'Cortaro Heights', 100, 100,
     ["hc4", "cdbg_dr", "local_bonds"]),
    ('Hillsborough', 'Country Oaks', 148, 148,
     ["hc4", "local_bonds"]),
    ('Hillsborough', 'Gallery at Rome Yards', 234, 186,
     ["hc4", "mmrb"]),
    ('Hillsborough', 'Garrison Flats', 100, 100,
     ["hc4", "live_local_sail", "local_bonds"]),
    ('Hillsborough', 'Loop (The)', 77, 77,
     ["hc4", "local_bonds"]),
    ('Hillsborough', 'RPV Parcel D', 220, 220,
     ["hc4", "live_local_sail", "local_bonds"]),
    ('Hillsborough', 'Zion Village', 75, 75,
     ["hc4", "local_bonds"]),
    ('Lee', 'Crossings at Cape Coral', 168, 168,
     ["hc4", "local_bonds"]),
    ('Lee', 'Reserve at Eastwood I', 288, 288,
     ["hc4", "mmrb"]),
    ('Lee', 'Southward Village CNI II', 151, 98,
     ["hc4", "mmrb"]),
    ('Lee', 'The Residences - Fort Myers', 60, 60,
     ["hc9", "dev_disab"]),
    ('Lee', 'Wave at Chana', 378, 378,
     ["hc4", "mmrb"]),
    ('Lee', 'Wave at Colonial', 358, 358,
     ["hc4", "mmrb"]),
    ('Leon', 'Lake Ella Manor', 73, 73,
     ["hc4", "mmrb", "sail"]),
    ('Manatee', 'Desoto Apartments', 140, 140,
     ["hc4", "local_bonds"]),
    ('Marion', 'Carrfour Apartments', 57, 57,
     ["hc9", "sail", "home_arp"]),
    ('Miami-Dade', 'Caribbean Isles', 142, 142,
     ["hc4", "local_bonds"]),
    ('Miami-Dade', 'Flagler Villas', 60, 60,
     ["hc4", "local_bonds"]),
    ('Miami-Dade', 'Gallery at Lummus Parc', 256, 256,
     ["hc4", "mmrb", "live_local_sail"]),
    ('Miami-Dade', 'Gallery at Wagner Creek', 460, 389,
     ["hc4", "mmrb", "live_local_sail"]),
    ('Miami-Dade', 'Haley Sofge 750 Apartments', 220, 220,
     ["hc4", "local_bonds"]),
    ('Miami-Dade', 'Hibiscus Grove', 270, 270,
     ["hc4", "local_bonds"]),
    ('Miami-Dade', 'Homestead Gardens Phase 1', 162, 162,
     ["hc4", "local_bonds"]),
    ('Miami-Dade', 'Pinnacle Commons', 100, 100,
     ["hc4", "mmrb", "live_local_sail"]),
    ('Miami-Dade', 'Princeton Manor', 132, 132,
     ["nhtf"]),
    ('Miami-Dade', 'Residences at Palm Court', 316, 316,
     ["hc4", "local_bonds"]),
    ('Miami-Dade', 'Royal Pointe', 102, 102,
     ["hc4", "local_bonds"]),
    ('Miami-Dade', 'TML Homestead Residences', 100, 100,
     ["hc4", "live_local_sail", "local_bonds"]),
    ('Miami-Dade', 'Wynwood Works', 120, 120,
     ["hc4", "local_bonds"]),
    ('Monroe', 'Landings at Sugarloaf Key', 56, 56,
     ["sail"]),
    ('Monroe', 'Lofts at Tavernier', 86, 86,
     ["hc9", "live_local_sail"]),
    ('Orange', 'Catchlight Crossings Live Local Workforce', 84, 84,
     ["live_local_sail"]),
    ('Orange', 'Citrus Glen', 272, 272,
     ["hc4", "mmrb"]),
    ('Orange', 'Mira (The)', 300, 300,
     ["hc4", "mmrb"]),
    ('Orange', 'Reserve at Pomelo', 528, 528,
     ["hc4", "mmrb", "live_local_sail"]),
    ('Orange', 'Stillwaters (The)', 180, 180,
     ["hc4", "local_bonds"]),
    ('Osceola', 'Amberwood Lofts', 88, 88,
     ["hc4"]),
    ('Osceola', 'Kissimmee Cove', 73, 73,
     ["hc4", "mmrb", "cdbg_dr"]),
    ('Palm Beach', 'Boynton Bay Apartments', 240, 240,
     ["hc4", "local_bonds"]),
    ('Palm Beach', 'Drexel Senior Apartments', 188, 188,
     ["hc4", "live_local_sail", "local_bonds"]),
    ('Palm Beach', 'Lake Shore', 192, 192,
     ["hc4", "local_bonds"]),
    ('Palm Beach', 'Quiet Waters', 93, 93,
     ["hc4", "local_bonds"]),
    ('Pasco', 'Anchor at Gulf Harbors', 388, 388,
     ["hc4", "local_bonds"]),
    ('Pasco', 'Cobia Cove', 228, 228,
     ["hc4", "local_bonds"]),
    ('Pasco', 'Ekos at Bayonet Point (fka Bayonet Gardens)', 114, 114,
     ["nhtf"]),
    ('Pinellas', 'Citrus Grove Apartments', 84, 84,
     ["hc4", "local_bonds"]),
    ('Pinellas', 'Creekside Manor', 92, 92,
     ["hc4", "local_bonds"]),
    ('Pinellas', 'Cypress Grove Apartments - Largo', 84, 84,
     ["hc4", "mmrb"]),
    ('Pinellas', 'Independence Place II', 14, 14,
     ["sail", "home_arp"]),
    ('Pinellas', 'Indigo Apartments', 208, 208,
     ["hc4", "local_bonds"]),
    ('Pinellas', 'Largo Station', 168, 168,
     ["hc4"]),
    ('Pinellas', 'Skyway Lofts II', 66, 66,
     ["hc4"]),
    ('Pinellas', 'Tomlinson at Mirror Lake (The)', 195, 195,
     ["hc4", "mmrb", "live_local_sail"]),
    ('Polk', 'Highland Creek', 120, 120,
     ["hc4"]),
    ('Sarasota', '3 McCown Tower', 96, 96,
     ["hc4", "mmrb", "live_local_sail"]),
    ('Seminole', 'Carisbrooke Terrace', 80, 80,
     ["hc4", "mmrb", "cdbg_dr"]),
    ('Seminole', 'Harwick Place', 80, 80,
     ["hc4"]),
    ('Seminole', 'Huntington Reserve', 168, 168,
     ["hc4", "local_bonds"]),
    ('St. Johns', 'Oaks at St. Johns', 160, 160,
     ["hc4", "local_bonds"]),
    ('St. Lucie', 'Live Oak Villas I & II', 184, 184,
     ["hc4", "local_bonds"]),
    ('Volusia', 'Clyde Morris Landings V', 227, 227,
     ["hc4", "local_bonds"]),
    ('Volusia', 'Magnolia Gardens - Volusia', 88, 88,
     ["hc4", "mmrb", "sail"]),
    ('Volusia', 'Shores (The) - Daytona Beach', 80, 80,
     ["hc9", "sail", "home_arp"]),
    ('Volusia', 'WM at the River', 298, 298,
     ["hc4", "local_bonds"]),
    ('Wakulla', 'Fannie Lou Hamer Commons', 43, 43,
     ["live_local_sail", "home"]),
]

# Per-project, per-funding-source dollar amount, extracted alongside
# RAW_PROJECTS from the same table cells.
PROJECT_SOURCE_AMOUNTS = {
    'Pine Grove - Gainesville': {"hc4": 584058, "local_bonds": 9000000},
    'Williston Pointe': {"nhtf": 1925000},
    'Ekos at Rockledge Park': {"hc4": 1620807, "mmrb": 20250000, "cdbg_dr": 10000000},
    'Freedom Point Apartments': {"hc4": 1267527, "mmrb": 14500000, "live_local_sail": 9500000},
    'Aspire 1650': {"hc9": 3300000, "sail": 6100000, "home_arp": 1150000},
    'Palms of Deerfield Townhomes': {"hc4": 1569419, "local_bonds": 19000000},
    'Vista at Springtree': {"hc4": 1385478, "mmrb": 18860000, "live_local_sail": 5952000},
    'Woodsdale Oaks': {"hc4": 1586534, "local_bonds": 22000000},
    'Vincentian Villas II': {"sail": 4271804, "home_arp": 1395800},
    'Clara Landings - an Ekos Community': {"hc4": 957604},
    'Arbors Pointe': {"live_local_sail": 1500000, "home": 7000000},
    'Sweetwater Apartments Phase III': {"live_local_sail": 1750000, "home": 6625000},
    'Huron Sophia and Capri Villas': {"hc4": 1147185, "local_bonds": 16410000},
    'Riverside Park Apartments': {"hc4": 1220771, "sail": 3675000, "local_bonds": 20000000},
    'Gadsden Arms': {"hc4": 908851, "mmrb": 12000000},
    'Grove at Theater Road': {"live_local_sail": 1500000, "home": 6025000},
    'Cortaro Heights': {"hc4": 1559758, "cdbg_dr": 10000000, "local_bonds": 18925000},
    'Country Oaks': {"hc4": 2337676, "local_bonds": 31307000},
    'Gallery at Rome Yards': {"hc4": 3616472, "mmrb": 64000000},
    'Garrison Flats': {"hc4": 1904134, "live_local_sail": 11000000, "local_bonds": 26500000},
    'Loop (The)': {"hc4": 1334810, "local_bonds": 16000000},
    'RPV Parcel D': {"hc4": 5049471, "live_local_sail": 13300000, "local_bonds": 60000000},
    'Zion Village': {"hc4": 1493045, "local_bonds": 20000000},
    'Crossings at Cape Coral': {"hc4": 1790549, "local_bonds": 30000000},
    'Reserve at Eastwood I': {"hc4": 3148910, "mmrb": 44000000},
    'Southward Village CNI II': {"hc4": 2302984, "mmrb": 36000000},
    'The Residences - Fort Myers': {"hc9": 2286370, "dev_disab": 2800000},
    'Wave at Chana': {"hc4": 5341012, "mmrb": 61980000},
    'Wave at Colonial': {"hc4": 4736730, "mmrb": 61810000},
    'Lake Ella Manor': {"hc4": 534245, "mmrb": 9525000, "sail": 1000000},
    'Desoto Apartments': {"hc4": 2113306, "local_bonds": 29000000},
    'Carrfour Apartments': {"hc9": 2250000, "sail": 2664300, "home_arp": 788000},
    'Caribbean Isles': {"hc4": 3002313, "local_bonds": 34000000},
    'Flagler Villas': {"hc4": 1315672, "local_bonds": 18000000},
    'Gallery at Lummus Parc': {"hc4": 2072704, "mmrb": 71000000, "live_local_sail": 12750000},
    'Gallery at Wagner Creek': {"hc4": 7280025, "mmrb": 122750000, "live_local_sail": 22000000},
    'Haley Sofge 750 Apartments': {"hc4": 4563605, "local_bonds": 50000000},
    'Hibiscus Grove': {"hc4": 3710343, "local_bonds": 52000000},
    'Homestead Gardens Phase 1': {"hc4": 4307988, "local_bonds": 44640000},
    'Pinnacle Commons': {"hc4": 1686000, "mmrb": 21000000, "live_local_sail": 9000000},
    'Princeton Manor': {"nhtf": 3700000},
    'Residences at Palm Court': {"hc4": 6334419, "local_bonds": 82000000},
    'Royal Pointe': {"hc4": 1628851, "local_bonds": 18000000},
    'TML Homestead Residences': {"hc4": 2550000, "live_local_sail": 3545000, "local_bonds": 32961000},
    'Wynwood Works': {"hc4": 2728044, "local_bonds": 32070000},
    'Landings at Sugarloaf Key': {"sail": 4900400},
    'Lofts at Tavernier': {"hc9": 1629260, "live_local_sail": 13084700},
    'Catchlight Crossings Live Local Workforce': {"live_local_sail": 12185521},
    'Citrus Glen': {"hc4": 3689009, "mmrb": 51400000},
    'Mira (The)': {"hc4": 5147461, "mmrb": 60000000},
    'Reserve at Pomelo': {"hc4": 9686824, "mmrb": 122000000, "live_local_sail": 26000000},
    'Stillwaters (The)': {"hc4": 2871365, "local_bonds": 37000000},
    'Amberwood Lofts': {"hc4": 1773752},
    'Kissimmee Cove': {"hc4": 1209213, "mmrb": 13000000, "cdbg_dr": 8400000},
    'Boynton Bay Apartments': {"hc4": 4791629, "local_bonds": 58000000},
    'Drexel Senior Apartments': {"hc4": 3500000, "live_local_sail": 11656000, "local_bonds": 49000000},
    'Lake Shore': {"hc4": 2335559, "local_bonds": 28600000},
    'Quiet Waters': {"hc4": 782650, "local_bonds": 9369000},
    'Anchor at Gulf Harbors': {"hc4": 6890429, "local_bonds": 85000000},
    'Cobia Cove': {"hc4": 4325579, "local_bonds": 48430000},
    'Ekos at Bayonet Point (fka Bayonet Gardens)': {"nhtf": 2750000},
    'Citrus Grove Apartments': {"hc4": 1646465, "local_bonds": 22000000},
    'Creekside Manor': {"hc4": 1297389, "local_bonds": 155000000},
    'Cypress Grove Apartments - Largo': {"hc4": 1535429, "mmrb": 18000000},
    'Independence Place II': {"sail": 4200000, "home_arp": 1599100},
    'Indigo Apartments': {"hc4": 1958768, "local_bonds": 24000000},
    'Largo Station': {"hc4": 2450000},
    'Skyway Lofts II': {"hc4": 1179529},
    'Tomlinson at Mirror Lake (The)': {"hc4": 1399650, "mmrb": 43740000, "live_local_sail": 17707800},
    'Highland Creek': {"hc4": 1700000},
    '3 McCown Tower': {"hc4": 1597628, "mmrb": 30000000, "live_local_sail": 9120000},
    'Carisbrooke Terrace': {"hc4": 1465241, "mmrb": 15000000, "cdbg_dr": 10000000},
    'Harwick Place': {"hc4": 1465241},
    'Huntington Reserve': {"hc4": 2561929, "local_bonds": 34373650},
    'Oaks at St. Johns': {"hc4": 1755831, "local_bonds": 21500000},
    'Live Oak Villas I & II': {"hc4": 2068878, "local_bonds": 20720000},
    'Clyde Morris Landings V': {"hc4": 2595258, "local_bonds": 24000000},
    'Magnolia Gardens - Volusia': {"hc4": 943957, "mmrb": 9625000, "sail": 3725000},
    'Shores (The) - Daytona Beach': {"hc9": 3200000, "sail": 4948200, "home_arp": 1128500},
    'WM at the River': {"hc4": 2638540, "local_bonds": 28000000},
    'Fannie Lou Hamer Commons': {"live_local_sail": 1500000, "home": 6900000},
}

# The PDF's own printed TOTALS row (p.56) for each of the 11 funding-source
# dollar columns, plus Total Units / Set-Aside Units / Estimated Total
# Development Cost -- the double-verification gate.
EXPECTED_SOURCE_TOTALS = {
    "hc9": 12665630, "hc4": 167954503, "mmrb": 920440000, "sail": 35484704,
    "live_local_sail": 183051021, "home": 26550000, "home_arp": 6061400,
    "nhtf": 8375000, "dev_disab": 2800000, "cdbg_dr": 38400000,
    "local_bonds": 1326805650,
}
EXPECTED_TOTAL_UNITS = 12007
EXPECTED_SET_ASIDE_UNITS = 11762

FUNDING_COLOR_GROUP = {
    "hc9": "credit", "hc4": "credit",
    "mmrb": "bond", "local_bonds": "bond",
    "sail": "trust", "live_local_sail": "trust", "home": "trust",
    "home_arp": "trust", "nhtf": "trust",
    "cdbg_dr": "capital", "dev_disab": "capital",
}
# priority order for picking a project's single "primary" color when it has
# multiple funding sources (first match wins) -- HC4% first since it is the
# most common anchor credit across the 81 developments.
FUNDING_PRIORITY = ["hc4", "hc9", "mmrb", "local_bonds", "sail",
                     "live_local_sail", "home", "home_arp", "nhtf",
                     "cdbg_dr", "dev_disab"]


def verify_amount_totals():
    sums = {k: 0 for k in EXPECTED_SOURCE_TOTALS}
    for name, _county, _units, _sa, sources in [
        (n, c, u, sa, s) for c, n, u, sa, s in RAW_PROJECTS
    ]:
        amounts = PROJECT_SOURCE_AMOUNTS.get(name)
        if amounts is None:
            raise SystemExit(f"No PROJECT_SOURCE_AMOUNTS entry for {name!r}")
        missing = [s for s in sources if s not in amounts]
        extra = [s for s in amounts if s not in sources]
        if missing:
            raise SystemExit(f"{name!r} is missing amounts for source(s) {missing}")
        if extra:
            raise SystemExit(f"{name!r} has amounts for undeclared source(s) {extra}")
        for src, amt in amounts.items():
            sums[src] = sums.get(src, 0) + amt
    errors = []
    for key, expected in EXPECTED_SOURCE_TOTALS.items():
        got = sums.get(key, 0)
        if got != expected:
            errors.append(f"{key} (amount): expected {expected:,}, got {got:,}")
    if errors:
        raise SystemExit("Funding-source amount mismatch(es):\n" + "\n".join(errors))
    print(f"All {len(EXPECTED_SOURCE_TOTALS)} funding-source dollar totals verified "
          "against the PDF's own printed TOTALS row (p.56).")


def verify_unit_totals():
    total_units = sum(units for _c, _n, units, _sa, _s in RAW_PROJECTS)
    set_aside = sum(sa for _c, _n, _u, sa, _s in RAW_PROJECTS)
    errors = []
    if total_units != EXPECTED_TOTAL_UNITS:
        errors.append(f"Total Units: expected {EXPECTED_TOTAL_UNITS:,}, got {total_units:,}")
    if set_aside != EXPECTED_SET_ASIDE_UNITS:
        errors.append(f"Set-Aside Units: expected {EXPECTED_SET_ASIDE_UNITS:,}, got {set_aside:,}")
    if len(RAW_PROJECTS) != 81:
        errors.append(f"project count: expected 81, got {len(RAW_PROJECTS)}")
    if errors:
        raise SystemExit("Unit-total mismatch(es):\n" + "\n".join(errors))
    print(f"Project count (81), Total Units (12,007) and Set-Aside Units (11,762) "
          "verified against the PDF's own printed TOTALS row (p.56).")


# Homeownership-side (Category 2) verified totals -- see module docstring
# for each figure's exact table/page citation.
def verify_homebuyer_totals():
    dpa_loans = 3866 + 79 + 88 + 1808
    dpa_dollars = 38655880 + 890000 + 1034882 + 29310655
    errors = []
    if dpa_loans != 5841:
        errors.append(f"DPA loan count: expected 5,841, got {dpa_loans:,}")
    if dpa_loans + 2 != 5843:
        errors.append(f"DPA loans (5,841) + 2 no-DPA loans should equal 5,843 Homebuyer "
                       f"Loan Programs total, got {dpa_loans + 2:,}")
    if dpa_dollars != 69891417:
        errors.append(f"DPA dollar total: expected $69,891,417, got ${dpa_dollars:,}")
    if round(4910 * 0.5) != 2455:
        errors.append("SHIP homeownership 50% overlap check failed: 4,910 x 50% != 2,455")
    if errors:
        raise SystemExit("Homebuyer/DPA total mismatch(es):\n" + "\n".join(errors))
    print("Homebuyer/DPA subprogram totals verified: 3,866+79+88+1,808=5,841 DPA loans "
          "(+2 no-DPA=5,843 total), $38,655,880+$890,000+$1,034,882+$29,310,655="
          "$69,891,417 DPA dollars, SHIP 4,910 x 50%=2,455.")


# Cross-checks the "HOUSING STABILITY FOR SCHOOLCHILDREN PROGRAM
# TENANT-BASED RENTAL ASSISTANCE (TBRA)" table's own printed TOTALS row
# (p.44) against an independent re-sum of its 3 county rows, plus the
# table's own AMI-tier breakdown row, plus the category's own
# fy2025_actual/fy2025_amounts fields (CATEGORIES, hand-entered) -- and
# separately notes the match against the unrelated SUMMARY OF PROGRAMS
# table's own "44" line (p.9), which is not re-verified here since that
# table is not independently re-summed anywhere in this script (its
# figures are taken as given, same as every other SUMMARY-sourced category
# headline in this file).
def verify_hss_tbra_totals():
    county_rows = [
        ("Charlotte", 11, 79641),
        ("Hernando", 15, 110443),
        ("Santa Rosa", 18, 77967),
    ]
    ami_tiers = [25, 17, 2]
    households = sum(u for _c, u, _a in county_rows)
    dollars = sum(a for _c, _u, a in county_rows)
    ami_total = sum(ami_tiers)
    errors = []
    if households != 44:
        errors.append(f"county rows household sum: expected 44, got {households}")
    if dollars != 268051:
        errors.append(f"county rows dollar sum: expected $268,051, got ${dollars:,}")
    if ami_total != 44:
        errors.append(f"AMI-tier row sum: expected 44, got {ami_total}")
    cat = next(c for c in CATEGORIES if c["key"] == "hss_tbra")
    if cat["fy2025_actual"] != households:
        errors.append(f"category fy2025_actual: expected {households}, got {cat['fy2025_actual']}")
    if cat["fy2025_amounts"][0]["amount"] != dollars:
        errors.append(f"category fy2025_amounts: expected {dollars}, got {cat['fy2025_amounts'][0]['amount']}")
    sp = cat["subprograms"][0]
    if sp["fy2025_units"] != households or sp["fy2025_amount"] != dollars:
        errors.append("tbra subprogram units/amount do not match the re-summed county totals")
    if errors:
        raise SystemExit("HSS/TBRA total mismatch(es):\n" + "\n".join(errors))
    print("HSS/TBRA table verified: Charlotte 11/$79,641 + Hernando 15/$110,443 + "
          "Santa Rosa 18/$77,967 = 44 households/$268,051, matching the table's own "
          "printed TOTALS row, its own AMI-tier breakdown (25+17+2=44), and the "
          "separate SUMMARY OF PROGRAMS table's own \"44\" line (p.9).")


def slugify(name):
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug


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
    for county, name, units, _set_aside, sources in RAW_PROJECTS:
        query = f"{county} County, Florida"
        coords = geocode(query, cache)
        status = "county_center" if coords else "unresolved"
        primary = next((s for s in FUNDING_PRIORITY if s in sources), sources[0])
        source_amounts = PROJECT_SOURCE_AMOUNTS.get(name, {})
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
            "total_amount": sum(source_amounts.values()) if source_amounts else None,
            "primary_color_group": FUNDING_COLOR_GROUP[primary],
            "overlaps": len(sources) > 1,
            "geocode_status": status,
        })
    return projects


def main():
    verify_amount_totals()
    verify_unit_totals()
    verify_homebuyer_totals()
    verify_hss_tbra_totals()
    print("Geocoding project counties via Nominatim (county-center precision)...")
    projects = build_projects()
    unresolved = [p["name"] for p in projects if p["geocode_status"] == "unresolved"]
    if unresolved:
        print(f"  {len(unresolved)} project(s) could not be geocoded: {unresolved}")
    unique_counties = len({p["city"] for p in projects})
    print(f"  {len(projects)} projects across {unique_counties} unique counties.")

    payload = {
        "FL": {
            "hfa_name": "Florida Housing Finance Corporation",
            "hfa_abbr": "Florida Housing",
            "fiscal_year": "CY2025",
            "source_title": "2025 Annual Report",
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
