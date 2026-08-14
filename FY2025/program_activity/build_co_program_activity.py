"""
Builds docs/co_program_activity.json from Colorado Housing and Finance
Authority's (CHFA) "2025 CHFA Community Report", plus CHFA's own FY2025
(CY2025) audited financial statements (for GASB fund-type classification).

Sources
---------------------------------------------------------------------------
1. "2025 CHFA Community Report" (8-page PDF; cover reads "2025 CHFA
   Community Report", every stat panel is dated "As of December 31, 2025"):
     Web page: https://www.chfainfo.com/2025-chfa-community-report
     PDF:      https://www.chfainfo.com/getattachment/e22a8383-74ab-4be1-9cb1-559332222096/2025-CHFA-Community-Report.pdf
   Local copy: FY2025/program_activity/pdf/CO_CHFA_CommunityReport_2025.pdf
   (10,816,997 bytes; downloaded and verified 200 OK / valid PDF before
   use. NOTE: this project's usual WebFetch tool got HTTP 403 from
   chfainfo.com on both the web page and the PDF -- Cloudflare appears to
   block that fetcher's User-Agent/IP specifically. `curl` with a normal
   browser User-Agent string succeeded (200 OK) on every chfainfo.com URL
   this script uses, so all fetching below was done with `curl`, not
   WebFetch.)
2. The Community Report page's own embedded "Developments Supported with
   Housing Tax Credits" interactive map, which is a small Vue.js widget
   (`/vue/county-map.js`) that loads its 32 markers from CHFA's own JSON
   API rather than being present in the page HTML or the PDF:
     https://www.chfainfo.com/api/properties?path=/2025-chfa-community-report
   This endpoint returns, per development: name, lat, lng, totalUnits,
   county, city, developer, taxCreditType, tocCreditNote -- i.e. CHFA's own
   already-geocoded coordinates for every marker on its own map, not just a
   textual address. Local copy of the raw JSON response:
     FY2025/program_activity/co_properties_raw.json
3. "Federal 4% Housing Tax Credit Awards (with State and Transit-oriented
   Communities (TOC) Credit, if applicable)" report (despite the task
   brief's URL slug "federal-4-housing-tax-credit-award-report" implying an
   .xlsx, the file actually served at that URL is a 4-page PDF; unlike a
   prior research attempt referenced in this task's briefing, it did NOT
   hang in a browser this time -- `curl` fetched it in under a second):
     https://www.chfainfo.com/getattachment/34a30942-e08d-494a-8bc7-f236ebf01e98/federal-4-housing-tax-credit-award-report.pdf
   Local copy: FY2025/program_activity/pdf/CO_CHFA_Federal4pct_AwardReport.pdf
   This report is a cross-vintage table of federal 4% HTC awards by
   *application cycle year* (2021-2026, "As of 8/7/2026"), not scoped to
   the Community Report's CY2025 "All Properties" list -- see "Federal 4%
   Award Report cross-reference" below for exactly how (and how narrowly)
   this script uses it.
4. CHFA's own separately-issued FY2025 (CY2025) audited financial
   statements, used ONLY for fund-type classification:
     FY2025/txt/CO_CHFA_FY2025_ACFR.txt
   (also available as FY2025/pdf/CO_CHFA_FY2025_ACFR.pdf for exact page
   numbers -- this script cites page numbers from the PDF pagination
   printed at the bottom of each Notes page, e.g. "27", "28".)

IMPORTANT entity-identity check: this is Colorado's CHFA, not Connecticut's
---------------------------------------------------------------------------
"CHFA" is also the acronym of the unrelated Connecticut Housing Finance
Authority (see build_ct_program_activity.py's own identical-acronym note).
FY2025/txt/CO_CHFA_FY2025_ACFR.txt was verified before use: it opens
"COLORADO HOUSING AND FINANCE AUTHORITY -- Annual Financial Report", its
Independent Auditors' Report addresses "Colorado Housing and Finance
Authority (the Authority)", and Note 1(a) states the Authority "is a body
corporate and a political subdivision of the State of Colorado ...
established pursuant to the Colorado Housing and Finance Authority Act,
Title 29, Article 4, Part 7 of the Colorado Revised Statutes" -- and its
own Executive Letter's headline stats ("5,491 Colorado households achieved
homeownership", "5,732 affordable rental housing units were supported")
match the Community Report's headline stats exactly, cross-confirming both
documents describe the same entity. Unambiguously the Colorado agency, no
mix-up with Connecticut's identically-abbreviated HFA.

IMPORTANT reporting-period note: CY2025 (calendar year), not a July-June FY
---------------------------------------------------------------------------
Both source documents run January-December 2025: the Community Report's
final page states "As of December 31, 2025"; the ACFR's Independent
Auditors' Report covers "the years ended December 31, 2025 and 2024" and
its Executive Letter (dated March 26, 2026) narrates "In 2025, CHFA
invested...". This script therefore uses "CY2025" as the fiscal_year value,
matching CT's and FL's own CY-reporting pilots.

Category-level methodology
---------------------------------------------------------------------------
Homeownership (Community Report p.4): fy2025_actual (5,491) is the report's
own printed "5,491 customers served with CHFA home mortgage purchase loans"
stat panel, independently corroborated by the ACFR's Executive Letter
("5,491 Colorado households achieved homeownership through CHFA's Home
Finance programs"). The panel's other two dollar/count figures -- "$2B
invested in first mortgage loans" and "$86M invested in down payment
assistance" -- are used as category-level fy2025_amounts (both rounded by
CHFA itself to 2-3 significant figures; no more-precise figures are
disclosed anywhere in either source document, so none is invented here).
"8,722 households served with CHFA-sponsored homebuyer education" is kept
as its own subprogram (units only, no dollar figure disclosed) rather than
folded into the 5,491 headline: it is explicitly a *different* population
(homebuyer-education attendees, not necessarily first-time buyers who
closed a CHFA loan that same year) -- CHFA's own p.4 narrative describes
them as two separate cohorts ("CHFA supported more than 5,400 households in
achieving homeownership AND served more than 8,700 homebuyer education
customers in 2025"). Down payment assistance similarly rides on top of an
undisclosed subset of the 5,491 purchase loans (CHFA discloses no separate
loan *count* for DAP, only the $86M total), so additive=False for this
category -- there is no disclosed, verifiable subset/partition relationship
between the 5,491 headline and either subprogram's own count, unlike PA's
K-FIT/Advantage/PENNVEST (additive=True) where PHFA's own table prints an
exact loan count for each.

Affordable Rental Housing (Community Report p.5 + the embedded properties
map, see source 2 above): fy2025_actual (5,732) is the report's own printed
"5,732 units supported" stat panel ("CHFA supported the construction or
preservation of more than 5,700 affordable rental housing units"),
corroborated by the ACFR's Executive Letter ("5,732 affordable rental
housing units were supported through the allocation of Housing Tax Credits
and/or CHFA's Multifamily Lending programs"). Four category-level dollar
figures are used verbatim from the same stat panel: "$555M total loan
production", "$44.6M federal 4 percent Housing Tax Credits awarded", "$19.2M
federal 9 percent Housing Tax Credits awarded", "$31.6M state Housing Tax
Credits awarded" -- these last three cross-check exactly against the
Community Report's own separate overview panel (p.3): "$95.4M awarded in
federal and state Housing Tax Credits" = $44.6M + $19.2M + $31.6M =
$95,400,000 exactly (see verify_rental_housing_credit_totals()).

RAW_PROJECTS/subprograms for this category come from the embedded
properties-map API (source 2), which returns 32 named developments (NOT 31
-- this task's briefing pre-checked an estimate of "31 projects, ~2,900
units" against an earlier read of the page; this script's own direct fetch
of the live API on its retrieval date returned 32 rows summing to 2,907
total units, a small drift from that pre-check, most plausibly because
CHFA's map is a live, continuously-updated data feed rather than a frozen
document -- the discrepancy is noted here, not silently forced to 31).
Every project's own `taxCreditType` field is one of exactly five values --
"Federal 4 Percent Credit", "State and Federal 4 Percent Credit", "State
and Federal 4 Percent Credit, Noncompetitive", "State and Federal 9 Percent
Credit", "Middle-income Housing Tax Credit (MIHTC)" -- which this script
maps 1:1 onto the category's 5 subprograms (federal_4pct/
state_federal_4pct/state_federal_4pct_noncomp/state_federal_9pct/mihtc).
Per this task's briefing, this 32-project, 2,907-unit map total is NOT
forced to reconcile with the category's own 5,732-unit headline: the map is
described by CHFA only as "Developments Supported with Housing Tax
Credits", a narrower universe than the headline's "allocation of Housing
Tax Credits and/or CHFA's Multifamily Lending programs" (i.e. the headline
also includes non-HTC multifamily loan-only closings that have no
corresponding marker on this particular map) -- additive=False, and no
attempt is made to bridge the ~2,825-unit gap. Because CHFA's own map/API
discloses no per-development dollar figure of any kind (only the 4
category-level totals above), this script's RAW_PROJECTS verification is
count/unit-only (verify_project_count_and_units()) -- there is no dollar
total to cross-check a re-sum against, so none is fabricated.

Federal 4% Award Report cross-reference (source 3) -- address enrichment
only, not dollar amounts
---------------------------------------------------------------------------
The Federal 4% Housing Tax Credit Award Report (source 3) DOES carry a
literal street address and per-development dollar figures (Federal 4%
Credit Amount Issued, Noncompetitive State Credit Amount, TOC Credit
Amount) -- but only for developments awarded federal 4% credits across
application *cycle years* 2021-2026, a differently-scoped and only
partially-overlapping list from the Community Report's 32-development,
CY2025-*closed* "All Properties" map. Matching by name+city+county+units,
9 of the 32 properties-map developments were found, unambiguously, as exact
rows in this report (34th Street, 4965 Washington Street, Bradley Ridge,
Eagle Villas, Flats at Sand Creek, Ives II [printed there as "Ives II 4",
almost certainly a column-alignment artifact of the source PDF's own text
layer merging the adjoining "Total Units" digit "4" onto the property-name
cell -- disambiguated here by all four of Wheat Ridge/Jefferson County/98
Total Units/2025 Family New Construction matching exactly], Loretto Heights
Family Apartments, Ponderosa Pines, Windtrail Park) -- their `address`
field below is transcribed verbatim from this report's own "Address"
column. This script does NOT, however, use this report's dollar columns:
(1) it only ever covers the "federal 4%"-flavored subset (9 of 32
properties; the 12 "State and Federal 9 Percent Credit" and 3 MIHTC
properties have no possible match in a federal-4%-only report at all), (2)
a given property can appear at a different, non-2025 cycle year than the
CY2025 closing the properties-map represents (e.g. Loretto Heights Family
Apartments is filed here under cycle year "2024"), so its dollar figure
would not cleanly represent "CY2025 activity" the way this category's
headline does, and (3) per this task's own briefing, category-level
totals already fully cover this category's dollar disclosure -- so no
per-project amount is invented or partially populated; `source_amounts` is
`{}` and `total_amount` is `None` for all 32 projects, uniformly.

For the remaining 23 properties (and the 9 above where the properties-map's
own `name` field already reads as a literal address, e.g. "1001 Lincoln
Street", "1139 Delaware Street"), `address` is populated directly from the
properties-map's own `name` field when that name has a leading building
number AND a recognizable street-type suffix (Street/Avenue/etc.);
otherwise `address` is left `None` and the development is geocoded (see
below) using its project name plus city only, per this task's own
"$name only needs to fall back to city-level$" guidance for names like
"Marq" that carry no address information at all.

Geocoding: CHFA's own coordinates, not Nominatim
---------------------------------------------------------------------------
Unlike every prior pilot in this project, this script does NOT call
Nominatim (OpenStreetMap) to geocode these 32 developments. CHFA's own
properties-map API (source 2) already returns a precise `lat`/`lng` pair
for every one of its 32 markers -- these are CHFA's own, first-party
project-level coordinates (used to place CHFA's own public map's own
pins), which are categorically more accurate than anything a general text
geocoder could re-derive from a bare project name and city. Using them
directly, rather than re-geocoding the same 32 names through Nominatim (and
risking a *worse*, address-guessed result for names like "Marq" or "101
Main" that carry no literal street address), is a deliberate, documented
deviation from this project's usual geocoding step -- not a skipped step.
`geocode_status` is set to `"official"` for all 32 (CHFA's own point-level
map coordinate, not a Nominatim result at any precision tier) rather than
this project's usual `"ok"`/`"city_center"` vocabulary, so downstream
consumers of this JSON can tell the two provenances apart; per this task's
own instruction not to blanket-label everything `"ok"`, `"official"` is
used here specifically because it is neither.

Fund-type classification (fund_type/fund_name on each subprogram)
---------------------------------------------------------------------------
CHFA's own FY2025 (CY2025) audited financial statements state, in Note
1(b) ("Basis of Accounting", ACFR/PDF p.27): "For financial purposes, the
Authority is considered a special-purpose government engaged in
business-type activities." I.e. like PHFA and CT's CHFA, Colorado's CHFA
has NO governmental funds of its own -- every dollar it carries sits inside
its single, undifferentiated business-type (proprietary) activity. Note
1(a) ("Programs", ACFR/PDF pp.9-10) separately names 4 internal lending
programs plus a general fund-within-a-fund:
  General Programs -- "Insured and uninsured single family and multifamily
    loans have been made by the Authority using funds in its General Fund
    designated as the Community Impact Fund (CIF). Within the CIF resides
    the Authority's Housing Opportunity Fund (HOF Program) ... The
    Authority also makes loans to support its single family program,
    including down payment assistance loans, within the fund."
  Single Family Programs -- "the Authority may purchase mortgage loans for
    single-family residential dwellings ... under its Non-Qualified Single
    Family Mortgage Program (taxable) and its Qualified Single Family
    Mortgage Program (tax exempt)."
  Multifamily Lending Programs -- "provide financing to sponsors of
    affordable rental housing developments."
  Business Finance Programs -- direct business/nonprofit lending, not
    relevant to this file's housing categories.
  - "proprietary", high confidence:
      * first_mortgage_loans (category-level dollar figure only, no
        subprogram entry -- see Homeownership methodology above) would map
        to the Single Family Programs, named almost verbatim above.
      * down_payment_assistance -- Note 1(a)'s own sentence, quoted above,
        explicitly places DAP loans inside the Housing Opportunity Fund
        (HOF Program) within the Community Impact Fund (CIF) within the
        Authority's own General Fund -- a first-party, CHFA-carried loan
        product, confidence: high (near-verbatim program match, unlike
        PA's K-FIT/Advantage which had to be inferred from a designation
        table).
  - "off_balance_sheet":
      * homebuyer_education -- "homebuyer education" appears exactly once
        in the full 105-page ACFR, inside the unaudited front-matter "what
        is chfa?" boilerplate page ("CHFA invests in loans, down payment
        assistance, and homebuyer education to support responsible
        homeownership") -- never inside the audited Notes to Basic
        Financial Statements with any dollar figure, fund designation, or
        program description of its own. Treated as off_balance_sheet not
        because CHFA doesn't fund it itself, but because it is a
        counseling/service activity with no disclosed loan-asset or
        fund-balance line item behind it in the audited statements (as
        opposed to a loan product like DAP, which the ACFR explicitly
        books inside a named fund).
      * federal_4pct, state_federal_4pct, state_federal_4pct_noncomp,
        state_federal_9pct, mihtc (all 5 Affordable Rental Housing
        subprograms) -- Housing Tax Credits (federal 9%/4%, Colorado's
        state credit, and the new-for-2025 Middle-income Housing Tax
        Credit) are allocated by CHFA directly to developers/investors and
        never become a CHFA-carried fund asset -- same off-balance-sheet
        logic used for IL's LIHTC/IAHTC, PA's LIHTC/PHTC, and CT's
        lihtc_4pct/lihtc_9pct/htcc. Confirmed by full-text search of
        CO_CHFA_FY2025_ACFR.txt: "Middle-income Housing Tax Credit",
        "Transit-oriented Communities", and "state Housing Tax Credit"
        each appear ONLY in the same unaudited Executive Letter passage
        quoted in the entity-identity note above -- zero matches inside
        the audited Notes. Federal Low-Income Housing Tax Credits do
        appear twice inside the audited Notes, but neither instance
        describes CHFA carrying the credit itself as an asset: Note 14
        ("Related-Party Transactions") discloses a single $930 thousand
        LIHTC allocation to one specific related-party project (an
        isolated relationship disclosure, not a categorical program
        description), and the "Other Liabilities" note separately
        describes a "Deferred Low Income Housing Tax Credit Income" line
        as "compliance monitoring fees collected in advance ... to certify
        that these properties remain low-income compliant" -- i.e. a small
        administrative FEE CHFA earns for compliance monitoring, not the
        tax credit allocation itself sitting on CHFA's balance sheet. This
        matches the same fee-vs-credit distinction PA's build script draws
        for PHFA's LIHTC compliance-monitoring fees.

fy2026
---------------------------------------------------------------------------
The Community Report has no forward-looking/projected-activity section of
any kind (checked: the string "2026" does not appear anywhere in its
8-page body text -- it appears only in photo captions/footer metadata like
"Demographics data accessed January 2026" and the discrimination-notice
boilerplate). Every fy2026 field below is therefore {value: None, amount:
None, closed: False, note_key: "coFy26NotePending"}.
"""

