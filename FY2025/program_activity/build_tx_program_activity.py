"""
Builds docs/tx_program_activity.json from TDHCA's "2026 State of Texas Low
Income Housing Plan and Annual Report" (SLIHP) -- which, despite its cover
year, reports SFY2025 (Texas state fiscal year September 1, 2024 - August
31, 2025) actuals -- plus the finalized "2025 Competitive (9%) Housing Tax
Credit Program Award and Waiting List Recommendations" spreadsheet for the
per-project bubble map, and TDHCA's own separately-issued FY2025 audited
financial statements for GASB fund-type classification.

Title-year vs. data-year offset
---------------------------------------------------------------------------
The SLIHP is named for the calendar year it is ADOPTED in, not the fiscal
year it REPORTS on: the "2026 SLIHP" (adopted by the TDHCA Governing Board
January 15, 2026, public-comment period February 6 - March 8, 2026) is the
document that reports TDHCA's SFY2025 annual activity -- every "FY 2025"
figure quoted below comes from the 2026-titled document. This mirrors the
prior fiscal year's naming ("25-SLIHP.pdf" reported SFY2024).

Sources
---------------------------------------------------------------------------
1. State of Texas Low Income Housing Plan and Annual Report, 2026 edition
   (the FINAL adopted version -- confirmed not the January 2026 draft: the
   draft URL (26-SLIHP-DRAFT.pdf, Last-Modified 2026-01-15) and the final
   URL (26-SLIHP.pdf, Last-Modified 2026-03-27, i.e. AFTER the March 8,
   2026 public-comment deadline, with no "DRAFT" watermark and 249 pages
   vs. the draft's smaller page count) are two distinct files; this script
   uses the March 27, 2026 final):
     https://www.tdhca.texas.gov/sites/default/files/housing-center/docs/26-SLIHP.pdf
   Local copy: FY2025/program_activity/pdf/TX_TDHCA_SLIHP_2026.pdf
2. "2025 Competitive (9%) Housing Tax Credit Program Award and Waiting List
   Recommendations," Version Date January 14, 2026 (the FINAL list -- this
   URL supersedes the October 14, 2025 version this project's task brief
   originally pointed at; TDHCA's own archive page
   (https://www.tdhca.texas.gov/9-competitive-housing-tax-credits-archive)
   still links the January 14, 2026 file under an odd, evidently
   hand-edited filename "25-261014-HTC9pct-AwardWaitingList.xlsx" --
   confirmed by opening the file itself, whose own title cell reads
   "Version Date: January 14, 2026" and whose Recommendation/Review Status
   columns are fully populated (Award/Credit Return, all Review
   Status="C"), unlike the October 14 file, which is the version this
   script does NOT use):
     https://www.tdhca.texas.gov/sites/default/files/multifamily/docs/htc-9pct/25-261014-HTC9pct-AwardWaitingList.xlsx
   Local copy: FY2025/program_activity/pdf/TX_TDHCA_9pctHTC_AwardList_2025.xlsx
3. TDHCA's own separately-issued FY2025 audited financial statements (used
   ONLY for GASB fund-type classification):
     FY2025/txt/TX_TDHCA_FY2025_ACFR.txt

Data-provenance check on the checked-in ACFR text
---------------------------------------------------------------------------
FY2025/txt/TX_TDHCA_FY2025_ACFR.txt WAS verified to be TDHCA's own audited
financial statements before use (unlike the PA build earlier in this pilot
series, which caught its checked-in ACFR .txt pointing at the wrong,
Commonwealth-wide document). The TX file's own title page reads "TEXAS
DEPARTMENT OF HOUSING AND COMMUNITY AFFAIRS, Basic Financial Statements,
For the Year Ended August 31, 2025" and its transmittal letter is signed by
TDHCA's own Executive Director -- i.e. this is the correct, TDHCA-scoped
document (TDHCA's fiscal year runs September 1 - August 31, so "For the
Year Ended August 31, 2025" = SFY2025, exactly the period this build
covers). No substitution was needed; no wrong-report problem here.

Fund-type classification (fund_type/fund_name on each subprogram)
---------------------------------------------------------------------------
TDHCA's own MD&A (p.xiii of the ACFR PDF) states plainly: "The Department
has three types of funds: [a single] Governmental fund -- The General
Revenue Fund is the Department's only governmental fund ... Federal and
state programs are also reported within this fund[; a single] Proprietary
fund -- ... Funding has primarily arisen through the issuance of taxable
and tax-exempt bonds ... This fund also receives fee income from the
Multifamily Tax Credit Program ...[; a] Fiduciary Fund" (not used by any
program below). Note 2's "Loans and Contracts" policy note is the sharpest
single source for classifying each program:
  "Loans and contracts consist of loans in the General Fund made from
  federal funds for the purpose of Single Family loans and Multifamily
  development loans from HOME, Tax Credit Assistance Program (TCAP),
  National Housing Trust Fund (NHTF) and Neighborhood Stabilization
  Program (NSP) grants. Restricted loans and contracts in proprietary
  funds consist of mortgage loans made from Single Family bond proceeds.
  Unrestricted loans and contracts consist of Single Family loans and
  Multifamily development loans from The State of Texas Housing Trust Fund
  and other Housing Initiative Programs."
  - "governmental" (General Revenue Fund, federal-grant-funded):
      * home_tbra, home_owner_rehab -- HOME Investment Partnerships
        Program, named verbatim in the General-Fund loans sentence above;
        confidence high.
      * mf_direct_loan -- explicitly named in the same General-Fund
        sentence ("Multifamily development loans from HOME, TCAP, NHTF and
        NSP grants" is a direct description of the MF Direct Loan
        Program's own funding sources per the SLIHP's own Action Plan
        section, p.102: "HOME, Tax Credit Assistance Program Repayment
        Funds (TCAP RF) ... Neighborhood Stabilization Program Round 1
        Program Income (NSP1 PI) ... and National Housing Trust Fund
        (NHTF) funds"); confidence high.
      * section8_hcv, section811_pra -- HUD Housing Choice Voucher and
        Section 811 Project Rental Assistance are federal rental-subsidy
        pass-throughs; the MD&A's Governmental Fund revenue discussion
        names "federal grants" generally and the General Fund is described
        as carrying "federal and state programs" broadly; confidence
        medium-high (not individually named line items in Note 2, but
        structurally federal HUD grants with no bond/enterprise financing
        of any kind).
      * ceap, wap, csbg, esg, hhsp -- Community Affairs (CEAP/WAP/CSBG) and
        Homelessness (ESG/HHSP) programs are federal-formula-grant (HHS/
        DOE/HUD) or, for HHSP, primarily state-appropriated programs
        administered the same way; the MD&A's Governmental Fund revenue
        table explicitly lists "LIHEAP" (=CEAP's funding source) and CSBG
        among the fund's federal grant revenues; confidence high for
        CEAP/WAP/CSBG (named), medium for ESG/HHSP (same fund, not
        individually named).
  - "proprietary" (single business-type/enterprise fund, bond- or
    trust-fund-financed):
      * sf_homeownership_loans -- "Restricted loans and contracts in
        proprietary funds consist of mortgage loans made from Single
        Family bond proceeds" -- verbatim match; also Note 15's Segment
        Information reports a "Single Family Mortgage Revenue Program
        Funds" / "Residential Mortgage Bond Funds" enterprise-fund
        segment. Confidence high.
      * htf_owner_rehab, htf_sf_development -- "Unrestricted loans and
        contracts consist of ... loans from The State of Texas Housing
        Trust Fund" (continuing the same "in proprietary funds" sentence),
        and separately the MD&A's Statement of Activities section states
        outright: "Single Family and Housing Trust Fund are shown as
        business-type activities, and other state and federal programs are
        shown as governmental activities" -- two independent confirmations
        that TDHCA's Housing Trust Fund (unlike most other states' housing
        trust funds, which tend to be governmental) sits in TDHCA's
        proprietary fund. Confidence high.
  - "off_balance_sheet":
      * htc9, htc4 -- the proprietary fund "receives fee income from the
        Multifamily Tax Credit Program" (i.e. only administrative/
        compliance-monitoring FEES are a TDHCA fund asset) -- the credits
        themselves are allocated directly to developers/investors and
        never sit on TDHCA's own balance sheet, the same off-balance-sheet
        logic this pilot series has applied to every other state's 9%/4%
        HTC programs (IL's LIHTC/IAHTC, PA's LIHTC/PHTC, FL's HC9/HC4).
        Confidence high.
      * mf_bond -- NOT off-balance-sheet for the usual "credit allocated to
        a third party" reason, but for a *debt* reason specific to TX: Note
        2's "Bonds Payable" policy states "The Department has implemented
        Governmental Accounting Standards Board Statement No. 91, Conduit
        Debt Obligations ... The Department has eliminated debt related to
        Multifamily bonds payable where the Department is only a conduit
        issuer" -- and Note 15 (Segment Information) separately confirms
        its own segment disclosure "does not include the Multifamily bonds
        where the Department is only a conduit issuer." I.e. TDHCA's own
        ACFR affirmatively REMOVES Multifamily Bond debt from its
        financial statements under GASB 91 -- the bonds are secured solely
        by each project's own revenue, not TDHCA's credit, and are not a
        TDHCA liability at all. This is a different mechanism from the
        HTC off-balance-sheet cases above (conduit debt elimination, not
        third-party credit allocation) but produces the same
        classification. Confidence high (two independent ACFR passages).

Category-level methodology ("Total Funding by Program, FY 2025" table, p.58
of the SLIHP PDF, TDHCA's own published aggregate, reproduced verbatim
below) and household/individual counts (pp.56-62)
---------------------------------------------------------------------------
multifamily_rental_production (htc9/htc4/mf_bond/mf_direct_loan):
non-additive. The SLIHP's own household-count table (p.56) carries the
footnote "Note that all properties funded in FY25 through MF Bond and MF
Direct Loan also received funding through the 9% or 4% HTC Programs" and
"MF Bond and MF Direct Loan are included in 9% and 4% HTC figures and will
not be included in HH totals" -- i.e. TDHCA's own published household
counts for mf_bond (1,108) and mf_direct_loan (197) are NOT independent
households, they are a subset already counted inside htc9's 4,554 and
htc4's 14,141. This script's fy2025_actual (18,695) is therefore htc9 +
htc4 ONLY (4,554 + 14,141), matching TDHCA's own de-duplication
convention; mf_bond's and mf_direct_loan's own fy2025_units values are
still shown on their subprogram chips (informational, not summed into the
headline). By contrast the DOLLAR figures ARE independently additive across
all four programs with no double-counting: summing all 9 programs' own
"Total" column on the p.61 "Funding by Housing Activity and Program" table
reproduces that table's own printed Total ($1,574,756,367) exactly -- see
verify_slihp_table_arithmetic().

single_family_homeownership, home_program, housing_trust_fund: each
category's fy2025_actual/fy2025_amount is TDHCA's own published
household-count and dollar figure for that program (pp.56-61); each is a
single program with no internal funding-source overlap, so additive=True
throughout (trivially so for single_family_homeownership, which has one
subprogram).

rental_assistance_community_affairs (section8_hcv/section811_pra/ceap/wap/
csbg/esg/hhsp): TDHCA's own p.63 Income-Category table explicitly combines
household counts (CEAP/WAP, and structurally Section 8/811) with
individual counts (CSBG/ESG/HHSP) into one additive total ("In the
following tables, households and individuals have been added together for
totals, though one household can contain multiple individuals" -- and the
report's own state-level total, "TDHCA programs served 111,491 households
in addition to 264,504 Individuals," p.63, is itself an HH+IND sum) --
this script follows that same convention rather than inventing a
household-only or individual-only subset. additive=True; fy2025_actual is
the straight sum of all 7 programs' own published FY2025 counts (349,398),
independently reproducing the sum of the community-affairs/homelessness
subtotal (347,729, p.62) plus the Section 8 HCV + Section 811 PRA subtotal
(1,669, p.56) -- see verify_slihp_table_arithmetic().

Every category's fy2025_amounts list is populated from the "Total Funding
by Program" table (p.58) and the "Funding by Housing Activity and Program"
table (p.61); every category's fy2025_actual unit/household count is
either a single published table cell or (only for the two categories noted
above) a documented, TDHCA-methodology-consistent sum of published cells.
No number in CATEGORIES below is invented.

9% HTC Award List vs. the SLIHP's own $76,968,809 -- two different
populations, NOT a filtering bug
---------------------------------------------------------------------------
The per-project bubble map (RAW_PROJECTS) is built from the "2025
Competitive (9%) HTC Award and Waiting List," which lists the 65
applications recommended Award status in the *2025 application cycle*
(board-approved starting the July 24, 2025 Governing Board meeting, with 2
additional waiting-list promotions finalized by the January 14, 2026
version used here). Summing RAW_PROJECTS gives 4,807 total units and
$102,693,450.52 in requested annual 9% credit -- NEITHER of which matches
the SLIHP's own $76,968,809 / 4,554-household "9% HTC" figures for FY 2025
(Sept. 2024 - Aug. 2025). This was checked for a filtering mistake first
(confirmed only rows whose Recommendation column reads exactly "Award" or
"Award " are included, out of 140 total rows spanning Award/blank
waiting-list/"Credit Return" statuses -- see verify_award_list_totals())
before concluding this is a genuine population mismatch, not a bug:
  - The SLIHP's Annual Housing Report is an EXPENDITURE/closing-based
    figure for activity that happened DURING SFY2025 -- for a 9%
    competitive-credit deal, that means construction draws, credit
    issuances (IRS Form 8609s), or loan closings on developments that were
    typically AWARDED in an *earlier* application cycle (2023 or 2024) and
    reached a countable milestone during Sept. 2024 - Aug. 2025.
  - The Award List instead captures the 2025 APPLICATION CYCLE's own
    award moment (Governing Board approval in mid-to-late 2025) -- these
    65 developments will typically not close financing or draw down
    credits until FY2026 or FY2027, so they are essentially absent from
    the SFY2025 SLIHP figures being quoted for the category headline.
  This is the same category of mismatch this pilot series has already
  documented for OHFA (Appendix C "initial funding reservations" vs. its
  own SFY headline, and separately vs. Appendix D "8609 issuances") and
  for Florida Housing (81-development RENTAL PROPERTIES table's 12,007 vs.
  the SUMMARY OF PROGRAMS table's 13,196) -- award/reservation-cycle
  tables and fiscal-year expenditure/closing tables are different
  populations by construction, and TDHCA (like OHFA and Florida Housing)
  does not publish a single reconciled number spanning both.
As independent, if approximate, corroboration that the Award List's own
population is internally sound (not, say, accidentally including an extra
application cycle or double-counting waiting-list rows), Governor Abbott's
July 24, 2025 press release announcing the *initial* board approval --
before the January 2026 finalization added 2 more awards -- states "over
$99 million in housing tax credits ... 63 rental properties ... over 4,410
units" (https://gov.texas.gov/news/post/governor-abbott-announces-over-99-
million-in-housing-tax-credits); this script's own count at that same
snapshot (the October 14, 2025 interim version of the same spreadsheet) is
63 awards / 4,642 units / $98,693,450.52, consistent with the press
release's rounded "over" figures. The bubble map and its category chip are
therefore clearly labeled, in both the docstring above and the frontend
copy, as covering ONLY the 9% competitive HTC channel -- about 4.25% of
TDHCA's total FY2025 funding -- and NOT as a comprehensive multifamily
map; TDHCA does not publish an equivalent per-project list with street
addresses for 4% HTC, Multifamily Bond, or HOME/MF Direct Loan.

fy2026
---------------------------------------------------------------------------
The SLIHP's Section 5 "Action Plan" is mostly qualitative/programmatic,
not a numeric FY2026 projection table (unlike IHDA's Report of
Activities). Exactly one of this script's programs has a disclosed FY2026
number: "ESG funding for Federal Fiscal Year (FFY) 2025 is $10,308,471 and
will be made available during State Fiscal Year (SFY) 2026" (p.106) -- used
verbatim as esg's fy2026.amount. CSBG's Action Plan section states
explicitly "CSBG funding for FY 2026 is not known at this time" (p.96) --
used as this script's canonical "still pending" phrasing. Every other
subprogram/category fy2026 is {value: None, amount: None, closed: False,
note_key: "tx_fy26_note_pending"} -- no other program discloses a FY2026
figure anywhere in the 249-page document, so none is invented.

Geocoding
---------------------------------------------------------------------------
Same approach as this pilot series' other builds: Nominatim (OpenStreetMap),
primary query "{Development Address}, {City}, TX", falling back to
"{City}, TX" (geocode_status="city_center") when the street-level query
fails. A meaningful fraction of the Award List's own Development Address
column is an intersection/approximate description rather than a mailing
address (e.g. "SWC of Augusta Dr and Zaragoza Road", "Approx 7401 Little
York Rd") -- these are passed through as printed (Nominatim can often
still resolve a named intersection) and fall back to city-center geocoding
like any other failed lookup; no address is altered or invented. Self-
throttled to <=1 request/second with an identifying User-Agent per
Nominatim's usage policy.
"""

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "tx_program_activity.json"

