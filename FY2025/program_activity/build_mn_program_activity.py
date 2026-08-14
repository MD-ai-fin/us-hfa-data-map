"""
Builds docs/mn_program_activity.json from two independently-scoped Minnesota
Housing Finance Agency ("Minnesota Housing") source layers, plus Minnesota
Housing's own FY2025 audited financial statements (for GASB fund-type
classification).

Sources
---------------------------------------------------------------------------
1. KPI/category layer -- "Minnesota Housing 2025 Program Assessment Report"
   (Minnesota Housing's statutorily-mandated annual report to the
   Legislature, Table 3 "Funding and Household Characteristics by Program"):
     https://mnhousing.gov/documents/53435/2025_program_assessment_report/view
   (also filed with the Legislative Reference Library:
     https://www.lrl.mn.gov/docs/2025/other/251924.pdf -- this is the URL
     already recorded for MN in FY2025/direct_urls.json / state_hfa_catalog.json)
   Local copy: FY2025/program_activity/pdf/MN_MNHousing_ProgramAssessmentReport_2025.pdf
2. Project/award layer -- "2025 Multifamily Consolidated RFP/2026 HTC Round 1,
   Summary of Recommendations: Detailed Report" (dollar-by-funding-source
   table) and its companion "Selected Applications" contact/address sheet:
     https://www.mnhousing.gov/home/rental-housing/housing-development-and-capital-programs/rfps/consolidated-rfp-htc
   Local copies:
     FY2025/program_activity/pdf/MN_MNHousing_ConsolidatedRFP_2025.pdf
     FY2025/program_activity/pdf/MN_MNHousing_SelectedApplications_2025.pdf
3. Minnesota Housing's own separately-issued FY2025 audited financial
   statements ("Annual Financial Report...year ended June 30, 2025"), used
   ONLY for fund-type classification:
     FY2025/txt/MN_MNHousing_FY2025_ACFR.txt
   VERIFIED before use (this project has repeatedly found mismatched .txt
   files under other states): title page reads "MINNESOTA HOUSING FINANCE
   AGENCY / Annual Financial Report as of and for the year ended June 30,
   2025 / A Component Unit of the State of Minnesota"; the Independent
   Auditor's Report is addressed "To the Board of Directors, Minnesota
   Housing Finance Agency, St. Paul, Minnesota"; Note 1 states the Agency
   "was created in 1971 by the Minnesota legislature through the enactment
   of Minnesota Statutes, Chapter 462A". Unambiguously the correct entity,
   no substitution needed.

IMPORTANT reporting-period note: THREE different fiscal-year conventions
are in play for Minnesota and are never mixed in this script's output
---------------------------------------------------------------------------
  - The Program Assessment Report (source 1, the KPI/category layer used
    for CATEGORIES below) is explicitly a FEDERAL fiscal year: "AWARDS FOR
    GAP FINANCING FOR CAPITAL PROJECTS During Program Year 2025" states
    "Minnesota Housing made [awards] during program year 2025 (October 1,
    2024 through September 30, 2025)" (Program Assessment Report, p.36) --
    i.e. FFY2025 = Oct 1, 2024 - Sep 30, 2025. This script labels every
    Program-Assessment-sourced figure "FFY2025" and sets the payload's own
    top-level fiscal_year to "FFY2025" accordingly (per this build's task
    brief -- do not silently relabel this "FY2025").
  - The Consolidated RFP / Selected Applications tables (source 2, used for
    RAW_PROJECTS) are undated by fiscal year in their own text but are
    fielded under the same FFY2025 Program Assessment umbrella (the
    Program Assessment Report's own p.36 "AWARDS FOR GAP FINANCING" section
    explicitly reproduces this same Consolidated RFP awards data, in a
    rotated/mirrored-text landscape table on pp.37+ -- see "Known PDF
    extraction quirk" below) and both PDFs are internally dated December
    2025 (their own footer timestamps: RFP Detailed Report "12/18/2025",
    Selected Applications "12/18/2025 11:38 AM") -- i.e. squarely inside
    the FFY2025 (Oct 2024-Sep 2025)-adjacent selection cycle that the
    Program Assessment Report describes as "will show up as disbursed
    funds in future Program Assessments" (see the awards-vs-disbursed note
    below). This script uses "FFY2025" for these too.
  - Minnesota Housing's own ACFR (source 3, used ONLY for fund-type
    classification) runs on the AGENCY's fiscal year, July 1 - June 30
    ("Annual Financial Report...for the year ended June 30, 2025"). This is
    NOT the same year as FFY2025 above (it overlaps only Oct 2024-Jun 2025
    of the two periods) -- irrelevant to this script's own headline
    numbers since the ACFR is cited only for fund-name/fund-type
    classification, never for dollar or unit figures, but flagged here so
    a reader does not assume "FY2025" on an ACFR citation means the same
    12 months as "FFY2025" on a Program Assessment citation.

CRITICAL data-scope distinction: AWARDS (RAW_PROJECTS, ~1,145 units) vs.
DISBURSED (CATEGORIES' "Rental Production" headline, 3,026 units) -- these
are NEVER added together or used to validate one another
---------------------------------------------------------------------------
The Program Assessment Report's own "AWARDS FOR GAP FINANCING FOR CAPITAL
PROJECTS" section (p.36) states this distinction explicitly, in its own
words: "The following five tables are based on funding awards that
Minnesota Housing made during program year 2025 (October 1, 2024 through
September 30, 2025). They reflect the funds Minnesota Housing will make
available for housing development projects, and it may take a year or two
for these funds to disburse because projects take time to go from funding
selection to construction. The previous sections of this Program
Assessment are based on disbursed funds, and the awarded funds presented
in the following tables will show up as disbursed funds in future Program
Assessments as construction is carried out."
  - CATEGORIES' "rental_production" (this script, below) uses Table 3's
    disbursed figure: $295,415,416 / 3,026 units, "Rental Production - New
    Construction and Rehabilitation (unduplicated count)" -- money that
    left the door in FFY2025 for construction/rehab already completed or
    underway.
  - RAW_PROJECTS (this script, below) uses the Consolidated RFP's own
    printed "STATE TOTALS" row: 1,145 units / $218,384,571 estimated total
    development cost, across 20 newly-SELECTED-but-not-yet-disbursed
    developments -- money committed to future construction, most of which
    will not appear as "disbursed" until FFY2026 or later per the Program
    Assessment's own quote above.
  These two numbers are structurally unrelated (different developments,
  different disbursement stage) and this script does not force any
  reconciliation between them -- consistent with this project's "never
  fabricate/never force a reconciliation across mismatched conventions"
  rule (same approach as CT's SSHP-gap and PA's Map-Doc-vs-press-release
  handling).

Known PDF extraction quirk, checked and NOT needed for this build
---------------------------------------------------------------------------
Per this build's task brief, pp.37-40 of the Program Assessment Report
("AWARDS FOR GAP FINANCING FOR CAPITAL PROJECTS", a landscape-oriented
table) extract with each line of text reversed character-by-character
(e.g. "Selections" -> "snoitceleS", "SELECTIONS" -> "SNOITCELES") --
confirmed present, unfixed, by a one-off pdfplumber text dump of the
Program Assessment Report during development (grep for
"snoitceleS"/"SNOITCELES" finds multiple hits on pp.37, 40-41). This
script does NOT attempt to de-mirror that text: pp.37+ is confirmed (by
its own readable column headers -- "Housing Infrastructure Bonds",
"Syndication Proceeds", "National Housing Trust Fund", "HOME", "Challenge"
-- matching every funding-source name already in the dedicated
Consolidated RFP Detailed Report) to be Minnesota Housing's own
in-report reproduction of the SAME Rental Housing Consolidated RFP
selections already used for RAW_PROJECTS below, via the separate,
non-rotated, fully machine-readable Detailed Report + Selected
Applications PDFs -- a strictly cleaner and independently cross-verified
source for the same data (see "Column-position verification" below), so
reversing the mirrored text would add risk without adding information.
Flagged here per the task brief's request to document this check.

Category-level methodology (Table 3, "Funding and Household
Characteristics by Program, FFY 2025")
---------------------------------------------------------------------------
"rental_production": headline $295,415,416 / 3,026 units is Table 3's own
printed "Rental Production - New Construction and Rehabilitation
(unduplicated count)" line, used verbatim. Its three printed subtotals
(New Construction Subtotal $194,609,019/900, Rehabilitation Subtotal
$85,972,086/1,764, Refinance Only Subtotal $14,079,311/295) sum to only
2,959 units / $294,660,416 -- 67 units and ~$755K short of the printed
"unduplicated count" headline. This script checked every footnote on this
line (footnote markers 7 and, by proximity, 3) for an explanation:
footnote 7 ("The demographic information for rental production numbers
excludes units that also receive Section 8 Project-Based assistance...")
addresses a DIFFERENT gap (a demographics-table exclusion, not a
unit-count reconciliation), and footnote 3 (about unduplicated
homeownership second-mortgage subtotals) is not about this line at all --
neither footnote explains the 67-unit/~$755K gap. Per this project's
"never force a reconciliation" rule, this script uses the report's own
3,026/$295,415,416 headline as fy2025_actual and treats the three
subtotals as non-additive reference chips (additive=False), recording the
unexplained gap here rather than silently absorbing it into a fabricated
4th bucket.

"lmir": Table 3's own single printed line, "Low and Moderate Income Rental
(LMIR) $107,629,000 877" -- used verbatim. NOTE: this is a DIFFERENT,
larger, differently-scoped LMIR figure than the "lmir_award" subprogram
under "multifamily_awards" below ($19,670,000 across 8 of the 20 newly
selected 2025 projects) -- the former is FFY2025 disbursed dollars
(Table 3), the latter is 2025-selection awarded dollars for a specific
funding source within a smaller set of new developments (Consolidated
RFP). Never added together, per the awards-vs-disbursed note above.

"lihtc": Table 3's own single printed line, "Low-Income Housing Tax
Credits (LIHTC) $9,426,276 308 ... - Tax Credit Allocation Amount" --
used verbatim. This is footnote-8: "The total amount of tax credit
allocation amounts is reported for developments with loans that closed in
the reporting year." Table 3 separately prints, immediately below this
line, "Syndication Proceeds ($s excluded from Rental Production Total)
$85,537,959 308 $277,721" -- Minnesota Housing's OWN table explicitly
labels this second, much larger figure as excluded from the Rental
Production Total, so this script surfaces it only as an extra
fy2025_amounts reference chip on the lihtc category (label
"mn_amt_lihtc_syndication_proceeds"), never as the category's own
fy2025_actual or as additive with the $9,426,276 allocation-amount figure.

"homeownership": headline $1,041,376,126 / 5,619 households is Table 3's
own printed "Homebuyer and Home Refinance (unduplicated count)" line, used
verbatim. Its six disclosed subprograms are NOT additive
(additive=False): Start Up ($748,385,139/3,374) and Step Up
($147,704,023/551) are first-mortgage loan products; Deferred Payment
Loans/DPL ($41,818,598/2,644), Monthly Payment Loans/MPL
($15,387,302/1,087), First-Generation Homebuyer Assistance - Minnesota
Housing ($30,112,077/871, "second mortgage" per Table 3's own row label)
and Community-Based First-Generation Homebuyers Assistance
($50,668,987/1,693) are all SECOND-mortgage/down-payment-assistance
products layered on top of a subset of the Start Up/Step Up first
mortgages (Table 3 labels DPL and MPL "(second mortgage)" directly in
their own row names) -- the naive sum of all six (3,374+551+2,644+1,087+
871+1,693 = 10,220) is nearly double the 5,619-household headline, since
one household's first mortgage and its layered second-mortgage assistance
are the SAME household counted under multiple subprogram rows. Same
overlapping-assistance-product pattern as PA's K-FIT/Advantage/PENNVEST
and CT's DAP/TTO, just with more simultaneous layers disclosed here.

Column-position verification (Consolidated RFP Detailed Report) --
RAW_PROJECTS / PROJECT_SOURCE_AMOUNTS methodology
---------------------------------------------------------------------------
The Detailed Report's PDF is a single wide (1008pt) landscape page whose
plain-text extraction interleaves multi-line wrapped column headers
unreadably (e.g. "Deferred Loan: Hsg Infrastructure Bonds Senior" prints
as scattered tokens across 4 separate physical text lines with other
columns' words interleaved between them). This script does NOT rely on
that flattened text for the funding-source breakdown. Instead, each
column's exact x-coordinate range was independently determined via
pdfplumber's word-level bounding boxes (extract_words()) on the header row
(y<140), producing 16 columns after City/Total Units: [1] [ESTIMATED]
Total Development Cost, [2] Other Committed/Pending Resources, [3]
[ESTIMATED] Syndication, [4] 9% HTC, [5] Deferred Loan: EDHC MF, [6]
Deferred Loan: Hsg Infrastructure Bonds - Preservation, [7] Deferred Loan:
Hsg Infrastructure Bonds - Senior, [8] Deferred Loan: Hsg Infrastructure
Bonds - Repayments, [9] Deferred Loan: HOME MF, [10] Deferred Loan: NHTF,
[11] Deferred Loan: PARIF, [12] Agency Deferred Loans Total, [13] LMIR
(HIF), [14] BBL (TEB), [15] HUD Section 811 Annualized Amount, [16] HUD
Section 811 Total Units. Every data row's words were then bucketed into
these same x-ranges to read off each project's per-column dollar value
(PROJECT_SOURCE_AMOUNTS below).

This column mapping was cross-checked two independent ways before being
trusted:
  (a) Internal arithmetic -- column [12] "Agency Deferred Loans Total"
      equals columns [5]+[6]+[7]+[8]+[9]+[10]+[11] summed, for every one
      of the 20 rows (verified in verify_deferred_loans_total_math()).
  (b) External reconciliation -- for the 18 of 20 projects that DO appear
      in the companion "Selected Applications" contact sheet (which
      independently prints named-source dollar lines like "EDHC MF
      $2,700,000", "LMIR 1st Mortgage $721,000", "HIB Senior $4,308,000"),
      every one of those explicit dollar figures matches this script's
      column-position-derived value exactly (verified in
      verify_selected_applications_cross_check()). Two figures this
      script derives from column position are NOT independently confirmed
      by Selected Applications, because that document simply omits them
      (an apparent gap in that document, not this script's transcription
      -- flagged inline in PROJECT_SOURCE_AMOUNTS' comments): Innsbruck
      Townhomes' $2,710,000 LMIR line, and Henry Hill Apartments'
      $4,480,000 BBL(TEB) line.
  (c) Column-sum reconciliation against the Detailed Report's own printed
      "STATE TOTALS" row -- every one of the 11 funding-source columns
      used in this script (9% HTC, EDHC MF, HIB-Preservation, HIB-Senior,
      HIB-Repayments, HOME MF, NHTF, PARIF, LMIR, BBL(TEB), HUD Section
      811 Annualized Amount) reconciles EXACTLY to the STATE TOTALS row's
      own printed figure for that column (verified in
      verify_state_totals(); STATE TOTALS: 1,145 units,
      $218,384,571 est. total development cost, 9% HTC $12,651,138, EDHC
      MF $13,717,100, HIB-Preservation $21,369,000, HIB-Senior
      $28,631,000, HIB-Repayments $3,572,000, HOME MF $20,005,000, NHTF
      $2,820,935, PARIF $17,800,200, Agency Deferred Loans Total
      $107,915,235, LMIR $19,670,000, BBL(TEB) $9,640,000, HUD Section 811
      Annualized Amount $668,748, HUD Section 811 Total Units 39). This is
      the strongest of the three checks and gives high confidence in the
      full column-position mapping, including the two Selected-
      Applications-silent figures noted in (b).

Two projects entirely absent from "Selected Applications" (not just
missing a street address) -- Missabe Manor and Lindquist Apartments
---------------------------------------------------------------------------
Per this build's task brief, "Selected Applications" was expected to cover
18 of 20 projects with a street address and 2 with "Multiple Building
Addresses" (city-level only). Investigation found a different split: only
18 of the Detailed Report's 20 projects appear in Selected Applications AT
ALL (confirmed by reading its own "Page 1 of 3" / "Page 2 of 3" / "Page 3
of 3" footers -- nothing is missing due to a truncated extraction). Of
those 18: 16 print a real street address, and 2 (White Earth Homes VI,
Torre De San Miguel) print "Multiple Building Addresses" verbatim,
matching the task brief's "2 Multiple Building Addresses" figure. The
remaining 2 Detailed-Report projects -- Missabe Manor (D8826) and
Lindquist Apartments (D3124) -- do not appear in Selected Applications at
all, under any address. Both share a distinguishing trait visible in the
Detailed Report's own columns: Lindquist Apartments' ONLY nonzero funding
column is 9% HTC ($679,550) -- it receives no Minnesota-Housing-
administered deferred loan or bond of any kind, which plausibly explains
its absence from a "Selected Applications" sheet that (per its own title)
is a contact/administration list for Minnesota-Housing-managed deferred-
loan resources. Missabe Manor is NOT fully explained by this same logic,
however -- it does have a nonzero LMIR figure ($735,000, column [13]) in
addition to 9% HTC ($2,647,213), so by the same reasoning it would be
expected to appear; its absence from Selected Applications is recorded
here as an unresolved, apparently genuine gap in that source document,
not a fabrication or an extraction error in this script. Both projects
therefore fall back to Detailed-Report-only City-level geocoding
(geocode_status="city_center"), exactly like the 2 explicit "Multiple
Building Addresses" projects -- 4 projects total at city_center precision,
not the 2 the task brief anticipated, with the reason documented
per-project in RAW_PROJECTS' inline comments.

One further address caveat: Third Rapids Apartments' own Selected
Applications street line prints "XXXX 15th St. S." -- "XXXX" is that
document's own placeholder for an undisclosed house number (not a
transcription artifact here), so this script treats Third Rapids as
address=None (city-center fallback) rather than fabricate or geocode a
placeholder as if it were real.

Fund-type classification (fund_type/fund_name on each subprogram)
---------------------------------------------------------------------------
Minnesota Housing's own FY2025 (year ended June 30, 2025) audited
financial statements state, in the Independent Auditors' Report and Note
2 ("Summary of Significant Accounting and Reporting Policies", "Basis of
Accounting"): "We have audited the financial statements of the
business-type activities of the Minnesota Housing Finance Agency" and
"[the] financial statements...have been prepared...utilizing the
proprietary fund concept". I.e., like PHFA, CHFA and Florida Housing (and
unlike IHDA's mixed governmental+proprietary major-fund structure),
Minnesota Housing has NO governmental funds of its own -- every dollar it
carries is inside its single proprietary/business-type presentation. Note
1 ("Nature of Business and Fund Structure") separately NAMES several of
the Agency's own internally-designated funds: General Reserve, Rental
Housing, Residential Housing Finance (which contains the "Alternative
Loan Fund"'s Pool 2/Housing Investment Fund and Pool 3/Housing
Affordability Fund sub-funds), Homeownership Finance, Multifamily
Housing, HOMES(SM), State Appropriated, and Federal Appropriated. The
working distinction below parallels PA/CT/FL's: "proprietary" (confidence
noted per item) when a subprogram maps onto one of these named funds by
literal name match or by the fund's own stated purpose/program
description, vs. "off_balance_sheet" when a subprogram is confirmed
absent from the Agency's own financial statements by name/description.
  - "proprietary", HIGH confidence (literal name or dollar-figure match in
    the ACFR itself):
      * hib_preservation, hib_senior, hib_repayments (Housing
        Infrastructure Bonds) -- Note 15/MD&A text states "the Agency
        recorded the Nonprofit Housing Bonds and Housing Infrastructure
        Bonds as bonds [payable]" -- Housing Infrastructure Bonds are
        literally named and recorded as the Agency's own bonded debt.
      * nhtf (National Housing Trust Fund) -- Note 4 ("Loans Receivable,
        Net") states the Agency "has deferred and/or forgivable loans
        with net carrying values of $0 in the Federal Appropriated,
        HOMES(SM), National Housing Trust Fund (NHTF) and [HOPWA]
        programs" -- NHTF is named verbatim as one of the Agency's own
        loan-carrying fund categories (net carrying value $0 because these
        loans are fully reserved at origination per Note 4's own
        explanation, not because NHTF itself is absent from the
        statements).
      * start_up, step_up (Home Mortgage Loans - Start Up/Step Up, first
        mortgages) -- Note 1's "Residential Housing Finance" and
        "Homeownership Finance" fund descriptions state these bond
        resolutions were "the principal sources of financing for
        bond-financed homeownership programs...for the purpose of funding
        purchases of single family first mortgage loans" -- Start Up/Step
        Up are exactly this product (Program Assessment Table 2 lists
        both as "Amortizing Loans" first-mortgage products); Note 4's
        loans-receivable table separately shows $144.6M/$55.6M of
        "Homeownership, first mortgage loans" carried in Residential
        Housing Finance/Pool 2.
  - "proprietary" (inferred by program description, not a literal brand-
    name match in the ACFR -- MEDIUM confidence, same caveat pattern PA's
    build used for K-FIT/Advantage):
      * edhc_mf, parif (Economic Development and Housing Challenge /
        Preservation Affordable Rental Investment Fund, both Deferred
        Loan columns) -- Note 1's "State Appropriated" fund description:
        "funds received from the Minnesota legislature which are to be
        used for programs...in the form of low-interest loans, no-
        interest deferred loans...down-payment assistance...and other
        housing-related program costs" -- matches EDHC/PARIF's own
        Program Assessment description as state-legislature-funded
        deferred-loan programs, though neither acronym appears verbatim
        in the ACFR.
      * home_mf (HOME MF, a federal HOME Investment Partnerships Program
        deferred loan) -- Note 1's "Federal Appropriated" fund
        description: "funds received from the federal government which
        are to be used for programs...in the form of no-interest deferred
        loans and grants...and other housing-related program costs" --
        matches HOME's federal-pass-through structure, though "HOME"
        itself does not appear verbatim (a generic word, not searchable
        as a literal string).
      * lmir_disbursed / lmir_award (Low and Moderate Income Rental) --
        Note 1's "Rental Housing" fund description: "Activities relating
        to bond-financed multifamily housing programs are maintained
        under the Rental Housing bond resolution. Loans are generally
        secured by first mortgages on real property" -- matches LMIR's
        own description (a multifamily first-mortgage loan program), and
        Note 4's loans-receivable table shows $294.3M of loans carried in
        the "Rental Housing" fund, though "LMIR" itself is never spelled
        out verbatim in the ACFR (same medium-confidence, by-description
        match as PA's K-FIT).
      * bbl_teb (BBL(TEB), read from the Selected Applications sheet's own
        abbreviation "BL") -- Note 1's "Residential Housing Finance"/Pool
        2 description states funds "provided capital for...tax credit
        bridge loans", and Note 12 separately references an "outstanding
        bridge loan liability" -- i.e. the Agency does carry bridge-loan
        financing (consistent with "BBL" = Bridge Bond Loan, "TEB" = Tax-
        Exempt Bond) as its own liability, though "BBL"/"TEB" themselves
        are never spelled out verbatim -- confidence: medium-low, flagged
        as inferred.
      * dpl, mpl, first_gen_mn, first_gen_community (Deferred Payment
        Loans / Monthly Payment Loans / First-Generation Homebuyer
        Assistance, all "second mortgage" homeownership-assistance
        products per Table 3's own row labels) -- same "State Appropriated"
        fund description as edhc_mf/parif above (state-legislature-funded
        down-payment assistance); the Commissioner's own message (p.2)
        additionally names "the one-time $50 million First-Generation
        Homebuyer Loan Program" as a 2023-legislative-session-funded
        Agency program, and p.28's "State Legislative Actions" section
        separately names "First-Time Homebuyer Downpayment Assistance,
        First-Generation Downpayment Assistance (administered...through
        Community Development Financial Institutions)" -- confirming
        Community-Based First-Generation Homebuyers Assistance is the
        same State-Appropriated-funded program administered through CDFI
        partners, not a separate off-balance-sheet pass-through.
  - "off_balance_sheet" (confirmed absent from the Agency's own financial
    statements by name/description, or structurally external to its own
    balance sheet):
      * 9pct_htc, lihtc_disbursed (9% Housing Tax Credits / Low-Income
        Housing Tax Credits) -- the MD&A states plainly: "The federal Low
        Income Housing Tax Credit is another resource the Agency
        allocates" -- "allocates" (not "holds"/"carries"), matching this
        project's consistent off-balance-sheet treatment of LIHTC
        everywhere else (IL/PA/FL/CT's LIHTC and PHTC/HTCC treatment):
        federal/state tax credits pass directly to developers/investors
        and are never booked as the Agency's own fund asset.
      * hud811 (HUD Section 811 Annualized Amount / HUD Section 811 Total
        Units) -- "Section 811"/"811" never appears anywhere in
        MN_MNHousing_FY2025_ACFR.txt in this program context (checked; the
        only "811" hits in the full-text search are unrelated page/table
        numbers) -- HUD's own Section 811 Supportive Housing for Persons
        with Disabilities program funds flow federally to the projects
        directly, administered but not carried by the Agency.

Geocoding
---------------------------------------------------------------------------
Nominatim (OpenStreetMap), primary query "{street address}, {city}, MN"
for the 15 projects with a real, non-placeholder street address, of which
14 resolve successfully (geocode_status="ok"; two -- Flour Exchange and
Cedar View Apartments -- needed a query-normalization fix, see
GEOCODE_QUERY_OVERRIDE, because Nominatim's search does not resolve
spelled-out ordinals like "Fourth" or a bare unordinaled number like "15
Ave"; the corrected queries independently confirm the addresses are real,
e.g. resolving to a place literally named "Flour Exchange Building").
Falls back to "{city}, MN" (geocode_status="city_center") for the
remaining 6 projects: Kendall Pointe's own printed address is a street
INTERSECTION ("18th Ave NW & 55th St NW"), which Nominatim's simple search
cannot resolve as a single point, so it falls back rather than guessing
which of the two streets to use; 2 explicit "Multiple Building Addresses"
(White Earth Homes VI, using the Detailed Report's own City column
"Mahnomen" rather than Selected Applications' "White Earth" community
name, since Mahnomen is the Detailed Report's -- this script's primary
RAW_PROJECTS source -- own standardized city join; Torre De San Miguel,
"Saint Paul"); 2 entirely absent from Selected Applications (Missabe Manor
"Hibbing", Lindquist Apartments "Minneapolis", both per the Detailed
Report's own City column); and 1 undisclosed-house-number placeholder
(Third Rapids Apartments, "Sartell"). Self-throttled to <=1 request/second
with an identifying User-Agent per Nominatim's usage policy, same approach
as every other pilot state's build script.

fy2026
---------------------------------------------------------------------------
Neither the Program Assessment Report nor the Consolidated RFP/Selected
Applications documents contain any FY2026/FFY2026-projected figures
(checked: "2026" appears exactly once in the entire 1,866-line Program
Assessment extraction, as a passing reference to "the 2026-2027 Affordable
Housing Plan" by name, with no accompanying number). Every fy2026 field
below is therefore {value: None, amount: None, closed: False,
note_key: "mnFy26NotePending"}.
"""

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "mn_program_activity.json"

