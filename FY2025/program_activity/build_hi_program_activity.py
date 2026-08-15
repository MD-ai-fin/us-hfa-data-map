"""
Builds docs/hi_program_activity.json from HHFDC's FY2025 Annual Report (housing
production summary, pp.38-42) plus its own state-financing-tools tables
(Table 1, "2025 Low-Income Housing Tax Credit Award Reservations", and the
HMMF narrative on p.16) and its own separately-issued FY2025 audited
financial statements (for GASB fund-type classification).

Sources (HHFDC's fiscal year = July 1, 2024 - June 30, 2025)
------------------------------------------------------------------------
1. "Hawaii Housing Finance and Development Corporation FY 2025 Annual Report"
     https://dbedt.hawaii.gov/hhfdc/files/2026/01/2025-Annual-Report.pdf
   (index page: https://dbedt.hawaii.gov/hhfdc/resources/reports/)
   Local copy: FY2025/program_activity/pdf/HI_HHFDC_AnnualReport_FY2025.pdf
   (59 pages; the site returns HTTP 403 to requests with no browser-like
   User-Agent header, so this script's own download step -- run once,
   manually, to produce the local copy above -- sets one.)
   - Table 1, "2025 Low-Income Housing Tax Credit Award Reservations" (p.14):
     8 projects, 1,234 total units -- used for the "lihtc_reservations"
     category and its RAW_PROJECTS detail.
   - HMMF narrative (p.16): "In 2025, HHFDC awarded $357,006,367 in HMMF
     financing, which will assist with the construction of 1,333 affordable
     housing units statewide." -- used for the "hmmf_financing" category.
     No per-project table ties precisely to this $357,006,367/1,333-unit
     figure (Table 6, "Issuance of Bonds for Construction", is the closest
     candidate but sums to only 8 projects / 1,279 units / $335,332,934 --
     a different, narrower population: bonds actually issued during the
     fiscal year, vs. "awarded" during the calendar year), so this category
     carries NO RAW_PROJECTS of its own rather than force a mapping that
     cannot be independently verified against a printed table total.
   - Table 10, "Projects Completed in FY 2025" (p.38): 14 projects, 1,460
     total units -- used for the "units_completed" category and its
     RAW_PROJECTS detail (see "Housing Production Summary" methodology
     below).
   - "Summary of Projects Completed in FY 2025" box (p.39) and "Five-Year
     Production Projection" table (p.39) -- see "The 1,189 + 523 vs 1,460
     discrepancy" and "fy2026" below.
   - Tables 11-14, "Projects Under Development" by county (pp.40-42): 63
     projects (7 Hawaii + 11 Kauai + 12 Maui + 33 Honolulu) reviewed but NOT
     used for RAW_PROJECTS -- see "Tables 11-14" below.
   - Executive Director's Welcome (p.4): "HHFDC assisted in the delivery of
     1,460 units that were placed in service and provided financing or
     development assistance for 10,875 units that are expected to come
     online in the coming years" -- corroborates Table 10's own 1,460
     printed total and the Five-Year Production Projection's 10,875-unit
     FY2026-2030 sum (1,546 + 1,374 + 2,199 + 3,553 + 2,203 = 10,875).
2. HHFDC's own separately-issued FY2025 financial and compliance audit (used
   ONLY for GASB fund-type classification):
     FY2025/txt/HI_HHFDC_FY2025_ACFR.txt
   Confirmed to be the correct, HHFDC-scoped document: its own title page
   reads "State of Hawaii, Hawaii Housing Finance and Development
   Corporation (A Component Unit of the State of Hawaii), Financial and
   Compliance Audit, June 30, 2025" -- i.e. HHFDC's complete basic financial
   statements, not a component-unit summary buried in a larger state-wide
   report (unlike the pre-existing PA .txt/.pdf mismatch flagged in this
   same pilot series' build_pa_program_activity.py). No data-provenance
   problem here.

Calendar-year vs. fiscal-year data (IMPORTANT caveat)
------------------------------------------------------------------------
The Annual Report states plainly, right before Table 1: "When presenting
facts on financing awards, HHFDC adheres to a calendar year schedule" (p.13).
This means:
  - "units_completed" (Table 10, the Executive Director's welcome, the
    Summary box, and the Five-Year Production Projection) is FISCAL YEAR
    2025 data (July 1, 2024 - June 30, 2025).
  - "lihtc_reservations" (Table 1) and "hmmf_financing" (p.16 narrative) are
    CALENDAR YEAR 2025 data (January 1, 2025 - December 31, 2025) -- a
    different, partially-overlapping 12-month window that extends five
    months past FY2025's own June 30, 2025 close. This script's
    fy2025_source_quote for both of those categories says so explicitly;
    they are still filed here under fiscal_year="FY2025" (matching this
    project's per-state, one-JSON-per-fiscal-year convention and how
    HHFDC's own report bundles all three inside a single "FY 2025 Annual
    Report"), but the underlying reporting *periods* are not identical, and
    a reader comparing "units_completed" against "lihtc_reservations" or
    "hmmf_financing" is not comparing the same twelve months.

The 1,189 + 523 vs. 1,460 discrepancy (Table 10 vs. the Summary box)
------------------------------------------------------------------------
Table 10 itself (p.38) prints a "Number of Units" column that sums to
1,460 exactly (verified below, verify_units_completed()) across its own 14
named projects -- matching the Executive Director's "1,460 units ... placed
in service" (p.4) and the table's own printed total row.
Immediately below it (p.39), a second box, "Summary of Projects Completed in
FY 2025", prints: New Construction 1,189 | Preservation 523 | For Rent 1,460
| For Sale 0 | Total 1,460. Because 1,189 + 523 = 1,712, not 1,460, this
second box's own "New Construction" and "Preservation" columns do NOT sum to
its own printed Total -- while "For Rent" (1,460) + "For Sale" (0) = 1,460
does. This script does not attempt to force a reconciliation (e.g. by
re-deriving "New Construction"/"Preservation" from Table 10's own
"Construction Type" column, which reads "new rentals" for 12 of the 14
projects and "acq rehab rentals" for 2 -- summing to 937 new-construction
units and 523 acq-rehab units, i.e. Table 10's own data would itself
produce a *different* 937/523 split that also does not match the Summary
box's printed 1,189/523). The Summary box's 1,189/523/1,460 figures are
reproduced verbatim in this category's fy2025_source_quote as HHFDC's own
printed numbers, and the internal inconsistency is flagged here rather than
silently corrected -- consistent with this project's "never fabricate a
number to force a match" rule. No subprogram in this script's
"units_completed" category is built from the New Construction/Preservation
split for this reason (the Table 10-derived financing-tool subprograms
below are unaffected by this specific inconsistency, since they come from a
different column of the same table).

Housing Production Summary (Table 10) methodology -- RAW_PROJECTS
------------------------------------------------------------------------
Table 10's own "Program Used" column lists, per project, a comma-separated
combination of up to 6 financing/regulatory tools drawn from LIHTC, RHRF
(Rental Housing Revolving Fund), HMMF (Hula Mae Multi-Family bond program),
HOME, HOME-ARP, HTF (Housing Trust Fund), GET (General Excise Tax
exemption), DURF (Dwelling Unit Revolving Fund), 201H (HRS Chapter 201H
expedited processing), EP (an alternate abbreviation for the same 201H
expedited-processing mechanism, used on only one row), and "Land"
(contributed state land, used on only one row). Table 10 discloses NO
dollar figure for any of these, project-by-project or in aggregate -- unlike
IL/PA/OH/FL's own multifamily award tables, it is a units-only table -- so
every subprogram's fy2025_amount below is None and every project's
source_amounts is {} (never invented). This script's "units_completed"
category therefore treats each of the 11 tool tags as a non-additive
reference chip (additive=False) whose fy2025_units is the sum of Table 10's
own "Number of Units" column across every project carrying that tag
(overlapping, since most of the 14 projects carry 2-6 tags at once -- see
verify_tag_tallies()). "201H" and "EP" are kept as two separate tags
(rather than merged into one) because Table 10 itself never states they are
the same mechanism, even though HRS Chapter 201H expedited processing is
the only 201H-branded program this report describes anywhere; this
uncertainty is flagged in-line on the "ep" subprogram rather than resolved
by assumption.

Double verification (Table 10 and Table 1 both print their own totals)
------------------------------------------------------------------------
  1. verify_units_completed(): RAW_PROJECTS' Table-10 subset must have
     exactly 14 projects and its own units column must sum to exactly 1,460
     -- Table 10's own printed total (p.38) and the Executive Director's
     independently-stated "1,460 units ... placed in service" (p.4).
  2. verify_lihtc_reservations(): RAW_PROJECTS' Table-1 subset must have
     exactly 8 projects and its own units column must sum to exactly 1,234
     -- Table 1's own printed total (p.14) and the narrative directly above
     it: "HHFDC awarded LIHTC reservations to 8 affordable housing
     projects, supporting the new construction or rehabilitation of 1,234
     units" (p.13-14).
  3. verify_tag_tallies(): re-sums RAW_PROJECTS' Table-10 subset by each of
     the 11 financing/regulatory tags and checks it reproduces
     EXPECTED_TAG_TALLIES exactly -- EXPECTED_TAG_TALLIES was computed once,
     directly off the transcribed Table 10 rows, before being hard-coded
     here; this is an internal transcription-integrity check (Table 10
     prints no per-tag subtotal of its own to check against), matching this
     pilot series' PHFA/OHFA "EXPECTED_SOURCE_TOTALS computed once, then
     checked" convention for source tables with no footer breakdown.

Table 1's "Kehalani Apartments" county correction
------------------------------------------------------------------------
Table 1 (p.14) prints "Kehalani Apartments Oahu 35". Every other table in
this same Annual Report that lists Kehalani Apartments places it in Maui
County instead: Table 3, "2025 Multi-Family Revenue Bond Applications"
(p.17, row 11: "Kehalani Apartments Maui $13,000,000"); Table 8, "Projects
Funded Targeting 30% AMI and Below" (p.21: "7/10/2025 Kehalani Apartments
Maui 3 35 8.6%" -- same 35-unit count as Table 1); and Table 13, "Projects
Under Development - Maui County" (p.42: "Kehalani Apartments new rentals
35" -- again the same 35 units). "Kehalani" is itself a well-known Wailuku,
Maui neighborhood. This script therefore treats Table 1's "Oahu" as a
data-entry slip in that one row and files the project under Maui, matching
this pilot series' identical PA "Belthlehem"->"Bethlehem" and OH
"Stubenville"->"Steubenville" typo corrections (cross-validated by 3 other
same-document tables, not invented) -- the unit count (35) and the
category-level 1,234-unit total are unaffected either way.

Tables 11-14 ("Projects Under Development" by county, pp.40-42)
------------------------------------------------------------------------
Reviewed but not incorporated into RAW_PROJECTS: unlike Table 10 and Table
1, Tables 11-14 disclose no funding-source/program-tool column at all (only
Project Name / Construction Type / [Rent-or-Sale] Type / Total Units), so
there is nothing to classify by fund_type or color_group, and their 63
projects' "under development" status is a different life-cycle stage than
either Table 10's "completed" or Table 1's "awarded" moments this script
otherwise maps. Their own county subtotals (Hawaii 7/663, Kauai 11/772,
Maui 12/1,394, Honolulu 33/8,046 -- printed on pp.40-42, alongside a
separate County-summary graphic on p.40 that gives Honolulu as "8,042" units,
4 short of Tables 11-14's own 8,046 sum -- yet another printed inconsistency
in this source document, flagged here rather than resolved) are not
reproduced anywhere in this script's output.

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
HHFDC's own MD&A and Note 1 report BOTH governmental funds and proprietary
(enterprise) funds -- unlike PHFA/OHFA in this same pilot series, which
report only proprietary/business-type activities. Governmental funds: 4
major (General Fund, General Obligation Bond Fund, HOME Investment
Partnership Program, Housing Trust Fund Program) + 2 non-major (Homeowner
Assistance Fund Program, Tax Credit Assistance Program) (MD&A p.11-12, Note
1 p.30). Proprietary (enterprise) funds: 4 major (Rental Housing Revolving
Fund, Dwelling Unit Revolving Fund, Single Family Mortgage Purchase Revenue
Bond Fund, Housing Finance Revolving Fund) + 5 non-major (Rental Assistance
Revolving Fund, Multifamily Housing Revenue Bond Fund, Disbursing Fund,
Grants in Aid Fund, Affordable Homeownership Revolving Fund) (MD&A p.12-13,
Note 1 p.30-31).
  - "governmental":
      * HOME -> HOME Investment Partnership Program, a major governmental
        fund named verbatim (MD&A p.11-12, Note 1 p.30; also the Schedule
        of Expenditures of Federal Awards, p.76, CFDA 14.239). Confidence:
        high.
      * HTF -> Housing Trust Fund Program, a major governmental fund named
        verbatim (MD&A p.13, Note 1 p.30; SEFA p.76, CFDA 14.275).
        Confidence: high.
      * HOME-ARP -> never named separately anywhere in the ACFR or the
        Schedule of Expenditures of Federal Awards (the SEFA, p.76, lists
        only "HOME Investment Partnership Program" CFDA 14.239, "Housing
        Trust Fund" CFDA 14.275, and a COVID-19 ARPA "Homeowner Assistance
        Fund" CFDA 21.026 -- HOME-ARP itself does not appear as its own
        line). HOME-ARP is HUD's own 2021 supplemental appropriation to the
        HOME program (same CFDA family, 14.239), so it is inferred to sit
        inside the same HOME Investment Partnership Program governmental
        fund as ordinary HOME -- confidence: medium, by federal-program
        family, not a verbatim ACFR name match.
  - "proprietary":
      * RHRF -> Rental Housing Revolving Fund, a major proprietary
        (enterprise) fund named verbatim, explicitly described as
        "provid[ing] developers of qualified rental housing projects with
        loans and/or grants for the development, predevelopment,
        construction, acquisition, preservation and rehabilitation of
        rental housing units" (MD&A p.11, Note 1 p.30-31). Confidence: high.
      * DURF -> Dwelling Unit Revolving Fund, a major proprietary
        (enterprise) fund named verbatim (MD&A p.12-13, Note 1 p.31).
        Confidence: high.
  - "off_balance_sheet":
      * LIHTC -> never appears anywhere in HHFDC's own FY2025 financial
        statements (checked "LIHTC"/"Low-Income Housing Tax Credit" --
        zero matches; the ACFR's only tax-credit-named fund, "Tax Credit
        Assistance Program (TCAP)", is a distinct, one-time federal ARRA-era
        program, not LIHTC). Federal/state tax credits are allocated
        directly to developers/investors, matching this pilot series'
        identical IL/PA/OH LIHTC treatment.
      * HMMF -> the Multifamily Housing Revenue Bond Fund is named as one
        of HHFDC's own 5 non-major proprietary funds (Note 1, p.31), but
        the MD&A's own "Debt Administration" section (p.14) states: "the
        Corporation adopted GASB Statement No. 91, Conduit Debt
        Obligations, and therefore derecognized all conduit bonds payable
        under the Multifamily Housing Revenue Bond Fund" -- i.e. the bonds
        themselves are conduit debt, not an HHFDC balance-sheet liability,
        the same GASB-91 conclusion OHFA's build script reaches for its own
        Multifamily Bond Program. HHFDC's ACFR never uses the brand name
        "Hula Mae Multi-Family"/"HMMF" verbatim -- the match to the
        Multifamily Housing Revenue Bond Fund is by program description
        (both are HHFDC's tax-exempt multifamily bond-financing vehicle),
        confidence: medium.
      * GET -> a General Excise Tax exemption granted under state tax law,
        not an HHFDC-administered fund; never appears anywhere in the ACFR
        (checked "General Excise Tax"/"GET" -- zero matches).
      * 201H / EP -> HRS Chapter 201H's expedited-processing/exemption
        mechanism is a regulatory tool (relief from certain state and
        county approval requirements), not a financing vehicle; never
        appears anywhere in the ACFR (checked "201H"/"Expedited Processing"
        -- zero matches).
      * "Land" (VOK: Northwest Corner project's tag) -> contributed state
        land. Unlike DURF (which the same project also separately carries
        as its own tag, ruling out a Land==DURF redundancy), no fund in
        Note 1's list is described as the specific vehicle for this
        project's land contribution, so fund_type is left None (not
        off_balance_sheet, not proprietary/governmental -- genuinely
        unclassified) rather than guessed.
  - "lihtc_award" (the single subprogram under the "lihtc_reservations"
    category) and "hmmf_award" (under "hmmf_financing") reuse the same
    off_balance_sheet classification as the "lihtc"/"hmmf" tags above, for
    the identical reasons.

Geocoding
------------------------------------------------------------------------
Both Table 10 and Table 1 give only an island/county for each project (no
street address, no city/municipality -- a coarser precision tier than IL/
PA/OH, matching this pilot series' existing FL precedent). This script
geocodes every project to its county's centroid via Nominatim
("{County} County, Hawaii"), falling back to "{County}, Hawaii" if the
county-qualified query fails, and marks every project geocode_status=
"county_center" -- the same tier and the same rationale FL's build script
documents (no finer location is disclosed anywhere in the source document).
"Oahu" (Table 10/Table 1's own label) is queried as "Honolulu County,
Hawaii" (HHFDC's own Board-composition language, p.10, calls it "the City
and County of Honolulu"). Self-throttled to <=1 request/second with an
identifying User-Agent per Nominatim's usage policy; only 4 distinct county
queries are ever made for this state's 22 projects.

Rental Assistance Revolving Fund (RARF) / Rental Assistance Program (RAP)
------------------------------------------------------------------------
Per user request (2026-08-14), the Annual Report was re-searched for an
independent, ongoing per-unit rental-subsidy program (as distinct from the
three development-financing categories above). Section III.A.5, "RENTAL
ASSISTANCE REVOLVING FUND (RARF)" (p.25-26), states in full: "The Rental
Assistance Revolving Fund (RARF) funds the Rental Assistance Program (RAP),
which was created by the Legislature in 1981 to encourage the development
of new or existing rental properties while maintaining rental rates for low
and moderate-income families. The fund's purpose is to provide monthly
rental subsidies. As of June 30, 2025, there are seven projects comprised
of 1,215 rental units with RAP commitments totaling $29,324,009. Although
the program is no longer accepting new projects or funding, it continues
to honor existing commitments until they sunset." This is a genuinely
different population from "units_completed"/"lihtc_reservations"/
"hmmf_financing" above (all one-time construction/preservation financing)
-- RAP pays ongoing MONTHLY rental subsidies to existing tenants of already
-built projects, matching this pilot series' IL Section 811 PRA/RHS
precedent. No per-project table of the 7 RAP projects is published
anywhere in this report (checked; unlike Table 1/Table 10, RARF/RAP gets
only this one narrative paragraph), so this category carries no
RAW_PROJECTS of its own, the same "single-sentence-only" treatment already
used here for hmmf_financing.
IMPORTANT unreconciled conflict across HHFDC's own documents: HHFDC's
separately-issued FY2025 financial statements (FY2025/txt/HI_HHFDC_FY2025_
ACFR.txt) give a DIFFERENT dollar figure for what is described as the same
underlying commitment: Note 13, "Commitments and Contingencies" -> "Rental
Subsidy Commitments" states "At June 30, 2025, the Rental Assistance
Revolving Fund had aggregate outstanding rental subsidy commitments of
approximately $18,911,000" -- about 35% below the Annual Report's own
$29,324,009. The ACFR's Statement of Activities (condensed, MD&A) gives a
THIRD, differently-scoped figure: the "Rental assistance program"
business-type activity's own FY2025 EXPENSE line is $1,276 thousand (a
one-year expense/flow figure, not a stock of outstanding commitments -- not
comparable to either of the other two numbers). None of these three
figures is forced to reconcile with another, per this project's "never
force a reconciliation" rule -- fy2025_actual/fy2025_amounts below use the
Annual Report's own headline sentence (this category's primary source,
matching how "units_completed" also draws from the Annual Report rather
than the ACFR), and the conflicting ACFR figures are recorded here for
transparency only.
Fund-type classification: "proprietary", high confidence -- the Rental
Assistance Revolving Fund is named verbatim as one of HHFDC's 5 non-major
proprietary (enterprise) funds (MD&A p.12-13, Note 1 p.30-31, already
documented in this docstring's "Fund-type classification" section above),
and independently corroborated by the ACFR's own Note 13 quote above (same
fund name, verbatim).

fy2026
------------------------------------------------------------------------
Unlike PA/OH/FL, HHFDC's own report DOES disclose a genuine FY2026 forecast
for "units_completed": the "Five-Year Production Projection" table (p.39)
gives, for fiscal year 2026, New Construction 1,240 + Preservation 306 =
1,546 = For Rent 1,496 + For Sale 50 -- i.e. unlike the FY2025 Summary box
immediately above it, THIS table's own New Construction/Preservation split
DOES sum correctly to its own printed Total (1,546), and that Total also
correctly sums the five FY2026-2030 fiscal-year Totals (1,546 + 1,374 +
2,199 + 3,553 + 2,203 = 10,875, matching the Executive Director's own
"10,875 units ... expected to come online" claim on p.4). "units_completed"
therefore carries fy2026={value: 1546, amount: None, closed: False,
note_key: None} -- a real, disclosed number, not a placeholder. Neither
"lihtc_reservations" nor "hmmf_financing" has any FY2026 figure disclosed
anywhere in the report (checked -- no forward-looking LIHTC/HMMF dollar or
unit projection exists), so both keep the uniform
{value: None, amount: None, closed: False, note_key: "hiFy26NotePending"}
pending placeholder used throughout this pilot series.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "hi_program_activity.json"

SOURCE_URL = "https://dbedt.hawaii.gov/hhfdc/files/2026/01/2025-Annual-Report.pdf"
SOURCE_FILE = "HI_HHFDC_AnnualReport_FY2025.pdf"
RETRIEVED = "2026-08-14"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
GEOCODER_USER_AGENT = "us-hfa-data-map/1.0 (github.com/MD-ai-fin/us-hfa-data-map)"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "hiFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "units_completed",
        "unit_type": "units",
        "fy2025_actual": 1460,
        "fy2025_source_quote": (
            "\"HHFDC assisted in the delivery of 1,460 units that were placed in "
            "service and provided financing or development assistance for 10,875 "
            "units that are expected to come online in the coming years.\" "
            "(Executive Director's Welcome, p.4) Table 10, \"Projects Completed in "
            "FY 2025\" (p.38): 14 projects, Number of Units column sums to 1,460. "
            "The \"Summary of Projects Completed in FY 2025\" box directly below it "
            "(p.39) prints: New Construction 1,189 | Preservation 523 | For Rent "
            "1,460 | For Sale 0 | Total 1,460 -- HHFDC's own New Construction (1,189) "
            "+ Preservation (523) = 1,712 does NOT equal its own printed Total "
            "(1,460); this script reproduces HHFDC's own printed figures verbatim "
            "and does not attempt to force a reconciliation (see module docstring, "
            "\"The 1,189 + 523 vs. 1,460 discrepancy\")."
        ),
        "fy2025_amounts": [],
        "additive": False,
        "fy2026": {"value": 1546, "amount": None, "closed": False, "note_key": None},
        "subprograms": [
            {"key": "lihtc", "fy2025_units": 1356, "fy2025_amount": None,
             "color_group": "credit",
             # Never appears in HHFDC's own FY2025 financial statements
             # (checked "LIHTC"/"Low-Income Housing Tax Credit" -- zero
             # matches) -- federal/state tax credits are allocated directly
             # to developers/investors, not booked as an HHFDC fund asset.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "rhrf", "fy2025_units": 724, "fy2025_amount": None,
             "color_group": "capital",
             # Rental Housing Revolving Fund, one of HHFDC's own 4 major
             # proprietary (enterprise) funds (MD&A p.11, Note 1 p.30-31).
             "fund_type": "proprietary", "fund_name": "Rental Housing Revolving Fund",
             "fy2026": _FY26_PENDING},
            {"key": "hmmf", "fy2025_units": 657, "fy2025_amount": None,
             "color_group": "bond",
             # The Multifamily Housing Revenue Bond Fund is named as one of
             # HHFDC's 5 non-major proprietary funds (Note 1, p.31), but its
             # own MD&A "Debt Administration" section (p.14) confirms all
             # conduit bonds under that fund were derecognized per GASB 91 --
             # not an HHFDC balance-sheet liability. HHFDC's ACFR never uses
             # the brand name "Hula Mae Multi-Family"/"HMMF" verbatim --
             # match by program description, confidence: medium.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "home", "fy2025_units": 237, "fy2025_amount": None,
             "color_group": "trust",
             # HOME Investment Partnership Program, a major governmental
             # fund named verbatim (MD&A p.11-12, Note 1 p.30; SEFA p.76,
             # CFDA 14.239).
             "fund_type": "governmental", "fund_name": "HOME Investment Partnership Program",
             "fy2026": _FY26_PENDING},
            {"key": "htf", "fy2025_units": 237, "fy2025_amount": None,
             "color_group": "trust",
             # Housing Trust Fund Program, a major governmental fund named
             # verbatim (MD&A p.13, Note 1 p.30; SEFA p.76, CFDA 14.275).
             "fund_type": "governmental", "fund_name": "Housing Trust Fund Program",
             "fy2026": _FY26_PENDING},
            {"key": "get", "fy2025_units": 1192, "fy2025_amount": None,
             "color_group": "capital",
             # A General Excise Tax exemption granted under state tax law,
             # not an HHFDC-administered fund; never appears anywhere in the
             # ACFR (checked "General Excise Tax"/"GET" -- zero matches).
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "durf", "fy2025_units": 317, "fy2025_amount": None,
             "color_group": "capital",
             # Dwelling Unit Revolving Fund, one of HHFDC's own 4 major
             # proprietary (enterprise) funds (MD&A p.12-13, Note 1 p.31).
             "fund_type": "proprietary", "fund_name": "Dwelling Unit Revolving Fund",
             "fy2026": _FY26_PENDING},
            {"key": "201h", "fy2025_units": 72, "fy2025_amount": None,
             "color_group": "capital",
             # HRS Chapter 201H expedited-processing/exemption mechanism --
             # a regulatory tool, not a financing vehicle; never appears
             # anywhere in the ACFR.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "ep", "fy2025_units": 169, "fy2025_amount": None,
             "color_group": "capital",
             # Appears on only 1 of the 14 completed projects; Table 10
             # never states whether "EP" is the same mechanism as "201H"
             # above (both plausibly denote HRS Chapter 201H expedited
             # processing) -- kept as a separate, unmerged tag rather than
             # assumed identical. Never appears anywhere in the ACFR.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "home_arp", "fy2025_units": 32, "fy2025_amount": None,
             "color_group": "trust",
             # Never named separately in the ACFR or the Schedule of
             # Expenditures of Federal Awards (p.76 lists only "HOME
             # Investment Partnership Program" CFDA 14.239, "Housing Trust
             # Fund" CFDA 14.275, and a COVID-19 ARPA "Homeowner Assistance
             # Fund" CFDA 21.026) -- inferred to sit inside the same HOME
             # Investment Partnership Program governmental fund as ordinary
             # HOME, since HOME-ARP is HUD's own supplemental appropriation
             # to the same CFDA-14.239 program family. Confidence: medium.
             "fund_type": "governmental", "fund_name": "HOME Investment Partnership Program (HOME-ARP, inferred)",
             "fy2026": _FY26_PENDING},
            {"key": "land", "fy2025_units": 200, "fy2025_amount": None,
             "color_group": "capital",
             # Contributed state land (VOK: Northwest Corner project only).
             # No fund in Note 1's list is described as the specific
             # vehicle for a land contribution distinct from DURF (which
             # the same project separately carries as its own tag) --
             # genuinely unclassified rather than guessed.
             "fund_type": None, "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "lihtc_reservations",
        "unit_type": "units",
        "fy2025_actual": 1234,
        "fy2025_source_quote": (
            "\"During 2025, HHFDC awarded LIHTC reservations to 8 affordable "
            "housing projects, supporting the new construction or rehabilitation of "
            "1,234 units\" (p.13-14). Table 1, \"2025 Low-Income Housing Tax Credit "
            "Award Reservations\" (p.14): 8 projects, Total Units column sums to "
            "1,234. NOTE: unlike \"units_completed\" (a fiscal-year, July 2024-June "
            "2025 figure), Table 1 covers CALENDAR year 2025 (Jan-Dec 2025) -- "
            "\"When presenting facts on financing awards, HHFDC adheres to a "
            "calendar year schedule\" (p.13) -- a different, only partially "
            "overlapping 12-month window (see module docstring)."
        ),
        "fy2025_amounts": [
            {"label_key": "hi_amt_lihtc_allocation", "amount": 4988856},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "lihtc_award", "fy2025_units": 1234, "fy2025_amount": None,
             "color_group": "credit",
             # Same off_balance_sheet reasoning as the "lihtc" tag under
             # "units_completed" above -- never appears in HHFDC's own
             # FY2025 financial statements.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "hmmf_financing",
        "unit_type": "units",
        "fy2025_actual": 1333,
        "fy2025_source_quote": (
            "\"In 2025, HHFDC awarded $357,006,367 in HMMF financing, which will "
            "assist with the construction of 1,333 affordable housing units "
            "statewide.\" (p.16) NOTE: like \"lihtc_reservations\" above, this is a "
            "CALENDAR year 2025 figure, not a fiscal-year one (see module "
            "docstring). No per-project table in this report ties precisely to "
            "this $357,006,367/1,333-unit figure -- Table 6, \"Issuance of Bonds "
            "for Construction\" (p.18), is the closest candidate but covers a "
            "narrower/different population (bonds actually issued during FY2025, "
            "not awarded during CY2025): 8 projects, 1,279 units, $335,332,934. "
            "This category therefore carries no project-level detail of its own "
            "rather than force an unverifiable mapping (see module docstring)."
        ),
        "fy2025_amounts": [
            {"label_key": "hi_amt_hmmf_financing", "amount": 357006367},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "hmmf_award", "fy2025_units": 1333, "fy2025_amount": 357006367,
             "color_group": "bond",
             # Same off_balance_sheet/GASB-91-conduit-debt reasoning as the
             # "hmmf" tag under "units_completed" above.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        # Section III.A.5, "RENTAL ASSISTANCE REVOLVING FUND (RARF)" -- an
        # ongoing, per-unit MONTHLY rental subsidy program, structurally
        # different from the three development-financing categories above
        # (see module docstring's "Rental Assistance Revolving Fund (RARF) /
        # Rental Assistance Program (RAP)" section for the full narrative
        # quote and the unreconciled $18,911,000/$1,276,000 ACFR figures).
        "key": "rental_assistance_program",
        "unit_type": "units",
        "fy2025_actual": 1215,
        "fy2025_source_quote": (
            "\"The Rental Assistance Revolving Fund (RARF) funds the Rental "
            "Assistance Program (RAP), which was created by the Legislature in "
            "1981 to encourage the development of new or existing rental "
            "properties while maintaining rental rates for low and moderate-"
            "income families. The fund's purpose is to provide monthly rental "
            "subsidies. As of June 30, 2025, there are seven projects comprised "
            "of 1,215 rental units with RAP commitments totaling $29,324,009. "
            "Although the program is no longer accepting new projects or "
            "funding, it continues to honor existing commitments until they "
            "sunset.\" (p.25-26). No per-project table is published for RAP's 7 "
            "projects anywhere in this report -- unlike Table 1/Table 10, this "
            "program gets only this one narrative paragraph -- so this category "
            "carries no RAW_PROJECTS of its own. HHFDC's own separately-issued "
            "FY2025 ACFR gives a DIFFERENT commitment total for the same fund "
            "(Note 13: \"approximately $18,911,000\" of outstanding rental "
            "subsidy commitments at June 30, 2025) and a third, differently-"
            "scoped figure (Statement of Activities: $1,276 thousand of FY2025 "
            "\"Rental assistance program\" business-type-activity EXPENSE, a "
            "one-year flow figure, not a commitment stock) -- neither is forced "
            "to reconcile with the Annual Report's own $29,324,009 headline "
            "used here; see module docstring."
        ),
        "fy2025_amounts": [
            {"label_key": "hi_amt_rap_commitments", "amount": 29324009},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "rap", "fy2025_units": 1215, "fy2025_amount": 29324009,
             "color_group": "trust",
             # Rental Assistance Revolving Fund, one of HHFDC's own 5
             # non-major proprietary (enterprise) funds (MD&A p.12-13, Note 1
             # p.30-31; independently corroborated by the ACFR's own Note 13,
             # "Rental Subsidy Commitments" -- same fund name verbatim).
             "fund_type": "proprietary", "fund_name": "Rental Assistance Revolving Fund (RARF)",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# ---------------------------------------------------------------------------
# Project-level detail. Two source tables, both giving only an island/county
# (no street address, no municipality):
#   - Table 10, "Projects Completed in FY 2025" (p.38): 14 projects, each
#     tagged with its own financing/regulatory-tool combination from the
#     "units_completed" category's 11 subprogram tags above.
#   - Table 1, "2025 LIHTC Award Reservations" (p.14): 8 projects, each
#     tagged with the single "lihtc_award" tag.
# (name, county, units, [tag keys], table)
# ---------------------------------------------------------------------------

RAW_PROJECTS = [
    # --- Table 10: Projects Completed in FY 2025 (14 projects, 1,460 units) ---
    ("Hale Na Koa O Hanakahi (fka West Kawili Street Senior/Veteran Housing)",
     "Hawaii", 92, ["lihtc", "rhrf", "hmmf", "home", "htf", "get"], "t10"),
    ("Hocking Hale (Hocking Building)", "Honolulu", 40,
     ["lihtc", "rhrf", "get"], "t10"),
    ("Jack Hall Waipahu Apartments", "Honolulu", 144, ["lihtc", "get"], "t10"),
    ("Kai Olino Phase 1 Bldg B", "Kauai", 24, ["lihtc"], "t10"),
    ("Kai Olino Phase 2", "Kauai", 27, ["lihtc", "rhrf"], "t10"),
    ("Kauhale I Ke Kula Uka (fka Kaloko Heights)", "Hawaii", 100,
     ["lihtc", "rhrf", "hmmf", "home", "htf"], "t10"),
    ("Koa Vista 1", "Honolulu", 96, ["lihtc", "rhrf", "hmmf", "get"], "t10"),
    ("Lima Ola, Phase 1 - Lot 1 - Permanently Supportive Housing Project (MF RH Units)",
     "Kauai", 32, ["home_arp", "durf"], "t10"),
    ("Lima Ola, Phase 1 - Lot 2 Senior MF RH Units", "Kauai", 40,
     ["lihtc", "durf"], "t10"),
    ("Lima Ola, Phase 1 - Lot 45 Family MF RH Units", "Kauai", 45,
     ["lihtc", "home", "htf", "durf"], "t10"),
    ("Maunakea Tower Apartments", "Honolulu", 379, ["lihtc", "get"], "t10"),
    ("Parkway Village at Kapolei - Lot 7", "Honolulu", 169,
     ["lihtc", "rhrf", "hmmf", "ep", "get"], "t10"),
    ("Villages of Leialii (VOL): Kaiaulu O Kukuia (fka Keawe Street Apartments)",
     "Maui", 200, ["lihtc", "rhrf", "hmmf", "durf", "land", "get"], "t10"),
    ("Wailuku Apartments (aka Kaulana Mahina Workforce Housing)", "Maui", 72,
     ["201h", "get"], "t10"),
    # --- Table 1: 2025 LIHTC Award Reservations (8 projects, 1,234 units) ---
    ("Aikanaha Residences", "Maui", 212, ["lihtc_award"], "t1"),
    ("Honuaula Living Community", "Hawaii", 105, ["lihtc_award"], "t1"),
    ("Hoonanea - Phase 1 at Hoopili Gateway", "Honolulu", 191, ["lihtc_award"], "t1"),
    # Table 1 prints "Kehalani Apartments Oahu 35" -- corrected to Maui here;
    # cross-validated by Table 3 (p.17, "Kehalani Apartments Maui
    # $13,000,000"), Table 8 (p.21, "Kehalani Apartments Maui 3 35 8.6%"),
    # and Table 13 (p.42, "Kehalani Apartments ... 35" under MAUI COUNTY) --
    # all 3 other same-document tables agree on Maui; a data-entry slip in
    # Table 1's own county column, not a fabrication (see module docstring).
    ("Kehalani Apartments", "Maui", 35, ["lihtc_award"], "t1"),
    ("Laulima Ph 4 - Maluhia", "Honolulu", 70, ["lihtc_award"], "t1"),
    ("VOK: Northwest Corner (Leiwili Kapolei) Buildings B&C", "Honolulu", 344,
     ["lihtc_award"], "t1"),
    ("Melia", "Honolulu", 247, ["lihtc_award"], "t1"),
    ("Villages of Laiopua - V4 Hema RP", "Hawaii", 30, ["lihtc_award"], "t1"),
]

# Independently computed once, directly off the transcribed Table 10 rows
# above, BEFORE this module's own EXPECTED_TAG_TALLIES constant was written
# -- Table 10 prints no per-tag subtotal of its own to check against, so
# this is an internal transcription-integrity check (recomputed by
# verify_tag_tallies() below), matching this pilot series' PHFA/OHFA
# "EXPECTED_SOURCE_TOTALS computed once, then checked" convention.
EXPECTED_TAG_TALLIES = {
    # key: (unit_sum, project_count)
    "lihtc": (1356, 12),
    "rhrf": (724, 7),
    "hmmf": (657, 5),
    "home": (237, 3),
    "htf": (237, 3),
    "get": (1192, 8),
    "durf": (317, 4),
    "201h": (72, 1),
    "ep": (169, 1),
    "home_arp": (32, 1),
    "land": (200, 1),
}

# Hawaii's own island->county naming: Table 10/Table 1 both print "Oahu" for
# what HHFDC's own governance-structure text (p.10) calls "the City and
# County of Honolulu". Geocoding queries below use "Honolulu County, Hawaii".
COUNTY_GEOCODE_NAME = {
    "Hawaii": "Hawaii", "Kauai": "Kauai", "Maui": "Maui", "Honolulu": "Honolulu",
}

FUNDING_COLOR_GROUP = {
    "lihtc": "credit", "lihtc_award": "credit",
    "hmmf": "bond", "hmmf_award": "bond",
    "home": "trust", "htf": "trust", "home_arp": "trust",
    "rhrf": "capital", "durf": "capital", "get": "capital",
    "201h": "capital", "ep": "capital", "land": "capital",
}
# priority order for picking a project's single "primary" color when it has
# multiple tags (first match wins) -- HMMF (bond) and LIHTC (credit) are the
# largest-scale tools on the projects that carry them, so they lead.
FUNDING_PRIORITY = ["hmmf", "hmmf_award", "lihtc", "lihtc_award", "home",
                     "htf", "home_arp", "rhrf", "durf", "get", "201h", "ep", "land"]


def verify_units_completed():
    t10 = [p for p in RAW_PROJECTS if p[4] == "t10"]
    if len(t10) != 14:
        raise SystemExit(f"Table 10 project count: expected 14, got {len(t10)}")
    total = sum(units for _n, _c, units, _tags, _t in t10)
    if total != 1460:
        raise SystemExit(
            f"Table 10 units sum: expected 1,460 (Table 10's own printed "
            f"total, p.38, matching the Executive Director's \"1,460 units "
            f"... placed in service\", p.4), got {total:,}"
        )
    print("Table 10 (\"Projects Completed in FY 2025\"): 14 projects, units sum = "
          "1,460 -- verified against the table's own printed total.")


def verify_lihtc_reservations():
    t1 = [p for p in RAW_PROJECTS if p[4] == "t1"]
    if len(t1) != 8:
        raise SystemExit(f"Table 1 project count: expected 8, got {len(t1)}")
    total = sum(units for _n, _c, units, _tags, _t in t1)
    if total != 1234:
        raise SystemExit(
            f"Table 1 units sum: expected 1,234 (Table 1's own printed "
            f"total, p.14, matching the narrative directly above it), got "
            f"{total:,}"
        )
    print("Table 1 (\"2025 LIHTC Award Reservations\"): 8 projects, units sum = "
          "1,234 -- verified against the table's own printed total.")


def verify_tag_tallies():
    t10 = [p for p in RAW_PROJECTS if p[4] == "t10"]
    unit_sums = {}
    counts = {}
    for _name, _county, units, tags, _table in t10:
        for tag in tags:
            unit_sums[tag] = unit_sums.get(tag, 0) + units
            counts[tag] = counts.get(tag, 0) + 1
    errors = []
    for key, (exp_units, exp_count) in EXPECTED_TAG_TALLIES.items():
        got_units = unit_sums.get(key, 0)
        got_count = counts.get(key, 0)
        if got_units != exp_units:
            errors.append(f"{key} unit_sum: expected {exp_units:,}, got {got_units:,}")
        if got_count != exp_count:
            errors.append(f"{key} count: expected {exp_count}, got {got_count}")
    if set(unit_sums) != set(EXPECTED_TAG_TALLIES):
        errors.append(
            f"tag set mismatch: RAW_PROJECTS has {sorted(unit_sums)}, "
            f"EXPECTED_TAG_TALLIES has {sorted(EXPECTED_TAG_TALLIES)}"
        )
    if errors:
        raise SystemExit("Tag tally mismatch(es):\n" + "\n".join(errors))
    print(f"Table 10 financing/regulatory-tool tags ({len(EXPECTED_TAG_TALLIES)} "
          f"tags across 14 projects) verified against the independently "
          f"pre-computed EXPECTED_TAG_TALLIES.")


def verify_rental_assistance_program():
    """Cross-checks the rental_assistance_program category's own headline
    figures against its single subprogram (a trivial 1:1 check, since RAP
    has no per-project exhibit to sum) -- and documents, without forcing a
    reconciliation, HHFDC's own conflicting ACFR figures (see module
    docstring)."""
    cat = next(c for c in CATEGORIES if c["key"] == "rental_assistance_program")
    sp = cat["subprograms"][0]
    errors = []
    if sp["fy2025_units"] != cat["fy2025_actual"]:
        errors.append(f"rap units: category says {cat['fy2025_actual']}, subprogram says {sp['fy2025_units']}")
    if sp["fy2025_amount"] != cat["fy2025_amounts"][0]["amount"]:
        errors.append(
            f"rap amount: category says {cat['fy2025_amounts'][0]['amount']}, subprogram says {sp['fy2025_amount']}"
        )
    if errors:
        raise SystemExit("Rental assistance program mismatch(es):\n" + "\n".join(errors))
    print(
        "Rental Assistance Program (RARF/RAP) verified: 1,215 units / $29,324,009 "
        "commitments, matching the Annual Report's own Section III.A.5 headline "
        "sentence. NOTE (not reconciled, per module docstring): HHFDC's own FY2025 "
        "ACFR Note 13 separately states approximately $18,911,000 of outstanding "
        "rental subsidy commitments for the same fund, and its Statement of "
        "Activities separately gives $1,276 thousand of FY2025 'Rental assistance "
        "program' business-type-activity expense (a different, flow-based figure)."
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
    for name, county, units, tags, table in RAW_PROJECTS:
        geo_name = COUNTY_GEOCODE_NAME[county]
        query = f"{geo_name} County, Hawaii"
        coords = geocode(query, cache)
        status = "county_center"
        if coords is None:
            coords = geocode(f"{geo_name}, Hawaii", cache)
            status = "county_center" if coords else "unresolved"
        primary = next((s for s in FUNDING_PRIORITY if s in tags), tags[0])
        projects.append({
            "id": name.lower().replace(" ", "-").replace("'", "").replace(".", "")
                        .replace("&", "and").replace(",", "").replace("(", "")
                        .replace(")", "").replace(":", "").replace("/", "-"),
            "name": name,
            "address": None,
            "city": county,
            "lat": round(coords[0], 5) if coords else None,
            "lon": round(coords[1], 5) if coords else None,
            "units": units,
            "funding_sources": tags,
            "source_amounts": {},
            "total_amount": None,
            "primary_color_group": FUNDING_COLOR_GROUP[primary],
            "overlaps": len(tags) > 1,
            "geocode_status": status,
        })
    return projects


def main():
    verify_units_completed()
    verify_lihtc_reservations()
    verify_tag_tallies()
    verify_rental_assistance_program()
    print("Geocoding project counties via Nominatim...")
    projects = build_projects()
    unresolved = [p["name"] for p in projects if p["geocode_status"] == "unresolved"]
    if unresolved:
        print(f"  {len(unresolved)} project(s) could not be geocoded: {unresolved}")
    print(f"  {sum(1 for p in projects if p['geocode_status'] == 'county_center')} "
          f"project(s) resolved to county-center coordinates.")

    payload = {
        "HI": {
            "hfa_name": "Hawaii Housing Finance and Development Corporation",
            "hfa_abbr": "HHFDC",
            "fiscal_year": "FY2025",
            "source_title": "HHFDC FY 2025 Annual Report -- Housing Production Summary (Table 10), 2025 LIHTC Award Reservations (Table 1), and HMMF financing narrative",
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
