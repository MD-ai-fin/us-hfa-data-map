"""
Builds docs/mi_program_activity.json from MSHDA's FY2025 Production Goals
Report -- a statutory report to the Governor and Legislature (Michigan
P.A. 346 of 1966, Sec. 32(14)) covering MSHDA's fiscal year July 1, 2024
through June 30, 2025 -- plus MSHDA's own separately-issued FY2025 audited
financial statements (used ONLY for GASB fund-type classification).

Sources
---------------------------------------------------------------------------
1. "FY 2025 Production Goals Report" (memo dated February 26, 2026, from
   Amy Hovey, MSHDA CEO/Executive Director, to Governor Whitmer and the
   Legislature):
     https://www.michigan.gov/mshda/-/media/Project/Websites/mshda/about/reports/production/FY25-Production-Goals-Report.docx
   Entry page: https://www.michigan.gov/mshda/about/transparency-and-reports
   Local copy: FY2025/program_activity/pdf/MI_MSHDA_ProductionGoalsReport_FY2025.pdf
   IMPORTANT: despite the ".docx" suffix in the URL, the server actually
   returns a real PDF (verified via `curl -I`: "Content-Type:
   application/pdf", "Content-Disposition: inline; filename=\"FY25
   Production Goals Report.pdf\""). This was checked before download, not
   assumed -- see the task briefing's own warning about this URL.
2. MSHDA's own FY2025 audited financial statements ("Michigan State
   Housing Development Authority Financial Report with Supplementary
   Information, June 30, 2025"), used only for the fund-type
   classification below:
     FY2025/txt/MI_MSHDA_FY2025_ACFR.txt
   Verified (before use) to actually be MSHDA's own statements, not a
   different report: the file's own title page and running headers read
   "Michigan State Housing Development Authority (a component unit of the
   State of Michigan) Financial Report with Supplementary Information June
   30, 2025", the independent auditor's report is addressed to "the Board
   of Directors and Mr. Doug A. Ringler, CPA, CIA, Auditor General, State
   of Michigan[,] Michigan State Housing Development Authority", and MD&A
   (p.4 equivalent) opens "Michigan State Housing Development Authority
   (MSHDA or the 'Authority') was created by the Michigan Legislature
   under the provisions of the State Housing Development Authority Act of
   1966" -- i.e. this is the real, correctly-scoped source, not another
   state's report mislabeled (a mismatch several other states' build
   scripts in this project have had to catch and flag).

A marketing-style companion document, "MSHDA FY2025: A Year of Housing
Impact" (https://www.michigan.gov/mshda/-/media/Project/Websites/mshda/about/MSHDA-FY-2025-A-Year-Of-Housing-Impact.pdf),
was used only as a cross-check on the executive-summary headline figures
below, never as a data source in its own right. MSHDA's "Year At-A-Glance"
page was deliberately NOT used -- per the task briefing, that page
currently still displays FY2024 data and would have been a silent
wrong-year substitution.

Executive-summary headline reconciliation ($2.610B / 12,414 units)
---------------------------------------------------------------------------
The memo's own headline states: "In fiscal year 2024-2025, MSHDA's total
investment in housing for low- and moderate-income Michiganders was $2.610
billion, serving nearly 45,000 households. MSHDA contributed $2.193
billion in funding toward home mortgages or newly constructed,
rehabilitated, and financed units of housing, resulting in 10,569 new,
improved, or newly owned units; $287 million in rental assistance; $28.8
million in Homeless Prevention grants; $50.7 million in Neighborhood
Development grants, and $49.8 million in Housing Solutions grants ...
MSHDA surpassed its goal by producing or financing the rehabilitation or
purchase of 12,414 housing units."

Unlike PA's Homeownership category or FL's two rental-unit totals (where
the headline figure does NOT equal the sum of the published sub-figures),
MSHDA's own $2.610B / 12,414-unit headline reconciles EXACTLY once each
of this script's six categories' own officially-printed production totals
is added up -- this was independently verified against the report's own
underlying tables, not assumed:
  - Multifamily Rental Development: 5,324 units, $1,417,752,404
  - Homeownership: 5,245 loans, $775,416,034 (the mortgage-loan total;
    Michigan Mortgage Credit Certificate Program's separate 96
    certificates / $15,576,056 is NOT part of this -- see below)
  - Rental Assistance: 32,595 households, $287,224,953
  - Homeless Prevention Grants: $28,826,165 (140 grants; no household/unit
    count is disclosed for grants, so none is used as "units" here)
  - Neighborhood Development: 1,404 units, $50,721,396
  - Housing Solutions: 441 units, $49,794,351
Units: 5,324 + 5,245 = 10,569 (matches "$2.193 billion ... 10,569 ...
units" EXACTLY) ; 10,569 + 1,404 + 441 = 12,414 (matches the report's own
"12,414 housing units" EXACTLY -- Rental Assistance and Homeless
Prevention Grants are service/grant metrics, not "produced or financed"
units, and are correctly excluded from this count by MSHDA itself).
Dollars: $1,417,752,404 + $775,416,034 + $287,224,953 + $28,826,165 +
$50,721,396 + $49,794,351 = $2,609,735,303, which rounds to the stated
"$2.610 billion" and matches EXACTLY the separately-printed "Investment in
Housing for Low- and Moderate-Income Michiganders ... Dollars Invested
$2,609,735,303" figure on the report's own front page. (The Homeownership
division's Michigan Mortgage Credit Certificate Program dollars,
$15,576,056, are deliberately excluded here -- MCC issues a federal tax
certificate, not an MSHDA loan, and including it would overshoot
$2,609,735,303 by exactly that amount.) The front page's separately-stated
"nearly 45,000 households" (44,873) does not decompose cleanly across
these six categories (Multifamily is counted in *units*, not households)
and is not reproduced or forced into any field below.

Category-level methodology and double-verification gates
---------------------------------------------------------------------------
Every category below carries its own double gate: the RAW_PROJECTS/
subprogram unit total AND dollar total both independently reproduce a
number MSHDA itself printed somewhere in the report (see verify_*()
below). All six categories' internal breakdowns were extracted with
pdfplumber's word-level x/y coordinates, NOT pdftotext -- pdftotext -layout
was tried first and found to silently misalign entire rows of the wide
Exhibit 1/2 tables (e.g. it dropped "725 Amsterdam - Affordable"'s Oct-24
Funding Round and its 40/40 unit values entirely, and it mislabeled
"Westbury Apartments" as "Direct Lending" when the PDF's own word
coordinates show it is in fact a "Pass-Through" row) -- this is the same
class of pdftotext-layout column-misalignment bug this project has
previously only documented for MI's Exhibit 6/7-style wide grant tables,
but it turned out to also corrupt Exhibit 1/2's narrower project tables,
so this script uses pdfplumber's coordinate-clustered word extraction for
every table in this file, not just Exhibit 6/7.

1. Multifamily Rental Development (RAW_PROJECTS = Exhibit 1 + Exhibit 2):
   Exhibit 1 ("FY 2024-2025 Projects Receiving 9% LIHTC Allocations") has
   25 rows (not the ballpark ~39 in the original task briefing -- that was
   an estimate, the PDF's actual row count is smaller); Exhibit 2 ("...
   Receiving 4% LIHTC Allocations") has 39 rows (10 Pass-Through + 29
   Direct Lending), for 64 RAW_PROJECTS total. Neither exhibit prints its
   own subtotal row (same situation PA's Map Doc was in), so this script
   independently sums each exhibit's own "9% Total Units" / "4% Total
   Units" columns via pdfplumber and checks the sums against MSHDA's own
   *narrative* "Production Goal Achievement" tables elsewhere in the
   report (which DO print official totals): 9% LIHTC 1,137 units /
   $314,483,080 (10-year credit); 4% LIHTC Pass-Through (~= "Short-Term
   Pass-Through Loans") 1,290 units / $160,516,518 (loan dollars); 4%
   LIHTC Direct Lending ("Direct Lending") 1,989 units / $499,931,256
   (loan dollars). Exhibit 1's own re-summed total (1,137) and Exhibit 2's
   Pass-Through re-summed total (1,290) match their respective official
   figures EXACTLY. Exhibit 2's Direct Lending rows re-sum to 1,954, 35
   units short of the official 1,989 -- MSHDA's own footnote 4 explains
   the gap: "The dollars and unit counts for these refinancings are
   accounted for in the Direct Lending section above," referring to a
   separately-disclosed "Multifamily Loan Programs Loan Refinancings"
   line ($184,065,065 across 15 refinancings) that has no development
   names or addresses anywhere in the report. Rather than force a
   reconciliation or invent 15 unnamed placeholder projects, this script
   (matching FL's precedent of preferring the fully project-traceable
   figure) uses MSHDA's own official 1,989/$499,931,256 for the
   lihtc_4pct_direct_lending SUBPROGRAM total (since that IS what MSHDA
   itself reports as "Direct Lending" production), while RAW_PROJECTS
   itself only contains the 29 individually named/addressed Direct-Lending
   developments (summing to 1,954 units) -- the remaining 35 units are
   not attributable to any named development in this report and are
   therefore not drawn on the map.
   A second, smaller anomaly: Exhibit 1's own row for "The Preserve on Ash
   II" prints BOTH a 9% Total/LIHTC Units figure (31/31) AND a 4% Total/
   LIHTC Units figure (60/60) -- i.e. this one development appears to have
   received some 4% allocation too, but it has no corresponding row of its
   own in Exhibit 2, and the report gives no Pass-Through-vs-Direct-Lending
   typing for that 60-unit figure. To avoid fabricating an unconfirmed
   funding-source type, RAW_PROJECTS uses only this row's confirmed 9%
   figure (31 units, funding_sources=["lihtc_9pct"]) for this project's
   marker; the 60 4%-side units are excluded from RAW_PROJECTS and were
   never included in any subprogram sum above either, so there is no
   double-counting risk to the category's own unit/dollar gates.
   additive=True: unlike FL's rental_multifamily category (non-additive,
   because most of its 81 projects draw on 2-3 funding sources
   *simultaneously*, so summing its 11 funding-source columns would
   massively over-count physical units), MSHDA's own "Total Units
   Developed" headline (5,324) is independently confirmed to be the CLEAN,
   non-overlapping sum of this category's six financing-program buckets:
   1,137 (9% LIHTC) + 1,290 (4% Pass-Through) + 1,989 (4% Direct Lending) +
   478 (Missing Middle) + 380 (EAHF) + 50 (H-TIF) = 5,324 exactly. Each
   subprogram's fy2025_amount below is its own single most meaningful
   dollar figure (10-year LIHTC credit value for 9%, since it has no loan
   counterpart; MSHDA loan dollars for Pass-Through/Direct Lending, since
   that is the capital MSHDA actually deployed) -- summing these six
   dollar figures gives $1,027,530,854, NOT the category's own printed
   $1,417,752,404 headline. The $390,221,550 gap is exactly the 4% LIHTC
   Pass-Through + Direct Lending 10-year credit VALUE ($129,885,890 +
   $260,335,660) -- MSHDA's own "Total MSHDA Dollars" headline evidently
   adds the tax-credit value of the 4% deals on top of the loan dollars
   for those same deals (a deliberate double-lens "total investment"
   figure on MSHDA's part, not a data error), which is why this script
   does not attempt to force the six subprogram amounts to sum to the
   category headline -- see fy2025_source_quote.
   Neither Exhibit 1 nor Exhibit 2 discloses a per-project dollar amount
   (unlike PA's Map Doc or FL's Rental Properties table), so every
   RAW_PROJECTS entry here has source_amounts={} and total_amount=None --
   this is a genuine gap in what MSHDA discloses, not an omission by this
   script.

2. Homeownership ("Single-Family Homeownership Mortgages Production Goal
   Achievement" table): a clean, fully additive partition -- MI 10K Down
   Payment Assistance (4,334 loans, $666,134,529) + MSHDA First-Generation
   DPA (241, $33,092,081) + MSHDA Rate-Relief Mortgage Program (300,
   $41,704,260) + Single-Family Loans w/ no DPA or Rate-Relief (370,
   $34,485,164) sum EXACTLY to the table's own printed "Total # of Loans"
   (5,245) and "Total $'s Loaned" ($775,416,034) -- unlike PA's
   K-FIT/Advantage/PENNVEST (assistance riding on a SUBSET of purchase
   loans), MSHDA's four buckets are mutually exclusive categories of the
   *same* 5,245 loans. The separate Michigan Mortgage Credit Certificate
   Program (96 certificates, $15,576,056) is a different production axis
   (# of certificates, not # of loans) and is not folded in here -- see
   the $2.610B headline reconciliation above for why it is excluded, not
   merely ignored.

3. Rental Assistance ("Rental Assistance Programs" table, 9 HUD voucher
   types): households are additive and clean -- the 9 rows sum to 32,595,
   EXACTLY matching this table's own printed "Total Number ... of Rental
   Assistance" row. Dollars are NOT as clean: the 9 rows' own individually-
   printed dollar figures sum to $288,082,211, but the table's own Total
   row prints $287,224,953 -- a $857,258 gap that is EXACTLY the "Key to
   Own" row's own dollar figure ($857,258), i.e. the printed Total row
   appears to have been computed before Key to Own's dollars were added to
   the table, even though Key to Own's 136 households clearly ARE included
   in the printed Total row's household count (32,595). This looks like a
   genuine arithmetic slip in MSHDA's own table (the same class of
   printed-total-vs-summed-rows inconsistency PA's PHARE table has), not
   an extraction error -- both figures were independently re-verified
   directly off the PDF's own cells with pdfplumber. This script does not
   force a reconciliation: fy2025_amounts uses MSHDA's own printed Total
   ($287,224,953) verbatim, while each subprogram below keeps its own
   individually-printed dollar figure (including Key to Own's), so the
   sub-chips' displayed amounts will not sum to the category's own
   fy2025_amounts total -- this is documented, not hidden.
   Separately, the report's own front-page executive-summary box states a
   DIFFERENT households-served figure for this same category, 32,459 --
   exactly the sum of this table's first 8 rows (all but Key to Own's 136
   households), suggesting the front-page box excludes Key to Own from its
   household count too (consistently with the dollar gap above) while the
   detailed table's own Total row includes Key to Own's households but not
   its dollars. This script uses 32,595 (the fully-itemized table's own
   printed household total) as fy2025_actual, and quotes 32,459 in
   fy2025_source_quote for transparency, without forcing the two to
   reconcile.

4. Homeless Prevention Grants ("Homeless Grants funded by MSHDA" table, 9
   grant types): additive by both grant-count (140) and dollars
   ($28,826,165), both matching this table's own printed Total row
   exactly. No household/unit count is disclosed for any of these 9 grant
   types (unlike PA's PHARE, which is the same kind of dollars-only
   category), so unit_type="dollars" and fy2025_actual=None, matching
   PA's phare_funding precedent.

5. Neighborhood Development ("Grants to Local Units of Government &
   Nonprofit Organizations" table plus "Discontinued Programs with Legacy
   Data"): a two-level rollup, fully verified. CDBG Housing Improving
   Local Livability (CHILL) Program (6 grants, $2,303,150, 86 units) + MI
   Neighborhood 1.0 (77, $35,041,685, 846 units) + MI Neighborhood 2.0
   (29, $12,916,250, 466 units) sum EXACTLY to the table's own printed "MI
   Neighborhood Grants" subtotal row (112 grants, $50,261,085, 1,199 rehab
   + 199 new = 1,398 units... actually 1,199+199=1,398; the table's own
   combined unit figure was cross-checked directly against this
   script's re-sum and both landed on 1,398, see verify_neighborhood_
   totals()). Adding the legacy "MSHDA Investing in Community Housing
   (MICH)" line (4 grants, $460,311, 6 units) reproduces the section's own
   front-of-page header total EXACTLY: 116 grants, $50,721,396, 1,404
   units.
   ("Rehab Units" and "New Units" are MSHDA's own two sub-columns of a
   single physical "Units" figure -- e.g. CHILL's 86 units are all rehab,
   0 new; this script uses the combined rehab+new figure as each
   subprogram's fy2025_units, matching how the section's own front-page
   header combines them into one number.)

6. Housing Solutions ("Grants to Local Units of Government & Nonprofit
   Organizations" table under "Housing Solutions Grants"): additive,
   5 grant types sum EXACTLY to the section's own front-of-page header:
   MSHDA Legislative Enhancement Grants (15, $44,210,000, 441 units) +
   Housing Readiness Incentive Grant Program (50, $2,326,850, 0) +
   Housing Development Fund (HDF) Collaborative Grants (9, $1,567,981, 0)
   + Housing & Community Development Fund (HCDF) Grants (8, $1,200,020,
   0) + Tribal Nations Housing Development Assistance Program (TNHDAP)
   (6, $489,500, 0) = 88 grants, $49,794,351, 441 units.

Fund-type classification (fund_type/fund_name on each subprogram)
---------------------------------------------------------------------------
MSHDA's own FY2025 financial statements state: "The Authority, as a
special purpose entity, is a component unit of the State of Michigan and
is reported as an enterprise fund in the State's Annual Comprehensive
Financial Report ... [and] presents all funds in a single-column
presentation" of business-type activities (Note 1/MD&A). Like Florida
Housing (and unlike IHDA's 7 major governmental + 4 major proprietary +
14 nonmajor governmental funds), MSHDA carries NO governmental funds of
its own -- so, as with FL, the "governmental" value of fund_type is never
used anywhere in this file. MSHDA's own Supplementary "Statement of Net
Position Information" (pp.56-57 of the audited statements) additionally
breaks its single enterprise fund into named internal "Activities":
Single-family Mortgage Revenue Bonds, Rental Housing Revenue Bonds,
General Obligation Bonds, General Operating, Escrow and Capital Reserve,
Federal and State [Reserve] Funds, and Other -- this combining schedule is
the primary evidence used below.
  - "proprietary" (named MSHDA-carried balance, high confidence):
      * lihtc_4pct_pass_through, lihtc_4pct_direct_lending -- "Rental
        Housing Revenue Bonds" activity column carries $1,913,583
        thousand of "Multifamily mortgage loans" (construction-in-progress
        + completed construction) on MSHDA's own Statement of Net
        Position Information (p.56); Note 5, Bonds Payable, describes
        MSHDA issuing bonds "to fund loans to finance multifamily housing
        developments."
      * mi10k, first_gen_dpa, rate_relief, no_dpa (all four Homeownership
        subprograms) -- "Single-family Mortgage Revenue Bonds" activity
        column carries $3,779,165 thousand of single-family mortgage
        loans (p.56).
      * chill, mi_neighborhood_1_0, mi_neighborhood_2_0 -- Note 2's
        "State Assistance Programs" section (p.14) names "Housing and
        Community Development Fund - The Authority received State of
        Michigan funding to provide grants and loans for a variety of
        housing-related projects. These include ... property acquisition
        ... rehabilitation ... new construction ... community
        development, and housing preservation costs" -- language matching
        this Neighborhood Development division almost verbatim; the
        Statement of Revenue, Expenses, and Changes in Net Position
        Information (p.57) separately books a "Housing and community
        development fund - state" revenue line of $50,000 thousand for
        the year, within $0.7M (1.4%) of this rollup's own $50,261,085
        MI-Neighborhood-Grants total for the same period, and MSHDA's
        Note 1 restricted-net-position disclosure separately states
        "$135.5 million ... was restricted for spending on the State of
        Michigan Housing and Community Development Fund program" at
        fiscal year end.
      * legislative_enhancement, hcdf_grants -- same Note 1 disclosure:
        "$133.3 million was restricted for spending on ... Legislative
        Enhancement Program," and Note 2 separately describes
        "Legislative Enhancement Programs - The Authority received a
        State of Michigan appropriation to provide grants for a variety
        of housing-related projects. These include ... housing counseling
        services, affordable housing projects, senior living, and other
        community developments" -- matching this Housing Solutions
        division; the Statement of Revenue (p.57) books a "Legislative
        enhancement program -state" line. hcdf_grants (Housing &
        Community Development Fund Grants) uses the same "Housing and
        Community Development Fund" balance as the Neighborhood
        Development subprograms above.
      * homeless_hcdf_sdp (HCDF Grants: Shelter Diversion Program) -- same
        "Housing and Community Development Fund" balance.
  - "proprietary" (inferred from the broader activity/revenue umbrella,
    medium confidence -- program not itself individually named in the
    ACFR):
      * missing_middle -- Note 2's "Federal Assistance Programs" section
        names "State and Local Fiscal Recovery Funds (SLFRF) - The
        Authority receives federal funds under the American Rescue Plan
        Act Coronavirus SLFRF for a variety of housing related programs,
        including ... the Missing Middle Housing program" verbatim; the
        Statement of Revenue's $935,755-thousand combined "Federal and
        state assistance programs" line (booked almost entirely inside
        the "Federal and State Funds" activity column) is presumed to
        include Missing Middle's SLFRF dollars, though that combined line
        is not broken out by individual program.
      * hcv, pbv, ehv, vash, ned, mainstream, fup, section811, key_to_own
        (all 9 Rental Assistance subprograms) -- Note 2 names "Section 8
        Program - The Authority receives federal financial assistance
        through various housing and rental programs to provide rental
        subsidies and tenant vouchers"; the same $935,755-thousand
        combined "Federal and state assistance programs" revenue line
        (Statement of Revenue, p.57) is presumed to carry these
        (Section-8-family, HUD-voucher) programs, and a separate
        "Section 8 program administrative fees $24,821" line is booked
        under MSHDA's own General Operating activity -- confidence is
        high on the Section-8-core programs (hcv, pbv, vash, mainstream,
        fup) and only medium on the smaller/non-Section-8-branded ones
        (ehv, ned, section811, key_to_own), none of which is individually
        named in the ACFR.
  - "off_balance_sheet" (confirmed absent from the ACFR by name, full-text
    checked):
      * lihtc_9pct -- checked "tax credit"/"LIHTC" -- zero matches
        anywhere in MSHDA's FY2025 financial statements; federal 9%
        credits are allocated directly to developers/investors, the same
        off-balance-sheet logic used for every other state's LIHTC in
        this project.
      * eahf (Employer-Assisted Housing Fund) -- checked "Employer-
        Assisted"/"EAHF" -- zero matches (the only "Employer" hits in the
        ACFR are pension "Employer Contributions," an unrelated topic);
        consistent with the report's own footnote describing EAHF as "a
        new pilot program" in its first year, not yet broken out in the
        FY2025 financial statements.
      * htif -- checked "TIF"/"Housing TIF"/"H-TIF" -- zero matches;
        MSHDA's own footnote describes H-TIF loans as tied to individual
        municipal tax-increment-financing districts, approved but not
        always funded by MSHDA, consistent with not being carried on
        MSHDA's own balance sheet as a distinct program.
      * esg, sp_ha, hmis, rhp, rhip, ces, home_arp_hnp, home_arp_hpp (8 of
        the 9 Homeless Prevention Grants subprograms) -- checked "Emergency
        Solutions," "HMIS," "Recovery Housing," "Coordinated Entry,"
        "HOME-ARP," "Continuum of Care" -- zero matches for any of them.
      * housing_readiness, hdf_collaborative, tnhdap (3 of the 5 Housing
        Solutions subprograms) -- checked "Housing Development Fund,"
        "HDF," "Tribal," "Readiness" -- zero matches for any of them.
      * mich_legacy (MSHDA Investing in Community Housing) -- checked
        "MICH" -- zero matches; the report itself labels this a
        "Discontinued Program with Legacy Data," consistent with it
        predating the current Housing and Community Development Fund
        structure and not appearing in the FY2025 statements.

Geocoding
---------------------------------------------------------------------------
Same approach as IL/PA: Nominatim (OpenStreetMap), primary query
"{street address}, {city}, MI", falling back to "{city}, MI" (flagged
geocode_status="city_center") when the street-level query fails or the
source table itself only gives "Scattered Sites" for a development's
address (Highland Park Housing Commission, Martin Gardens, Royal Oak
Cottages I). Self-throttled to <=1 request/second with an identifying
User-Agent per Nominatim's usage policy.

fy2026
---------------------------------------------------------------------------
Unlike PA/FL (whose annual reports have no forward-looking section at
all), MSHDA's Production Goals Report DOES publish an official "FY
2025-2026 Goal" figure for Multifamily Rental Development (as a whole and
for 4 of its 6 subprograms: 9% LIHTC, 4% Pass-Through, 4% Direct Lending;
Missing Middle is explicitly closed out -- "Funding for the Missing
Middle Program has been fully awarded. There are currently no planned
funds for FY 2025-2026," closed=True) and for Homeownership (as a whole,
with no per-subprogram FY26 breakdown). These are MSHDA's own stated
production targets, not projections invented by this script. Rental
Assistance, Homeless Prevention Grants, Neighborhood Development, and
Housing Solutions have no "Goal Achievement"-style table with an FY26
column anywhere in the report, so every field in those four categories
uses the uniform pending shape below.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "mi_program_activity.json"

SOURCE_URL = "https://www.michigan.gov/mshda/about/transparency-and-reports"
SOURCE_FILE = "MI_MSHDA_ProductionGoalsReport_FY2025.pdf (FY 2025 Production Goals Report)"
RETRIEVED = "2026-08-13"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
GEOCODER_USER_AGENT = "us-hfa-data-map/1.0 (github.com/MD-ai-fin/us-hfa-data-map)"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "miFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "multifamily_rental_development",
        "unit_type": "units",
        "fy2025_actual": 5324,
        "fy2025_source_quote": (
            "\"Multifamily Rental Development Production Goal Achievement\" table: FY "
            "2024-2025 Production, Total MSHDA Dollars $1,417,752,404, Total Units "
            "Developed 5,324, TDC of MSHDA Projects $1,566,223,402. Summing this "
            "category's own 6 financing-program subprograms' unit figures reproduces "
            "5,324 exactly (1,137+1,290+1,989+478+380+50); summing their dollar figures "
            "gives $1,027,530,854, NOT $1,417,752,404 -- the $390,221,550 gap is the "
            "10-year LIHTC credit VALUE of the 4% Pass-Through ($129,885,890) and Direct "
            "Lending ($260,335,660) deals, which MSHDA's own headline adds on top of the "
            "loan dollars for those same deals (a deliberate double-lens \"total "
            "investment\" figure, not a data error -- see module docstring)."
        ),
        "fy2025_amounts": [
            {"label_key": "mi_amt_multifamily_dollars", "amount": 1417752404},
            {"label_key": "mi_amt_multifamily_tdc", "amount": 1566223402},
        ],
        "additive": True,
        "fy2026": {"value": 5456, "amount": 1226870021, "closed": False,
                    "note_key": "mi_fy26_multifamily"},
        "subprograms": [
            {"key": "lihtc_9pct", "fy2025_units": 1137, "fy2025_amount": 314483080,
             "color_group": "credit",
             # Federal 9% tax credits allocated to developers/investors; never
             # appears in MSHDA's own FY2025 financial statements (checked
             # "tax credit"/"LIHTC" -- zero matches).
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": {"value": 1150, "amount": 340000000, "closed": False,
                        "note_key": "mi_fy26_lihtc9"}},
            {"key": "lihtc_4pct_pass_through", "fy2025_units": 1290, "fy2025_amount": 160516518,
             "color_group": "bond",
             # "Rental Housing Revenue Bonds" activity column on MSHDA's own
             # Statement of Net Position Information (p.56) carries $1.91B of
             # multifamily mortgage loans; Note 5 (Bonds Payable) describes
             # MSHDA issuing bonds to fund multifamily loans.
             "fund_type": "proprietary",
             "fund_name": "Rental Housing Revenue Bonds (multifamily mortgage loans receivable)",
             "fy2026": {"value": 2300, "amount": 350000000, "closed": False,
                        "note_key": "mi_fy26_lihtc4pt"}},
            {"key": "lihtc_4pct_direct_lending", "fy2025_units": 1989, "fy2025_amount": 499931256,
             "color_group": "bond",
             # Same Rental Housing Revenue Bonds activity/multifamily mortgage
             # loans receivable balance as lihtc_4pct_pass_through above.
             "fund_type": "proprietary",
             "fund_name": "Rental Housing Revenue Bonds (multifamily mortgage loans receivable)",
             "fy2026": {"value": 2006, "amount": 350000000, "closed": False,
                        "note_key": "mi_fy26_lihtc4dl"}},
            {"key": "missing_middle", "fy2025_units": 478, "fy2025_amount": 38800000,
             "color_group": "capital",
             # Note 2's "Federal Assistance Programs" section names the
             # "Missing Middle Housing program" verbatim as one of the
             # SLFRF-funded programs administered by MSHDA; not individually
             # broken out within the $935.8M combined "Federal and state
             # assistance programs" revenue line, so confidence is medium.
             "fund_type": "proprietary",
             "fund_name": "Federal and State Funds activity (SLFRF - Missing Middle Housing program, inferred)",
             "fy2026": {"value": None, "amount": None, "closed": True,
                        "note_key": "mi_fy26_missing_middle_closed"}},
            {"key": "eahf", "fy2025_units": 380, "fy2025_amount": 4500000,
             "color_group": "capital",
             # A new FY2025 pilot program (per the report's own footnote);
             # checked "Employer-Assisted"/"EAHF" -- zero matches in MSHDA's
             # FY2025 financial statements.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": {"value": None, "amount": 4610000, "closed": False,
                        "note_key": "mi_fy26_eahf"}},
            {"key": "htif", "fy2025_units": 50, "fy2025_amount": 9300000,
             "color_group": "capital",
             # Checked "TIF"/"Housing TIF"/"H-TIF" -- zero matches; MSHDA
             # approves but does not always fund H-TIF projects, consistent
             # with not being a distinct MSHDA-carried balance.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "homeownership",
        "unit_type": "households",
        "fy2025_actual": 5245,
        "fy2025_source_quote": (
            "\"Single-Family Homeownership Mortgages Production Goal Achievement\" "
            "table, FY 2024-2025 Production: # of DPA Loans 4,767, DPA $'s Loaned "
            "$49,298,627, Total # of Loans 5,245, Total $'s Loaned $775,416,034. The "
            "table's own 4 sub-rows (MI 10K DPA, MSHDA First-Generation DPA, MSHDA "
            "Rate-Relief Mortgage Program, Single-Family Loans w/ no DPA or "
            "Rate-Relief) are a clean, mutually-exclusive partition of these same "
            "5,245 loans -- their Total # of Loans and Total $'s Loaned columns sum "
            "EXACTLY to 5,245 / $775,416,034 (verify_homeownership_totals())."
        ),
        "fy2025_amounts": [
            {"label_key": "mi_amt_home_total", "amount": 775416034},
            {"label_key": "mi_amt_home_dpa_total", "amount": 49298627},
        ],
        "additive": True,
        "fy2026": {"value": 5225, "amount": 821569895, "closed": False,
                    "note_key": "mi_fy26_homeownership"},
        "subprograms": [
            {"key": "mi10k", "fy2025_units": 4334, "fy2025_amount": 666134529,
             "color_group": "bond",
             "fund_type": "proprietary", "fund_name": "Single-family Mortgage Revenue Bonds",
             "fy2026": _FY26_PENDING},
            {"key": "first_gen_dpa", "fy2025_units": 241, "fy2025_amount": 33092081,
             "color_group": "bond",
             "fund_type": "proprietary", "fund_name": "Single-family Mortgage Revenue Bonds",
             "fy2026": _FY26_PENDING},
            {"key": "rate_relief", "fy2025_units": 300, "fy2025_amount": 41704260,
             "color_group": "bond",
             "fund_type": "proprietary", "fund_name": "Single-family Mortgage Revenue Bonds",
             "fy2026": _FY26_PENDING},
            {"key": "no_dpa", "fy2025_units": 370, "fy2025_amount": 34485164,
             "color_group": "bond",
             "fund_type": "proprietary", "fund_name": "Single-family Mortgage Revenue Bonds",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "rental_assistance",
        "unit_type": "households",
        "fy2025_actual": 32595,
        "fy2025_source_quote": (
            "\"Rental Assistance Programs\" table, \"Total Number and Dollar Amounts of "
            "Rental Assistance\" row: 32,595 households, $287,224,953. This script's own "
            "9-row resum matches 32,595 households exactly but sums to $288,082,211 in "
            "dollars -- $857,258 (exactly Key to Own's own dollar figure) more than the "
            "table's own printed $287,224,953, an apparent arithmetic slip in MSHDA's "
            "own table (see module docstring). The report's own front-page "
            "executive-summary box separately states 32,459 households served for this "
            "same $287,224,953 -- exactly this table's first 8 rows (all but Key to Own, "
            "136 households). MSHDA does not explain either discrepancy; this script "
            "uses 32,595 (the fully-itemized table's own printed household total) as "
            "fy2025_actual and records 32,459 here for transparency, without forcing "
            "either figure to reconcile."
        ),
        "fy2025_amounts": [
            {"label_key": "mi_amt_rental_assist_total", "amount": 287224953},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "hcv", "fy2025_units": 24105, "fy2025_amount": 219821618,
             "color_group": "trust",
             "fund_type": "proprietary",
             "fund_name": "Federal and State Funds activity (Section 8 Program, Note 2)",
             "fy2026": _FY26_PENDING},
            {"key": "pbv", "fy2025_units": 5514, "fy2025_amount": 44618691,
             "color_group": "trust",
             "fund_type": "proprietary",
             "fund_name": "Federal and State Funds activity (Section 8 Program, Note 2)",
             "fy2026": _FY26_PENDING},
            {"key": "ehv", "fy2025_units": 657, "fy2025_amount": 6675328,
             "color_group": "trust",
             "fund_type": "proprietary",
             "fund_name": "Federal and State Funds activity (federal rental assistance programs, inferred)",
             "fy2026": _FY26_PENDING},
            {"key": "vash", "fy2025_units": 1315, "fy2025_amount": 9026852,
             "color_group": "trust",
             "fund_type": "proprietary",
             "fund_name": "Federal and State Funds activity (Section 8 Program, Note 2)",
             "fy2026": _FY26_PENDING},
            {"key": "ned", "fy2025_units": 317, "fy2025_amount": 2457166,
             "color_group": "trust",
             "fund_type": "proprietary",
             "fund_name": "Federal and State Funds activity (federal rental assistance programs, inferred)",
             "fy2026": _FY26_PENDING},
            {"key": "mainstream", "fy2025_units": 173, "fy2025_amount": 1374752,
             "color_group": "trust",
             "fund_type": "proprietary",
             "fund_name": "Federal and State Funds activity (Section 8 Program, Note 2)",
             "fy2026": _FY26_PENDING},
            {"key": "fup", "fy2025_units": 223, "fy2025_amount": 1915546,
             "color_group": "trust",
             "fund_type": "proprietary",
             "fund_name": "Federal and State Funds activity (Section 8 Program, Note 2)",
             "fy2026": _FY26_PENDING},
            {"key": "section811", "fy2025_units": 155, "fy2025_amount": 1335000,
             "color_group": "trust",
             "fund_type": "proprietary",
             "fund_name": "Federal and State Funds activity (federal rental assistance programs, inferred)",
             "fy2026": _FY26_PENDING},
            {"key": "key_to_own", "fy2025_units": 136, "fy2025_amount": 857258,
             "color_group": "trust",
             "fund_type": "proprietary",
             "fund_name": "Federal and State Funds activity (federal rental assistance programs, inferred)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "homeless_prevention_grants",
        "unit_type": "dollars",
        "fy2025_actual": None,
        "fy2025_source_quote": (
            "\"Homeless Grants funded by MSHDA\" table, \"Total Number and Dollar "
            "Amount of Homeless Grants funded by MSHDA\" row: $28,826,165 across 140 "
            "grants -- the sum of this table's own 9 grant-type rows, verified exactly "
            "on both grant count and dollars (verify_homeless_grant_totals()). No "
            "household/unit count is disclosed for any of these programs."
        ),
        "fy2025_amounts": [
            {"label_key": "mi_amt_homeless_total", "amount": 28826165},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "esg", "fy2025_units": None, "fy2025_amount": 10833372,
             "color_group": "capital",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "sp_ha", "fy2025_units": None, "fy2025_amount": 313175,
             "color_group": "capital",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "hmis", "fy2025_units": None, "fy2025_amount": 1232805,
             "color_group": "capital",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "rhp", "fy2025_units": None, "fy2025_amount": 1726208,
             "color_group": "capital",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "rhip", "fy2025_units": None, "fy2025_amount": 1924860,
             "color_group": "capital",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "ces", "fy2025_units": None, "fy2025_amount": 795745,
             "color_group": "capital",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "home_arp_hnp", "fy2025_units": None, "fy2025_amount": 3000000,
             "color_group": "capital",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "home_arp_hpp", "fy2025_units": None, "fy2025_amount": 5000000,
             "color_group": "capital",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "homeless_hcdf_sdp", "fy2025_units": None, "fy2025_amount": 4000000,
             "color_group": "capital",
             # Housing and Community Development Fund -- same ACFR-confirmed
             # restricted-net-position balance as the Neighborhood
             # Development / Housing Solutions HCDF subprograms below.
             "fund_type": "proprietary", "fund_name": "Housing and Community Development Fund",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "neighborhood_development",
        "unit_type": "units",
        "fy2025_actual": 1404,
        "fy2025_source_quote": (
            "\"FY 2024-2025 Dollars and Unit production in Neighborhood Development in "
            "Michigan\" header: 116 grants, $50,721,396, 1,404 units (1,201 rehab + 203 "
            "new). This equals \"MI Neighborhood Grants\" (112 grants, $50,261,085, "
            "1,199 rehab + 199 new = 1,398 units, itself the sum of CHILL + MI "
            "Neighborhood 1.0 + MI Neighborhood 2.0) plus the discontinued \"MSHDA "
            "Investing in Community Housing (MICH)\" legacy line (4 grants, $460,311, "
            "2 rehab + 4 new = 6 units) -- both levels of this rollup verified exactly "
            "(verify_neighborhood_totals())."
        ),
        "fy2025_amounts": [
            {"label_key": "mi_amt_neighborhood_total", "amount": 50721396},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "chill", "fy2025_units": 86, "fy2025_amount": 2303150,
             "color_group": "capital",
             "fund_type": "proprietary", "fund_name": "Housing and Community Development Fund (inferred)",
             "fy2026": _FY26_PENDING},
            {"key": "mi_neighborhood_1_0", "fy2025_units": 846, "fy2025_amount": 35041685,
             "color_group": "capital",
             "fund_type": "proprietary", "fund_name": "Housing and Community Development Fund (inferred)",
             "fy2026": _FY26_PENDING},
            {"key": "mi_neighborhood_2_0", "fy2025_units": 466, "fy2025_amount": 12916250,
             "color_group": "capital",
             "fund_type": "proprietary", "fund_name": "Housing and Community Development Fund (inferred)",
             "fy2026": _FY26_PENDING},
            {"key": "mich_legacy", "fy2025_units": 6, "fy2025_amount": 460311,
             "color_group": "capital",
             # Discontinued predecessor program (MSHDA's own "Legacy Data"
             # label); checked "MICH" -- zero matches in the FY2025 ACFR.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "housing_solutions",
        "unit_type": "units",
        "fy2025_actual": 441,
        "fy2025_source_quote": (
            "\"FY 2024-2025 Dollars and Units towards Housing Solutions Grants in "
            "Michigan\" header: 88 grants, $49,794,351, 441 units -- the exact sum of "
            "this section's own 5 grant-type rows (verify_housing_solutions_totals())."
        ),
        "fy2025_amounts": [
            {"label_key": "mi_amt_housing_solutions_total", "amount": 49794351},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "legislative_enhancement", "fy2025_units": 441, "fy2025_amount": 44210000,
             "color_group": "capital",
             "fund_type": "proprietary", "fund_name": "Legislative Enhancement Program",
             "fy2026": _FY26_PENDING},
            {"key": "housing_readiness", "fy2025_units": 0, "fy2025_amount": 2326850,
             "color_group": "capital",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "hdf_collaborative", "fy2025_units": 0, "fy2025_amount": 1567981,
             "color_group": "capital",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "hcdf_grants", "fy2025_units": 0, "fy2025_amount": 1200020,
             "color_group": "capital",
             "fund_type": "proprietary", "fund_name": "Housing and Community Development Fund",
             "fy2026": _FY26_PENDING},
            {"key": "tnhdap", "fy2025_units": 0, "fy2025_amount": 489500,
             "color_group": "capital",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
]

# ---------------------------------------------------------------------------
# Multifamily project-level detail (Exhibit 1 "FY 2024-2025 Projects
# Receiving 9% LIHTC Allocations" + Exhibit 2 "... Receiving 4% LIHTC
# Allocations"). Extracted with pdfplumber word-coordinate row-clustering
# (see module docstring) -- both exhibits sit on the same PDF page with no
# printed subtotal of their own; see verify_exhibit_totals() below for the
# independent cross-check against MSHDA's own narrative production tables.
# (name, address, city, units, [funding source keys])
# address=None marks developments whose own PDF row lists no street address
# ("Scattered Sites") -- these fall back to city-center geocoding.
# ---------------------------------------------------------------------------

RAW_PROJECTS = [
    # --- Exhibit 1: 9% LIHTC (25 rows) ---
    ("725 Amsterdam - Affordable", "725 Amsterdam St", "Detroit", 40, ["lihtc_9pct"]),
    ("Centennial Arms I", "601 W 1st St", "Evart", 80, ["lihtc_9pct"]),
    ("Centennial Arms II", "601 W 1st St", "Evart", 65, ["lihtc_9pct"]),
    ("Flats on Bridge", "401 S Bridge St", "Elk Rapids", 24, ["lihtc_9pct"]),
    ("Gesu Senior Housing", "17181 Birchcrest Dr", "Detroit", 36, ["lihtc_9pct"]),
    ("Lincoln Avenue Lofts", "810 Lincoln Ave", "Port Huron", 40, ["lihtc_9pct"]),
    ("LVD LIHTC I", "3rd St & 4th St", "Watersmeet", 44, ["lihtc_9pct"]),
    ("Nelson School Apartments", "550 W Grand Ave", "Muskegon", 52, ["lihtc_9pct"]),
    ("Orchardview", "10200 E Carter Rd", "Traverse City", 54, ["lihtc_9pct"]),
    ("Paw Paw Arms Apartments", "146 Lake St", "Paw Paw", 24, ["lihtc_9pct"]),
    ("Rivercrest Apartments", "125 W Harrington St", "Croswell", 24, ["lihtc_9pct"]),
    ("Shea Ravines II", "2929 Burlingame Ave SW", "Wyoming", 56, ["lihtc_9pct"]),
    # Exhibit 1's own row for this project also prints a 4% Total/LIHTC
    # Units figure of 60 with no Pass-Through/Direct-Lending typing and no
    # matching row of its own in Exhibit 2 -- excluded here, see docstring.
    ("The Preserve on Ash II", "Butternut St & 14th St", "Detroit", 31, ["lihtc_9pct"]),
    ("Villages of Parkside Phase III (Oct-24 Round)", "5000 Conner St", "Detroit", 54, ["lihtc_9pct"]),
    ("Vineyard Villas", "675 Hazen St", "Paw Paw", 24, ["lihtc_9pct"]),
    ("130 E Grand Boulevard Apartments", "130 E Grand Blvd", "Detroit", 54, ["lihtc_9pct"]),
    ("Allen Crossing III", "162 E Apple Ave", "Muskegon", 42, ["lihtc_9pct"]),
    ("Alpine Senior Apartments", "1625 Alpine Ave NW", "Grand Rapids", 52, ["lihtc_9pct"]),
    ("Brown City Homes", "5111 Hawthorne Dr", "Brown City", 27, ["lihtc_9pct"]),
    ("Froebel Place", "417 Jackson Ave", "Muskegon", 46, ["lihtc_9pct"]),
    ("Lighthouse Ridge Apartments", "09010 73rd St", "South Haven Township", 52, ["lihtc_9pct"]),
    ("Northern Pines", "240 E Michigan Ave", "Battle Creek", 56, ["lihtc_9pct"]),
    ("Union Suites on Coit II", "628 Coit Ave NE", "Grand Rapids", 52, ["lihtc_9pct"]),
    ("Villages of Parkside - Phase IV", "5000 Conner St", "Detroit", 54, ["lihtc_9pct"]),
    ("Villages of Parkside Phase III (Apr-25 Round)", "5000 Conner St", "Detroit", 54, ["lihtc_9pct"]),

    # --- Exhibit 2: 4% LIHTC, Pass-Through (10 rows) ---
    ("4401 Rosa Parks", "4401 Rosa Parks", "Detroit", 36, ["lihtc_4pct_pass_through"]),
    ("Avon Towers", "435 S Livernois Rd", "Rochester Hills", 125, ["lihtc_4pct_pass_through"]),
    ("Cambridge Towers", "19101 Evergreen Rd", "Detroit", 250, ["lihtc_4pct_pass_through"]),
    ("Kalamazoo Community Courtyard", "3405 Duke St", "Kalamazoo", 19, ["lihtc_4pct_pass_through"]),
    ("Lee Plaza 4", "2240 W Grand Blvd", "Detroit", 65, ["lihtc_4pct_pass_through"]),
    ("Midblock", "444 Watson St", "Detroit", 184, ["lihtc_4pct_pass_through"]),
    ("North Port", "2631 Krafft Rd", "Port Huron", 251, ["lihtc_4pct_pass_through"]),
    ("Old Mill Pond Apartments", "100 E Mill Pond St", "Brooklyn", 48, ["lihtc_4pct_pass_through"]),
    ("Plymouth Square", "20201 Plymouth Rd", "Detroit", 280, ["lihtc_4pct_pass_through"]),
    ("Westbury Apartments", "201 Hickory Ct", "Wayland", 32, ["lihtc_4pct_pass_through"]),

    # --- Exhibit 2: 4% LIHTC, Direct Lending (29 rows) ---
    ("1309 Madison", "1309 Madison Ave SE", "Grand Rapids", 50, ["lihtc_4pct_direct_lending"]),
    ("206 North Washington", "206 N Washington St", "Ypsilanti", 22, ["lihtc_4pct_direct_lending"]),
    ("Annika Place II", "1020 Hastings St", "Traverse City", 52, ["lihtc_4pct_direct_lending"]),
    ("Auburn Place", "454 Auburn Ave", "Pontiac", 54, ["lihtc_4pct_direct_lending"]),
    ("Beacon Place", "101 Mechanic St", "Pontiac", 40, ["lihtc_4pct_direct_lending"]),
    ("Buersmeyer Manor", "8520 Wyoming Ave", "Detroit", 35, ["lihtc_4pct_direct_lending"]),
    ("Calumet", "4387 Third Ave", "Detroit", 104, ["lihtc_4pct_direct_lending"]),
    ("Carriage Towne Place", "204 E Williams St", "Ovid", 24, ["lihtc_4pct_direct_lending"]),
    ("Corner at Wall Street", "126 W Wall St", "Benton Harbor", 46, ["lihtc_4pct_direct_lending"]),
    ("Crossroads Apartments", "848 Chestnut St", "Reed City", 39, ["lihtc_4pct_direct_lending"]),
    ("Elmdale Apartments", "1361 Elmdale St NE", "Grand Rapids", 18, ["lihtc_4pct_direct_lending"]),
    ("Grand Vista Place", "220 E Kalamazoo St", "Lansing", 63, ["lihtc_4pct_direct_lending"]),
    ("Henry Street Redevelopment (4%)", "447 Henry St", "Detroit", 44, ["lihtc_4pct_direct_lending"]),
    ("Higginbotham School Development", "20119 Wisconsin St", "Detroit", 100, ["lihtc_4pct_direct_lending"]),
    ("Highland Park Housing Commission", None, "Highland Park", 164, ["lihtc_4pct_direct_lending"]),
    ("Hive on Russell", "2105 Russell St", "Detroit", 73, ["lihtc_4pct_direct_lending"]),
    ("Legacy Senior Housing, The (4%)", "120 E North St", "Kalamazoo", 34, ["lihtc_4pct_direct_lending"]),
    ("Martin Gardens", None, "Detroit", 46, ["lihtc_4pct_direct_lending"]),
    ("Minock Park", "19505 Grand River Ave", "Detroit", 42, ["lihtc_4pct_direct_lending"]),
    ("Mystic View", "928 Ryan St", "Pullman", 40, ["lihtc_4pct_direct_lending"]),
    ("Peterboro Place", "8 Peterboro St", "Detroit", 70, ["lihtc_4pct_direct_lending"]),
    ("Preston Townhomes", "7200 Mack Ave", "Detroit", 31, ["lihtc_4pct_direct_lending"]),
    ("Rivers Edge", "508 Harrison St", "Kalamazoo", 226, ["lihtc_4pct_direct_lending"]),
    ("Royal Oak Cottages I", None, "Royal Oak", 32, ["lihtc_4pct_direct_lending"]),
    ("Russell Woods 4%", "11421 Dexter Ave", "Detroit", 42, ["lihtc_4pct_direct_lending"]),
    ("Sanctuary at Brewster, The", "2900 St Antoine St", "Detroit", 52, ["lihtc_4pct_direct_lending"]),
    ("Union at A2", "2050 Commerce Blvd", "Ann Arbor", 256, ["lihtc_4pct_direct_lending"]),
    ("Verne Barry Place", "60 S Division Ave", "Grand Rapids", 116, ["lihtc_4pct_direct_lending"]),
    ("Villa Esperanza", "1446 44th St SW", "Wyoming", 39, ["lihtc_4pct_direct_lending"]),
]

FUNDING_COLOR_GROUP = {
    "lihtc_9pct": "credit",
    "lihtc_4pct_pass_through": "bond",
    "lihtc_4pct_direct_lending": "bond",
}
FUNDING_PRIORITY = ["lihtc_9pct", "lihtc_4pct_direct_lending", "lihtc_4pct_pass_through"]

# Independently re-summed (via pdfplumber, directly off Exhibit 1/2's own
# table cells) unit totals, cross-checked against MSHDA's own narrative
# "Production Goal Achievement" tables -- see verify_exhibit_totals().
EXPECTED_EX1_9PCT_TOTAL_UNITS = 1137        # matches "9% LIHTC ... Production ... 1,137"
EXPECTED_EX2_PASS_THROUGH_UNITS = 1290      # matches "Short-Term Pass-Through Loans ... Production ... 1,290"
EXPECTED_EX2_DIRECT_LENDING_RAW_UNITS = 1954  # Exhibit 2's own 29 named Direct-Lending rows
EXPECTED_EX2_DIRECT_LENDING_OFFICIAL_UNITS = 1989  # official "Direct Lending ... Production ... 1,989" (includes 15 unnamed refinancings, see docstring)


def verify_exhibit_totals():
    errors = []
    if len(RAW_PROJECTS) != 64:
        errors.append(f"RAW_PROJECTS count: expected 64, got {len(RAW_PROJECTS)}")
    ex1 = [p for p in RAW_PROJECTS if p[4] == ["lihtc_9pct"]]
    ex2_pt = [p for p in RAW_PROJECTS if p[4] == ["lihtc_4pct_pass_through"]]
    ex2_dl = [p for p in RAW_PROJECTS if p[4] == ["lihtc_4pct_direct_lending"]]
    if len(ex1) != 25:
        errors.append(f"Exhibit 1 (9% LIHTC) row count: expected 25, got {len(ex1)}")
    if len(ex2_pt) != 10:
        errors.append(f"Exhibit 2 Pass-Through row count: expected 10, got {len(ex2_pt)}")
    if len(ex2_dl) != 29:
        errors.append(f"Exhibit 2 Direct Lending row count: expected 29, got {len(ex2_dl)}")
    sum_ex1 = sum(p[3] for p in ex1)
    sum_pt = sum(p[3] for p in ex2_pt)
    sum_dl = sum(p[3] for p in ex2_dl)
    if sum_ex1 != EXPECTED_EX1_9PCT_TOTAL_UNITS:
        errors.append(f"Exhibit 1 unit sum: expected {EXPECTED_EX1_9PCT_TOTAL_UNITS}, got {sum_ex1}")
    if sum_pt != EXPECTED_EX2_PASS_THROUGH_UNITS:
        errors.append(f"Exhibit 2 Pass-Through unit sum: expected {EXPECTED_EX2_PASS_THROUGH_UNITS}, got {sum_pt}")
    if sum_dl != EXPECTED_EX2_DIRECT_LENDING_RAW_UNITS:
        errors.append(f"Exhibit 2 Direct Lending (named projects) unit sum: expected {EXPECTED_EX2_DIRECT_LENDING_RAW_UNITS}, got {sum_dl}")
    if errors:
        raise SystemExit("Exhibit 1/2 total mismatch(es):\n" + "\n".join(errors))
    print(f"Exhibit 1 (25 rows, {sum_ex1} units) and Exhibit 2 (10 Pass-Through rows, "
          f"{sum_pt} units + 29 Direct Lending rows, {sum_dl} units) verified against "
          f"MSHDA's own narrative Production Goal Achievement tables.")


def verify_category_unit_and_dollar_totals():
    errors = []
    for cat in CATEGORIES:
        subs = cat["subprograms"]
        unit_vals = [sp["fy2025_units"] for sp in subs if sp["fy2025_units"] is not None]
        if cat["fy2025_actual"] is not None and unit_vals and len(unit_vals) == len(subs):
            total = sum(unit_vals)
            if total != cat["fy2025_actual"]:
                errors.append(f"{cat['key']}: subprogram units sum to {total}, "
                               f"category fy2025_actual is {cat['fy2025_actual']}")
    if errors:
        raise SystemExit("Category unit-total mismatch(es):\n" + "\n".join(errors))
    print("All category-level subprogram unit sums verified against their own "
          "fy2025_actual headline (multifamily_rental_development, homeownership, "
          "rental_assistance, neighborhood_development, housing_solutions).")


def verify_homeownership_totals():
    units = 4334 + 241 + 300 + 370
    dpa_dollars = 41556849 + 5893504 + 1848274 + 0
    total_dollars = 666134529 + 33092081 + 41704260 + 34485164
    errors = []
    if units != 5245:
        errors.append(f"Homeownership loan count: expected 5,245, got {units:,}")
    if dpa_dollars != 49298627:
        errors.append(f"Homeownership DPA dollars: expected $49,298,627, got ${dpa_dollars:,}")
    if total_dollars != 775416034:
        errors.append(f"Homeownership total dollars: expected $775,416,034, got ${total_dollars:,}")
    if errors:
        raise SystemExit("Homeownership total mismatch(es):\n" + "\n".join(errors))
    print("Homeownership subprogram totals verified: 4,334+241+300+370=5,245 loans, "
          "DPA $41,556,849+$5,893,504+$1,848,274=$49,298,627, "
          "total $666,134,529+$33,092,081+$41,704,260+$34,485,164=$775,416,034.")


def verify_rental_assistance_totals():
    units = 24105 + 5514 + 657 + 1315 + 317 + 173 + 223 + 155 + 136
    dollars = 219821618 + 44618691 + 6675328 + 9026852 + 2457166 + 1374752 + 1915546 + 1335000 + 857258
    printed_total_dollars = 287224953
    key_to_own_dollars = 857258
    errors = []
    if units != 32595:
        errors.append(f"Rental Assistance households: expected 32,595, got {units:,}")
    if dollars - key_to_own_dollars != printed_total_dollars:
        errors.append(
            f"Rental Assistance dollars: expected the 9-row resum ({dollars:,}) to "
            f"exceed the table's own printed Total (${printed_total_dollars:,}) by "
            f"exactly Key to Own's own dollar figure (${key_to_own_dollars:,}); got a "
            f"gap of ${dollars - printed_total_dollars:,}"
        )
    if units - 136 != 32459:
        errors.append("Rental Assistance minus Key to Own should equal the front-page 32,459 figure")
    if errors:
        raise SystemExit("Rental Assistance total mismatch(es):\n" + "\n".join(errors))
    print("Rental Assistance subprogram totals verified: 9 voucher types sum to "
          "32,595 households (matches the detailed table's own Total row) but "
          "$288,082,211 in dollars, $857,258 more than the table's own printed "
          "$287,224,953 Total -- exactly Key to Own's own dollar figure, an apparent "
          "arithmetic slip in MSHDA's own table (documented, not forced to reconcile); "
          "households minus Key to Own (136) = 32,459 (matches the front-page summary "
          "box).")


def verify_homeless_grant_totals():
    grants = 34 + 2 + 2 + 11 + 8 + 21 + 20 + 30 + 12
    dollars = 10833372 + 313175 + 1232805 + 1726208 + 1924860 + 795745 + 3000000 + 5000000 + 4000000
    errors = []
    if grants != 140:
        errors.append(f"Homeless grant count: expected 140, got {grants}")
    if dollars != 28826165:
        errors.append(f"Homeless grant dollars: expected $28,826,165, got ${dollars:,}")
    if errors:
        raise SystemExit("Homeless grant total mismatch(es):\n" + "\n".join(errors))
    print("Homeless Prevention Grants subprogram totals verified: 9 grant types sum "
          "to 140 grants / $28,826,165, matching the table's own printed Total row "
          "exactly on both axes.")


def verify_neighborhood_totals():
    mi_neighborhood_grants_count = 6 + 77 + 29
    mi_neighborhood_grants_dollars = 2303150 + 35041685 + 12916250
    mi_neighborhood_grants_units = 86 + 846 + 466
    total_count = mi_neighborhood_grants_count + 4
    total_dollars = mi_neighborhood_grants_dollars + 460311
    total_units = mi_neighborhood_grants_units + 6
    errors = []
    if mi_neighborhood_grants_count != 112:
        errors.append(f"MI Neighborhood Grants count: expected 112, got {mi_neighborhood_grants_count}")
    if mi_neighborhood_grants_dollars != 50261085:
        errors.append(f"MI Neighborhood Grants dollars: expected $50,261,085, got ${mi_neighborhood_grants_dollars:,}")
    if mi_neighborhood_grants_units != 1398:
        errors.append(f"MI Neighborhood Grants units: expected 1,398 (1,199 rehab + 199 new), got {mi_neighborhood_grants_units}")
    if total_count != 116:
        errors.append(f"Neighborhood Development total grants: expected 116, got {total_count}")
    if total_dollars != 50721396:
        errors.append(f"Neighborhood Development total dollars: expected $50,721,396, got ${total_dollars:,}")
    if total_units != 1404:
        errors.append(f"Neighborhood Development total units: expected 1,404, got {total_units}")
    if errors:
        raise SystemExit("Neighborhood Development total mismatch(es):\n" + "\n".join(errors))
    print("Neighborhood Development rollup verified at both levels: CHILL+MI "
          "Neighborhood 1.0+2.0 = 112 grants/$50,261,085/1,398 units (\"MI "
          "Neighborhood Grants\" subtotal), + MICH legacy (4/$460,311/6) = 116 "
          "grants/$50,721,396/1,404 units (section header total).")


def verify_housing_solutions_totals():
    grants = 15 + 50 + 9 + 8 + 6
    dollars = 44210000 + 2326850 + 1567981 + 1200020 + 489500
    units = 441 + 0 + 0 + 0 + 0
    errors = []
    if grants != 88:
        errors.append(f"Housing Solutions grant count: expected 88, got {grants}")
    if dollars != 49794351:
        errors.append(f"Housing Solutions dollars: expected $49,794,351, got ${dollars:,}")
    if units != 441:
        errors.append(f"Housing Solutions units: expected 441, got {units}")
    if errors:
        raise SystemExit("Housing Solutions total mismatch(es):\n" + "\n".join(errors))
    print("Housing Solutions subprogram totals verified: 5 grant types sum to 88 "
          "grants / $49,794,351 / 441 units, matching the section's own header "
          "exactly.")


def verify_headline_reconciliation():
    total_units = 5324 + 5245 + 1404 + 441
    total_dollars = 1417752404 + 775416034 + 287224953 + 28826165 + 50721396 + 49794351
    errors = []
    if total_units != 12414:
        errors.append(f"Headline unit reconciliation: expected 12,414, got {total_units:,}")
    if 5324 + 5245 != 10569:
        errors.append("Multifamily + Homeownership should equal 10,569 units")
    if total_dollars != 2609735303:
        errors.append(f"Headline dollar reconciliation: expected $2,609,735,303, got ${total_dollars:,}")
    if errors:
        raise SystemExit("Headline reconciliation mismatch(es):\n" + "\n".join(errors))
    print("Executive-summary headline verified: Multifamily(5,324)+Homeownership(5,245)"
          "+NeighborhoodDev(1,404)+HousingSolutions(441)=12,414 units; all six "
          "categories' dollars sum to $2,609,735,303 (~$2.610B).")


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
    for name, address, city, units, sources in RAW_PROJECTS:
        query = f"{address}, {city}, MI" if address else f"{city}, MI"
        coords = geocode(query, cache)
        status = "ok"
        if coords is None:
            coords = geocode(f"{city}, MI", cache)
            status = "city_center" if coords else "unresolved"
        primary = next((s for s in FUNDING_PRIORITY if s in sources), sources[0])
        base_id = (name.lower().replace(" ", "-").replace("'", "").replace(".", "")
                   .replace(",", "").replace("&", "and").replace("(", "").replace(")", "")
                   .replace("%", "pct").replace("/", "-"))
        while "--" in base_id:
            base_id = base_id.replace("--", "-")
        base_id = base_id.strip("-")
        pid = base_id
        n = 2
        while pid in seen_ids:
            pid = f"{base_id}-{n}"
            n += 1
        seen_ids.add(pid)
        projects.append({
            "id": pid,
            "name": name,
            "address": address,
            "city": city,
            "lat": round(coords[0], 5) if coords else None,
            "lon": round(coords[1], 5) if coords else None,
            "units": units,
            "funding_sources": sources,
            # Neither Exhibit 1 nor Exhibit 2 discloses a per-project dollar
            # amount -- see module docstring. Not fabricated here.
            "source_amounts": {},
            "total_amount": None,
            "primary_color_group": FUNDING_COLOR_GROUP[primary],
            "overlaps": len(sources) > 1,
            "geocode_status": status,
        })
    return projects


def main():
    verify_exhibit_totals()
    verify_category_unit_and_dollar_totals()
    verify_homeownership_totals()
    verify_rental_assistance_totals()
    verify_homeless_grant_totals()
    verify_neighborhood_totals()
    verify_housing_solutions_totals()
    verify_headline_reconciliation()
    print("Geocoding project addresses via Nominatim...")
    projects = build_projects()
    unresolved = [p["name"] for p in projects if p["geocode_status"] == "unresolved"]
    if unresolved:
        print(f"  {len(unresolved)} project(s) could not be geocoded: {unresolved}")
    city_center = [p["name"] for p in projects if p["geocode_status"] == "city_center"]
    if city_center:
        print(f"  {len(city_center)} project(s) fell back to city-center geocoding: {city_center}")

    payload = {
        "MI": {
            "hfa_name": "Michigan State Housing Development Authority",
            "hfa_abbr": "MSHDA",
            "fiscal_year": "FY2025",
            "source_title": "FY 2025 Production Goals Report",
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
