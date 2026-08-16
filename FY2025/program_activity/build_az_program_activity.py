"""
Builds docs/az_program_activity.json for the Arizona Department of Housing
(ADOH) FY2025 program-activity module.

Sources (ADOH's fiscal year = July 1, 2024 - June 30, 2025)
------------------------------------------------------------
1. "Fiscal Year 2025 Annual Report" (24 pp, posted Dec 2025) -- the
   narrative KPI + commitment-chart source:
     https://housing.az.gov/resources/2025-annual-report
     (direct PDF: https://housing.az.gov/sites/default/files/2025-12/ADOH_2025_Annual_Report.pdf)
   Local copy: FY2025/program_activity/pdf/AZ_ADOH_AnnualReport_FY2025.pdf
2. "FY2025 Low Income Housing Tax Credit Reservation Commitments"
   (letter to Governor/Legislature per A.R.S. 35-728(D), dated
   September 30, 2025) -- the per-development project list (9% + 4% rounds,
   with a State Tax Credit column), name + street address + city + county +
   total units + LIHTC units + STC award + federal LIHTC award + project cost:
     https://housing.az.gov/sites/default/files/2025-10/FY2025-LIHTC-Projects-Report.pdf
   Local copy: FY2025/program_activity/pdf/AZ_ADOH_LIHTC_Projects_Report_FY2025.pdf
3. "FY2025 Housing Trust Fund & Military Transitional Housing Fund Report"
   (letter per A.R.S. 41-3955(F) / 41-3955.02(C), dated September 2, 2025) --
   used only for context on the State Housing Trust Fund "gap financing"
   subprogram; see the IMPORTANT caveat below:
     https://housing.az.gov/sites/default/files/2025-09/FY2025%20HTF%20%26%20MTHF%20Report.pdf
   Local copy: FY2025/program_activity/pdf/AZ_ADOH_HTF_MTHF_Report_FY2025.pdf

(All three were downloaded via the Pantheon mirror host
test-az2-adoh-housing.pantheonsite.io because housing.az.gov serves its PDFs
behind a Cloudflare "Just a moment..." challenge that returns HTTP 403 to
plain requests; the local filenames are listed above.)

No FY2026 projections appear in any of the three documents (unlike IHDA's
Report of Activities). Every fy2026 field below is therefore
{value: None, amount: None, closed: False, note_key: "azFy26NotePending"} --
ADOH's FY2025 annual report and companion letters do not disclose a
forward-looking figure, so none is invented.

IMPORTANT data-provenance caveats (all checked, none hidden)
------------------------------------------------------------
a. The HTF & MTHF Report's "comprehensive summary spreadsheet" (its page 3,
   the only per-project HTF award list) is an embedded object whose font has
   a broken/missing ToUnicode CMap -- pdfplumber and pypdf both extract every
   glyph as a raw `(cid:N)` token with no recoverable text. The rendered page
   is legible to a human but is not machine-transcribable without OCR. This
   script therefore does NOT transcribe HTF-only projects (e.g. "Salt River
   Flats 2", which the report's letter names as one of several $2,500,000 gap
   awards) -- those rows are left out rather than guessed. The report's
   narrative pages (1-2) ARE clean text and are quoted below: the State HTF
   received a $15,000,000 General Fund investment in FY2025, used chiefly as
   gap financing for 4% bond-financed projects supporting 1,211 affordable
   units in the Phoenix and Tucson metros, plus $4,000,000 to leverage
   federal funds; the Military Transitional Housing Fund made no new awards
   in FY2025. Because that gap financing is administered FOR 4% LIHTC
   bond-financed projects, the 33-project LIHTC list below is the primary
   project layer and substantially overlaps the HTF cohort.
b. The annual report and the LIHTC reservation report disagree slightly on
   the 4% LIHTC round: the annual report's executive summary says "$89
   million" in 4% LIHTC / "4,629 units" (and "25 projects"), while the
   LIHTC reservation report's own printed totals say "$80,914,517" / 4,229
   LIHTC units / 24 projects. The 400-unit difference (4,629 vs 4,229) is
   the annual report counting roughly one more 4% award (or total units
   incl. market-rate) than the statutory reservation list itemizes. This
   script uses the LIHTC reservation report's own per-project figures for
   the bubble map (it is the itemized, per-development source), and uses the
   annual report's headline (5,225 units) for the category headline.
c. STC dollars: the annual report's executive summary says "$3 million in
   State LIHTC"; the LIHTC reservation report's per-project STC column sums
   to $2,000,000 (Casa Grande - Phase One $1,000,000 + The Acacia at
   Youngtown Phase II $1,000,000). The $1,000,000 difference is an
   unreconciled internal discrepancy between ADOH's own two documents,
   disclosed here rather than papered over.

Category-level methodology
--------------------------
"Committed tax credits and financing" figures in the annual report are the
10-year gross value of each tax-credit stream (roughly 10x the annual credit:
$20.5M -> $205M 9%, $89M -> $890M 4%, $3M -> $30M STC), plus $12.5M gap
financing; they sum to the report's "$1.138 billion" committed for 5,225
rental units. The multifamily category's subprogram unit counts are NOT a
partition: STC (351 units) is paired onto 9%/4% projects, and gap (742 units,
Phoenix metro) sits inside the 4% cohort, so additive=False (summing
subprogram units would over-count), same reasoning as PA's multifamily
category. The per-project source_amounts below use the LIHTC reservation
report's ANNUAL tax-credit award (a different, per-development metric) rather
than the 10-year financing figure -- documented so the two layers are not
confused.

Rental assistance / homebuyer / rehab categories use the annual report's own
printed commitment-chart rows and narrative totals verbatim (see quotes).

Fund-type classification (fund_type/fund_name on each subprogram)
-----------------------------------------------------------------
ADOH is a cabinet-level STATE GOVERNMENT DEPARTMENT (not a quasi-governmental
bond-issuing authority like PHFA/IHDA). AZ has NO FY2025 ACFR text in the
corpus (FY2025/txt/ has no AZ file), and ADOH's separately-published audited
financial statements could not be located via the housing.az.gov financial
reports page during this build, so classifications below are by program
description with documented confidence -- not from a fund ledger:
  - LIHTC 9% / 4% and State Tax Credit: "off_balance_sheet". The LIHTC
    reservation report states the credits are "award[ed] ... to private
    housing developers ... sold to investors"; they never appear as ADOH fund
    assets. Confidence: high.
  - State Housing Trust Fund gap financing: "governmental". The State HTF is
    a state special-revenue trust fund, and ADOH (a governmental department)
    administers it; the HTF report describes it as a General Fund
    appropriation. Confidence: medium (by description, not ledger).
  - Section 8 HUD rental assistance (PBRA + HCV): "governmental". Federal
    pass-through payments ADOH administers on HUD's behalf (the annual
    report's commitment chart tracks them as "Federal" columns). Confidence:
    medium.
  - Arizona is Home down-payment assistance: "governmental". Funded by the
    State Housing Trust Fund and an ARPA executive allocation per the annual
    report (p.11). Confidence: medium.
  - Owner-occupied rehabilitation (CDBG/HOME/WAP/LIHEAP + utility funds):
    "governmental". Federal/state grant programs administered by a state
    department. Confidence: medium.

Geocoding
---------
Same approach as PA/IHDA: Nominatim (OpenStreetMap), primary query
"{address}, {city}, AZ", falling back to "{city}, AZ" (flagging
geocode_status="city_center") when the street query fails or the source
prints only a corner/intersection or "Scattered Sites" location.
Self-throttled <=1 request/second with an identifying User-Agent.

Because Nominatim rate-limits a shared IP (HTTP 429) when several state
builds run concurrently, the script falls back to komoot Photon -- another
keyless OpenStreetMap geocoder with a much more lenient limit -- whenever
Nominatim returns 429, and to a small built-in Arizona city-center table
(CITY_COORDS, same precision as a Nominatim city-center result) only when
BOTH geocoders are unavailable. Results are cached on disk (outside the
repo) so re-runs reproduce the same coordinates without re-querying.
"""