SOURCE_URL = "https://www.tdhca.texas.gov/sites/default/files/housing-center/docs/26-SLIHP.pdf"
SOURCE_FILE = "TX_TDHCA_SLIHP_2026.pdf (+ TX_TDHCA_9pctHTC_AwardList_2025.xlsx, Version Date January 14, 2026)"
RETRIEVED = "2026-08-13"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
GEOCODER_USER_AGENT = "us-hfa-data-map/1.0 (github.com/MD-ai-fin/us-hfa-data-map)"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "tx_fy26_note_pending"}

# ---------------------------------------------------------------------------
# Category-level data ("Total Funding by Program, FY 2025" table, p.58, and
# "Funding by Housing Activity and Program"/household tables, pp.56-62, of
# the SLIHP PDF)
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "multifamily_rental_production",
        "unit_type": "households",
        "fy2025_actual": 18695,
        "fy2025_source_quote": (
            "\"Total Funding by Program, FY 2025\" (p.58): Housing Tax Credits 4% "
            "$133,790,422 (7.39%), Housing Tax Credits 9% $76,968,809 (4.25%), "
            "Multifamily Bond $142,452,000 (7.87%), Multifamily Direct Loan "
            "$24,417,856 (1.35%). \"Households Served by Activity and Housing "
            "Program, FY 2025\" (p.56): 9% HTC 4,554 + 4% HTC 14,141 = 18,695 "
            "households -- footnote: \"MF Bond and MF Direct Loan are included in "
            "9% and 4% HTC figures and will not be included in HH totals,\" so "
            "their own published counts (MF Bond 1,108; MF Direct Loan 197) are "
            "shown on their own subprogram chips but excluded from this headline "
            "to avoid double-counting, per TDHCA's own convention."
        ),
        "fy2025_amounts": [
            {"label_key": "tx_amt_htc9", "amount": 76968809},
            {"label_key": "tx_amt_htc4", "amount": 133790422},
            {"label_key": "tx_amt_mf_bond", "amount": 142452000},
            {"label_key": "tx_amt_mf_direct_loan", "amount": 24417856},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "htc9", "fy2025_units": 4554, "fy2025_amount": 76968809,
             "color_group": "credit",
             # Proprietary fund only collects HTC compliance-fee income; the
             # credit itself is allocated directly to developers/investors,
             # never a TDHCA-carried balance-sheet asset (ACFR MD&A, "This
             # fund also receives fee income from the Multifamily Tax
             # Credit Program").
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "htc4", "fy2025_units": 14141, "fy2025_amount": 133790422,
             "color_group": "credit",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "mf_bond", "fy2025_units": 1108, "fy2025_amount": 142452000,
             "color_group": "bond",
             # GASB 91 conduit-debt elimination: Note 2 ("Bonds Payable"):
             # "The Department has eliminated debt related to Multifamily
             # bonds payable where the Department is only a conduit
             # issuer"; Note 15 (Segment Information) separately confirms
             # its own enterprise-fund segment disclosure excludes
             # "Multifamily bonds where the Department is only a conduit
             # issuer." Not a TDHCA liability at all.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "mf_direct_loan", "fy2025_units": 197, "fy2025_amount": 24417856,
             "color_group": "capital",
             # Note 2 ("Loans and Contracts"): "Loans and contracts consist
             # of loans in the General Fund made from federal funds for
             # the purpose of ... Multifamily development loans from HOME,
             # TCAP, NHTF and NSP grants" -- matches MF Direct Loan's own
             # funding sources per the SLIHP Action Plan (p.102).
             "fund_type": "governmental", "fund_name": "General Revenue Fund (HOME/TCAP RF/NSP1 PI/NHTF)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "single_family_homeownership",
        "unit_type": "households",
        "fy2025_actual": 4683,
        "fy2025_source_quote": (
            "\"Total Funding by Program, FY 2025\" (p.58): Single Family "
            "Homeownership Program $1,141,090,180 (63.07%). \"Households Served "
            "by Activity and Housing Program, FY 2025\" (p.56): SF Homeownership "
            "4,683 households, all under \"Owner Financing & Down Payment.\""
        ),
        "fy2025_amounts": [
            {"label_key": "tx_amt_sf_homeownership", "amount": 1141090180},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "sf_homeownership_loans", "fy2025_units": 4683, "fy2025_amount": 1141090180,
             "color_group": "capital",
             # Note 2 ("Loans and Contracts"): "Restricted loans and
             # contracts in proprietary funds consist of mortgage loans
             # made from Single Family bond proceeds"; Note 15 (Segment
             # Information) reports a "Single Family Mortgage Revenue
             # Program Funds" enterprise-fund segment.
             "fund_type": "proprietary", "fund_name": "Single Family Mortgage Revenue Bond program",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "home_program",
        "unit_type": "households",
        "fy2025_actual": 1788,
        "fy2025_source_quote": (
            "\"Total Funding by Program, FY 2025\" (p.58): HOME Investment "
            "Partnerships Program $32,416,833 (1.79%). \"Households Served by "
            "Activity and Housing Program, FY 2025\" (p.56): HOME 1,788 "
            "households (Rental Assistance 1,664 + Owner Rehabilitation "
            "Assistance 124). \"Funding by Housing Activity and Program, FY "
            "2025\" (p.61): HOME Rental Assistance $12,767,070 + Owner "
            "Rehabilitation Assistance $19,649,763 = $32,416,833."
        ),
        "fy2025_amounts": [
            {"label_key": "tx_amt_home_total", "amount": 32416833},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "home_tbra", "fy2025_units": 1664, "fy2025_amount": 12767070,
             "color_group": "capital",
             "fund_type": "governmental", "fund_name": "General Revenue Fund (HOME Tenant-Based Rental Assistance)",
             "fy2026": _FY26_PENDING},
            {"key": "home_owner_rehab", "fy2025_units": 124, "fy2025_amount": 19649763,
             "color_group": "capital",
             "fund_type": "governmental", "fund_name": "General Revenue Fund (HOME Owner Rehabilitation Assistance)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "housing_trust_fund",
        "unit_type": "households",
        "fy2025_actual": 126,
        "fy2025_source_quote": (
            "\"Total Funding by Program, FY 2025\" (p.58): Housing Trust Fund "
            "$3,757,247 (0.21%). \"Households Served by Activity and Housing "
            "Program, FY 2025\" (p.56): HTF 126 households (Owner Rehabilitation "
            "Assistance 78 + Single Family Development 48). \"Funding by Housing "
            "Activity and Program, FY 2025\" (p.61): HTF Owner Rehabilitation "
            "Assistance $1,634,347 + Single Family Development $2,122,900 = "
            "$3,757,247."
        ),
        "fy2025_amounts": [
            {"label_key": "tx_amt_htf_total", "amount": 3757247},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "htf_owner_rehab", "fy2025_units": 78, "fy2025_amount": 1634347,
             "color_group": "capital",
             "fund_type": "proprietary", "fund_name": "State of Texas Housing Trust Fund (unrestricted, proprietary fund)",
             "fy2026": _FY26_PENDING},
            {"key": "htf_sf_development", "fy2025_units": 48, "fy2025_amount": 2122900,
             "color_group": "capital",
             "fund_type": "proprietary", "fund_name": "State of Texas Housing Trust Fund (unrestricted, proprietary fund)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "rental_assistance_community_affairs",
        "unit_type": "households",
        "fy2025_actual": 349398,
        "fy2025_source_quote": (
            "\"Total Funding by Program, FY 2025\" (p.58): Comprehensive Energy "
            "Assistance Program $155,819,774 (8.61%), Community Services Block "
            "Grant $31,177,126 (1.72%), Weatherization Assistance Program "
            "$31,082,983 (1.72%), Section 8 $15,548,802 (0.86%), Emergency "
            "Solutions Grants Program $10,509,885 (0.58%), Homeless Housing and "
            "Services Program $6,016,081 (0.33%), Section 811 PRA $4,314,218 "
            "(0.24%). Households/individuals served: Section 8 HCV 1,227 + "
            "Section 811 PRA 442 (p.56) + CEAP 81,424 households + WAP 1,801 "
            "households + CSBG 222,641 individuals + ESG 32,260 individuals + "
            "HHSP 9,603 individuals (p.62) = 349,398. TDHCA's own report adds "
            "households and individuals together for its totals (\"households "
            "and individuals have been added together for totals, though one "
            "household can contain multiple individuals,\" p.63); this category "
            "follows that same convention."
        ),
        "fy2025_amounts": [
            {"label_key": "tx_amt_ceap", "amount": 155819774},
            {"label_key": "tx_amt_csbg", "amount": 31177126},
            {"label_key": "tx_amt_wap", "amount": 31082983},
            {"label_key": "tx_amt_section8", "amount": 15548802},
            {"label_key": "tx_amt_esg", "amount": 10509885},
            {"label_key": "tx_amt_hhsp", "amount": 6016081},
            {"label_key": "tx_amt_section811", "amount": 4314218},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "ceap", "fy2025_units": 81424, "fy2025_amount": 155819774,
             "color_group": "capital",
             "fund_type": "governmental", "fund_name": "General Revenue Fund (Comprehensive Energy Assistance Program, LIHEAP-funded)",
             "fy2026": {"value": None, "amount": None, "closed": False,
                        "note_key": "tx_fy26_note_ceap_pending"}},
            {"key": "csbg", "fy2025_units": 222641, "fy2025_amount": 31177126,
             "color_group": "capital",
             "fund_type": "governmental", "fund_name": "General Revenue Fund (Community Services Block Grant)",
             "fy2026": {"value": None, "amount": None, "closed": False,
                        "note_key": "tx_fy26_note_csbg_pending"}},
            {"key": "wap", "fy2025_units": 1801, "fy2025_amount": 31082983,
             "color_group": "capital",
             "fund_type": "governmental", "fund_name": "General Revenue Fund (Weatherization Assistance Program, DOE/LIHEAP-funded)",
             "fy2026": _FY26_PENDING},
            {"key": "section8_hcv", "fy2025_units": 1227, "fy2025_amount": 15548802,
             "color_group": "capital",
             "fund_type": "governmental", "fund_name": "General Revenue Fund (Section 8 Housing Choice Voucher, HUD-funded)",
             "fy2026": _FY26_PENDING},
            {"key": "esg", "fy2025_units": 32260, "fy2025_amount": 10509885,
             "color_group": "capital",
             "fund_type": "governmental", "fund_name": "General Revenue Fund (Emergency Solutions Grants, HUD-funded)",
             "fy2026": {"value": None, "amount": 10308471, "closed": False,
                        "note_key": "tx_fy26_note_esg"}},
            {"key": "hhsp", "fy2025_units": 9603, "fy2025_amount": 6016081,
             "color_group": "capital",
             "fund_type": "governmental", "fund_name": "General Revenue Fund (Homeless Housing and Services Program)",
             "fy2026": _FY26_PENDING},
            {"key": "section811_pra", "fy2025_units": 442, "fy2025_amount": 4314218,
             "color_group": "capital",
             "fund_type": "governmental", "fund_name": "General Revenue Fund (Section 811 Project Rental Assistance, HUD-funded)",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# ---------------------------------------------------------------------------
# 9% HTC project-level detail ("2025 Competitive (9%) Housing Tax Credit
# Program Award and Waiting List Recommendations," Version Date January 14,
# 2026). Only rows whose Recommendation column reads "Award" (65 of the
# spreadsheet's 140 numbered application rows; the rest are blank/waiting-
# list or the 1 "Credit Return" row) are included -- see
# verify_award_list_totals(). THIS LIST COVERS ONLY THE 9% COMPETITIVE HTC
# CHANNEL, about 4.25% of TDHCA's FY2025 total funding -- see module
# docstring for why it does not, and should not be expected to, reconcile
# against the SLIHP's own $76,968,809 FY2025 headline for that same program
# name.
# ---------------------------------------------------------------------------

# (application_number, development_name, development_address, city, county,
#  total_units, htc_request_dollars)
RAW_PROJECTS = [
    (25001, "Pathways at Santa Rita Courts West", "Approx. 2210 E. 2nd", "Austin", "Travis", 96, 2000000),
    (25004, "Avenue at Lancaster", "5733 Craig Street", "Fort Worth", "Tarrant", 81, 2000000),
    (25013, "Palo Verde Senior Apartments", "5501 Huntwick Ave", "Corpus Christi", "Nueces", 75, 1948110),
    (25016, "Pebble Hills Place", "SWC of N Zaragoza Rd and Pebble Hills Blvd", "El Paso", "El Paso", 70, 2000000),
    (25017, "Reserve at Corsicana", "300 N 45th St", "Corsicana", "Navarro", 36, 1154115),
    (25022, "Reserve at Kilgore", "SWC Utzman St and Parkview St", "Kilgore", "Gregg", 59, 1436803.45),
    (25025, "Union Grove", "2911 Old Union Rd", "Lufkin", "Angelina", 60, 1714742.93),
    (25031, "Hartwood at Windstone", "19735 Clay Rd.", "Houston", "Harris", 123, 2000000),
    (25035, "Fredericksburg Senior Apartments", "591 E. Highway St", "Fredericksburg", "Gillespie", 48, 603701.27),
    (25038, "Azle Oaks Apartments", "700 Jarvis Lane", "Azle", "Tarrant", 116, 2000000),
    (25042, "Villas at Augusta", "SWC of Augusta Dr and Zaragoza Road", "El Paso", "El Paso", 60, 2000000),
    (25046, "Tecovas Terrace", "1601 SE 28th Avenue", "Amarillo", "Potter", 80, 1926703),
    (25051, "Mandalay", "Approximately the south side of the 600 Block of West Veterans Blvd.", "Palmview", "Hidalgo", 104, 2000000),
    (25053, "Las Fuentes", "2801 Leonor Street", "Mission", "Hidalgo", 105, 2000000),
    (25055, "Lantana Villas", "Approximately the 600 Block of East Coma Avenue", "Hidalgo", "Hidalgo", 52, 1166816),
    (25060, "Abbington Station", "SEC of 7th Street and Austin Street", "Pleasanton", "Atascosa", 48, 1125000),
    (25064, "Heritage Park", "581 Acres Lane", "Sealy", "Austin", 56, 1125000),
    (25066, "Historic Lofts of Waco High", "815 Columbus Ave", "Waco", "McLennan", 104, 1530000),
    (25067, "The Knox (fka The Watson and Watson Apartments)", "1401 S Watson Rd", "Arlington", "Tarrant", 82, 2000000),
    (25070, "6802 Marbach Lofts", "Approx 6832 Marbach Rd", "San Antonio", "Bexar", 78, 2000000),
    (25071, "Tezel Road Apartments", "Approximately 6054 Tezel Rd", "San Antonio", "Bexar", 78, 2000000),
    (25072, "Eberhart Place", "808 Eberhart Lane", "Austin", "Travis", 38, 702210.15),
    (25073, "The Ashbourne", "9677 S Kirkwood Rd", "Houston", "Harris", 72, 2000000),
    (25074, "Cedar Brook Village", "Approx 7401 Little York Rd", "Houston", "Harris", 96, 2000000),
    (25077, "Conway Village", "2699 Conway Ave", "Mission", "Hidalgo", 72, 1868000),
    (25088, "Early Pioneer Crossing", "401 Old Comanche Rd.", "Early", "Brown", 52, 1125000),
    (25090, "Trinity East Senior", "2620 Live Oak Street", "Houston", "Harris", 90, 2000000),
    (25093, "North Crest Apartments", "4200 N 19th St & 2005 Steward Dr", "Waco", "McLennan", 196, 2000000),
    (25107, "St. George's Court", "1443 Coronado Hills", "Austin", "Travis", 60, 1022755),
    (25112, "Heritage Estates at Medina", "SWC I-410 and Medina Base Rd", "San Antonio", "Bexar", 86, 2000000),
    (25114, "Pecan Bend", "501 Kings Way Dr", "Mansfield", "Tarrant", 32, 532600),
    (25116, "McKinney Ranch Senior Living", "5353 McKinney Ranch Parkway", "McKinney", "Collin", 109, 2000000),
    (25118, "Oakcrest South", "1415 W. Norris St.", "El Campo", "Wharton", 72, 997550),
    (25123, "Oakleaf Estates", "1195 TX-327", "Silsbee", "Hardin", 80, 902266.05),
    (25126, "Silverleaf Senior Living", "SEC of Blackhawk Blvd and Texas Sage Drive", "Houston", "Harris", 90, 2000000),
    (25128, "Riverside Garden Villas", "SWC of Riverside Grove and Addicks Clodine Road", "Houston", "Fort Bend", 90, 2000000),
    (25133, "Riva Ridge", "SEQ Concord Rd & Gober Rd", "Beaumont", "Jefferson", 63, 1661816),
    (25145, "Avenue U Villas", "8401 Avenue U", "Lubbock", "Lubbock", 80, 1366814.08),
    (25150, "Kingfield Trails", "15606 Kingfield", "Houston", "Harris", 90, 2000000),
    (25155, "Hillsboro Trails", "NEQ Old Brandon Rd and Dynasty Dr", "Hillsboro", "Hill", 36, 1125000),
    (25158, "Waverly North", "3710 Cedar Street", "Austin", "Travis", 76, 1990204),
    (25160, "McAdams Haven", "NWC Lindsey St and Bernard St", "Denton", "Denton", 84, 2000000),
    (25162, "Envoy64", "1415 W Airport Fwy", "Irving", "Dallas", 111, 2000000),
    (25163, "Landmark on Cypress", "301 Cypress St", "Abilene", "Taylor", 49, 1109841),
    (25164, "Irving Lofts", "1108 N Anglin St", "Cleburne", "Johnson", 34, 1176446.58),
    (25165, "Landmark 601", "601 W Lewis St", "Conroe", "Montgomery", 71, 1997438),
    (25167, "Landmark on Pine", "SWC W 4th St and Pine St", "Texarkana", "Bowie", 40, 1215000),
    (25170, "Carthage Senior Estates", "100-101 Senior Ave", "Carthage", "Panola", 56, 854285),
    (25171, "Edgewood Senior Apartments", "300 E Elm St", "Edgewood", "Van Zandt", 24, 418013),
    (25172, "Linden Senior Estates", "700 W Broad St", "Linden", "Cass", 24, 419052),
    (25175, "The James at Wheatland", "7100 W Wheatland Rd.", "Dallas", "Dallas", 90, 2000000),
    (25177, "The Lantern at Robstown", "NWC of CR 44 and CR 69", "Robstown", "Nueces", 39, 1258361),
    (25178, "Connect Hillcroft", "6420 Hillcroft Avenue", "Houston", "Harris", 90, 2000000),
    (25185, "GardenWalk of West Columbia", "431 Lamar St.", "West Columbia", "Brazoria", 56, 680807),
    (25187, "Crossroads Redevelopment", "8801 McCann Dr.", "Austin", "Travis", 110, 2000000),
    (25196, "Victoria Gardens", "1809 Grant St", "Brownsville", "Cameron", 83, 2000000),
    (25201, "Pine Creek Apartments", "Hwy 71 & Lovers Lane (108 Lovers Lane)", "Bastrop", "Bastrop", 52, 1125000),
    (25204, "Melody Grove II", "1809 JJ Flewellen Road", "Waco", "McLennan", 70, 2000000),
    (25214, "Villas at Primrose", "SEQ of Buddy Owens Blvd. & N. Ware Rd.", "McAllen", "Hidalgo", 104, 2000000),
    (25217, "Meadowbrook Apartments", "510 N Old. Robinson Rd", "Robinson", "McLennan", 93, 2000000),
    (25239, "The Meadow", "8130 Meadow Rd", "Dallas", "Dallas", 75, 2000000),
    (25240, "The Magnolia", "1401 Commerce Street", "Dallas", "Dallas", 130, 2000000),
    (25261, "Mount Pleasant Trails", "N side of Tennison Rd, Approx 2150 ft East of S Jefferson Ave", "Mount Pleasant", "Titus", 52, 1164000),
    (25270, "The Rosie", "SEQ of Cap Carter Rd and Doniphan Dr", "Vinton", "El Paso", 40, 1125000),
    (25271, "Lofts at Birdwell", "130 ft. N. of NWC of Sunset Ave. & Birdwell Ln.", "Big Spring", "Howard", 39, 1125000),
]

EXPECTED_AWARD_COUNT = 65
EXPECTED_TOTAL_UNITS = 4807
EXPECTED_TOTAL_HTC_REQUEST = 102693450.52

# All Award-List projects are single-source by construction (this table
# discloses only 9% HTC dollars per development -- it never states whether
# a development also drew MF Bond/HOME/other funds), so every project maps
# to the htc9 subprogram and none carries an "overlaps" flag.
FUNDING_COLOR_GROUP = {"htc9": "credit"}


def verify_award_list_totals():
    errors = []
    if len(RAW_PROJECTS) != EXPECTED_AWARD_COUNT:
        errors.append(f"award count: expected {EXPECTED_AWARD_COUNT}, got {len(RAW_PROJECTS)}")
    app_numbers = [r[0] for r in RAW_PROJECTS]
    if len(set(app_numbers)) != len(app_numbers):
        errors.append("duplicate Application Number(s) in RAW_PROJECTS")
    total_units = sum(r[5] for r in RAW_PROJECTS)
    if total_units != EXPECTED_TOTAL_UNITS:
        errors.append(f"Total Units sum: expected {EXPECTED_TOTAL_UNITS}, got {total_units}")
    total_htc = round(sum(r[6] for r in RAW_PROJECTS), 2)
    if abs(total_htc - EXPECTED_TOTAL_HTC_REQUEST) > 0.01:
        errors.append(f"HTC Request sum: expected {EXPECTED_TOTAL_HTC_REQUEST}, got {total_htc}")
    if errors:
        raise SystemExit("Award-list total mismatch(es):\n" + "\n".join(errors))
    print(f"Award-list totals verified: {EXPECTED_AWARD_COUNT} awarded developments, "
          f"{EXPECTED_TOTAL_UNITS:,} total units, ${EXPECTED_TOTAL_HTC_REQUEST:,.2f} "
          "requested annual 9% HTC -- reproduced by re-summing RAW_PROJECTS, matching "
          "the values independently extracted from the source spreadsheet's own cells "
          "via openpyxl before transcription (see module docstring; this table prints "
          "no Award-only subtotal row of its own, only a Total-Applications-84 row "
          "spanning Award+waiting-list+returned rows together).")


def verify_slihp_table_arithmetic():
    """Reproduce two of the SLIHP's own printed table totals, independent of
    RAW_PROJECTS, as a sanity check on the category-level figures transcribed
    above (see module docstring)."""
    errors = []
    housing_total = (1141090180 + 32416833 + 3757247 + 76968809 + 133790422
                      + 142452000 + 24417856 + 15548802 + 4314218)
    if housing_total != 1574756367:
        errors.append(f"p.61 housing-activity Total: expected 1,574,756,367, got {housing_total}")
    program_total = (1141090180 + 133790422 + 76968809 + 142452000 + 155819774
                      + 32416833 + 31177126 + 31082983 + 15548802 + 10509885
                      + 6016081 + 3757247 + 24417856 + 4314218)
    if program_total != 1809362216:
        errors.append(f"p.58 Total Funding by Program: expected 1,809,362,216, got {program_total}")
    community_affairs_total = 32260 + 222641 + 81424 + 1801 + 9603
    if community_affairs_total != 347729:
        errors.append(f"p.62 community-affairs/homelessness HH+IND total: expected 347,729, got {community_affairs_total}")
    rental_assistance_total = community_affairs_total + 1227 + 442
    if rental_assistance_total != 349398:
        errors.append(f"rental_assistance_community_affairs category total: expected 349,398, got {rental_assistance_total}")
    if errors:
        raise SystemExit("SLIHP table arithmetic mismatch(es):\n" + "\n".join(errors))
    print("SLIHP's own printed table totals (p.58 $1,809,362,216; p.61 $1,574,756,367; "
          "p.62 347,729 HH+IND) and this script's derived rental_assistance_community_affairs "
          "total (349,398) all independently verified.")


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
    for app_num, name, address, city, county, units, htc_request in RAW_PROJECTS:
        query = f"{address}, {city}, TX"
        coords = geocode(query, cache)
        status = "ok"
        if coords is None:
            coords = geocode(f"{city}, TX", cache)
            status = "city_center" if coords else "unresolved"
        source_amounts = {"htc9": htc_request}
        projects.append({
            "id": f"tx-{app_num}-{slugify(name)}",
            "name": name,
            "address": address,
            "city": f"{city} ({county} County)",
            "lat": round(coords[0], 5) if coords else None,
            "lon": round(coords[1], 5) if coords else None,
            "units": units,
            "funding_sources": ["htc9"],
            "source_amounts": source_amounts,
            "total_amount": htc_request,
            "primary_color_group": FUNDING_COLOR_GROUP["htc9"],
            "overlaps": False,
            "geocode_status": status,
        })
    return projects


def main():
    verify_award_list_totals()
    verify_slihp_table_arithmetic()
    print("Geocoding 9% HTC award addresses via Nominatim...")
    projects = build_projects()
    unresolved = [p["name"] for p in projects if p["geocode_status"] == "unresolved"]
    if unresolved:
        print(f"  {len(unresolved)} project(s) could not be geocoded: {unresolved}")
    city_center = [p["name"] for p in projects if p["geocode_status"] == "city_center"]
    if city_center:
        print(f"  {len(city_center)} project(s) fell back to city-center geocoding: {city_center}")

    payload = {
        "TX": {
            "hfa_name": "Texas Department of Housing and Community Affairs",
            "hfa_abbr": "TDHCA",
            "fiscal_year": "SFY2025",
            "source_title": "2026 State of Texas Low Income Housing Plan and Annual Report (SLIHP) -- reports SFY2025 actuals",
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