SOURCE_URL = "https://mnhousing.gov/documents/53435/2025_program_assessment_report/view"
SOURCE_FILE = (
    "MN_MNHousing_ProgramAssessmentReport_2025.pdf (+ 2025 Multifamily "
    "Consolidated RFP/2026 HTC Round 1 Detailed Report and Selected "
    "Applications)"
)
RETRIEVED = "2026-08-14"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
GEOCODER_USER_AGENT = "us-hfa-data-map/1.0 (github.com/MD-ai-fin/us-hfa-data-map)"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "mnFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data (Program Assessment Report, Table 3, "Funding and
# Household Characteristics by Program, FFY 2025")
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "rental_production",
        "unit_type": "units",
        "fy2025_actual": 3026,
        "fy2025_source_quote": (
            "Table 3: \"Rental Production - New Construction and Rehabilitation "
            "(unduplicated count) $295,415,416 3,026\". Printed subtotals: New "
            "Construction Subtotal $194,609,019 / 900; Rehabilitation Subtotal "
            "$85,972,086 / 1,764; Refinance Only Subtotal $14,079,311 / 295 -- these "
            "three sum to only 2,959 units / $294,660,416, 67 units and ~$755K short "
            "of the printed 3,026/$295,415,416 headline. Neither footnote near this "
            "line (7 or 3) explains the gap (footnote 7 covers a demographic-table "
            "exclusion for Section-8-Project-Based units, unrelated to this unit "
            "count). This script uses the report's own printed headline "
            "(3,026/$295,415,416) as fy2025_actual and does not force a "
            "reconciliation of the unexplained gap -- see module docstring."
        ),
        "fy2025_amounts": [
            {"label_key": "mn_amt_new_construction", "amount": 194609019},
            {"label_key": "mn_amt_rehabilitation", "amount": 85972086},
            {"label_key": "mn_amt_refinance_only", "amount": 14079311},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "new_construction", "fy2025_units": 900, "fy2025_amount": 194609019,
             "color_group": "capital",
             # Aggregates multiple underlying funding sources (LMIR, HIB, HOME,
             # NHTF, EDHC, PARIF, LIHTC, etc.) per project -- Table 3 does not
             # break this construction-type subtotal down by funding source, so
             # no single named MN Housing fund applies.
             "fund_type": "mixed",
             "fund_name": "Multiple bond/state/federal programs (LMIR, HIB, HOME, "
                           "NHTF, EDHC, PARIF, LIHTC and others; program-level "
                           "breakdown not separately disclosed in this table)",
             "fy2026": _FY26_PENDING},
            {"key": "rehabilitation", "fy2025_units": 1764, "fy2025_amount": 85972086,
             "color_group": "capital",
             "fund_type": "mixed",
             "fund_name": "Multiple bond/state/federal programs (LMIR, HIB, HOME, "
                           "NHTF, EDHC, PARIF, LIHTC and others; program-level "
                           "breakdown not separately disclosed in this table)",
             "fy2026": _FY26_PENDING},
            {"key": "refinance_only", "fy2025_units": 295, "fy2025_amount": 14079311,
             "color_group": "capital",
             "fund_type": "mixed",
             "fund_name": "Multiple bond/state/federal programs (LMIR, HIB, HOME, "
                           "NHTF, EDHC, PARIF, LIHTC and others; program-level "
                           "breakdown not separately disclosed in this table)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "lmir",
        "unit_type": "units",
        "fy2025_actual": 877,
        "fy2025_source_quote": (
            "Table 3: \"Low and Moderate Income Rental (LMIR) $107,629,000 877 "
            "$122,724 $27,403 50.9%\" -- Minnesota Housing's disbursed FFY2025 LMIR "
            "first-mortgage lending, used verbatim. NOTE: this is a different, "
            "larger, differently-scoped figure than the lmir_award subprogram under "
            "multifamily_awards below ($19,670,000 across 8 of the 20 newly-selected "
            "2025 projects) -- disbursed-FFY2025 vs. selected-but-not-yet-disbursed "
            "2025 awards -- never added together."
        ),
        "fy2025_amounts": [
            {"label_key": "mn_amt_lmir_disbursed", "amount": 107629000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "lmir_disbursed", "fy2025_units": 877, "fy2025_amount": 107629000,
             "color_group": "capital",
             # Note 1's "Rental Housing" fund description ("bond-financed
             # multifamily housing programs...secured by first mortgages") matches
             # LMIR's own first-mortgage structure; Note 4 shows $294.3M of loans
             # carried in the Rental Housing fund. "LMIR" itself is never spelled
             # out verbatim in the ACFR -- confidence: medium (by description).
             "fund_type": "proprietary", "fund_name": "Rental Housing (inferred, not separately named in the ACFR)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "lihtc",
        "unit_type": "units",
        "fy2025_actual": 308,
        "fy2025_source_quote": (
            "Table 3: \"Low-Income Housing Tax Credits (LIHTC) $9,426,276 308 "
            "$30,605 $24,760 50.2% - Tax Credit Allocation Amount\" (footnote 8: "
            "\"reported for developments with loans that closed in the reporting "
            "year\"), used verbatim. Table 3 separately, immediately below, prints "
            "\"Syndication Proceeds ($s excluded from Rental Production Total) "
            "$85,537,959 308 $277,721\" -- the report's OWN table explicitly labels "
            "this larger syndication-proceeds figure as excluded from the Rental "
            "Production Total, so it is shown here only as a reference amount, never "
            "as fy2025_actual or added to the $9,426,276 allocation amount."
        ),
        "fy2025_amounts": [
            {"label_key": "mn_amt_lihtc_allocation", "amount": 9426276},
            {"label_key": "mn_amt_lihtc_syndication_proceeds", "amount": 85537959},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "lihtc_disbursed", "fy2025_units": 308, "fy2025_amount": 9426276,
             "color_group": "credit",
             # MD&A: "The federal Low Income Housing Tax Credit is another resource
             # the Agency allocates" -- allocated directly to developers/investors,
             # never a Minnesota Housing-carried fund asset. Same off-balance-sheet
             # treatment as every other pilot state's LIHTC/HTC subprogram.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "homeownership",
        "unit_type": "households",
        "fy2025_actual": 5619,
        "fy2025_source_quote": (
            "Table 3: \"Homebuyer and Home Refinance (unduplicated count) "
            "$1,041,376,126 5,619\", used verbatim. Subprograms: \"Home Mortgage "
            "Loans - Start Up $748,385,139 3,374\"; \"Home Mortgage Loans - Step Up "
            "$147,704,023 551\"; \"Deferred Payment Loans (DPL) (second mortgage) "
            "$41,818,598 2,644\"; \"Monthly Payment Loans (MPL) (second mortgage) "
            "$15,387,302 1,087\"; \"First-Generation Homebuyer Assistance Program - "
            "Minnesota Housing (second mortgage) $30,112,077 871\"; \"Community-Based "
            "First-Generation Homebuyers Assistance $50,668,987 1,693\". DPL/MPL/"
            "First-Generation are all second-mortgage assistance layered on top of a "
            "subset of the Start Up/Step Up first mortgages (Table 3 labels DPL and "
            "MPL \"(second mortgage)\" directly) -- the six subprograms' naive sum "
            "(10,220) is nearly double the 5,619-household headline, so they are "
            "shown as non-additive reference chips, not stacked."
        ),
        "fy2025_amounts": [
            {"label_key": "mn_amt_homebuyer_total", "amount": 1041376126},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "start_up", "fy2025_units": 3374, "fy2025_amount": 748385139,
             "color_group": "bond",
             # Note 1's "Residential Housing Finance"/"Homeownership Finance" bond
             # resolutions: "the principal sources of financing for bond-financed
             # homeownership programs...for the purpose of funding purchases of
             # single family first mortgage loans"; Note 4 shows $144.6M/$55.6M
             # first-mortgage loans carried in these funds.
             "fund_type": "proprietary", "fund_name": "Residential Housing Finance / Homeownership Finance (bond-financed first mortgages)",
             "fy2026": _FY26_PENDING},
            {"key": "step_up", "fy2025_units": 551, "fy2025_amount": 147704023,
             "color_group": "bond",
             "fund_type": "proprietary", "fund_name": "Residential Housing Finance / Homeownership Finance (bond-financed first mortgages)",
             "fy2026": _FY26_PENDING},
            {"key": "dpl", "fy2025_units": 2644, "fy2025_amount": 41818598,
             "color_group": "capital",
             # Note 1's "State Appropriated" fund: "funds received from the
             # Minnesota legislature...in the form of...down-payment assistance".
             # "DPL" itself not spelled out verbatim -- confidence: medium.
             "fund_type": "proprietary", "fund_name": "State Appropriated (inferred, not separately named in the ACFR)",
             "fy2026": _FY26_PENDING},
            {"key": "mpl", "fy2025_units": 1087, "fy2025_amount": 15387302,
             "color_group": "capital",
             "fund_type": "proprietary", "fund_name": "State Appropriated (inferred, not separately named in the ACFR)",
             "fy2026": _FY26_PENDING},
            {"key": "first_gen_mn", "fy2025_units": 871, "fy2025_amount": 30112077,
             "color_group": "capital",
             # Commissioner's message (p.2) names "the one-time $50 million
             # First-Generation Homebuyer Loan Program" as a 2023-legislative-
             # session-funded Agency program; matches State Appropriated fund
             # purpose. Confidence: medium.
             "fund_type": "proprietary", "fund_name": "State Appropriated (First-Generation Homebuyer Loan Program)",
             "fy2026": _FY26_PENDING},
            {"key": "first_gen_community", "fy2025_units": 1693, "fy2025_amount": 50668987,
             "color_group": "capital",
             # p.28 "State Legislative Actions": "First-Generation Downpayment
             # Assistance (administered...through Community Development Financial
             # Institutions)" -- same State-Appropriated-funded program, delivered
             # via CDFI partners rather than directly. Confidence: medium.
             "fund_type": "proprietary", "fund_name": "State Appropriated (First-Generation Downpayment Assistance via CDFIs)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "multifamily_awards",
        "unit_type": "units",
        "fy2025_actual": 1145,
        "fy2025_source_quote": (
            "\"2025 Multifamily Consolidated RFP/2026 HTC Round 1, Summary of "
            "Recommendations: Detailed Report\", printed \"STATE TOTALS\" row: 1,145 "
            "units, $218,384,571 estimated total development cost, across 20 newly-"
            "selected developments (GREATER MINNESOTA TOTALS 435 units / METROPOLITAN "
            "TOTALS 710 units). This is a SEPARATE, smaller, differently-scoped "
            "figure from the rental_production category above (3,026 units) -- these "
            "20 developments are 2025 AWARDS (selected but not yet disbursed), not "
            "the FFY2025 DISBURSED total; see module docstring's awards-vs-disbursed "
            "note. Never added to or reconciled against rental_production."
        ),
        "fy2025_amounts": [
            {"label_key": "mn_amt_award_total_dev_cost", "amount": 218384571},
            {"label_key": "mn_amt_award_9pct_htc", "amount": 12651138},
            {"label_key": "mn_amt_award_deferred_loans_total", "amount": 107915235},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "9pct_htc", "fy2025_units": 322, "fy2025_amount": 12651138,
             "color_group": "credit",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "edhc_mf", "fy2025_units": 398, "fy2025_amount": 13717100,
             "color_group": "capital",
             "fund_type": "proprietary", "fund_name": "State Appropriated (inferred, not separately named in the ACFR)",
             "fy2026": _FY26_PENDING},
            {"key": "hib_preservation", "fy2025_units": 88, "fy2025_amount": 21369000,
             "color_group": "bond",
             "fund_type": "proprietary", "fund_name": "Housing Infrastructure Bonds",
             "fy2026": _FY26_PENDING},
            {"key": "hib_senior", "fy2025_units": 189, "fy2025_amount": 28631000,
             "color_group": "bond",
             "fund_type": "proprietary", "fund_name": "Housing Infrastructure Bonds",
             "fy2026": _FY26_PENDING},
            {"key": "hib_repayments", "fy2025_units": 31, "fy2025_amount": 3572000,
             "color_group": "bond",
             "fund_type": "proprietary", "fund_name": "Housing Infrastructure Bonds",
             "fy2026": _FY26_PENDING},
            {"key": "home_mf", "fy2025_units": 342, "fy2025_amount": 20005000,
             "color_group": "trust",
             "fund_type": "proprietary", "fund_name": "Federal Appropriated (inferred, not separately named in the ACFR)",
             "fy2026": _FY26_PENDING},
            {"key": "nhtf", "fy2025_units": 48, "fy2025_amount": 2820935,
             "color_group": "trust",
             "fund_type": "proprietary", "fund_name": "National Housing Trust Fund (NHTF)",
             "fy2026": _FY26_PENDING},
            {"key": "parif", "fy2025_units": 255, "fy2025_amount": 17800200,
             "color_group": "trust",
             "fund_type": "proprietary", "fund_name": "State Appropriated (inferred, not separately named in the ACFR)",
             "fy2026": _FY26_PENDING},
            {"key": "lmir_award", "fy2025_units": 382, "fy2025_amount": 19670000,
             "color_group": "capital",
             "fund_type": "proprietary", "fund_name": "Rental Housing (inferred, not separately named in the ACFR)",
             "fy2026": _FY26_PENDING},
            {"key": "bbl_teb", "fy2025_units": 94, "fy2025_amount": 9640000,
             "color_group": "bond",
             "fund_type": "proprietary", "fund_name": "Residential Housing Finance / Pool 2 (bridge loan financing, inferred)",
             "fy2026": _FY26_PENDING},
            # fy2025_units uses HUD Section 811's OWN disclosed sub-unit count (39,
            # column [16] of the Detailed Report) rather than the project-total-
            # units-sum proxy used for the other 10 sources (which would overstate
            # this program's reach as 418 -- most units in a Section-811-touched
            # project do NOT themselves carry Section 811 assistance). See module
            # docstring.
            {"key": "hud811", "fy2025_units": 39, "fy2025_amount": 668748,
             "color_group": "capital",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
]

# ---------------------------------------------------------------------------
# Multifamily project-level detail (Consolidated RFP Detailed Report +
# Selected Applications). One row per development:
# (name, address_or_None, city, total_units, {source_key: amount})
# address=None marks a project with no usable street address (2 explicit
# "Multiple Building Addresses", 2 entirely absent from Selected
# Applications, 1 undisclosed "XXXX" house-number placeholder) -- see
# module docstring for the per-project reason.
# ---------------------------------------------------------------------------

RAW_PROJECTS = [
    # GREATER MINNESOTA (10 projects, 435 units)
    ("Third Rapids Apartments", None, "Sartell", 48,
     # Selected Applications prints "XXXX 15th St. S." -- XXXX is that
     # document's own undisclosed-house-number placeholder.
     {"9pct_htc": 1950000, "edhc_mf": 2963000, "lmir_award": 1400000, "hud811": 55140}),
    ("Hilltop Square Apartments", "405 Main St", "Eagle Bend", 23,
     {"hib_senior": 4308000}),
    ("Freeport Square Apartments", "109 3rd Ave NE", "Freeport", 19,
     {"9pct_htc": 425666, "parif": 1606200}),
    ("Missabe Manor", None, "Hibbing", 48,
     # Absent from Selected Applications entirely (not just missing an
     # address) -- see module docstring's "unresolved gap" note.
     {"9pct_htc": 2647213, "lmir_award": 735000}),
    ("Kendall Pointe", "18th Ave NW & 55th St NW", "Rochester", 40,
     {"9pct_htc": 1850000, "home_mf": 4001000, "lmir_award": 1431000, "hud811": 90840}),
    ("Innsbruck Townhomes", "1530 50th St NW", "Rochester", 40,
     # LMIR $2,710,000 is column-position-derived only -- Selected
     # Applications' own line for this project omits it (see docstring).
     {"hib_preservation": 9269000, "parif": 218000, "lmir_award": 2710000}),
    ("West Transit Village Ph. 1", "2905 2nd St SW", "Rochester", 75,
     {"hib_senior": 9700000, "lmir_award": 7808000}),
    ("Cedar View Apartments", "300 15 Ave NE", "Austin", 40,
     {"edhc_mf": 2700000, "home_mf": 5716000, "lmir_award": 721000, "bbl_teb": 5160000}),
    ("Henry Hill Apartments", "150 7th Ave", "Granite Falls", 54,
     # BBL(TEB) $4,480,000 is column-position-derived only -- Selected
     # Applications' own line for this project omits it (see docstring).
     {"parif": 10476000, "bbl_teb": 4480000}),
    ("White Earth Homes VI", None, "Mahnomen", 48,
     # "Multiple Building Addresses" per Selected Applications, which lists
     # city/county as "White Earth / Becker County"; this script uses the
     # Detailed Report's own City column ("Mahnomen") for geocoding
     # consistency with its primary RAW_PROJECTS source (see docstring).
     {"hib_preservation": 12100000}),
    # METROPOLITAN (10 projects, 710 units)
    ("Lindquist Apartments", None, "Minneapolis", 26,
     # Absent from Selected Applications entirely; its ONLY funding source
     # is 9% HTC (no MN-Housing-administered deferred loan/bond), plausibly
     # explaining the absence (see module docstring).
     {"9pct_htc": 679550}),
    ("Logan Avenue Flats Senior", "529 - 535 Logan Ave North", "Minneapolis", 48,
     {"hib_senior": 8083000}),
    ("Zaria", "3030 Nicollet Ave S", "Minneapolis", 90,
     {"edhc_mf": 2097500, "home_mf": 3444500}),
    ("Flour Exchange", "310 Fourth Avenue South", "Minneapolis", 110,
     {"edhc_mf": 2267000, "hud811": 108072}),
    ("Torre de San Miguel", None, "Saint Paul", 142,
     # "Multiple Building Addresses" per Selected Applications.
     {"parif": 5500000}),
    ("Hamm's Brewery - East End Apartments", "694 Minnehaha Avenue East", "Saint Paul", 110,
     {"edhc_mf": 3689600, "home_mf": 5832500, "hud811": 225588}),
    ("Trails Edge Senior Apartments", "905 Airport Road", "Waconia", 43,
     {"hib_senior": 6540000, "lmir_award": 1646000}),
    ("The Community Corner", "1500 69th Ave", "Brooklyn Center", 31,
     {"9pct_htc": 1344050, "hib_repayments": 3572000}),
    ("Terrano Apts", "111 99th Ave NE", "Blaine", 48,
     {"9pct_htc": 1904659, "nhtf": 2820935, "lmir_award": 3219000, "hud811": 101160}),
    ("Heights Ridge Apartments", "1515 44th Avenue NE", "Columbia Heights", 62,
     {"9pct_htc": 1850000, "home_mf": 1011000, "hud811": 87948}),
]

EXPECTED_PROJECT_COUNT = 20
EXPECTED_TOTAL_UNITS = 1145
EXPECTED_GREATER_MN_UNITS = 435
EXPECTED_METRO_UNITS = 710

# Detailed Report's own printed "STATE TOTALS" row, one figure per funding-
# source column (see module docstring's "Column-position verification").
# "hud811_units" is column [16] (HUD Section 811 Total Units, a unit count,
# not a dollar figure) -- checked separately, not part of the dollar dict.
EXPECTED_STATE_TOTALS = {
    "9pct_htc": 12651138,
    "edhc_mf": 13717100,
    "hib_preservation": 21369000,
    "hib_senior": 28631000,
    "hib_repayments": 3572000,
    "home_mf": 20005000,
    "nhtf": 2820935,
    "parif": 17800200,
    "lmir_award": 19670000,
    "bbl_teb": 9640000,
    "hud811": 668748,
}
EXPECTED_DEFERRED_LOANS_TOTAL = 107915235  # = edhc_mf+hib_pres+hib_senior+hib_repay+home_mf+nhtf+parif
EXPECTED_HUD811_TOTAL_UNITS = 39
# Per-project HUD Section 811 Total Units (column [16]) -- used only for the
# verify_state_totals() cross-check below, not surfaced per-project in the
# output JSON (the category-level subprogram already carries the total).
HUD811_UNITS_BY_PROJECT = {
    "Third Rapids Apartments": 5,
    "Kendall Pointe": 6,
    "Flour Exchange": 6,
    "Hamm's Brewery - East End Apartments": 11,
    "Terrano Apts": 6,
    "Heights Ridge Apartments": 5,
}

FUNDING_COLOR_GROUP = {
    "9pct_htc": "credit",
    "edhc_mf": "capital",
    "hib_preservation": "bond", "hib_senior": "bond", "hib_repayments": "bond",
    "home_mf": "trust", "nhtf": "trust", "parif": "trust",
    "lmir_award": "capital",
    "bbl_teb": "bond",
    "hud811": "capital",
}
# priority order for picking a project's single "primary" color when it has
# multiple funding sources (first match wins) -- Housing Infrastructure
# Bonds first since they carry the largest total dollar footprint across
# the 20 awards ($53.57M combined).
FUNDING_PRIORITY = ["hib_senior", "hib_preservation", "hib_repayments", "bbl_teb",
                     "home_mf", "parif", "nhtf", "9pct_htc", "edhc_mf",
                     "lmir_award", "hud811"]


def verify_project_count_and_units():
    errors = []
    if len(RAW_PROJECTS) != EXPECTED_PROJECT_COUNT:
        errors.append(f"project count: expected {EXPECTED_PROJECT_COUNT}, got {len(RAW_PROJECTS)}")
    total_units = sum(units for _n, _a, _c, units, _s in RAW_PROJECTS)
    if total_units != EXPECTED_TOTAL_UNITS:
        errors.append(f"Total Units sum: expected {EXPECTED_TOTAL_UNITS}, got {total_units}")
    greater_mn_units = sum(units for _n, _a, _c, units, _s in RAW_PROJECTS[:10])
    metro_units = sum(units for _n, _a, _c, units, _s in RAW_PROJECTS[10:])
    if greater_mn_units != EXPECTED_GREATER_MN_UNITS:
        errors.append(f"GREATER MINNESOTA TOTALS units: expected {EXPECTED_GREATER_MN_UNITS}, got {greater_mn_units}")
    if metro_units != EXPECTED_METRO_UNITS:
        errors.append(f"METROPOLITAN TOTALS units: expected {EXPECTED_METRO_UNITS}, got {metro_units}")
    if errors:
        raise SystemExit("Project count/unit mismatch(es):\n" + "\n".join(errors))
    print(f"Project count ({EXPECTED_PROJECT_COUNT}), Total Units sum ({EXPECTED_TOTAL_UNITS} = "
          f"{EXPECTED_GREATER_MN_UNITS} Greater MN + {EXPECTED_METRO_UNITS} Metro) verified against "
          "the Detailed Report's own printed STATE/region TOTALS rows.")


def verify_state_totals():
    sums = {k: 0 for k in EXPECTED_STATE_TOTALS}
    hud811_units_sum = 0
    for name, _addr, _city, _units, sources in RAW_PROJECTS:
        for src, amt in sources.items():
            sums[src] = sums.get(src, 0) + amt
        if name in HUD811_UNITS_BY_PROJECT:
            hud811_units_sum += HUD811_UNITS_BY_PROJECT[name]
    errors = []
    for key, expected in EXPECTED_STATE_TOTALS.items():
        got = sums.get(key, 0)
        if got != expected:
            errors.append(f"{key} (amount): expected {expected:,}, got {got:,}")
    deferred_total = (sums["edhc_mf"] + sums["hib_preservation"] + sums["hib_senior"]
                       + sums["hib_repayments"] + sums["home_mf"] + sums["nhtf"] + sums["parif"])
    if deferred_total != EXPECTED_DEFERRED_LOANS_TOTAL:
        errors.append(f"Agency Deferred Loans Total: expected {EXPECTED_DEFERRED_LOANS_TOTAL:,}, got {deferred_total:,}")
    if hud811_units_sum != EXPECTED_HUD811_TOTAL_UNITS:
        errors.append(f"HUD Section 811 Total Units: expected {EXPECTED_HUD811_TOTAL_UNITS}, got {hud811_units_sum}")
    if set(HUD811_UNITS_BY_PROJECT) - {n for n, *_ in RAW_PROJECTS}:
        errors.append("HUD811_UNITS_BY_PROJECT references a project not in RAW_PROJECTS")
    if errors:
        raise SystemExit("STATE TOTALS mismatch(es):\n" + "\n".join(errors))
    print(f"All {len(EXPECTED_STATE_TOTALS)} funding-source dollar totals, the Agency Deferred "
          "Loans Total ($107,915,235), and HUD Section 811 Total Units (39) verified exactly "
          "against the Detailed Report's own printed STATE TOTALS row.")


def verify_category_subprogram_totals():
    """Cross-checks multifamily_awards' own subprogram fy2025_units/
    fy2025_amount fields (CATEGORIES, hand-entered) against RAW_PROJECTS'
    independently-computed per-source sums -- closing the loop between the
    two data structures. fy2025_units uses project-total-units summed
    across every project touching that source (the same proxy CT's build
    used), except hud811 which instead checks against its own disclosed
    unit sub-count (see module docstring).
    """
    units_by_source = {}
    amounts_by_source = {}
    for name, _addr, _city, units, sources in RAW_PROJECTS:
        for src, amt in sources.items():
            if src != "hud811":
                units_by_source[src] = units_by_source.get(src, 0) + units
            amounts_by_source[src] = amounts_by_source.get(src, 0) + amt
    units_by_source["hud811"] = sum(HUD811_UNITS_BY_PROJECT.values())
    mf_cat = next(c for c in CATEGORIES if c["key"] == "multifamily_awards")
    errors = []
    for sp in mf_cat["subprograms"]:
        key = sp["key"]
        if sp["fy2025_units"] != units_by_source.get(key, 0):
            errors.append(f"{key} fy2025_units: category says {sp['fy2025_units']}, "
                           f"RAW_PROJECTS sums to {units_by_source.get(key, 0)}")
        if sp["fy2025_amount"] != amounts_by_source.get(key, 0):
            errors.append(f"{key} fy2025_amount: category says {sp['fy2025_amount']:,}, "
                           f"RAW_PROJECTS sums to {amounts_by_source.get(key, 0):,}")
    if errors:
        raise SystemExit("Category/RAW_PROJECTS subprogram mismatch(es):\n" + "\n".join(errors))
    print("multifamily_awards category's 11 subprogram fy2025_units/fy2025_amount fields "
          "verified against RAW_PROJECTS' own independently-computed per-source sums.")


def verify_rental_production_subtotals():
    cat = next(c for c in CATEGORIES if c["key"] == "rental_production")
    subtotal_units = sum(sp["fy2025_units"] for sp in cat["subprograms"])
    subtotal_amount = sum(sp["fy2025_amount"] for sp in cat["subprograms"])
    if subtotal_units != 2959 or subtotal_amount != 294660416:
        raise SystemExit(
            f"rental_production subtotal drift: expected 2,959 units / $294,660,416, "
            f"got {subtotal_units} / {subtotal_amount:,} -- update the module docstring's "
            "gap-vs-headline note if this transcription intentionally changed."
        )
    print("rental_production's 3 subtotals (900+1,764+295=2,959 units, $294,660,416) "
          "verified as internally self-consistent; documented 67-unit/~$755K gap vs. "
          "the 3,026/$295,415,416 printed headline is intentional -- see module docstring.")


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


# A handful of source-printed street addresses use a spelling Nominatim's
# search does not resolve (spelled-out ordinals like "Fourth" instead of
# "4th", or a bare number missing its ordinal suffix like "15 Ave" instead
# of "15th Ave") even though the underlying address is real and otherwise
# unambiguous -- confirmed by geocoding the numeral-ordinal form and
# checking the result names the same building/street (Flour Exchange's
# corrected query resolves to a place literally named "Flour Exchange
# Building" at 310 4th Avenue South, Minneapolis; Cedar View's corrected
# query resolves to "15th Avenue Northeast, Austin"). This is a query-
# normalization fix for the geocoder only -- the "address" field in the
# output JSON keeps the source document's own original spelling.
GEOCODE_QUERY_OVERRIDE = {
    "Flour Exchange": "310 4th Avenue South, Minneapolis, MN",
    "Cedar View Apartments": "300 15th Ave NE, Austin, MN",
}


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
    for name, address, city, units, sources in RAW_PROJECTS:
        if name in GEOCODE_QUERY_OVERRIDE:
            query = GEOCODE_QUERY_OVERRIDE[name]
        else:
            query = f"{address}, {city}, MN" if address else f"{city}, MN"
        coords = geocode(query, cache)
        status = "ok" if address else None
        if coords is None and address:
            coords = geocode(f"{city}, MN", cache)
            status = "city_center" if coords else "unresolved"
        elif coords is not None and not address:
            status = "city_center"
        elif coords is None and not address:
            status = "unresolved"
        primary = next((s for s in FUNDING_PRIORITY if s in sources), list(sources)[0])
        projects.append({
            "id": slugify(name),
            "name": name,
            "address": address,
            "city": city,
            "lat": round(coords[0], 5) if coords else None,
            "lon": round(coords[1], 5) if coords else None,
            "units": units,
            "funding_sources": list(sources.keys()),
            "source_amounts": sources,
            "total_amount": sum(sources.values()) if sources else None,
            "primary_color_group": FUNDING_COLOR_GROUP[primary],
            "overlaps": len(sources) > 1,
            "geocode_status": status,
        })
    return projects


def main():
    verify_project_count_and_units()
    verify_state_totals()
    verify_category_subprogram_totals()
    verify_rental_production_subtotals()
    print("Geocoding project addresses via Nominatim...")
    projects = build_projects()
    unresolved = [p["name"] for p in projects if p["geocode_status"] == "unresolved"]
    if unresolved:
        print(f"  {len(unresolved)} project(s) could not be geocoded: {unresolved}")
    city_center = [p["name"] for p in projects if p["geocode_status"] == "city_center"]
    if city_center:
        print(f"  {len(city_center)} project(s) fell back to city-center geocoding: {city_center}")

    payload = {
        "MN": {
            "hfa_name": "Minnesota Housing Finance Agency",
            "hfa_abbr": "MN Housing",
            "fiscal_year": "FFY2025",
            "source_title": "Minnesota Housing 2025 Program Assessment Report (Table 3) "
                             "+ 2025 Multifamily Consolidated RFP/2026 HTC Round 1 "
                             "Detailed Report and Selected Applications",
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
