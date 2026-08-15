"""
Builds docs/ia_program_activity.json from the Iowa Finance Authority's (IFA)
FY2025 Performance Report (statewide KPI headlines) plus its two separately
published FY2025 Housing Tax Credit award lists (project-level detail), and
IFA's own FY2025 audited financial statements (used ONLY for GASB fund-type
classification). IFA's fiscal year 2025 = July 1, 2024 - June 30, 2025.

IMPORTANT domain note: IFA merged into a new umbrella agency and its web
presence moved from iowafinance.com to opportunityiowa.gov (old domain
301-redirects); every URL below is the new opportunityiowa.gov domain.

Sources
---------------------------------------------------------------------------
1. "IFA FY2025 Performance Report" (an 8-page KPI/goals report -- 41
   performance measures with FY25 targets vs. actuals, plus a 2-page
   executive-summary "FY25 Major Accomplishments" narrative):
     https://opportunityiowa.gov/media/7574/download?inline
   Entry page (if the direct link ever breaks):
     https://opportunityiowa.gov/about/iowa-finance-authority/financial-reports
   Local copy: FY2025/program_activity/pdf/IA_IFA_PerformanceReport_FY2025.pdf
2. "2025 9% Federal Housing Tax Credit with HOME & NHTF Award Listing"
   (dated June 25, 2026, a single-page project-by-project award table):
     https://opportunityiowa.gov/media/6512/download?inline
   Local copy: FY2025/program_activity/pdf/IA_IFA_9pctHTC_AwardList_2025.pdf
3. "2025 4% Federal Housing Tax Credit (LIHTC) Awards" (dated June 25, 2026,
   an .xlsx workbook, one row per project):
     https://opportunityiowa.gov/media/7457/download?inline
   Local copy: FY2025/program_activity/pdf/IA_IFA_4pctHTC_AwardList_2025.xlsx
   Entry page for both award lists: https://opportunityiowa.gov/housing/
   rental-programs/programs-developers-communities-and-property-owners/
   housing-tax-credit-program/resources
4. IFA's own FY2025 Annual Comprehensive Financial Report (used ONLY for
   fund-type classification, see below): FY2025/txt/IA_IFA_FY2025_ACFR.txt

IMPORTANT data-provenance note on the checked-in ACFR text
---------------------------------------------------------------------------
FY2025/txt/IA_IFA_FY2025_ACFR.txt WAS verified (before use) to actually be
IFA's own financial statements, not a mismatched report -- a recurring bug
class this project's other state build scripts have had to catch. The
file's own title page reads "IOWA FINANCE AUTHORITY (A Component Unit of
the State of Iowa) ANNUAL COMPREHENSIVE FINANCIAL REPORT FOR FISCAL YEAR
ENDED JUNE 30, 2025", the Transmittal Letter is addressed "TO THE CITIZENS,
GOVERNOR, AND BOARD OF DIRECTORS" of the Authority and is signed off by
"Debi Durham, Director", and MD&A / Note 1 both describe "The Authority was
created in 1975 under Chapter 16 of the Code of Iowa" -- i.e. this is the
real, correctly-scoped IFA source, not another agency's or another state's
report. Printed page numbers cited below (e.g. "p.10", "p.70") refer to
this document's own internal pagination, visible as running page-footer
numbers in the .txt dump.

Executive-summary headline cross-checks
---------------------------------------------------------------------------
Two of this file's three category headlines are independently confirmed by
BOTH the Performance Report AND the ACFR's own Transmittal Letter narrative
(different documents, same underlying fiscal year, written by the same
agency at different times) -- a stronger-than-usual provenance signal:
  - Homeownership: Performance Report p.5, "FY25 Major Accomplishments" --
    "2,908 Iowans purchased a home through an IFA homeownership program in
    FY25, a 9% increase over the previous year and the second most
    homebuyers assisted in a single year in IFA's 50-year history." The
    Performance Report's own KPI table (p.6) separately confirms this as
    "Number of Homebuyers assisted with mortgages: Target 2,200, Actual
    2,908, Yes." The ACFR's Transmittal Letter (p.2) independently states
    "The single-family program assisted 2,908 home buyers by funding
    nearly $509 million in mortgage-backed securities during fiscal year
    2025. Approximately 94% of these home buyers also benefitted from the
    Authority's down payment and closing cost assistance" -- both the
    2,908 figure and the ~94% DPA-attach-rate claim recur verbatim across
    the two documents. The Performance Report's KPI table separately gives
    "Number of Iowans assisted with down payment: Target 1,870, Actual
    2,722, Yes" -- 2,722 / 2,908 = 93.6%, consistent with the "~94%"
    narrative claim. No dollar figure is disclosed anywhere for the DPA
    subprogram specifically (only the combined $509M mortgage-backed-
    securities total), so dpa's fy2025_amount is None, not estimated.
  - LIHTC: Performance Report p.5 -- "889 Iowa families will have access
    to affordable housing through more than $15.5 million in federal 9%
    and 4% housing tax credits," confirmed by the KPI table (p.5): "Number
    of units awarded tax credits: Target 1,000, Actual 889, No" and
    "Percent of available tax credits awarded: Target 100%, Actual 99%,
    No." The ACFR's Transmittal Letter (p.2) gives a THIRD, materially
    different figure for what appears to be the same underlying award
    activity: "The Authority allocated a total of $144 million in Federal
    Housing Tax Credits in fiscal year 2025 which will create or preserve
    816 safe and affordable homes for Iowa families. These awards
    leveraged an additional $102 million in local contributions." Neither
    816 nor $144M is used anywhere in this file's CATEGORIES/subprograms --
    $144M is almost certainly the full 10-year LIHTC credit stream (a
    different unit of account than the $15.5M figure, which itself doesn't
    exactly match this script's own $16,385,570 two-round credit resum
    either, see below) and 816 does not match any other total this script
    can independently verify. This third figure is recorded here, in this
    docstring, purely for transparency -- it is NOT reconciled or forced to
    match 889/907, following this project's "never fabricate a
    reconciliation" rule.

Category-level methodology and double-verification gates
---------------------------------------------------------------------------
1. Homeownership: fy2025_actual=2,908 is IFA's own printed headline (see
   above), used verbatim -- there is no county-by-county or per-loan detail
   published for this program anywhere IFA discloses (unlike PA's
   Homeownership table or MI's Single-Family Homeownership Mortgages
   table), so RAW_PROJECTS contains no homeownership entries at all, only
   LIHTC multifamily developments -- per the task briefing's own
   instruction, this category "stays at the KPI level." additive=False:
   the mortgage_loans (2,908) and dpa (2,722) subprograms are NOT a clean
   partition -- dpa rides on top of a SUBSET of the 2,908 purchase loans
   (~94% of them), the same overlapping-subset relationship PA's
   K-FIT/Advantage/PENNVEST have with their own purchase-loan total.

2. LIHTC (RAW_PROJECTS, both award lists): each award list prints its OWN
   TOTAL row, used verbatim and independently re-verified against this
   script's own pdfplumber-extracted table cells (verify_9pct_totals(),
   verify_4pct_totals()):
     - 2025 9% round: TOTAL row "10 [projects] / 286 LI Units / 0 Market
       Rate / 286 Total Units / $8,320,433 Credit / $2,664,999 [State]
       HOME / $1,000,000 NHTF". Of the 10 printed rows, ONE ("25-15 Encore
       Senior Living") is marked "WITHDREW 2026" with 0 units and $0 of
       every dollar column -- excluded from RAW_PROJECTS (no housing was
       ever built) but its zeros don't change any sum. A SECOND row
       ("24-01 Townhall Food Hall and Apartments") is a "2024 Innovation
       Set-Aside" "Supplemental Award" of $94,037 to a project that was
       already awarded (and its units already counted) in the PRIOR fiscal
       year's list -- it carries no LI-Units/Total-Units figure of its own
       in this list. This script's own resum of the remaining 8 fully-
       specified rows gives exactly 286 LI/Total Units and $8,226,396 of
       Credit Award; $8,226,396 + the unmapped $94,037 supplemental =
       $8,320,433, reproducing the TOTAL row's own Credit Award figure
       EXACTLY. RAW_PROJECTS therefore contains 8 developments (not 10):
       24-01 is excluded (no unit count to attribute a marker to, and its
       units were already on the map via a prior fiscal year's build
       script, not this one) and 25-15 is excluded (withdrawn, never
       built). This is the same "officially-reported total includes a
       dollar amount this script cannot attribute to a specific mapped
       development" pattern MI documents for its own Multifamily Direct
       Lending subprogram.
     - 2025 4% round: TOTAL row "4 Projects / 621 LI Units / 0 Market Rate
       / 621 Total Units / $58,902,467 Tax-Exempt Bond Amount / $8,065,137
       Credit Award" -- the workbook's own TOTAL label ("4 Projects")
       already excludes the 5th row, "25-26 South Market Apartments",
       which is marked "WITHDRAWN" with 0 units/0 credit and a text value
       ("WITHDRAWN") in place of a Tax-Exempt Bond Amount. RAW_PROJECTS
       therefore contains exactly the 4 named, funded developments; this
       script's own resum of all four columns (LI Units, Credit Award,
       Tax-Exempt Bond Amount) matches the TOTAL row EXACTLY on every axis
       (verify_4pct_totals()).
   Category headline (fy2025_actual=889, official Performance Report
   figure) vs. RAW_PROJECTS (286+621=907 units, per the task briefing's own
   flagged ~2% gap): this script does NOT force these to reconcile. 907 is
   the sum of two independently-printed, internally-consistent TOTAL rows;
   889 is IFA's own separately-published KPI-table figure. The ~2% gap
   (18 units) most plausibly reflects the withdrawn/supplemental rows
   above being counted differently between the KPI report (compiled
   earlier in the production cycle) and the two June 25, 2026 award-list
   documents (compiled later, after "25-15 Encore Senior Living"
   withdrew and "25-26 South Market Apartments" withdrew) -- but this is
   informed speculation, not a confirmed explanation, so it is not
   asserted as fact. CATEGORIES uses 889 (the Performance Report's own
   official KPI headline) for fy2025_actual; RAW_PROJECTS and the
   subprogram-level fy2025_units fields use each award list's own
   independently-verified 286/621 totals, exactly as the task briefing
   instructs ("如实标注CATEGORIES用官方889，RAW_PROJECTS用两轮清单各自的...
   总计做校验"). Combined LIHTC Credit Award across both rounds is
   $8,320,433 + $8,065,137 = $16,385,570, about 5.7% above the Performance
   Report's own "more than $15.5 million" -- also not forced to reconcile
   (see the $144M/816-unit ACFR figure above for a THIRD data point on the
   same underlying question).
   additive=False: HOME and NHTF ride on top of a SUBSET of the 9% round's
   8 developments (only 5 of 8 carry a nonzero HOME amount, only 1 of 8
   carries NHTF), and the Tax-Exempt Bond Amount is disclosed for every 4%
   development but is a financing mechanism layered on the SAME projects
   as lihtc_4pct, not a separate physical-unit-producing program -- summing
   all 5 subprograms' units would over-count actual developments, the same
   reasoning PA/MI document for their own multifamily categories.

3. State Housing Trust Fund: fy2025_actual=2,636, from the Performance
   Report's own KPI table (p.6): "Number of units created/preserved
   through the Local Housing Trust Fund Program: Target 2,300, Actual
   2,636, Yes" (100% of appropriated Local Housing Trust Fund Program
   funds allocated). The executive-summary narrative (p.5) separately
   states "More than 2,600 families will be assisted through more than
   $12.6 million in State Housing Trust Fund grants to help finance
   affordable housing activities, the most in a single year in program
   history" -- "more than 2,600" is consistent with (not contradicted by)
   the KPI table's more precise 2,636, and "more than $12.6 million" is
   used verbatim (as a floor, not an exact figure -- IFA discloses no more
   precise number anywhere) for fy2025_amounts. No per-grant or per-county
   list is published for this program anywhere IFA discloses (checked the
   Performance Report and both LIHTC award-list documents; the ACFR
   discloses only the combining-schedule dollar balance, not a grant-level
   breakdown) -- per the task briefing, this category also stays at the
   KPI level, with no RAW_PROJECTS entries.

4. Homeless Prevention (Emergency Solutions Grant + Shelter Assistance
   Fund): fy2025_actual=None (unlike the three categories above, IFA
   publishes no single combined headline for these two programs together).
   The Performance Report's executive summary (p.5) states "5,124
   households and 6,088 households were assisted through the Emergency
   Solutions Grant and Shelter Assistance Funds programs respectively to
   help avoid homelessness or get rapidly rehoused in their time of need."
   The KPI table (p.5) separately tracks each program by PROJECT count, not
   households ("Emergency Solutions Grant (ESG): Number of projects
   assisted, Target 27, Actual 27, Yes"; "Shelter Assistance Fund (SAF):
   Number of projects assisted, Target 27, Actual 30, Yes") -- these
   project counts are a different unit of measure than the household
   counts used as fy2025_units here, and are not reproduced. No dollar
   figure for either program is disclosed anywhere in the Performance
   Report. The ACFR's own Schedule of Expenditures of Federal Awards
   (SEFA, p.88) DOES separately disclose "Emergency Solutions Grants
   Program 14.231 ... $3,264,506" of FY2025 federal expenditures -- a
   different document, a different accounting concept (cash expenditures
   under a federal compliance schedule, not "households assisted" from the
   Performance Report), but a genuine, audited, IFA-disclosed dollar figure
   for the same program in the same fiscal year, so it is used here as
   esg's fy2025_amount with this provenance spelled out. SAF is a
   state-only (non-federal) program and is never itemized by name or
   dollar amount in the SEFA or anywhere else in the ACFR, so saf's
   fy2025_amount is None, not estimated or borrowed from ESG.

Fund-type classification (fund_type/fund_name on each subprogram)
---------------------------------------------------------------------------
IFA reports on a business-type-activities-only basis (no governmental
funds of its own -- like FL/MI/PA, "governmental" is never used below) but,
unlike FL/MI/PA (which each carry a single enterprise fund), IFA's own
ACFR states it "presents two major funds: (1) Housing Agency Fund, and (2)
State Revolving Fund (SRF)" (Notes to Financial Statements, p.29). SRF
(Clean Water / Drinking Water infrastructure lending) is entirely outside
this file's housing-program scope. The Housing Agency Fund is itself
broken into 6 named sub-accounts on IFA's own Combining Schedules of Net
Position (pp.70-71) and described narratively in MD&A (pp.9-11) and Notes
(p.29): General Operating Account, Single-Family Bond Programs (columns
"1991 MB" / "2009 MRB"), Multi-Family Bond Programs ("Multi-Family Housing
Bonds"), Federal and State Programs, Iowa Agricultural Development
Division, and Iowa Title Guaranty Division.
  - "proprietary" (named IFA-carried balance, high confidence):
      * mortgage_loans -- MD&A p.10: "Single-Family homeownership programs
        include the FirstHome and Homes for Iowans Programs... funded
        through the issuance of bonds under the 1991 Single-Family
        Mortgage Bond Resolution, 2009 Single-Family Mortgage Revenue Bond
        Resolution." Combining Schedule p.70 shows the "1991 MB" and
        "2009 MRB" columns together carrying $2.06B+ of mortgage-backed
        securities and Housing Agency loans.
      * dpa -- Notes to Financial Statements, (l) "Deferred Down Payment
        Assistance" (p.31): "Down payment grant assistance paid in
        connection with the Authority's Single Family Program is deferred
        and amortized over 10 years. As of June 30, 2025, there was a
        balance of $7.1 million included in other assets" -- an explicit,
        dollar-quantified IFA-carried balance for exactly this program.
      * home, nhtf -- MD&A p.10 names both verbatim under "Federal and
        State Programs": "Some federal programs the Authority administers
        include the HOME Investment Partnerships Program (HOME)... and the
        National Housing Trust Fund (NHTF)... funded by [HUD]." The
        Combining Schedule's own "Federal and State Programs" column
        (p.70-71) carries $178.2M of total assets and $129.6M of total net
        position as of June 30, 2025 -- a real IFA-carried balance, not a
        pure pass-through with no footprint on IFA's own statements. SEFA
        (p.88) separately discloses FY2025 federal expenditures of
        $10,448,698 (HOME, CFDA 14.239) + $591,146 (HOME-ARP) and
        $3,959,398 (NHTF, CFDA 14.275).
      * local_htf_grants (State Housing Trust Fund) -- MD&A p.10, same
        "Federal and State Programs" paragraph block: "The State Housing
        Trust Fund provides grants to advance and preserve affordable
        Single-Family and Multi-Family housing throughout the State" --
        near-verbatim name match, same Combining Schedule column as
        home/nhtf above.
      * esg -- MD&A p.10 names "the Emergency Solutions Grant (ESG)
        Program" verbatim in the same "Federal and State Programs"
        paragraph block; SEFA (p.88) discloses $3,264,506 of FY2025
        federal ESG expenditures (CFDA 14.231).
      * saf (Shelter Assistance Fund) -- MD&A p.10: "The Shelter
        Assistance Fund (SAF) Program supports costs of operations of
        shelters for the homeless and domestic violence shelters" --
        named in the same "Federal and State Programs" section as ESG/
        HOME/NHTF/State Housing Trust Fund, but (being state-funded, not
        federal) it is never separately itemized by dollar amount on the
        SEFA or the Combining Schedule the way the others are -- confidence
        is medium (grouped by textual/structural proximity within the same
        MD&A section and the same "Federal and State Programs" combining
        column, not an individually dollar-quantified line of its own).
  - "off_balance_sheet" (federal/state tax-credit or conduit-financing
    allocations that never appear as an IFA-carried asset or liability):
      * lihtc_9pct, lihtc_4pct -- checked "LIHTC" / "Low-Income Housing Tax
        Credit" throughout the ACFR: the only hits are (a) MD&A p.11 --
        "The General Operating Account receives fees from administering
        programs such as the Low-Income Housing Tax Credit (LIHTC)..." and
        (b) Notes p.30-31, "(t) Unearned Revenue" -- "Compliance monitoring
        fees received by the Authority at the time a [LIHTC] project is
        placed in service are deferred..." -- both describe only a small
        administrative FEE booked in the General Operating Account, never
        the tax-credit award value itself. This matches every other
        state's build script in this project: federal/state tax credits
        are allocated directly to developers/investors, not carried as the
        housing finance agency's own fund asset.
      * tax_exempt_bond -- the 4% award list's "Tax-Exempt Bond Amount"
        column (required to trigger 4% credits) is inferred to be
        conduit/private-activity bond financing, NOT an IFA-carried
        Multi-Family Bond Programs liability: MD&A p.11 separately
        describes IFA's "Private Activity Bond Program, which issues
        tax-exempt bonds on behalf of private entities or organizations
        for eligible purposes" under the General Operating Account (i.e. a
        conduit-issuer role collecting only a fee, structurally distinct
        from IFA's own "Multi-Family Bond Programs" sub-account). This is
        corroborated quantitatively: the 4 mapped 4%-round projects alone
        sum to $58,902,467 of Tax-Exempt Bond Amount, which EXCEEDS the
        entire "Multi-Family Housing Bonds" column's own total net
        position on the Combining Schedule ($48,626 thousand at June 30,
        2025, p.70) -- if these bonds were carried as IFA's own Multi-
        Family Bond Programs liability, that column's own balance would
        need to be larger than just this one year's four 4%-round deals
        alone, which it is not. Confidence: medium (inferential, not a
        literal named match -- IFA's ACFR never uses the phrase "4% credit"
        or "tax-exempt bond" in connection with any specific development).

Geocoding
---------------------------------------------------------------------------
Same approach as every other state's build script in this project:
Nominatim (OpenStreetMap), primary query "{street address}, {city}, IA",
falling back to "{city}, IA" (flagged geocode_status="city_center") when
the street-level query fails or -- as with "25-25 Sioux City 3", whose own
award-list row lists three separate street addresses for one scattered-site
development -- when no single street address can be queried. Self-throttled
to <=1 request/second with an identifying User-Agent per Nominatim's usage
policy.

5. Section 8 Project-Based Rental Assistance: per user request (2026-08-14),
   IFA's own FY2025 ACFR was re-searched for an independent, ongoing
   per-unit rental-subsidy program administered by IFA (as distinct from
   the four development/homeownership-financing categories above). Two
   figures, printed in two DIFFERENT tables of the SAME audited document
   and covering the SAME federal program (CFDA 14.195) for the SAME fiscal
   year (year ended June 30, 2025), independently corroborate each other:
     - Statistical Section, "Operating Indicators" table (p.86): "Section 8
       project-based rental units" -- a 10-year trend row (FY2016-FY2025)
       whose FY2025 (rightmost) column reads 11,440.
     - Schedule of Expenditures of Federal Awards (SEFA, p.87), "Section 8
       Project-Based Cluster": "Section 8 Housing Assistance Payments
       Program 14.195 ... $75,309,895" of FY2025 federal expenditures, with
       $0 passed through to subrecipients (i.e. IFA itself disburses the
       full amount directly, not via a sub-grantee) -- "Total Section 8
       Project-Based Cluster $75,309,895".
   Note 1(a) describes the underlying activity in exactly the terms this
   task is looking for: "The Authority has contracted with [HUD] to serve
   as contract administrator for Section 8 Housing Assistance Payment (HAP)
   contracts. The Authority disburses subsidy payments monthly to the
   multi-family projects and monitors the individual units and projects for
   compliance with HUD regulations" -- an ONGOING, per-unit monthly rental
   subsidy to already-occupied units, structurally different from
   lihtc_awards' one-time construction-financing subprograms.
   The Performance Report separately discloses two SMALLER, differently-
   scoped, per-household (not per-unit) rental-assistance KPI lines that
   this script does NOT incorporate because neither discloses a dollar
   figure anywhere (checked the full Performance Report and the ACFR;
   per this project's "never fabricate a number" rule, a unit/household
   count alone is not sufficient to build a category): "Home and
   Community-Based Services Rent Subsidy: Number of households assisted,
   Target 415, Actual 338" (p.5) and, under "HOME Program": "Number of
   renters provided tenant-based rental assistance: Target 550, Actual 592"
   (p.6) -- both genuinely appear to be ongoing per-household rental
   subsidies (the former literally named "Rent Subsidy"; the latter is
   HOME-funded Tenant-Based Rental Assistance, TBRA), but with no
   corroborating dollar figure in either source document, they are
   recorded here as "found but not included" rather than assigned an
   invented amount.
   additive=True: section_8_hap is this category's only subprogram (no
   overlap concern).
   Fund-type classification: "proprietary", medium confidence -- MD&A p.10's
   "Federal and State Programs" paragraph block separately lists "Section 8
   Project HAP Program" among the Authority's own non-operating revenues
   and expenses (Notes p.32-33, same sentence as HOME/NHTF/ESG/State
   Housing Trust Fund, all classified "proprietary" above by the same
   textual-proximity precedent) -- Section 8 itself is never named as its
   own dedicated Combining-Schedule column (unlike HOME/NHTF, which sit
   inside the "Federal and State Programs" column with a disclosed
   dollar balance), so this is grouped with that same column, not a
   literal named-balance match.

fy2026
---------------------------------------------------------------------------
The Performance Report is a KPI/goals document (FY2025 targets vs. FY2025
actuals) with no forward-looking FY2026 target table anywhere, and neither
LIHTC award list discloses a forward-looking figure either -- matching PA's
precedent (annual data tables with no FY26 section at all), every fy2026
field in this file uses the uniform pending shape below; none is invented.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "ia_program_activity.json"

SOURCE_URL = "https://opportunityiowa.gov/about/iowa-finance-authority/financial-reports"
SOURCE_FILE = "IA_IFA_PerformanceReport_FY2025.pdf (+ 2025 9% and 4% Housing Tax Credit Award Lists)"
RETRIEVED = "2026-08-14"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
GEOCODER_USER_AGENT = "us-hfa-data-map/1.0 (github.com/MD-ai-fin/us-hfa-data-map)"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "iaFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "homeownership_loans",
        "unit_type": "households",
        "fy2025_actual": 2908,
        "fy2025_source_quote": (
            "\"2,908 Iowans purchased a home through an IFA homeownership program in "
            "FY25, a 9% increase over the previous year and the second most homebuyers "
            "assisted in a single year in IFA's 50-year history.\" (Performance Report "
            "p.5); KPI table (p.6): \"Number of Homebuyers assisted with mortgages: "
            "Target 2,200, Actual 2,908, Yes\" and \"Number of Iowans assisted with down "
            "payment: Target 1,870, Actual 2,722, Yes.\" IFA's own FY2025 ACFR Transmittal "
            "Letter (p.2) independently confirms: \"The single-family program assisted "
            "2,908 home buyers by funding nearly $509 million in mortgage-backed "
            "securities during fiscal year 2025. Approximately 94% of these home buyers "
            "also benefitted from the Authority's down payment and closing cost "
            "assistance.\" No per-loan or county-level list is published for this program "
            "anywhere IFA discloses, so this category stays at the KPI level (no "
            "RAW_PROJECTS entries)."
        ),
        "fy2025_amounts": [
            {"label_key": "ia_amt_mbs_financed", "amount": 509000000},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "mortgage_loans", "fy2025_units": 2908, "fy2025_amount": 509000000,
             "color_group": "bond",
             # MD&A p.10: FirstHome / Homes for Iowans first-mortgage programs,
             # funded via the 1991 Single-Family Mortgage Bond Resolution / 2009
             # Single-Family Mortgage Revenue Bond Resolution; Combining Schedule
             # p.70 "1991 MB"/"2009 MRB" columns.
             "fund_type": "proprietary",
             "fund_name": "Housing Agency Fund – Single-Family Bond Programs (1991 MB / 2009 MRB)",
             "fy2026": _FY26_PENDING},
            {"key": "dpa", "fy2025_units": 2722, "fy2025_amount": None,
             "color_group": "bond",
             # Notes to Financial Statements, (l) "Deferred Down Payment
             # Assistance" (p.31): explicit $7.1M IFA-carried balance for down
             # payment grant/second-loan assistance under the Single-Family
             # Program.
             "fund_type": "proprietary",
             "fund_name": "Housing Agency Fund – Single-Family Bond Programs (Deferred Down Payment Assistance)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "lihtc_awards",
        "unit_type": "units",
        "fy2025_actual": 889,
        "fy2025_source_quote": (
            "\"889 Iowa families will have access to affordable housing through more "
            "than $15.5 million in federal 9% and 4% housing tax credits.\" (Performance "
            "Report p.5); KPI table (p.5): \"Number of units awarded tax credits: Target "
            "1,000, Actual 889, No\" and \"Percent of available tax credits awarded: "
            "Target 100%, Actual 99%, No.\" This script's own two award lists -- \"2025 9% "
            "Federal Housing Tax Credit with HOME & NHTF Award Listing\" (TOTAL row: 10 "
            "projects, 286 Total Units, $8,320,433 Credit Award, $2,664,999 [State] HOME, "
            "$1,000,000 NHTF) and \"2025 4% Federal Housing Tax Credit (LIHTC) Awards\" "
            "(TOTAL row: 4 Projects, 621 Total Units, $58,902,467 Tax-Exempt Bond Amount, "
            "$8,065,137 Credit Award) -- sum to 286+621=907 units, about 2% above the "
            "official 889 headline; this ~2% gap is not reconciled (see module "
            "docstring). CATEGORIES uses 889 (the official KPI headline); RAW_PROJECTS "
            "and each subprogram's own fy2025_units use the two award lists' own "
            "independently-verified 286/621 totals."
        ),
        "fy2025_amounts": [
            {"label_key": "ia_amt_lihtc_9pct_credit", "amount": 8320433},
            {"label_key": "ia_amt_lihtc_4pct_credit", "amount": 8065137},
            {"label_key": "ia_amt_home", "amount": 2664999},
            {"label_key": "ia_amt_nhtf", "amount": 1000000},
            {"label_key": "ia_amt_tax_exempt_bond", "amount": 58902467},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "lihtc_9pct", "fy2025_units": 286, "fy2025_amount": 8320433,
             "color_group": "credit",
             # Federal 9% credits allocated directly to developers/investors;
             # IFA's own ACFR mentions "LIHTC" only in connection with a small
             # administrative compliance-monitoring fee (MD&A p.11, Notes p.30-31),
             # never as a carried credit-value asset.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "lihtc_4pct", "fy2025_units": 621, "fy2025_amount": 8065137,
             "color_group": "credit",
             # Same off-balance-sheet reasoning as lihtc_9pct.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "home", "fy2025_units": None, "fy2025_amount": 2664999,
             "color_group": "trust",
             # MD&A p.10 names HOME verbatim under "Federal and State Programs";
             # Combining Schedule p.70-71 "Federal and State Programs" column
             # carries $129.6M net position; SEFA p.88 discloses $10,448,698 +
             # $591,146 (HOME-ARP) of FY2025 federal HOME expenditures.
             "fund_type": "proprietary",
             "fund_name": "Housing Agency Fund – Federal and State Programs",
             "fy2026": _FY26_PENDING},
            {"key": "nhtf", "fy2025_units": None, "fy2025_amount": 1000000,
             "color_group": "trust",
             # Same Federal and State Programs balance as home above; SEFA p.88
             # discloses $3,959,398 of FY2025 federal NHTF expenditures.
             "fund_type": "proprietary",
             "fund_name": "Housing Agency Fund – Federal and State Programs",
             "fy2026": _FY26_PENDING},
            {"key": "tax_exempt_bond", "fy2025_units": None, "fy2025_amount": 58902467,
             "color_group": "bond",
             # Inferred conduit/private-activity bond financing, not an IFA-
             # carried Multi-Family Bond Programs liability -- MD&A p.11
             # describes IFA's "Private Activity Bond Program, which issues
             # tax-exempt bonds on behalf of private entities"; the 4 mapped
             # projects' own $58.9M bond total exceeds the entire Multi-Family
             # Housing Bonds column's own net position ($48.626M, Combining
             # Schedule p.70) -- see module docstring. Confidence: medium.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "state_housing_trust_fund",
        "unit_type": "households",
        "fy2025_actual": 2636,
        "fy2025_source_quote": (
            "KPI table (p.6): \"Number of units created/preserved through the Local "
            "Housing Trust Fund Program: Target 2,300, Actual 2,636, Yes\" and \"Percent "
            "of Local Housing Trust Fund Program Funds Appropriated: Target 100%, Actual "
            "100%, Yes.\" The executive-summary narrative (p.5) separately states \"More "
            "than 2,600 families will be assisted through more than $12.6 million in "
            "State Housing Trust Fund grants to help finance affordable housing "
            "activities, the most in a single year in program history\" -- consistent "
            "with, though less precise than, the KPI table's 2,636. No per-grant or "
            "county-level list is published for this program anywhere IFA discloses, so "
            "this category stays at the KPI level (no RAW_PROJECTS entries)."
        ),
        "fy2025_amounts": [
            {"label_key": "ia_amt_shtf_total", "amount": 12600000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "local_htf_grants", "fy2025_units": 2636, "fy2025_amount": 12600000,
             "color_group": "capital",
             # MD&A p.10, "Federal and State Programs" section: "The State
             # Housing Trust Fund provides grants to advance and preserve
             # affordable Single-Family and Multi-Family housing throughout the
             # State" -- near-verbatim name match, same combining column as
             # home/nhtf above.
             "fund_type": "proprietary",
             "fund_name": "Housing Agency Fund – Federal and State Programs",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "homeless_prevention",
        "unit_type": "households",
        "fy2025_actual": None,
        "fy2025_source_quote": (
            "\"5,124 households and 6,088 households were assisted through the "
            "Emergency Solutions Grant and Shelter Assistance Funds programs "
            "respectively to help avoid homelessness or get rapidly rehoused in their "
            "time of need.\" (Performance Report p.5). No combined headline is published "
            "for these two programs together, so fy2025_actual is None here (not "
            "invented as 5,124+6,088). The KPI table (p.5) separately tracks each "
            "program by PROJECT count, a different unit of measure: \"Emergency "
            "Solutions Grant (ESG): Number of projects assisted, Target 27, Actual 27, "
            "Yes\"; \"Shelter Assistance Fund (SAF): Number of projects assisted, Target "
            "27, Actual 30, Yes.\" No dollar figure for either program appears in the "
            "Performance Report; ESG's fy2025_amount below ($3,264,506) instead comes "
            "from IFA's own FY2025 ACFR Schedule of Expenditures of Federal Awards "
            "(SEFA, p.88): \"Emergency Solutions Grants Program 14.231 ... $3,264,506\" "
            "of FY2025 federal expenditures -- a genuine, audited IFA-disclosed dollar "
            "figure for the same program/year, but from a different document/accounting "
            "concept than the 5,124-households figure, so it is not claimed to equal "
            "\"dollars per ESG household.\" SAF is a state-only (non-federal) program with "
            "no dollar figure disclosed anywhere in the ACFR (it is not a SEFA line), so "
            "saf's fy2025_amount is None."
        ),
        "fy2025_amounts": [
            {"label_key": "ia_amt_esg_total", "amount": 3264506},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "esg", "fy2025_units": 5124, "fy2025_amount": 3264506,
             "color_group": "capital",
             # MD&A p.10 names "the Emergency Solutions Grant (ESG) Program"
             # verbatim under "Federal and State Programs"; SEFA p.88 discloses
             # $3,264,506 of FY2025 federal ESG expenditures (CFDA 14.231).
             "fund_type": "proprietary",
             "fund_name": "Housing Agency Fund – Federal and State Programs",
             "fy2026": _FY26_PENDING},
            {"key": "saf", "fy2025_units": 6088, "fy2025_amount": None,
             "color_group": "capital",
             # MD&A p.10: "The Shelter Assistance Fund (SAF) Program supports
             # costs of operations of shelters for the homeless and domestic
             # violence shelters" -- named in the same "Federal and State
             # Programs" section as ESG/HOME/NHTF/State Housing Trust Fund, but
             # (being state-funded) never itemized by dollar amount on the SEFA
             # or Combining Schedule the way the others are. Confidence: medium.
             "fund_type": "proprietary",
             "fund_name": "Housing Agency Fund – Federal and State Programs",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        # Section 8 Project-Based Rental Assistance -- an ongoing, per-unit
        # monthly rental subsidy program IFA administers as HUD's contracted
        # Section 8 HAP contract administrator, structurally different from
        # every other category above (all one-time development/homeownership
        # financing). See module docstring's item 5 for the full two-table
        # cross-check and the two smaller, dollar-figure-less KPI lines
        # found but not incorporated (HCBS Rent Subsidy, HOME TBRA).
        "key": "section_8_project_based",
        "unit_type": "units",
        "fy2025_actual": 11440,
        "fy2025_source_quote": (
            "IFA's own FY2025 ACFR, Statistical Section \"Operating Indicators\" "
            "table (p.86), \"Compliance Monitoring\" row \"Section 8 project-based "
            "rental units\": 11,440 for the fiscal year ended June 30, 2025 (a "
            "10-year trend row, FY2016-FY2025). The Schedule of Expenditures of "
            "Federal Awards (SEFA, p.87), \"Section 8 Project-Based Cluster\": "
            "\"Section 8 Housing Assistance Payments Program 14.195 ... "
            "$75,309,895\" of FY2025 federal expenditures, $0 passed through to "
            "subrecipients. Note 1(a): \"The Authority has contracted with [HUD] "
            "to serve as contract administrator for Section 8 Housing Assistance "
            "Payment (HAP) contracts. The Authority disburses subsidy payments "
            "monthly to the multi-family projects and monitors the individual "
            "units and projects for compliance with HUD regulations.\" Both "
            "figures are independently printed in the same audited document, for "
            "the same fiscal year and the same CFDA 14.195 program."
        ),
        "fy2025_amounts": [
            {"label_key": "ia_amt_section8_hap", "amount": 75309895},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "section_8_hap", "fy2025_units": 11440, "fy2025_amount": 75309895,
             "color_group": "trust",
             # MD&A p.10's "Federal and State Programs" paragraph names
             # "Section 8 Project HAP Program" among the Authority's own
             # non-operating revenues and expenses, the same sentence block as
             # HOME/NHTF/ESG/State Housing Trust Fund above -- grouped with the
             # same Combining Schedule column by textual proximity, not a
             # literal named-balance match. Confidence: medium.
             "fund_type": "proprietary",
             "fund_name": "Housing Agency Fund – Federal and State Programs (Section 8 Project HAP Program)",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# ---------------------------------------------------------------------------
# LIHTC project-level detail (both 2025 award lists, dated June 25, 2026).
# Manually transcribed via pdfplumber table extraction, one row per
# development. "units" uses each list's own "Total Units" column (which for
# every mapped row equals "LI Units" -- no market-rate units are mixed into
# any of these 12 developments).
# (name, address, city, county, units, {source_key: amount, ...})
# address=None marks developments whose own award-list row lists more than
# one street address for a single scattered-site development -- these fall
# back to city-center geocoding.
# ---------------------------------------------------------------------------

RAW_PROJECTS_9PCT = [
    # (proj_id, name, address, city, county, units, funding amounts)
    ("25-01", "Goldfinch Lofts", "3404 Ingersoll Avenue", "Des Moines", "Polk", 28,
     {"lihtc_9pct": 1000000, "home": 500000}),
    ("25-02", "Maplecrest Apartments", "2205 Central Avenue", "Hawarden", "Sioux", 20,
     {"lihtc_9pct": 514800, "home": 564999}),
    ("25-13", "Brockton Place", "S. 15th Avenue W.", "Newton", "Jasper", 44,
     {"lihtc_9pct": 1300000, "home": 500000}),
    ("25-05", "River District", "801 3rd Avenue NW", "Fort Dodge", "Webster", 40,
     {"lihtc_9pct": 1195346}),
    ("25-06", "Foundry Lofts", "509 SE 6th Street", "Des Moines", "Polk", 46,
     {"lihtc_9pct": 1300000, "home": 500000, "nhtf": 1000000}),
    ("25-22", "The Iris", "60 Act Pl", "Iowa City", "Johnson", 44,
     {"lihtc_9pct": 1300000}),
    ("25-10", "The Residence at Carter Lake", "NE Corner N. 9th St and Ave K", "Carter Lake", "Pottawattamie", 54,
     {"lihtc_9pct": 1300000}),
    ("25-03", "Manor 2.0", "215 E 37th Street", "Davenport", "Scott", 10,
     {"lihtc_9pct": 316250, "home": 600000}),
    # Excluded from RAW_PROJECTS (see module docstring): "25-15 Encore Senior
    # Living" (WITHDREW 2026, 0 units/$0) and "24-01 Townhall Food Hall and
    # Apartments" (a $94,037 supplemental award to a project whose units were
    # already counted in a prior fiscal year's list).
]

RAW_PROJECTS_4PCT = [
    ("25-27", "Martin Tower Apartments", "410 Pierce Street", "Sioux City", "Woodbury", 86,
     {"lihtc_4pct": 685182, "tax_exempt_bond": 5215000}),
    ("25-29", "The Atheneum", "4010 20th Ave SW", "Cedar Rapids", "Linn", 192,
     {"lihtc_4pct": 2881783, "tax_exempt_bond": 20282551}),
    ("25-24", "Central at Orchard Court", "204 W. Benton Street", "Iowa City", "Johnson", 183,
     {"lihtc_4pct": 2708050, "tax_exempt_bond": 19794458}),
    # Three street addresses on one scattered-site development -- no single
    # street-level geocode query is attempted, falls back to city center.
    ("25-25", "Sioux City 3", None, "Sioux City", "Woodbury", 160,
     {"lihtc_4pct": 1790122, "tax_exempt_bond": 13610458}),
    # Excluded from RAW_PROJECTS: "25-26 South Market Apartments" (WITHDRAWN,
    # 0 units/$0), consistent with the workbook's own TOTAL row already
    # labeling itself "4 Projects" (not 5).
]

EXPECTED_9PCT_TOTALS = {"projects": 8, "units": 286, "lihtc_9pct": 8226396,
                          "home": 2664999, "nhtf": 1000000}
EXPECTED_9PCT_OFFICIAL_CREDIT_TOTAL = 8320433  # includes the $94,037 unmapped supplemental
EXPECTED_4PCT_TOTALS = {"projects": 4, "units": 621, "lihtc_4pct": 8065137,
                          "tax_exempt_bond": 58902467}

FUNDING_COLOR_GROUP = {
    "lihtc_9pct": "credit", "lihtc_4pct": "credit",
    "home": "trust", "nhtf": "trust",
    "tax_exempt_bond": "bond",
}
# priority order for a project's single "primary" marker color -- the LIHTC
# credit itself (9% or 4%, whichever applies) is the universal anchor on
# every one of the 12 mapped developments.
FUNDING_PRIORITY = ["lihtc_9pct", "lihtc_4pct", "home", "nhtf", "tax_exempt_bond"]


def verify_9pct_totals():
    errors = []
    if len(RAW_PROJECTS_9PCT) != EXPECTED_9PCT_TOTALS["projects"]:
        errors.append(f"9% round project count: expected {EXPECTED_9PCT_TOTALS['projects']}, "
                       f"got {len(RAW_PROJECTS_9PCT)}")
    units_sum = sum(p[5] for p in RAW_PROJECTS_9PCT)
    if units_sum != EXPECTED_9PCT_TOTALS["units"]:
        errors.append(f"9% round Total Units sum: expected {EXPECTED_9PCT_TOTALS['units']}, got {units_sum}")
    sums = {}
    for *_rest, amounts in RAW_PROJECTS_9PCT:
        for k, v in amounts.items():
            sums[k] = sums.get(k, 0) + v
    for key in ("lihtc_9pct", "home", "nhtf"):
        expected = EXPECTED_9PCT_TOTALS[key]
        got = sums.get(key, 0)
        if got != expected:
            errors.append(f"9% round {key} sum: expected {expected}, got {got}")
    official_gap_check = sums.get("lihtc_9pct", 0) + 94037
    if official_gap_check != EXPECTED_9PCT_OFFICIAL_CREDIT_TOTAL:
        errors.append(
            f"9% round Credit Award + $94,037 supplemental: expected "
            f"{EXPECTED_9PCT_OFFICIAL_CREDIT_TOTAL}, got {official_gap_check}"
        )
    if errors:
        raise SystemExit("9% round total mismatch(es):\n" + "\n".join(errors))
    print("2025 9% round verified: 8 mapped projects, 286 Total Units, $8,226,396 Credit "
          "Award (+ $94,037 unmapped supplemental = $8,320,433, matching the award list's "
          "own TOTAL row), $2,664,999 HOME, $1,000,000 NHTF.")


def verify_4pct_totals():
    errors = []
    if len(RAW_PROJECTS_4PCT) != EXPECTED_4PCT_TOTALS["projects"]:
        errors.append(f"4% round project count: expected {EXPECTED_4PCT_TOTALS['projects']}, "
                       f"got {len(RAW_PROJECTS_4PCT)}")
    units_sum = sum(p[5] for p in RAW_PROJECTS_4PCT)
    if units_sum != EXPECTED_4PCT_TOTALS["units"]:
        errors.append(f"4% round Total Units sum: expected {EXPECTED_4PCT_TOTALS['units']}, got {units_sum}")
    sums = {}
    for *_rest, amounts in RAW_PROJECTS_4PCT:
        for k, v in amounts.items():
            sums[k] = sums.get(k, 0) + v
    for key in ("lihtc_4pct", "tax_exempt_bond"):
        expected = EXPECTED_4PCT_TOTALS[key]
        got = sums.get(key, 0)
        if got != expected:
            errors.append(f"4% round {key} sum: expected {expected}, got {got}")
    if errors:
        raise SystemExit("4% round total mismatch(es):\n" + "\n".join(errors))
    print("2025 4% round verified: 4 mapped projects, 621 Total Units, $8,065,137 Credit "
          "Award, $58,902,467 Tax-Exempt Bond Amount -- all match the award list's own "
          "TOTAL row exactly.")


def verify_combined_lihtc_gap():
    combined_units = EXPECTED_9PCT_TOTALS["units"] + EXPECTED_4PCT_TOTALS["units"]
    if combined_units != 907:
        raise SystemExit(f"Combined 9%+4% unit total: expected 907, got {combined_units}")
    official = 889
    gap_pct = (combined_units - official) / official * 100
    print(f"Combined 9%+4% award-list units ({combined_units}) vs. official Performance "
          f"Report headline ({official}): {gap_pct:.1f}% gap -- documented in module "
          f"docstring, not reconciled.")


def verify_section8_totals():
    """Cross-checks the section_8_project_based category's own headline
    figures against its single subprogram (a trivial 1:1 check, since this
    program has no per-project exhibit to sum) -- documents that both
    figures are independently printed in two different tables of the same
    audited ACFR (see module docstring item 5)."""
    cat = next(c for c in CATEGORIES if c["key"] == "section_8_project_based")
    sp = cat["subprograms"][0]
    errors = []
    if sp["fy2025_units"] != cat["fy2025_actual"]:
        errors.append(f"section_8_hap units: category says {cat['fy2025_actual']}, subprogram says {sp['fy2025_units']}")
    if sp["fy2025_amount"] != cat["fy2025_amounts"][0]["amount"]:
        errors.append(
            f"section_8_hap amount: category says {cat['fy2025_amounts'][0]['amount']}, subprogram says {sp['fy2025_amount']}"
        )
    if errors:
        raise SystemExit("Section 8 total mismatch(es):\n" + "\n".join(errors))
    print(
        "Section 8 Project-Based Rental Assistance verified: 11,440 units (ACFR "
        "Statistical Section, Operating Indicators table, p.86) / $75,309,895 "
        "(ACFR SEFA, p.87, CFDA 14.195) -- both figures independently printed in "
        "the same audited document for the same fiscal year and program."
    )


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
    seen_ids = set()
    all_rows = [(pid, name, addr, city, county, units, amounts, ["lihtc_9pct"])
                for pid, name, addr, city, county, units, amounts in RAW_PROJECTS_9PCT]
    all_rows += [(pid, name, addr, city, county, units, amounts, ["lihtc_4pct"])
                 for pid, name, addr, city, county, units, amounts in RAW_PROJECTS_4PCT]
    for pid, name, address, city, county, units, amounts, base_source in all_rows:
        sources = list(amounts.keys())
        query = f"{address}, {city}, IA" if address else f"{city}, IA"
        coords = geocode(query, cache)
        status = "ok"
        if coords is None:
            coords = geocode(f"{city}, IA", cache)
            status = "city_center" if coords else "unresolved"
        primary = next((s for s in FUNDING_PRIORITY if s in sources), sources[0])
        base_id = (name.lower().replace(" ", "-").replace("'", "").replace(".", "")
                   .replace(",", "").replace("&", "and"))
        while "--" in base_id:
            base_id = base_id.replace("--", "-")
        base_id = base_id.strip("-")
        pid_slug = base_id
        n = 2
        while pid_slug in seen_ids:
            pid_slug = f"{base_id}-{n}"
            n += 1
        seen_ids.add(pid_slug)
        projects.append({
            "id": pid_slug,
            "name": name,
            "address": address,
            "city": city,
            "county": county,
            "lat": round(coords[0], 5) if coords else None,
            "lon": round(coords[1], 5) if coords else None,
            "units": units,
            "funding_sources": sources,
            "source_amounts": amounts,
            "total_amount": sum(amounts.values()) if amounts else None,
            "primary_color_group": FUNDING_COLOR_GROUP[primary],
            "overlaps": len(sources) > 1,
            "geocode_status": status,
        })
    return projects


def main():
    verify_9pct_totals()
    verify_4pct_totals()
    verify_combined_lihtc_gap()
    verify_section8_totals()
    print("Geocoding project addresses via Nominatim...")
    projects = build_projects()
    unresolved = [p["name"] for p in projects if p["geocode_status"] == "unresolved"]
    if unresolved:
        print(f"  {len(unresolved)} project(s) could not be geocoded: {unresolved}")
    city_center = [p["name"] for p in projects if p["geocode_status"] == "city_center"]
    if city_center:
        print(f"  {len(city_center)} project(s) fell back to city-center geocoding: {city_center}")

    payload = {
        "IA": {
            "hfa_name": "Iowa Finance Authority",
            "hfa_abbr": "IFA",
            "fiscal_year": "FY2025",
            "source_title": "IFA FY2025 Performance Report + 2025 9%/4% Housing Tax Credit Award Lists",
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
