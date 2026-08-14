"""
Builds docs/nc_program_activity.json from the North Carolina Housing Finance
Agency's (NCHFA) FY2025 "2025 Housing Credit Awards" list plus its own
FY2025 audited financial statements (for GASB fund-type classification) and
its "2025 Investment and Impact Report" website (for the homeownership
category headline).

Sources
---------------------------------------------------------------------------
1. "2025 Housing Credit Awards" (NCHFA), published August 21, 2025:
     https://www.nchfa.com/sites/default/files/forms_resources/2025-08/2025%20Awards%20List.pdf
   Local copy: FY2025/program_activity/pdf/NC_NCHFA_2025_Awards_List.pdf
   A single-page PDF containing TWO separate award tables (9% Housing
   Credits, and 4% Housing Credits + Tax-Exempt Bonds) plus a one-row
   "Forward Commitment of 2026 Housing Credits" section -- see "Table
   layout and extraction" and "The excluded 2026 Forward Commitment row"
   below.
2. NCHFA's own FY2025 audited financial statements (fiscal year July 1,
   2024 - June 30, 2025), used ONLY for GASB fund-type classification:
     FY2025/txt/NC_NCHFA_FY2025_ACFR.txt
   Verified as NCHFA's own (not a substitute/wrong-agency document, the
   mistake caught in PA's build): the file's own title page reads
   "NORTH CAROLINA HOUSING FINANCE AGENCY FINANCIAL STATEMENTS AND
   SUPPLEMENTARY INFORMATION FOR THE YEAR ENDED JUNE 30, 2025" and the
   independent auditor's report opinion is on "the business-type
   activities of the North Carolina Housing Finance Agency (the Agency),
   a public agency component unit of the State of North Carolina" --
   i.e. this is NCHFA's own single-agency financial statements (not a
   statewide North Carolina ACFR with NCHFA folded in as a component
   unit), and June 30 fiscal year-end matches NCHFA's known 7/1-6/30
   fiscal year.
3. NCHFA "2025 Investment and Impact Report" website (homeownership
   category headline only -- see "The 2024-vs-2025 trap on this website"
   below):
     https://2025.housingbuildsnc.com/

Table layout and extraction
---------------------------------------------------------------------------
The Awards List PDF is ONE page containing two physically separate tables
with different columns, extracted via pdfplumber word-level x-position
bucketing (not simple whitespace-splitting -- the RPP/WHLP/GLF dollar
columns have extensive blank cells, so a project's printed numbers shift
left/right depending on which sources it drew on; bucketing every word by
its x0/x1 midpoint against the header's own measured column boundaries is
the only reliable way to assign, e.g., a lone "$1,300,000 $500,000" pair to
the correct two of five possible dollar columns). Both tables' own footer
TOTALS rows were independently reproduced by resumming this script's own
transcription -- see verify_table1_totals()/verify_table2_totals() -- as
the double-verification gate:
  - Table 1, "2025 Housing Credit Awards" (9% competitive credits), columns
    Project Name/City/County, Housing Credits, RPP, WHLP Amount, GLF
    Amount, Total Units, Type, Target Pop, Applicant/Contact/Phone: 29 rows,
    footer TOTALS row Housing Credits $31,416,430 / RPP $12,222,000 / WHLP
    Amount $32,777,415 / Units 1,503. The GLF Amount column is entirely
    blank for every one of the 29 rows (confirmed by scanning that column's
    x-range for the whole table -- zero words found), consistent with the
    footer TOTALS row itself printing no GLF figure at all -- so no "glf"
    subprogram is created (a program with zero disclosed FY2025 activity is
    omitted, not assigned a fabricated $0 entry).
  - Table 2, "[4% Housing Credits + Tax-Exempt Bond]" (same page, no table
    title of its own beyond reused/mangled column headers), columns Project
    Name/City/County, Housing Credits, Bond Volume, Total Units, Type,
    Target Pop, Applicant/Contact/Phone: 20 rows, footer TOTALS row Bond
    Volume $542,682,000 / Units 3,439 (this table's own Housing Credits
    column has NO printed footer total -- this script's own resummed
    $43,333,208 is therefore labeled in fy2025_amounts as computed, not
    quoted as a PDF-printed figure).

The excluded 2026 Forward Commitment row
---------------------------------------------------------------------------
The PDF's final section, "Forward Commitment of 2026 Housing Credits",
lists exactly one project (Winston-Salem CNI Phase V, Forsyth County,
$1,300,000 housing credits / $2,000,000 bond volume / 70 units) that is NOT
part of either table's own TOTALS row and is explicitly captioned as 2026
credits, not FY2025 production. Per this project's rule against mixing
fiscal years, this row is deliberately EXCLUDED from RAW_PROJECTS and from
every category total below -- it is not folded into fy2025_actual, not
geocoded, and not used as the category's fy2026 projection either (one
forward-committed deal is not NC's full FY2026 pipeline, and presenting it
as such would overstate what NCHFA has actually disclosed about FY2026).
This leaves 29 + 20 = 49 transcribed projects, not the "50-plus" a same-day
skim of the PDF might suggest before separating out this row.

The two "^"/"+"" award-date footnote markers printed after some Table 2
project names ("Awarded in February 2025" / "Awarded in June 2025") are
stripped from the transcribed name for display, since both dates already
fall inside NCHFA's FY2025 (July 1, 2024 - June 30, 2025) -- they are a
within-year timing footnote, not a fiscal-year qualifier, so dropping the
symbol does not lose any year information relevant to this file.

The 2024-vs-2025 trap on this website (see task instructions)
---------------------------------------------------------------------------
housingbuildsnc.com's domain is literally "2025", but per-page content was
checked sentence-by-sentence via fetches of the homepage, /home-ownership/,
and /rental-investments/ before using anything from it:
  - /rental-investments/: its LIHTC-application/tax-exempt-bond/9%-award
    statistics sit under an explicit "Our Impact in 2024" heading, and its
    own headline number ("3,631 apartments for families and 580 for
    seniors") differs from the homepage's teaser sentence ("5,000
    apartments for families ... in 2025") -- confirming these are two
    different years' data, not a rounding difference. NOT used anywhere in
    this file; the Rental/Multifamily category below is built entirely from
    the Awards List PDF instead, which is unambiguously dated (published
    August 21, 2025, captioned "2025 Housing Credit Awards").
  - /home-ownership/: explicitly captioned "Our Impact in 2024" with its own
    different headline ("5,880 North Carolinians become homeowners ... in
    2024"). NOT used.
  - Homepage (https://2025.housingbuildsnc.com/, root only): contains a
    distinct "In 2025 ..." narrative block with its own numbers, different
    from both subpages above -- "With more than $1.2 billion in mortgage
    financing provided by the Agency statewide in 2025, 5,140 North
    Carolinians made their dreams of home ownership come true", plus a
    subprogram breakdown (NC Home Advantage Mortgage 4,760 households, NC
    1st Home Advantage Down Payment 3,930 home buyers, Community Partners
    Loan Pool 310 home buyers assisted, Self-Help Loan Pool 130 home buyers
    assisted) under the same "Home Ownership" homepage section, plus its
    own top-line KPIs ("$3 Billion Real Estate Activity Produced", "12,500
    Homes and Apartments Financed", "530 Communities Reached"). Because
    these homepage figures are the ONLY ones on this site whose surrounding
    sentence explicitly says "in 2025" (verified via two independent,
    differently-worded fetches asking for verbatim quotes, not a
    paraphrase), this file uses ONLY the homepage's own Home Ownership
    section for the homeownership_loans category below -- never the
    /home-ownership/ subpage. The three homepage top-line KPIs
    ($3B/12,500/530) are NOT used as their own category (no subprogram or
    fund-type detail is disclosed for them anywhere on the site, so forcing
    them into this file's category+subprogram JSON shape would mean
    inventing structure that was never actually published) -- they are
    documented here for context only, consistent with "better to do less
    than use a wrong-year or fabricated number."

Category-level methodology
---------------------------------------------------------------------------
Category 1, "housing_credit_awards" (Rental/Multifamily, RAW_PROJECTS):
fy2025_actual = 4,942 units = Table 1's own 1,503-unit TOTALS row + Table
2's own 3,439-unit TOTALS row (both printed totals, simply added -- not a
re-derivation of either). additive=False: within Table 1, most of the 29
projects draw on 2 or 3 of {hc9, rpp, whlp} simultaneously for the SAME
units (28 of 29 have hc9+whlp; 11 of those also have rpp), and within Table
2 every one of the 20 projects draws on BOTH hc4 and bond for the same
units -- so summing subprogram unit counts would substantially overcount
physical units, the same reasoning IL/PA/FL's builds use for their own
multifamily categories.

Category 2, "homeownership_loans": fy2025_actual = 5,140 (the homepage's
own headline households figure, see "2024-vs-2025 trap" above).
additive=False: the homepage's own subprogram figures (4,760 + 3,930 + 310
+ 130 = 9,130) sum to far more than the 5,140 headline, indicating
substantial overlap (a buyer commonly combines a HomeAd first mortgage with
1st Home DPA or another down-payment product) -- same non-additive pattern
FL's own footnote states explicitly for its analogous category. This
category has NO RAW_PROJECTS entry (the website discloses only statewide
totals, no per-development or per-county detail), so it contributes no
markers to the bubble map -- shown as a KPI card only, matching how PA's
PHARE category (dollars-only, no unit count disclosed) also carries no map
detail without fabricating one.

Fund-type classification (fund_type/fund_name on each subprogram)
---------------------------------------------------------------------------
Like PHFA (PA) and Florida Housing, NCHFA's own FY2025 financial statements
report ONLY business-type activities (the independent auditor's report
opinion is on "the business-type activities of the North Carolina Housing
Finance Agency") -- no governmental funds of its own. The working
distinction below is therefore "proprietary" (the resulting loan/asset is
carried on NCHFA's own Statement of Net Position) vs. "off_balance_sheet"
(explicitly stated in the ACFR to be excluded from NCHFA's own financial
statements, or a program NCHFA administers/monitors but never carries an
asset for).
  - hc9, hc4 (Low-Income Housing Tax Credit, 9% and 4%) -- "off_balance_sheet".
    Note 2 describes the Agency's role as administering applications and
    "monitoring the rental properties for the compliance period ... The
    Agency earns fees related to the applications and monitoring of LIHTC
    properties" -- fee income only; the tax credit itself is never a
    NCHFA-carried asset, same off-balance-sheet logic IL/PA/FL's builds use
    for their own LIHTC-family subprograms.
  - bond (Table 2's tax-exempt Bond Volume column) -- "off_balance_sheet",
    HIGH confidence, directly and explicitly confirmed: Note D, "Special
    Facilities (Conduits)": "The Agency issued Multifamily Housing Revenue
    Bonds which are not presented in the financial statements of the
    Agency. These bonds are limited obligations of the Agency, secured
    solely by the revenues and other assets pledged for their payment.
    These bonds do not constitute a debt of and are not guaranteed by the
    State or any political subdivision thereof. Accordingly, these
    obligations are excluded from the Agency's financial statements." That
    same note's own "special facilities" bond list includes a "Series 2024
    (Fitch Irick Portfolio)" issue -- Fitch Irick Development is the named
    applicant on this file's own "Rocky River Apartments" (Table 2) -- an
    independent corroboration that Table 2's bond-financed deals are
    exactly this conduit-bond program.
  - rpp (Rental Production Program), whlp (Workforce Housing Loan Program)
    -- "proprietary", medium-high confidence. Both are described in the
    MD&A's "Rental Development Programs" section as NCHFA's own long-term
    financing/loan programs ("Rental Production Program provides long-term
    financing for tax credit developments. Amortizing or deferred loans are
    available up to 20 years"; "Workforce Housing Loan Program provides
    long-term financing for tax credit developments ... 30-year balloon
    loans"), and both are named among the federal/State-fund expenditure
    programs that feed Note C's own "Mortgage Loans Receivable" table
    (broken out by Home Ownership Bond Programs / Agency Programs / Housing
    Trust Fund and HOME Programs / Federal and State Programs columns) --
    i.e. these are loans NCHFA itself originates and carries as a
    receivable, not a pass-through grant. Confidence is "medium-high" (not
    "high" the way the bond note above is) because the Loans Receivable
    table's 4 columns are not broken out further by individual program
    name (RPP/WHLP aren't separately labeled within it), so this is a
    reasonable, cited inference from the program descriptions plus the
    aggregate receivable table, not a literal named-line-item match.
  - homead (NC Home Advantage Mortgage), first_home_dpa (NC 1st Home
    Advantage Down Payment Assistance) -- "proprietary", HIGH confidence.
    The MD&A states plainly: "The Agency issued taxable and tax-exempt
    bonds in fiscal year 2025 to finance a portion of its HomeAd
    production" and, on the Series 55 bond issuance specifically,
    "Proceeds have been used to finance production of both the Agency's
    first mortgage purchases and the NC 1st Home Advantage Down Payment
    Assistance" -- both sit inside NCHFA's own 1998 Home Ownership Bond
    Program, and Note C's Loans Receivable table has a dedicated "Home
    Ownership Bond Programs" column.
  - cplp (Community Partners Loan Pool), shlp (Self-Help Loan Pool) --
    "proprietary", medium confidence. Both are named among the federal/
    State-fund program lists (CPLP appears in all three of NCHFA's federal/
    State/other funding-source expenditure lists; SHLP appears in the
    federal-funds list) whose resulting loans are carried in Note C's
    Loans Receivable table's "Federal and State Programs" column -- not
    individually named within that column the way HomeAd's bond-program
    column is, hence "medium" rather than "high" confidence.

Geocoding
---------------------------------------------------------------------------
The Awards List gives only City + County for every project (no street
address, as the task brief anticipated). Nominatim query
"{City}, {County} County, NC", falling back to "{City}, NC" and marking
geocode_status="city_center" (per this project's convention, every
successfully-resolved NC project is tagged "city_center" rather than "ok"
since no address-level precision is ever available here). Self-throttled
to <=1 request/second with an identifying User-Agent per Nominatim's usage
policy.

fy2026
---------------------------------------------------------------------------
Neither the Awards List PDF nor the Investment and Impact Report website
discloses a genuine FY2026 (or CY2026) full-pipeline projection -- the only
FY2026-labeled figure anywhere in the source material is the single
"Forward Commitment of 2026 Housing Credits" row excluded above, which is
one project, not a projection. Every fy2026 field below is therefore
{value: None, amount: None, closed: False, note_key: "ncFy26NotePending"}.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "nc_program_activity.json"

SOURCE_URL = "https://www.nchfa.com/sites/default/files/forms_resources/2025-08/2025%20Awards%20List.pdf"
SOURCE_FILE = "NC_NCHFA_2025_Awards_List.pdf (+ housingbuildsnc.com homepage 2025 Home Ownership figures)"
RETRIEVED = "2026-08-14"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
GEOCODER_USER_AGENT = "us-hfa-data-map/1.0 (github.com/MD-ai-fin/us-hfa-data-map)"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "ncFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "housing_credit_awards",
        "unit_type": "units",
        "fy2025_actual": 4942,
        "fy2025_source_quote": (
            "\"2025 Housing Credit Awards\" (published August 21, 2025). Table 1 (9% "
            "competitive credits) TOTALS row: Housing Credits $31,416,430, RPP "
            "$12,222,000, WHLP Amount $32,777,415, Total Units 1,503, across 29 "
            "developments. Table 2 (4% credits + tax-exempt bonds) TOTALS row: Bond "
            "Volume $542,682,000, Total Units 3,439, across 20 developments (this "
            "table prints no separate Housing Credits dollar total; this script's own "
            "resummed $43,333,208 is shown as computed, not a quoted PDF figure). "
            "4,942 = 1,503 + 3,439. A separate one-project \"Forward Commitment of "
            "2026 Housing Credits\" row (Winston-Salem CNI Phase V, 70 units) is "
            "excluded from this total -- it is explicitly 2026 credits, not FY2025 "
            "production."
        ),
        "fy2025_amounts": [
            {"label_key": "nc_amt_hc9", "amount": 31416430},
            {"label_key": "nc_amt_rpp", "amount": 12222000},
            {"label_key": "nc_amt_whlp", "amount": 32777415},
            {"label_key": "nc_amt_hc4", "amount": 43333208},
            {"label_key": "nc_amt_bond", "amount": 542682000},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "hc9", "fy2025_units": 1503, "fy2025_amount": 31416430,
             "color_group": "credit",
             # Note 2: Agency "earns fees related to the applications and
             # monitoring of LIHTC properties" -- fee income only, never a
             # NCHFA-carried loan/tax-credit asset.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "rpp", "fy2025_units": 654, "fy2025_amount": 12222000,
             "color_group": "trust",
             # MD&A "Rental Development Programs": "Rental Production
             # Program provides long-term financing for tax credit
             # developments. Amortizing or deferred loans are available up
             # to 20 years" -- an Agency-originated loan feeding Note C's
             # Mortgage Loans Receivable table; medium-high confidence
             # (program not separately labeled within that table's own
             # 4 fund columns).
             "fund_type": "proprietary", "fund_name": "Rental Production Program (loans receivable, inferred)",
             "fy2026": _FY26_PENDING},
            {"key": "whlp", "fy2025_units": 1419, "fy2025_amount": 32777415,
             "color_group": "trust",
             # MD&A: "Workforce Housing Loan Program provides long-term
             # financing for tax credit developments ... 30-year balloon
             # loans"; State-funds expenditure list confirms WHLP is
             # State-appropriated. Same Loans Receivable table logic as RPP
             # above; medium-high confidence.
             "fund_type": "proprietary", "fund_name": "Workforce Housing Loan Program (loans receivable, inferred)",
             "fy2026": _FY26_PENDING},
            {"key": "hc4", "fy2025_units": 3439, "fy2025_amount": 43333208,
             "color_group": "credit",
             # Same off-balance-sheet LIHTC administration/fee-only logic as
             # hc9 above -- 4% credits are the same federal LIHTC program at
             # a different (non-competitive, bond-paired) rate.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "bond", "fy2025_units": 3439, "fy2025_amount": 542682000,
             "color_group": "bond",
             # Note D, "Special Facilities (Conduits)": these Multifamily
             # Housing Revenue Bonds "are not presented in the financial
             # statements of the Agency ... excluded from the Agency's
             # financial statements." High confidence -- explicit,
             # verbatim ACFR statement, corroborated by the "Series 2024
             # (Fitch Irick Portfolio)" conduit-bond line item matching this
             # file's own "Rocky River Apartments" applicant.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "homeownership_loans",
        "unit_type": "households",
        "fy2025_actual": 5140,
        "fy2025_source_quote": (
            "housingbuildsnc.com homepage (root URL only, NOT the /home-ownership/ "
            "subpage -- see module docstring), \"Home Ownership\" section: \"With more "
            "than $1.2 billion in mortgage financing provided by the Agency statewide "
            "in 2025, 5,140 North Carolinians made their dreams of home ownership come "
            "true.\" Subprogram figures from the same homepage section: NC Home "
            "Advantage Mortgage 4,760 households, NC 1st Home Advantage Down Payment "
            "3,930 home buyers, Community Partners Loan Pool 310 home buyers assisted, "
            "Self-Help Loan Pool 130 home buyers assisted -- these sum to 9,130, far "
            "more than the 5,140 headline, indicating most buyers combine 2+ of these "
            "products (non-additive)."
        ),
        "fy2025_amounts": [
            {"label_key": "nc_amt_mortgage_financing", "amount": 1200000000},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "homead", "fy2025_units": 4760, "fy2025_amount": None,
             "color_group": "bond",
             # MD&A: bonds issued in FY2025 "to finance a portion of its
             # HomeAd production"; Note C's Loans Receivable table has a
             # dedicated "Home Ownership Bond Programs" column. High
             # confidence.
             "fund_type": "proprietary", "fund_name": "Home Ownership Bond Programs (1998 Housing Revenue Bonds Trust Agreement)",
             "fy2026": _FY26_PENDING},
            {"key": "first_home_dpa", "fy2025_units": 3930, "fy2025_amount": None,
             "color_group": "bond",
             # MD&A, on the Series 55 bond issuance: "Proceeds have been
             # used to finance production of both the Agency's first
             # mortgage purchases and the NC 1st Home Advantage Down
             # Payment Assistance" -- same Home Ownership Bond Program as
             # homead. High confidence.
             "fund_type": "proprietary", "fund_name": "Home Ownership Bond Programs (1998 Housing Revenue Bonds Trust Agreement)",
             "fy2026": _FY26_PENDING},
            {"key": "cplp", "fy2025_units": 310, "fy2025_amount": None,
             "color_group": "trust",
             # CPLP appears in NCHFA's own federal/State/other-funds
             # expenditure program lists; the resulting loans are presumed
             # to sit inside Note C's "Federal and State Programs" Loans
             # Receivable column (not individually named within it).
             # Medium confidence.
             "fund_type": "proprietary", "fund_name": "Federal and State Programs (loans receivable, inferred)",
             "fy2026": _FY26_PENDING},
            {"key": "shlp", "fy2025_units": 130, "fy2025_amount": None,
             "color_group": "trust",
             # Same Federal and State Programs loans-receivable logic as
             # CPLP above. Medium confidence.
             "fund_type": "proprietary", "fund_name": "Federal and State Programs (loans receivable, inferred)",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# ---------------------------------------------------------------------------
# Category 1 project-level detail ("2025 Housing Credit Awards" PDF, both
# tables). Extracted via pdfplumber word-position column bucketing (see
# module docstring); (name, city, county, units, [funding source keys]).
# The "^"/"+" award-timing footnote markers printed after some Table 2 names
# are stripped (both dates fall inside FY2025 -- see docstring).
# ---------------------------------------------------------------------------

RAW_PROJECTS = [
    # --- Table 1: 2025 Housing Credit Awards (9% competitive credits), 29 rows ---
    ("Greyson Reserve", "Burlington", "Alamance", 60, ["hc9", "rpp", "whlp"]),
    ("Southport Green Rehab", "Southport", "Brunswick", 44, ["hc9", "rpp"]),
    ("The Villas at Haywood", "Asheville", "Buncombe", 52, ["hc9", "whlp"]),
    ("Archer Commons", "Morganton", "Burke", 48, ["hc9", "whlp"]),
    ("Blue Point Bay Apartments", "Newport", "Carteret", 64, ["hc9", "whlp"]),
    ("Aspen Pointe", "Fayetteville", "Cumberland", 32, ["hc9", "whlp"]),
    ("Tulip Commons at Old Vineyard", "Winston-Salem", "Forsyth", 60, ["hc9", "whlp"]),
    ("Preserve at Forest Heights", "Gastonia", "Gaston", 52, ["hc9", "whlp"]),
    ("Overland Place Apartments", "Greensboro", "Guilford", 48, ["hc9", "whlp"]),
    ("The Grayson", "Greensboro", "Guilford", 84, ["hc9", "rpp", "whlp"]),
    ("Maynard Crossing Apartments", "Erwin", "Harnett", 64, ["hc9", "rpp", "whlp"]),
    ("Countryside Apartments", "Raeford", "Hoke", 40, ["hc9"]),
    ("Palmer Green Apartments (Rehab)", "Raeford", "Hoke", 40, ["hc9", "whlp"]),
    ("Keystone Landing", "Mooresville", "Iredell", 48, ["hc9", "whlp"]),
    ("Spaulding Woods I", "Marion", "McDowell", 44, ["hc9", "whlp"]),
    ("Baker Crossing", "Charlotte", "Mecklenburg", 58, ["hc9", "rpp", "whlp"]),
    ("Long Creek Commons", "Huntersville", "Mecklenburg", 48, ["hc9", "whlp"]),
    ("Onyx Place", "Wilmington", "New Hanover", 48, ["hc9", "rpp", "whlp"]),
    ("Maddry Meadows", "Chapel Hill", "Orange", 53, ["hc9", "rpp", "whlp"]),
    ("Park Ridge Trace", "Greenville", "Pitt", 72, ["hc9", "rpp", "whlp"]),
    ("The Reserve at Fairmont", "Fairmont", "Robeson", 64, ["hc9", "rpp", "whlp"]),
    ("Norman Court", "Eden", "Rockingham", 30, ["hc9", "whlp"]),
    ("Uwharrie Trail Phase II", "Albemarle", "Stanly", 48, ["hc9", "whlp"]),
    ("Abbey Spring", "Apex", "Wake", 56, ["hc9", "rpp", "whlp"]),
    ("The Canopy", "Cary", "Wake", 51, ["hc9", "rpp", "whlp"]),
    ("Heritage Park Senior Phase 1B", "Raleigh", "Wake", 51, ["hc9", "whlp"]),
    ("The Villas at South Fork", "Boone", "Watauga", 48, ["hc9", "whlp"]),
    ("Central Garden Phase II", "Goldsboro", "Wayne", 48, ["hc9", "whlp"]),
    ("Waverly Trace", "Wilson", "Wilson", 48, ["hc9", "whlp"]),
    # --- Table 2: 4% Housing Credits + Tax-Exempt Bonds, 20 rows ---
    ("Rocky River Apartments", "Woodfin", "Buncombe", 120, ["hc4", "bond"]),
    ("902 S. Briggs Avenue", "Durham", "Durham", 124, ["hc4", "bond"]),
    ("DHA Fayette Place Phase I", "Durham", "Durham", 252, ["hc4", "bond"]),
    ("Page Road Development", "Morrisville", "Durham", 160, ["hc4", "bond"]),
    ("The Lofts at Motor Road", "Winston-Salem", "Forsyth", 216, ["hc4", "bond"]),
    ("The Residences at Indiana Avenue", "Winston-Salem", "Forsyth", 180, ["hc4", "bond"]),
    ("Bolding Street Lofts", "Gastonia", "Gaston", 168, ["hc4", "bond"]),
    ("Shotwell Apartments", "Clayton", "Johnston", 90, ["hc4", "bond"]),
    ("Avenue Flats", "Wilmington", "New Hanover", 184, ["hc4", "bond"]),
    ("Walker Landing", "Elizabeth City", "Pasquotank", 155, ["hc4", "bond"]),
    ("Barton Oaks", "Raleigh", "Wake", 152, ["hc4", "bond"]),
    ("Battle Bridge", "Raleigh", "Wake", 200, ["hc4", "bond"]),
    ("Garner Apartments", "Raleigh", "Wake", 224, ["hc4", "bond"]),
    ("Hoke Street", "Raleigh", "Wake", 120, ["hc4", "bond"]),
    ("Maple Ridge", "Raleigh", "Wake", 146, ["hc4", "bond"]),
    ("Moore Square Commons", "Raleigh", "Wake", 160, ["hc4", "bond"]),
    ("Old Poole Place", "Raleigh", "Wake", 181, ["hc4", "bond"]),
    ("The Pointe at Town Center", "Raleigh", "Wake", 192, ["hc4", "bond"]),
    ("Tryon Flats", "Raleigh", "Wake", 220, ["hc4", "bond"]),
    ("Union at Capital", "Raleigh", "Wake", 195, ["hc4", "bond"]),
]

# Per-project, per-funding-source dollar amount, transcribed alongside
# RAW_PROJECTS from the same table cells.
PROJECT_SOURCE_AMOUNTS = {
    "Greyson Reserve": {"hc9": 1300000, "rpp": 825000, "whlp": 1500000},
    "Southport Green Rehab": {"hc9": 501059, "rpp": 682000},
    "The Villas at Haywood": {"hc9": 1300000, "whlp": 500000},
    "Archer Commons": {"hc9": 1250000, "whlp": 1100000},
    "Blue Point Bay Apartments": {"hc9": 704525, "whlp": 710000},
    "Aspen Pointe": {"hc9": 660929, "whlp": 710000},
    "Tulip Commons at Old Vineyard": {"hc9": 1300000, "whlp": 2000000},
    "Preserve at Forest Heights": {"hc9": 1300000, "whlp": 500000},
    "Overland Place Apartments": {"hc9": 1300000, "whlp": 2000000},
    "The Grayson": {"hc9": 1300000, "rpp": 1600000, "whlp": 2000000},
    "Maynard Crossing Apartments": {"hc9": 1300000, "rpp": 1280000, "whlp": 2000000},
    "Countryside Apartments": {"hc9": 450067},
    "Palmer Green Apartments (Rehab)": {"hc9": 486625, "whlp": 1350000},
    "Keystone Landing": {"hc9": 1096540, "whlp": 500000},
    "Spaulding Woods I": {"hc9": 727820, "whlp": 1655990},
    "Baker Crossing": {"hc9": 1300000, "rpp": 870000, "whlp": 500000},
    "Long Creek Commons": {"hc9": 1300000, "whlp": 500000},
    "Onyx Place": {"hc9": 1110000, "rpp": 720000, "whlp": 500000},
    "Maddry Meadows": {"hc9": 1300000, "rpp": 1600000, "whlp": 500000},
    "Park Ridge Trace": {"hc9": 1300000, "rpp": 1440000, "whlp": 2000000},
    "The Reserve at Fairmont": {"hc9": 1300000, "rpp": 1600000, "whlp": 3000000},
    "Norman Court": {"hc9": 383754, "whlp": 1535000},
    "Uwharrie Trail Phase II": {"hc9": 1028816, "whlp": 1470000},
    "Abbey Spring": {"hc9": 1300000, "rpp": 840000, "whlp": 500000},
    "The Canopy": {"hc9": 1300000, "rpp": 765000, "whlp": 500000},
    "Heritage Park Senior Phase 1B": {"hc9": 1300000, "whlp": 500000},
    "The Villas at South Fork": {"hc9": 1300000, "whlp": 500000},
    "Central Garden Phase II": {"hc9": 1105014, "whlp": 1500000},
    "Waverly Trace": {"hc9": 1111281, "whlp": 2746425},
    "Rocky River Apartments": {"hc4": 2153232, "bond": 24000000},
    "902 S. Briggs Avenue": {"hc4": 1791425, "bond": 20000000},
    "DHA Fayette Place Phase I": {"hc4": 2795264, "bond": 44000000},
    "Page Road Development": {"hc4": 2475253, "bond": 29000000},
    "The Lofts at Motor Road": {"hc4": 1592703, "bond": 23000000},
    "The Residences at Indiana Avenue": {"hc4": 1865579, "bond": 20500000},
    "Bolding Street Lofts": {"hc4": 1830993, "bond": 22000000},
    "Shotwell Apartments": {"hc4": 1320301, "bond": 14500000},
    "Avenue Flats": {"hc4": 2324828, "bond": 28000000},
    "Walker Landing": {"hc4": 1852011, "bond": 22000000},
    "Barton Oaks": {"hc4": 1518796, "bond": 23000000},
    "Battle Bridge": {"hc4": 1776232, "bond": 25000000},
    "Garner Apartments": {"hc4": 3027355, "bond": 36000000},
    "Hoke Street": {"hc4": 1212000, "bond": 15000000},
    "Maple Ridge": {"hc4": 2063318, "bond": 24500000},
    "Moore Square Commons": {"hc4": 2272125, "bond": 31682000},
    "Old Poole Place": {"hc4": 2819097, "bond": 32500000},
    "The Pointe at Town Center": {"hc4": 3101351, "bond": 35000000},
    "Tryon Flats": {"hc4": 3583799, "bond": 43000000},
    "Union at Capital": {"hc4": 1957546, "bond": 30000000},
}

# Table 1's own printed TOTALS row (Housing Credits, RPP, WHLP Amount, Units).
EXPECTED_T1_TOTALS = {"hc9": 31416430, "rpp": 12222000, "whlp": 32777415}
EXPECTED_T1_UNITS = 1503
EXPECTED_T1_COUNT = 29

# Table 2's own printed TOTALS row (Bond Volume, Units only -- no Housing
# Credits dollar total is printed for this table, see module docstring).
EXPECTED_T2_TOTALS = {"bond": 542682000}
EXPECTED_T2_UNITS = 3439
EXPECTED_T2_COUNT = 20

FUNDING_COLOR_GROUP = {
    "hc9": "credit", "hc4": "credit",
    "rpp": "trust", "whlp": "trust",
    "bond": "bond",
}
# priority order for picking a project's single "primary" color when it has
# multiple funding sources (first match wins) -- the Housing Credit (9%/4%)
# is the universal anchor credit for every one of the 49 awards.
FUNDING_PRIORITY = ["hc9", "hc4", "whlp", "rpp", "bond"]


def verify_table1_totals():
    t1 = [p for p in RAW_PROJECTS if any(s in ("hc9", "rpp", "whlp") for s in p[4])]
    errors = []
    if len(t1) != EXPECTED_T1_COUNT:
        errors.append(f"Table 1 project count: expected {EXPECTED_T1_COUNT}, got {len(t1)}")
    units_sum = sum(u for _n, _c, _co, u, _s in t1)
    if units_sum != EXPECTED_T1_UNITS:
        errors.append(f"Table 1 Total Units: expected {EXPECTED_T1_UNITS}, got {units_sum}")
    sums = {"hc9": 0, "rpp": 0, "whlp": 0}
    for name, _city, _county, _units, sources in t1:
        amounts = PROJECT_SOURCE_AMOUNTS.get(name)
        if amounts is None:
            raise SystemExit(f"No PROJECT_SOURCE_AMOUNTS entry for {name!r}")
        missing = [s for s in sources if s not in amounts]
        extra = [s for s in amounts if s not in sources]
        if missing:
            errors.append(f"{name!r} is missing amounts for source(s) {missing}")
        if extra:
            errors.append(f"{name!r} has amounts for undeclared source(s) {extra}")
        for src, amt in amounts.items():
            sums[src] = sums.get(src, 0) + amt
    for key, expected in EXPECTED_T1_TOTALS.items():
        got = sums.get(key, 0)
        if got != expected:
            errors.append(f"Table 1 {key} total: expected {expected:,}, got {got:,}")
    if errors:
        raise SystemExit("Table 1 mismatch(es):\n" + "\n".join(errors))
    print(f"Table 1 verified: {EXPECTED_T1_COUNT} projects, {EXPECTED_T1_UNITS:,} units, "
          "and all 3 funding-source dollar totals match the PDF's own printed TOTALS row.")


def verify_table2_totals():
    t2 = [p for p in RAW_PROJECTS if any(s in ("hc4", "bond") for s in p[4])]
    errors = []
    if len(t2) != EXPECTED_T2_COUNT:
        errors.append(f"Table 2 project count: expected {EXPECTED_T2_COUNT}, got {len(t2)}")
    units_sum = sum(u for _n, _c, _co, u, _s in t2)
    if units_sum != EXPECTED_T2_UNITS:
        errors.append(f"Table 2 Total Units: expected {EXPECTED_T2_UNITS}, got {units_sum}")
    sums = {"hc4": 0, "bond": 0}
    for name, _city, _county, _units, sources in t2:
        amounts = PROJECT_SOURCE_AMOUNTS.get(name)
        if amounts is None:
            raise SystemExit(f"No PROJECT_SOURCE_AMOUNTS entry for {name!r}")
        if set(sources) != {"hc4", "bond"}:
            errors.append(f"{name!r}: expected exactly hc4+bond, got {sources}")
        for src, amt in amounts.items():
            sums[src] = sums.get(src, 0) + amt
    for key, expected in EXPECTED_T2_TOTALS.items():
        got = sums.get(key, 0)
        if got != expected:
            errors.append(f"Table 2 {key} total: expected {expected:,}, got {got:,}")
    hc4_computed = sums.get("hc4", 0)
    if errors:
        raise SystemExit("Table 2 mismatch(es):\n" + "\n".join(errors))
    print(f"Table 2 verified: {EXPECTED_T2_COUNT} projects, {EXPECTED_T2_UNITS:,} units, and "
          f"Bond Volume total match the PDF's own printed TOTALS row (Housing Credits "
          f"column has no printed total; this script's own computed sum is ${hc4_computed:,}).")


def verify_category_headline():
    total = EXPECTED_T1_UNITS + EXPECTED_T2_UNITS
    expected_cat = next(c for c in CATEGORIES if c["key"] == "housing_credit_awards")
    if expected_cat["fy2025_actual"] != total:
        raise SystemExit(
            f"Category headline mismatch: CATEGORIES has "
            f"{expected_cat['fy2025_actual']}, but {EXPECTED_T1_UNITS} + "
            f"{EXPECTED_T2_UNITS} = {total}"
        )
    print(f"Category headline verified: {EXPECTED_T1_UNITS:,} + {EXPECTED_T2_UNITS:,} = "
          f"{total:,} units.")


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
    for name, city, county, units, sources in RAW_PROJECTS:
        query = f"{city}, {county} County, NC"
        coords = geocode(query, cache)
        status = "city_center"
        if coords is None:
            coords = geocode(f"{city}, NC", cache)
            status = "city_center" if coords else "unresolved"
        primary = next((s for s in FUNDING_PRIORITY if s in sources), sources[0])
        source_amounts = PROJECT_SOURCE_AMOUNTS.get(name, {})
        projects.append({
            "id": name.lower().replace(" ", "-").replace("'", "").replace(".", "").replace("&", "and").replace("(", "").replace(")", ""),
            "name": name,
            "address": None,
            "city": f"{city}, {county} County",
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
    verify_table1_totals()
    verify_table2_totals()
    verify_category_headline()
    print("Geocoding project city/county centers via Nominatim...")
    projects = build_projects()
    unresolved = [p["name"] for p in projects if p["geocode_status"] == "unresolved"]
    if unresolved:
        print(f"  {len(unresolved)} project(s) could not be geocoded: {unresolved}")
    print(f"  {len(projects)} projects geocoded.")

    payload = {
        "NC": {
            "hfa_name": "North Carolina Housing Finance Agency",
            "hfa_abbr": "NCHFA",
            "fiscal_year": "FY2025",
            "source_title": "2025 Housing Credit Awards (+ housingbuildsnc.com 2025 Home Ownership figures)",
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