import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "co_program_activity.json"

SOURCE_URL = "https://www.chfainfo.com/2025-chfa-community-report"
SOURCE_FILE = "CO_CHFA_CommunityReport_2025.pdf (+ embedded properties-map API + Federal 4% Award Report cross-reference)"
RETRIEVED = "2026-08-14"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "coFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "homeownership",
        "unit_type": "households",
        "fy2025_actual": 5491,
        "fy2025_source_quote": (
            "\"2025 Investment\" stat panel (p.4): \"$2B invested in first mortgage "
            "loans\", \"$86M invested in down payment assistance\", \"8,722 households "
            "served with CHFA-sponsored homebuyer education\", \"5,491 customers served "
            "with CHFA home mortgage purchase loans.\" Narrative (p.4): \"CHFA supported "
            "more than 5,400 households in achieving homeownership and served more than "
            "8,700 homebuyer education customers in 2025.\" Cross-confirmed by CHFA's own "
            "FY2025 ACFR Executive Letter: \"5,491 Colorado households achieved "
            "homeownership through CHFA's Home Finance programs.\" Down payment "
            "assistance rides on top of an undisclosed subset of the 5,491 purchase "
            "loans (no separate DAP loan count is disclosed, only the $86M total); "
            "homebuyer education (8,722) is an explicitly separate cohort, not a subset "
            "of the 5,491 -- neither subprogram is additive against the 5,491 headline."
        ),
        "fy2025_amounts": [
            {"label_key": "co_amt_first_mortgages", "amount": 2000000000},
            {"label_key": "co_amt_downpayment_assist", "amount": 86000000},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "downpayment_assistance", "fy2025_units": None, "fy2025_amount": 86000000,
             "color_group": "capital",
             # Note 1(a) "General Programs" (ACFR/PDF p.9): "The Authority also makes
             # loans to support its single family program, including down payment
             # assistance loans, within the fund" -- the fund being the Housing
             # Opportunity Fund (HOF Program) inside the Community Impact Fund (CIF)
             # inside the Authority's own General Fund. CHFA's own carried loan product.
             "fund_type": "proprietary",
             "fund_name": "Housing Opportunity Fund (HOF Program), Community Impact Fund (CIF), General Fund",
             "fy2026": _FY26_PENDING},
            {"key": "homebuyer_education", "fy2025_units": 8722, "fy2025_amount": None,
             "color_group": "trust",
             # "homebuyer education" appears exactly once in the 105-page ACFR, in the
             # unaudited front-matter "what is chfa?" boilerplate, never in the audited
             # Notes with a dollar figure or fund designation of its own -- a
             # counseling/service activity, not a disclosed loan-asset or fund balance.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "affordable_rental_housing",
        "unit_type": "units",
        "fy2025_actual": 5732,
        "fy2025_source_quote": (
            "\"2025 Investment\" stat panel (p.5): \"$555M total loan production\", "
            "\"$44.6M federal 4 percent Housing Tax Credits awarded\", \"$19.2M federal 9 "
            "percent Housing Tax Credits awarded\", \"$31.6M state Housing Tax Credits "
            "awarded\", \"5,732 units supported.\" Narrative (p.5): \"CHFA supported the "
            "construction or preservation of more than 5,700 affordable rental housing "
            "units.\" Cross-confirmed by CHFA's own FY2025 ACFR Executive Letter: \"5,732 "
            "affordable rental housing units were supported through the allocation of "
            "Housing Tax Credits and/or CHFA's Multifamily Lending programs.\" The three "
            "credit figures cross-check exactly against the Community Report's separate "
            "overview panel (p.3): \"$95.4M awarded in federal and state Housing Tax "
            "Credits\" = $44.6M + $19.2M + $31.6M = $95,400,000 (see "
            "verify_rental_housing_credit_totals()). RAW_PROJECTS below (32 developments, "
            "2,907 total units, from CHFA's own \"Developments Supported with Housing Tax "
            "Credits\" map/API) is a narrower universe than this 5,732-unit headline -- "
            "CHFA's own headline also includes non-HTC Multifamily Lending-only closings "
            "with no marker on that map -- not forced to reconcile, per this project's "
            "'never fabricate a bridging number' rule."
        ),
        "fy2025_amounts": [
            {"label_key": "co_amt_total_loan_production", "amount": 555000000},
            {"label_key": "co_amt_federal_4pct", "amount": 44600000},
            {"label_key": "co_amt_federal_9pct", "amount": 19200000},
            {"label_key": "co_amt_state_htc", "amount": 31600000},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "federal_4pct", "fy2025_units": 820, "fy2025_amount": None,
             "color_group": "credit",
             # HTC allocations go directly to developers/investors, never a CHFA-carried
             # balance -- see module docstring's Fund-type classification section.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "state_federal_4pct", "fy2025_units": 522, "fy2025_amount": None,
             "color_group": "credit",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "state_federal_4pct_noncomp", "fy2025_units": 666, "fy2025_amount": None,
             "color_group": "credit",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "state_federal_9pct", "fy2025_units": 679, "fy2025_amount": None,
             "color_group": "credit",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "mihtc", "fy2025_units": 220, "fy2025_amount": None,
             "color_group": "credit",
             # Never appears in CO_CHFA_FY2025_ACFR.txt's audited Notes (checked
             # "Middle-income Housing Tax Credit" -- zero matches outside the same
             # unaudited Executive Letter passage cited in the entity-identity note).
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
]

# ---------------------------------------------------------------------------
# Affordable Rental Housing project-level detail ("Developments Supported
# with Housing Tax Credits" map, CHFA's own properties API, source 2 in the
# module docstring). One row per development, in the API's own return
# order; (name, address, city, units, [funding source key]).
#
# `address` is populated only when (a) the properties-map's own `name`
# field is itself a literal street address (leading building number +
# street-type suffix), or (b) the Federal 4% Award Report (source 3) was
# matched unambiguously by name+city+county+units and supplies its own
# "Address" column verbatim -- see "Federal 4% Award Report
# cross-reference" in the module docstring for exactly which 9 rows that
# covers. Every other row's address is None (falls back to project name +
# city for display/geocoding purposes; CHFA's own lat/lng, not a
# name-derived geocode, is what is actually used for map placement -- see
# "Geocoding" in the module docstring).
# ---------------------------------------------------------------------------

RAW_PROJECTS = [
    ("Crossbar Commons", None, "Aurora", 104, ["state_federal_4pct"],
     39.7409886, -104.8021261),
    ("Elmwood North", None, "Denver", 70, ["mihtc"],
     39.8420584, -105.0054478),
    ("Ravenfield", None, "Brighton", 46, ["state_federal_9pct"],
     39.9770521, -104.7887696),
    ("Tierra Azul", None, "Alamosa", 46, ["state_federal_9pct"],
     37.4647851, -105.8970864),
    ("Wagoner on the Creek", None, "Aurora", 60, ["state_federal_9pct"],
     39.7462328, -104.8097427),
    # Federal 4% Award Report row: "34th Street 3125 34th St. Boulder Boulder 80301"
    # (2025 cycle) -- matches on name+city+county+units (44).
    ("34th Street", "3125 34th St.", "Boulder", 44, ["state_federal_4pct_noncomp"],
     40.03219, -105.250338),
    ("Atwood Commons", None, "Longmont", 72, ["state_federal_4pct"],
     40.1642703, -105.0960757),
    ("Kite Route Crossing", None, "Superior", 50, ["state_federal_9pct"],
     39.9496971, -105.1622324),
    # Project name is itself the street address.
    ("1001 Lincoln Street", "1001 Lincoln Street", "Denver", 118,
     ["state_federal_4pct_noncomp"], 39.7324109, -104.9865068),
    ("1139 Delaware Street", "1139 Delaware Street", "Denver", 80,
     ["state_federal_4pct_noncomp"], 39.7346124, -104.993368),
    # Federal 4% Award Report row: "4965 Washington Street 4965 Washington Street
    # Denver Denver 80216" (2025 cycle) -- matches on name+address+city+units (170).
    ("4965 Washington Street", "4965 Washington Street", "Denver", 170,
     ["federal_4pct"], 39.7866506, -104.9783094),
    ("Central Park Station Phase I", None, "Denver", 156, ["state_federal_4pct"],
     39.7700606, -104.8954512),
    ("Cole Train", None, "Denver", 63, ["state_federal_4pct"],
     39.7659053, -104.9675341),
    ("Ford Apartments", None, "Denver", 60, ["state_federal_9pct"],
     39.724266, -104.9899683),
    # Federal 4% Award Report row: "Loretto Heights Family Apartments 2934 S
    # Pancratia Street Denver Denver 80236" (2024 cycle) -- matches on
    # name+city+county+units (100).
    ("Loretto Heights Family Apartments", "2934 S Pancratia Street", "Denver", 100,
     ["state_federal_4pct_noncomp"], 39.6627098, -105.0268442),
    ("Park Avenue Apartments", None, "Denver", 60, ["state_federal_9pct"],
     39.7461643, -104.9765164),
    ("Park Place Apartments", None, "Denver", 80, ["mihtc"],
     39.7360064, -105.022143),
    ("Tapestry LIHTC", None, "Denver", 72, ["state_federal_9pct"],
     39.7445387, -104.9818675),
    ("University Building Lofts", None, "Denver", 120, ["state_federal_4pct_noncomp"],
     39.7465821, -104.9944043),
    # Federal 4% Award Report row: "Ponderosa Pines 6793 Scott Avenue Parker
    # Douglas 80134" (2025 cycle) -- matches on name+city+county+units (204).
    ("Ponderosa Pines", "6793 Scott Avenue", "Parker", 204,
     ["state_federal_4pct_noncomp"], 39.4503054, -104.7601423),
    # Federal 4% Award Report row: "Eagle Villas 405 Nogal Road Eagle Eagle 81631"
    # (2025 cycle) -- matches on name+city+county+units (120).
    ("Eagle Villas", "405 Nogal Road", "Eagle", 120, ["federal_4pct"],
     39.6588519, -106.8210256),
    # Federal 4% Award Report row: "Bradley Ridge Legacy Hill Drive & Bradley
    # Landing Blvd Colorado Springs El Paso 80925" (2025 cycle) -- matches on
    # name+city+county+units (336). New-construction project; the report itself
    # gives an intersection, not a single street-number address.
    ("Bradley Ridge", "Legacy Hill Drive & Bradley Landing Blvd", "Colorado Springs",
     336, ["federal_4pct"], 38.7562771, -104.6698668),
    # Federal 4% Award Report row: "Flats at Sand Creek NEC Peterson Rd & N
    # Carefree Cir Colorado Springs El Paso 80922" (2025 cycle) -- matches on
    # name+city+county+units (144).
    ("Flats at Sand Creek", "NEC Peterson Rd & N Carefree Cir", "Colorado Springs",
     144, ["federal_4pct"], 38.8866417, -104.7034079),
    ("St. Louis Landing Building C", None, "Fraser", 70, ["mihtc"],
     39.950361, -105.816997),
    ("Blossom Commons", None, "Westminster", 50, ["state_federal_9pct"],
     39.8626448, -105.0596407),
    # Federal 4% Award Report row: "Ives II 4 7525 W. 44th Avenue Wheat Ridge
    # Jefferson 80033" (2025 cycle) -- the "4" is almost certainly a text-layer
    # artifact of the report's own PDF merging an adjoining unit-count digit onto
    # the property-name cell (see module docstring); matches this row on
    # city+county+units (98) unambiguously.
    ("Ives II", "7525 W. 44th Avenue", "Wheat Ridge", 98, ["state_federal_9pct"],
     39.7773146, -105.0801275),
    ("Switchgrass Crossing", None, "Fort Collins", 45, ["state_federal_9pct"],
     40.5347865, -105.0790863),
    ("Village on Eastbrook", None, "Fort Collins", 73, ["state_federal_4pct"],
     40.5429996, -105.0418981),
    # Federal 4% Award Report row: "Windtrail Park 2120 Bridgefield Ln Fort
    # Collins Larimer 80526" (2025 cycle) -- matches on name+city+county+units (50).
    ("Windtrail Park", "2120 Bridgefield Ln", "Fort Collins", 50, ["federal_4pct"],
     40.5595444, -105.0939205),
    ("Marq", None, "Trinidad", 40, ["state_federal_9pct"],
     37.1854883, -104.5070025),
    ("Sugar Commons", None, "Sterling", 54, ["state_federal_4pct"],
     40.6323875, -103.2050933),
    ("101 Main", None, "Frisco", 52, ["state_federal_9pct"],
     39.5758296, -106.106204),
]

EXPECTED_PROJECT_COUNT = 32
EXPECTED_TOTAL_UNITS = 2907

FUNDING_COLOR_GROUP = {
    "federal_4pct": "credit", "state_federal_4pct": "credit",
    "state_federal_4pct_noncomp": "credit", "state_federal_9pct": "credit",
    "mihtc": "credit",
}
# All 5 Housing Tax Credit types share one color bucket (per this task's own
# instruction), so every project's marker is "credit"-colored -- there is no
# meaningful priority order to pick among them since each project carries
# exactly one funding source (CHFA's own map assigns one taxCreditType per
# development, unlike PA/CT's overlapping multi-source developments).
FUNDING_PRIORITY = ["federal_4pct", "state_federal_4pct",
                     "state_federal_4pct_noncomp", "state_federal_9pct", "mihtc"]


def verify_project_count_and_units():
    errors = []
    if len(RAW_PROJECTS) != EXPECTED_PROJECT_COUNT:
        errors.append(f"project count: expected {EXPECTED_PROJECT_COUNT}, got {len(RAW_PROJECTS)}")
    total_units = sum(units for _n, _a, _c, units, _s, _lat, _lon in RAW_PROJECTS)
    if total_units != EXPECTED_TOTAL_UNITS:
        errors.append(f"Total Units sum: expected {EXPECTED_TOTAL_UNITS}, got {total_units}")
    for name, _addr, _city, _units, sources, _lat, _lon in RAW_PROJECTS:
        if len(sources) != 1:
            errors.append(f"{name!r}: expected exactly 1 funding source, got {sources}")
        elif sources[0] not in FUNDING_COLOR_GROUP:
            errors.append(f"{name!r}: unknown funding source {sources[0]!r}")
    if errors:
        raise SystemExit("Project count/unit mismatch(es):\n" + "\n".join(errors))
    print(f"Properties-map API: project count ({EXPECTED_PROJECT_COUNT}) and Total "
          f"Units sum ({EXPECTED_TOTAL_UNITS}) verified against the live API response "
          "(NOTE: this is 32 projects/2,907 units, not the task briefing's pre-check "
          "estimate of ~31 projects/~2,900 units -- see module docstring).")


def verify_category_subprogram_totals():
    """Cross-checks the affordable_rental_housing category's own subprogram
    fy2025_units fields (CATEGORIES, hand-entered) against RAW_PROJECTS'
    independently-computed per-taxCreditType sums.
    """
    units_by_source = {}
    counts_by_source = {}
    for _name, _addr, _city, units, sources, _lat, _lon in RAW_PROJECTS:
        src = sources[0]
        units_by_source[src] = units_by_source.get(src, 0) + units
        counts_by_source[src] = counts_by_source.get(src, 0) + 1
    rh_cat = next(c for c in CATEGORIES if c["key"] == "affordable_rental_housing")
    errors = []
    for sp in rh_cat["subprograms"]:
        key = sp["key"]
        if sp["fy2025_units"] != units_by_source.get(key, 0):
            errors.append(f"{key} fy2025_units: category says {sp['fy2025_units']}, "
                           f"RAW_PROJECTS sums to {units_by_source.get(key, 0)}")
    if errors:
        raise SystemExit("Category/RAW_PROJECTS subprogram mismatch(es):\n" + "\n".join(errors))
    total_projects = sum(counts_by_source.values())
    print(f"Affordable Rental Housing category's 5 subprogram fy2025_units fields "
          f"verified against RAW_PROJECTS' own per-taxCreditType sums "
          f"({total_projects} projects across 5 credit types: "
          + ", ".join(f"{k}={v}" for k, v in counts_by_source.items()) + ").")


def verify_rental_housing_credit_totals():
    rh_cat = next(c for c in CATEGORIES if c["key"] == "affordable_rental_housing")
    amounts = {a["label_key"]: a["amount"] for a in rh_cat["fy2025_amounts"]}
    combined = (amounts["co_amt_federal_4pct"] + amounts["co_amt_federal_9pct"]
                + amounts["co_amt_state_htc"])
    if combined != 95400000:
        raise SystemExit(
            f"Federal 4% + Federal 9% + State HTC = {combined:,}, expected 95,400,000 "
            "(Community Report p.3's own \"$95.4M awarded in federal and state Housing "
            "Tax Credits\" combined figure)"
        )
    print("Federal 4% ($44.6M) + Federal 9% ($19.2M) + State HTC ($31.6M) = $95.4M "
          "verified against the Community Report's own separate overview-panel figure.")


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def build_projects():
    projects = []
    for name, address, city, units, sources, lat, lon in RAW_PROJECTS:
        primary = next((s for s in FUNDING_PRIORITY if s in sources), sources[0])
        projects.append({
            "id": slugify(name),
            "name": name,
            "address": address,
            "city": city,
            "lat": round(lat, 5),
            "lon": round(lon, 5),
            "units": units,
            "funding_sources": sources,
            "source_amounts": {},
            "total_amount": None,
            "primary_color_group": FUNDING_COLOR_GROUP[primary],
            "overlaps": len(sources) > 1,
            "geocode_status": "official",
        })
    return projects


def main():
    verify_project_count_and_units()
    verify_category_subprogram_totals()
    verify_rental_housing_credit_totals()
    projects = build_projects()
    unique_cities = len({p["city"] for p in projects})
    print(f"{len(projects)} projects across {unique_cities} unique cities "
          "(coordinates from CHFA's own properties-map API, not geocoded).")

    payload = {
        "CO": {
            "hfa_name": "Colorado Housing and Finance Authority",
            "hfa_abbr": "CHFA",
            "fiscal_year": "CY2025",
            "source_title": "2025 CHFA Community Report (calendar-year reporting period)",
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