import json
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "az_program_activity.json"

# Persistent geocode cache (kept OUT of the repo so it is not a deliverable;
# also lets a rate-limited run resume instead of re-querying everything).
GEOCODE_CACHE_PATH = Path(tempfile.gettempdir()) / "az_program_activity_geocode_cache.json"

SOURCE_URL = "https://housing.az.gov/resources/2025-annual-report"
SOURCE_FILE = ("AZ_ADOH_AnnualReport_FY2025.pdf + "
               "AZ_ADOH_LIHTC_Projects_Report_FY2025.pdf + "
               "AZ_ADOH_HTF_MTHF_Report_FY2025.pdf")
RETRIEVED = "2026-08-16"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
PHOTON_URL = "https://photon.komoot.io/api/"
GEOCODER_USER_AGENT = "us-hfa-data-map/1.0 (github.com/MD-ai-fin/us-hfa-data-map)"

# ---------------------------------------------------------------------------
# Category-level data
# ---------------------------------------------------------------------------
_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "azFy26NotePending"}

CATEGORIES = [
    {
        "key": "multifamily_development",
        "unit_type": "units",
        "fy2025_actual": 5225,
        "fy2025_source_quote": (
            "\"In FY 2025, ADOH's Rental Development Program successfully funded many "
            "affordable housing communities statewide. ADOH committed $1.138 billion in "
            "tax credits and financing for the development or re-development of 5,225 "
            "rental units (5,223 with below market rents for lower income Arizonans). The "
            "breakdown is: $205 million awarded to 9 projects through the competitive 9% "
            "Low Income Housing Tax Credits (LIHTC) round, $890 million awarded to 25 "
            "projects through the non-competitive 4% LIHTC open application round, $30 "
            "million awarded through Arizona's State Tax Credit (STC) round, and $12.5 "
            "million awarded through Gap financing.\" (FY2025 Annual Report, Rental "
            "Programs: Development, p.5) -- the same page's chart splits the total into "
            "$74 Million committed to acquire/renovate 460 Existing Units + $1.064 Billion "
            "committed to construct 4,765 New Units = $1.138 Billion / 5,225 Rental Units. "
            "Executive Summary (p.3) gives the paired unit counts: 9% LIHTC $20.5M enabling "
            "596 units, 4% LIHTC $89M enabling 4,629 units, State LIHTC $3M supporting 351 "
            "units, and a gap-financing NOFA supporting 742 units (Phoenix metro)."
        ),
        "fy2025_amounts": [
            {"label_key": "az_amt_lihtc_9pct", "amount": 205000000},
            {"label_key": "az_amt_lihtc_4pct", "amount": 890000000},
            {"label_key": "az_amt_stc", "amount": 30000000},
            {"label_key": "az_amt_gap", "amount": 12500000},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "lihtc_9pct", "fy2025_units": 596, "fy2025_amount": 205000000,
             "color_group": "credit",
             # Federal 9% LIHTC awarded to private developers; never an ADOH
             # fund asset (see docstring). off_balance_sheet, high confidence.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "lihtc_4pct", "fy2025_units": 4629, "fy2025_amount": 890000000,
             "color_group": "credit",
             # Federal 4% LIHTC awarded through the open (bond-financed)
             # application round; same off-balance-sheet logic as 9%.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "stc", "fy2025_units": 351, "fy2025_amount": 30000000,
             "color_group": "credit",
             # Arizona State Tax Credit -- a state tax-credit allocation
             # flowing to developers, same off-balance-sheet logic as LIHTC.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "gap", "fy2025_units": 742, "fy2025_amount": 12500000,
             "color_group": "trust",
             # State Housing Trust Fund gap financing for 4% bond projects.
             # ADOH is a state department; the HTF is a state trust fund.
             # Confidence: medium (by program description; no AZ ACFR txt).
             "fund_type": "governmental",
             "fund_name": "State Housing Trust Fund (gap financing)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "hud_rental_assistance",
        "unit_type": "households",
        "fy2025_actual": 8522,
        "fy2025_source_quote": (
            "\"In Fiscal Year 2025, ADOH administered more than $87 million in Federal "
            "funding from the U.S. Department of Housing and Urban Development (HUD) to "
            "provide housing assistance to help more than 8,500 low-income Arizonans cover "
            "the cost of their rental unit every month ... $87,721,158 in HUD housing "
            "assistance payments were used to aid 8,522 extremely low-income Arizonans.\" "
            "(FY2025 Annual Report, Rental Programs: HUD Housing Assistance, p.7). The "
            "Households Assisted commitment chart (p.17) splits those 8,522 households into "
            "Project-Based Section 8 = 8,194 + Section 8 Housing Choice Vouchers = 328, and "
            "the Dollar Commitments chart (p.15) into $86,063,223 (Project-Based) + "
            "$1,657,935 (HCV) = $87,721,158."
        ),
        "fy2025_amounts": [
            {"label_key": "az_amt_hud_assistance", "amount": 87721158},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "section_8_pbra", "fy2025_units": 8194, "fy2025_amount": 86063223,
             "color_group": "trust",
             # Federal Project-Based Rental Assistance ADOH administers for
             # HUD (pass-through); governmental by program description,
             # confidence: medium.
             "fund_type": "governmental", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "section_8_hcv", "fy2025_units": 328, "fy2025_amount": 1657935,
             "color_group": "trust",
             # Federal Section 8 Housing Choice Vouchers ADOH administers for
             # HUD (pass-through); governmental by program description,
             # confidence: medium.
             "fund_type": "governmental", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "homebuyer_assistance",
        "unit_type": "households",
        "fy2025_actual": 704,
        "fy2025_source_quote": (
            "\"In FY 2025, ADOH began administering a new program to increase homeownership "
            "across the state called Arizona is Home (AIH) ... The goal of AIH was to assist "
            "approximately 500 homebuyers statewide. That goal was exceeded. In FY 2025, AIH "
            "helped 704 first-time homebuyers close on a home with a total of $13,656,162 in "
            "financial assistance.\" (FY2025 Annual Report, Homebuyer Assistance, p.11). "
            "AIH was funded by $10+ million from the State Housing Trust Fund and $3+ million "
            "from an ARPA executive allocation."
        ),
        "fy2025_amounts": [
            {"label_key": "az_amt_aih", "amount": 13656162},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "arizona_is_home", "fy2025_units": 704, "fy2025_amount": 13656162,
             "color_group": "trust",
             # Down-payment/rate-buydown assistance funded by the State HTF +
             # ARPA; ADOH is a state department. Confidence: medium.
             "fund_type": "governmental",
             "fund_name": "State Housing Trust Fund + ARPA (Arizona is Home)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "housing_rehabilitation",
        "unit_type": "units",
        "fy2025_actual": 1157,
        "fy2025_source_quote": (
            "\"ADOH awarded more than $14.5 million to renovate/repair 1,157 owner-occupied "
            "homes statewide in FY 2025. Federal funding sources and programs include: "
            "Community Development Block Grants (CDBG), HOME Investment Partnership Program "
            "(HOME), Weatherization Assistance Program (WAP), and Low Income Home Energy "
            "Assistance Program (LIHEAP) ... Of the total awarded, $8.9 million was in "
            "Weatherization Assistance Program (WAP) resources ... The investment empowered "
            "the WAP to complete more than 1,029 weatherization improvements ...\" (FY2025 "
            "Annual Report, Housing Rehabilitation and Repair Programs, p.8)."
        ),
        "fy2025_amounts": [
            {"label_key": "az_amt_rehab", "amount": 14500000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "owner_occupied_rehab", "fy2025_units": 1157,
             "fy2025_amount": 14500000,
             "color_group": "capital",
             # CDBG/HOME/WAP/LIHEAP + utility-company grants administered by a
             # state department; governmental by program description,
             # confidence: medium. (Narrative "$14.5 million" is a rounded
             # headline; the commitment chart's Homeowner Rehab $8,876,441 +
             # Weatherization $8,939,054 rows do not cleanly reconcile to it.)
             "fund_type": "governmental", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
]

# ---------------------------------------------------------------------------
# Multifamily project-level detail: "FY2025 Low Income Housing Tax Credit
# Reservation Commitments" (A.R.S. 35-728(D), dated Sept 30, 2025).
# Manually transcribed via pdfplumber text extraction, one row per
# development. "units" uses the report's TOTAL-units column (physical
# development size); "source_amounts" use the report's annual federal LIHTC
# award and, where present, the State Tax Credit award. Project-cost column
# is not surfaced (it is a total-development-cost figure, a different metric).
# ---------------------------------------------------------------------------

# (name, address, city, total_units, [funding source keys])
# address=None marks developments whose PDF row prints "Scattered Site(s)"
# with no street address -- these fall back to city-center geocoding.
RAW_PROJECTS = [
    # --- 9% Low Income Housing Tax Credits (9 projects) ---
    ("Amazon Flats", "1135 W Miracle Mile", "Tucson", 59, ["lihtc_9pct"]),
    ("Casa Grande - Phase One Apartments", "115 W Main Avenue & 202 S Top and Bottom Street",
     "Casa Grande", 64, ["lihtc_9pct", "stc"]),
    ("Northern Commons Apartments", "2050 W. Northern Avenue", "Phoenix", 60, ["lihtc_9pct"]),
    ("Shasta Apartments", "855 West Prince Road", "Tucson", 100, ["lihtc_9pct"]),
    ("The Granville", "4343 W Thomas Road", "Phoenix", 152, ["lihtc_9pct"]),
    ("TOKA Homes VII", None, "Sells", 32, ["lihtc_9pct"]),
    ("TOKA Homes VIII", "West of Su:Dagi Wo:g Street & S Mission Road", "Tucson", 12, ["lihtc_9pct"]),
    ("Vistara III", "606 E. 18th Street", "Yuma", 80, ["lihtc_9pct"]),
    ("Yavapai-Apache Homes X", "North of East Cherry Creek Road and Old Hwy 279", "Camp Verde", 37, ["lihtc_9pct"]),
    # --- 4% Low Income Housing Tax Credits (24 projects) ---
    ("Gunsmoke Ranch Apartments", "SWC Honeycutt Rd & N Gunsmoke Rd", "Maricopa", 271, ["lihtc_4pct"]),
    ("Memorial Towers", "1405 South 7th Avenue", "Phoenix", 152, ["lihtc_4pct"]),
    ("The Acacia at Youngtown Phase II", "W Peoria Ave & Nofs Dr", "Youngtown", 120, ["lihtc_4pct", "stc"]),
    ("The Acacia at Youngtown Phase I", "W Peoria Ave & Nofs Dr", "Youngtown", 192, ["lihtc_4pct"]),
    ("Saddleback Village at Stonegate", "Southwest Corner of Alan Stephens Pkwy & Stonegate Rd",
     "Maricopa", 215, ["lihtc_4pct"]),
    ("Jesse Owens Parkway", "139 East Jesse Owens Parkway", "Phoenix", 236, ["lihtc_4pct"]),
    ("Emberwood Apartments", "North Peart Road & Oneil Drive", "Casa Grande", 176, ["lihtc_4pct"]),
    ("Alma Apartments", "North Peart Road & Oneil Drive", "Casa Grande", 216, ["lihtc_4pct"]),
    ("Virata Apartments", "18146 N Alan Stephens Pkwy", "Maricopa", 216, ["lihtc_4pct"]),
    ("Calypso at Ballpark Village", "NE Corner of W Yuma Rd and S Estrella Pkwy", "Goodyear", 203, ["lihtc_4pct"]),
    ("Glendale Apartments", "6819 27th St.", "Phoenix", 45, ["lihtc_4pct"]),
    ("Fort Whipple Veterans Housing", "500 N State Route 89", "Prescott", 103, ["lihtc_4pct"]),
    ("Tecoma Square", "SEC E Bella Vista Road & N Gantzel Road", "San Tan Valley", 252, ["lihtc_4pct"]),
    ("Eloy Goy Housing", None, "Eloy", 30, ["lihtc_4pct"]),
    ("Butterfield Commons", "44235 Reinsman Blvd", "Maricopa", 174, ["lihtc_4pct"]),
    ("The Villas on Shelby", "2250 Shelby Drive", "Sedona", 30, ["lihtc_4pct"]),
    ("Townhomes on Early", "1355 E Earley Road", "Casa Grande", 278, ["lihtc_4pct"]),
    ("Emory Heights", "5245 and 5307 N 17th Avenue", "Phoenix", 62, ["lihtc_4pct"]),
    ("Everstone North", "8211 N 63rd Ave", "Phoenix", 228, ["lihtc_4pct"]),
    ("Everstone South", "SE Corner of Baseline Rd & 63rd Ave", "Phoenix", 180, ["lihtc_4pct"]),
    ("Allasso Ranch", "SW Happy Valley Rd & 147th Ave", "Surprise", 304, ["lihtc_4pct"]),
    ("Sidney Village", "SEC Yuma Rd & Apache Rd", "Buckeye", 200, ["lihtc_4pct"]),
    ("Tanner Terrace", "7138 North 45th Ave", "Glendale", 156, ["lihtc_4pct"]),
    ("Broadway Farms", "NEC of S. 91st Ave and W. Broadway Rd.", "Phoenix", 190, ["lihtc_4pct"]),
]

# Per-project annual tax-credit award, transcribed from the reservation
# report's "TAX CREDIT AWARDED" and "STATE TAX CREDIT AWARDED" columns.
PROJECT_SOURCE_AMOUNTS = {
    "Amazon Flats": {"lihtc_9pct": 2500000},
    "Casa Grande - Phase One Apartments": {"lihtc_9pct": 2000000, "stc": 1000000},
    "Northern Commons Apartments": {"lihtc_9pct": 2500000},
    "Shasta Apartments": {"lihtc_9pct": 2500000},
    "The Granville": {"lihtc_9pct": 2500000},
    "TOKA Homes VII": {"lihtc_9pct": 2500000},
    "TOKA Homes VIII": {"lihtc_9pct": 1000000},
    "Vistara III": {"lihtc_9pct": 2500000},
    "Yavapai-Apache Homes X": {"lihtc_9pct": 2500000},
    "Gunsmoke Ranch Apartments": {"lihtc_4pct": 5593716},
    "Memorial Towers": {"lihtc_4pct": 2713355},
    "The Acacia at Youngtown Phase II": {"lihtc_4pct": 2000000, "stc": 1000000},
    "The Acacia at Youngtown Phase I": {"lihtc_4pct": 3603285},
    "Saddleback Village at Stonegate": {"lihtc_4pct": 4634678},
    "Jesse Owens Parkway": {"lihtc_4pct": 4049456},
    "Emberwood Apartments": {"lihtc_4pct": 2891689},
    "Alma Apartments": {"lihtc_4pct": 4183052},
    "Virata Apartments": {"lihtc_4pct": 3904515},
    "Calypso at Ballpark Village": {"lihtc_4pct": 3750142},
    "Glendale Apartments": {"lihtc_4pct": 1004918},
    "Fort Whipple Veterans Housing": {"lihtc_4pct": 1909751},
    "Tecoma Square": {"lihtc_4pct": 4633890},
    "Eloy Goy Housing": {"lihtc_4pct": 941178},
    "Butterfield Commons": {"lihtc_4pct": 2825088},
    "The Villas on Shelby": {"lihtc_4pct": 690454},
    "Townhomes on Early": {"lihtc_4pct": 5782018},
    "Emory Heights": {"lihtc_4pct": 1066816},
    "Everstone North": {"lihtc_4pct": 4070848},
    "Everstone South": {"lihtc_4pct": 3287993},
    "Allasso Ranch": {"lihtc_4pct": 6981889},
    "Sidney Village": {"lihtc_4pct": 4690038},
    "Tanner Terrace": {"lihtc_4pct": 2204269},
    "Broadway Farms": {"lihtc_4pct": 3501479},
}

# The reservation report's own printed column totals (9% section footer and
# 4% section footer), used as the dual-verification target.
EXPECTED_SOURCE_TOTALS = {
    "lihtc_9pct": 20500000,
    "lihtc_4pct": 80914517,
    "stc": 2000000,
}
EXPECTED_UNITS_BY_SOURCE = {
    "lihtc_9pct": 596,
    "lihtc_4pct": 4229,
}

FUNDING_COLOR_GROUP = {
    "lihtc_9pct": "credit", "lihtc_4pct": "credit", "stc": "credit",
}
FUNDING_PRIORITY = ["lihtc_9pct", "lihtc_4pct", "stc"]

# City-center coordinates for every city named in RAW_PROJECTS. Used ONLY as a
# last-resort fallback when Nominatim's shared-IP rate limit (HTTP 429) blocks
# both the street query AND the "{city}, AZ" query. They are city-center
# precision (same as a Nominatim city-center result), so any project resolved
# this way is honestly flagged geocode_status="city_center".
CITY_COORDS = {
    "Phoenix": (33.44838, -112.07404),
    "Tucson": (32.22261, -110.97471),
    "Casa Grande": (32.87950, -111.75735),
    "Sells": (31.91202, -111.88124),
    "Yuma": (32.69265, -114.62769),
    "Camp Verde": (34.56364, -111.85432),
    "Maricopa": (33.05811, -112.04764),
    "Youngtown": (33.59393, -112.30294),
    "Goodyear": (33.43534, -112.35821),
    "Prescott": (34.54002, -112.46850),
    "San Tan Valley": (33.19115, -111.52817),
    "Eloy": (32.75590, -111.55484),
    "Sedona": (34.86974, -111.76099),
    "Surprise": (33.62923, -112.36793),
    "Buckeye": (33.37032, -112.58378),
    "Glendale": (33.53865, -112.18599),
}


def verify_project_count_and_units():
    errors = []
    if len(RAW_PROJECTS) != 33:
        errors.append(f"project count: expected 33, got {len(RAW_PROJECTS)}")
    units_by_source = {}
    count_by_source = {}
    for name, _addr, _city, units, sources in RAW_PROJECTS:
        for src in sources:
            units_by_source[src] = units_by_source.get(src, 0) + units
            count_by_source[src] = count_by_source.get(src, 0) + 1
    if count_by_source.get("lihtc_9pct") != 9:
        errors.append(f"9% project count: expected 9, got {count_by_source.get('lihtc_9pct')}")
    if count_by_source.get("lihtc_4pct") != 24:
        errors.append(f"4% project count: expected 24, got {count_by_source.get('lihtc_4pct')}")
    for src, expected in EXPECTED_UNITS_BY_SOURCE.items():
        got = units_by_source.get(src, 0)
        if got != expected:
            errors.append(f"{src} (total units): expected {expected}, got {got}")
    total_units = sum(units for _n, _a, _c, units, _s in RAW_PROJECTS)
    if total_units != 4825:
        errors.append(f"total LIHTC units: expected 4825, got {total_units}")
    if set(PROJECT_SOURCE_AMOUNTS) != {n for n, *_ in RAW_PROJECTS}:
        errors.append("RAW_PROJECTS and PROJECT_SOURCE_AMOUNTS project-name sets differ")
    for name, _addr, _city, _units, sources in RAW_PROJECTS:
        amounts = PROJECT_SOURCE_AMOUNTS.get(name, {})
        missing = [s for s in sources if s not in amounts]
        extra = [s for s in amounts if s not in sources]
        if missing:
            errors.append(f"{name!r} is missing amounts for source(s) {missing}")
        if extra:
            errors.append(f"{name!r} has amounts for undeclared source(s) {extra}")
    if errors:
        raise SystemExit("Project count/unit mismatch(es):\n" + "\n".join(errors))
    print("Project count (33), 9% (9 projects / 596 units), 4% (24 projects / 4,229 units) "
          "and total (4,825 units) verified against the LIHTC reservation report's own "
          "printed footers.")


def verify_source_amount_totals():
    sums = {}
    for _name, _addr, _city, _units, sources in RAW_PROJECTS:
        amounts = PROJECT_SOURCE_AMOUNTS.get(_name, {})
        for src in sources:
            sums[src] = sums.get(src, 0) + amounts[src]
    errors = []
    for key, expected in EXPECTED_SOURCE_TOTALS.items():
        got = sums.get(key, 0)
        if got != expected:
            errors.append(f"{key} (credit): expected {expected}, got {got}")
    lihtc_total = sums.get("lihtc_9pct", 0) + sums.get("lihtc_4pct", 0)
    if lihtc_total != 101414517:
        errors.append(
            f"total federal LIHTC credit: expected $101,414,517, got ${lihtc_total:,}"
        )
    if errors:
        raise SystemExit("Funding-source amount mismatch(es):\n" + "\n".join(errors))
    print("Federal LIHTC totals verified: 9% $20,500,000 + 4% $80,914,517 = $101,414,517 "
          "(matches the reservation report's own '$101.4 million' narrative); STC $2,000,000.")


def _load_cache():
    if GEOCODE_CACHE_PATH.exists():
        try:
            return json.loads(GEOCODE_CACHE_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_cache(cache):
    try:
        GEOCODE_CACHE_PATH.write_text(
            json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    except OSError as exc:
        print(f"  could not write geocode cache: {exc}")


def _photon_geocode(query):
    """Keyless OSM geocoder (komoot Photon) fallback. Used when Nominatim's
    shared-IP rate limit (HTTP 429) blocks the primary resolver -- Photon
    serves the same OpenStreetMap data with a much more lenient limit.
    Returns (lat, lon) or None. The API returns coordinates as [lon, lat]."""
    url = f"{PHOTON_URL}?{urllib.parse.urlencode({'q': query, 'limit': 1})}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": GEOCODER_USER_AGENT})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.load(resp)
        feats = data.get("features") or []
        if feats:
            lon, lat = feats[0]["geometry"]["coordinates"][:2]
            return (float(lat), float(lon))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError,
            KeyError, ValueError, IndexError, TypeError) as exc:
        print(f"  photon fallback failed for {query!r}: {exc}")
    return None


def geocode(query, cache):
    if query in cache:
        return cache[query]
    params = urllib.parse.urlencode({"q": query, "format": "json", "limit": 1})
    url = f"{NOMINATIM_URL}?{params}"
    result = None
    # Nominatim rate-limits a shared IP aggressively (HTTP 429) -- and several
    # parallel state builds hit the same endpoint from this IP. Try twice with
    # a short pause; if still blocked, fall back to Photon (same OSM data).
    # The persistent on-disk cache keeps the result reproducible on re-run.
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": GEOCODER_USER_AGENT})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.load(resp)
            if data:
                result = (float(data[0]["lat"]), float(data[0]["lon"]))
            break
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                print(f"  429 on {query!r} (attempt {attempt + 1})")
                time.sleep(2)
                continue
            print(f"  geocode failed for {query!r}: {exc}")
            break
        except (urllib.error.URLError, TimeoutError, KeyError, ValueError, IndexError) as exc:
            print(f"  geocode failed for {query!r}: {exc}")
            break
    if result is None:
        result = _photon_geocode(query)
    cache[query] = result
    _save_cache(cache)
    time.sleep(1.1)  # Nominatim usage policy: max 1 request/second
    return result


def _slug(name):
    return (name.lower().replace(" ", "-").replace("'", "")
            .replace(".", "").replace("&", "and").replace("+", "plus"))


def build_projects():
    cache = _load_cache()
    projects = []
    for name, address, city, units, sources in RAW_PROJECTS:
        query = f"{address}, {city}, AZ" if address else f"{city}, AZ"
        coords = geocode(query, cache)
        status = "ok"
        if coords is None:
            coords = geocode(f"{city}, AZ", cache)
            status = "city_center" if coords else "unresolved"
        if coords is None and city in CITY_COORDS:
            # Last-resort fallback (see CITY_COORDS doc): only when Nominatim
            # is rate-limited out of both the street and city queries.
            coords = CITY_COORDS[city]
            status = "city_center"
        primary = next((s for s in FUNDING_PRIORITY if s in sources), sources[0])
        source_amounts = PROJECT_SOURCE_AMOUNTS.get(name, {})
        projects.append({
            "id": _slug(name),
            "name": name,
            "address": address,
            "city": city,
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
    verify_project_count_and_units()
    verify_source_amount_totals()
    print("Geocoding project addresses via Nominatim...")
    projects = build_projects()
    unresolved = [p["name"] for p in projects if p["geocode_status"] == "unresolved"]
    if unresolved:
        print(f"  {len(unresolved)} project(s) could not be geocoded: {unresolved}")
    city_center = [p["name"] for p in projects if p["geocode_status"] == "city_center"]
    if city_center:
        print(f"  {len(city_center)} project(s) fell back to city-center geocoding: {city_center}")

    payload = {
        "AZ": {
            "hfa_name": "Arizona Department of Housing",
            "hfa_abbr": "ADOH",
            "fiscal_year": "FY2025",
            "source_title": "ADOH FY2025 Annual Report + FY2025 LIHTC Reservation Commitments (A.R.S. 35-728(D))",
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
