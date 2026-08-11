"""
Builds docs/il_program_activity.json from IHDA's FY2025 Report of Activities.

Source: Illinois Housing Development Authority, "Report of Activities for
FY 2025 and Projected Activities for FY 2026," submitted to the Governor and
the General Assembly's Commission on Government Forecasting and Accountability.
  https://www.ihda.org/wp-content/uploads/2026/03/FY-2025_IHDA_Report-of-Activities.pdf
Local copy: FY2025/program_activity/pdf/IL_IHDA_ReportOfActivities_FY2025.pdf

This is a *program activity* report (units financed / households served),
not an audited financial statement (ACFR) -- it is a different data
category from docs/state_data.json and is kept in its own JSON file,
il_program_activity.json, fetched lazily by docs/il_activity.js only when a
user opens the Illinois program-activity view.

Methodology
-----------
The four top-level category totals (FY2025_ACTUAL below) are IHDA's own
published aggregates, taken verbatim from the "Summary of Financing
Activity" paragraph in the report's Introduction/Section I (page 4). They
are NOT derived by summing the category's subprograms, because subprogram
totals within Category 1 (multifamily) overlap heavily -- the same
development is routinely financed by Bonds + LIHTC + HOME + Trust Fund +
IAHTC simultaneously, so naively adding subprogram unit counts would double-
(or triple-, or quadruple-) count the same housing units. Categories 2-4 do
NOT have this problem (each loan/household belongs to exactly one
subprogram), which is why their subprograms are additive and Category 1's
are not -- see each category's "additive" flag below.

Fund-type classification (fund_type/fund_name on each subprogram) comes from
a SEPARATE source document -- IHDA's own FY2025 audited financial statements
(FY2025/pdf/IL_IHDA_FY2025_ACFR.pdf), Note 2 "Summary of Significant
Accounting Policies" (pages 43-45, naming the 7 major governmental funds and
4 major proprietary/enterprise funds) and the Combining Balance Sheet --
Nonmajor Governmental Funds (pages 100-101, naming the 14 smaller
governmental funds). This is the Report of Activities' cousin document, not
itself -- the Report of Activities never states which GASB fund type backs
each program, so this mapping is done by matching each subprogram's own
"funded by ..." language (already present in the Report of Activities' prose)
against the ACFR's named funds:
  - "governmental": a GASB governmental fund (modified-accrual, funded by
    state appropriation, HUD/federal pass-through, or other grant revenue --
    IHDA administers the money but doesn't carry entrepreneurial risk on it).
  - "proprietary": one of IHDA's 4 GASB enterprise funds (full-accrual,
    self-supporting through bond issuance and mortgage interest/fees).
  - "off_balance_sheet": confirmed NOT to appear as a named fund anywhere in
    the ACFR (checked against all 7 major governmental + 4 proprietary + 14
    nonmajor governmental fund names) -- LIHTC and IAHTC are tax-credit
    *allocation* programs where IHDA administers federal/state credits that
    are issued directly to private developers/investors; the credit value
    and syndication equity never sit on IHDA's own balance sheet as fund
    assets, so neither GASB fund category applies.
  - "mixed": the subprogram itself draws from more than one fund type
    depending on the specific deal (documented per entry below).
Confidence is high for names taken verbatim from the ACFR (Illinois
Affordable Housing Trust Fund, HOME Program Fund, National Housing Trust
Fund, Cook County Mortgage Foreclosure Mediation Program Fund, Housing
Counseling Resource Program Fund, Illinois General Revenue Fund, COVID-19
Homeowner Assistance Fund, Mortgage Loan Program Fund, Single Family Program
Fund); lower (marked "inferred") where the Report of Activities' "funded by
the Capital Bill" language was matched to the ACFR's "Build Illinois Bond
Program Fund" without an exact program-name cross-reference in either
document, or where a program (ASERAP) is DHS-administered and never appears
as an IHDA-carried fund at all in the ACFR.

Category-1 project-level detail (used only for the geographic bubble map)
was manually transcribed from Appendix II's closing-report exhibits
(Exhibits XIV, XV, XVI, XVII, XVIII, XIX, XXII, XXIII -- pages A.19-A.27 of
the PDF). Rental-assistance/operating-subsidy exhibits (Section 811 PRA,
Exhibit XX; Rental Housing Support, Exhibit XXI) were intentionally
excluded from Category 1, because IHDA's own "5,932 units" sentence is
followed by a *separate* sentence describing the "465 affordable rental
units" financed under its rental-assistance-and-operations programs -- i.e.
IHDA itself does not count those units inside the 5,932 figure.

Every exhibit's project list below was cross-checked against that exhibit's
own printed subtotal row (e.g. "7 Developments Closed ... 909") before
being accepted; see PROJECT_SOURCE_TOTALS for the verification.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "il_program_activity.json"

SOURCE_URL = "https://www.ihda.org/wp-content/uploads/2026/03/FY-2025_IHDA_Report-of-Activities.pdf"
SOURCE_FILE = "IL_IHDA_ReportOfActivities_FY2025.pdf"
RETRIEVED = "2026-08-11"

# The Census Geocoder (geocoding.geo.census.gov) only matches addresses that
# fall inside its TIGER/Line house-number ranges and returns an empty match
# list for anything else -- including plain "City, State" queries, which
# means it can't serve as its own city-center fallback. Nominatim (OpenStreetMap)
# handles both street-level and city-level queries reliably, so it is used
# for both the primary lookup and the city-center fallback. Per Nominatim's
# usage policy this script self-throttles to <=1 request/second and sends an
# identifying User-Agent.
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
GEOCODER_USER_AGENT = "us-hfa-data-map/1.0 (github.com/MD-ai-fin/us-hfa-data-map)"

# ---------------------------------------------------------------------------
# Category-level data (Section I narrative, IHDA's own published aggregates)
# ---------------------------------------------------------------------------

# Every fy2026 dict uses a uniform shape: {value, amount, closed, note_key}.
#   value  = unit/household count projected for FY2026 (None if not disclosed)
#   amount = dollar amount projected for FY2026 (None if not disclosed) --
#            IHDA frequently discloses a dollar figure for FY2026 even when it
#            does not give a unit/household count, so the two are tracked
#            independently rather than folded into one "status" flag.
#   closed = True when IHDA states the program will see no further activity
# A subprogram with value=None, amount=None, closed=False is genuinely
# qualitative -- IHDA gave only prose ("will continue to serve as
# administrator") with no figure of any kind for FY2026.

CATEGORIES = [
    {
        "key": "multifamily_new_preserve",
        "unit_type": "units",
        "fy2025_actual": 5932,
        "fy2025_source_quote": (
            "In FY 2025, the Authority financed $291,988,754 in state and federal "
            "resources, paired with 88,757,727 in state and federal tax credits for "
            "the creation and/or preservation of 5,932 multifamily and single-family "
            "housing units in Illinois."
        ),
        # Two distinct funding mechanisms (cash resources vs. tax credits) --
        # shown separately rather than summed, same non-overlap discipline as
        # the unit figures below.
        "fy2025_amounts": [
            {"label_key": "il_amt_cash_resources", "amount": 291988754},
            {"label_key": "il_amt_tax_credits", "amount": 88757727},
        ],
        "additive": False,
        "fy2026": {
            "value": None, "amount": None, "closed": False,
            "note_key": "il_fy26_note_multifamily",
        },
        "subprograms": [
            {"key": "bonds", "fy2025_units": 909, "fy2025_amount": 127551000,
             "color_group": "bond",
             "fund_type": "proprietary", "fund_name": "Mortgage Loan Program Fund",
             "fy2026": {"value": 2132, "amount": None, "closed": False,
                        "note_key": "il_bonds_fy26_note"}},
            {"key": "lihtc_9", "fy2025_units": 1173, "fy2025_amount": 33794999,
             "color_group": "credit",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": {"value": None, "amount": None, "closed": False,
                        "note_key": "il_lihtc9_fy26_note"}},
            {"key": "lihtc_4", "fy2025_units": 1593, "fy2025_amount": 23558654,
             "color_group": "credit",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": {"value": None, "amount": None, "closed": False,
                        "note_key": "il_lihtc4_fy26_note"}},
            {"key": "iahtc", "fy2025_units": 902, "fy2025_amount": 31404074,
             "color_group": "credit",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": {"value": None, "amount": 38028389, "closed": False,
                        "note_key": "il_iahtc_fy26_note"}},
            {"key": "home", "fy2025_units": 452, "fy2025_amount": 43145393,
             "color_group": "trust",
             "fund_type": "governmental", "fund_name": "HOME Program Fund",
             "fy2026": {"value": None, "amount": 15500000, "closed": False,
                        "note_key": "il_home_fy26_note"}},
            {"key": "nhtf", "fy2025_units": 101, "fy2025_amount": 21234706,
             "color_group": "trust",
             "fund_type": "governmental", "fund_name": "National Housing Trust Fund (nonmajor)",
             "fy2026": {"value": None, "amount": 6000000, "closed": False,
                        "note_key": "il_nhtf_fy26_note"}},
            {"key": "trust_fund", "fy2025_units": 736, "fy2025_amount": 37172268,
             "color_group": "trust",
             "fund_type": "governmental", "fund_name": "Illinois Affordable Housing Trust Fund",
             "fy2026": {"value": None, "amount": 55000000, "closed": False,
                        "note_key": "il_trustfund_fy26_note"}},
            {"key": "capital_bill", "fy2025_units": 30, "fy2025_amount": 8425000,
             "color_group": "capital",
             "fund_type": "governmental", "fund_name": "Build Illinois Bond Program Fund (inferred)",
             "fy2026": {"value": 80, "amount": 40000000, "closed": False,
                        "note_key": "il_capitalbill_fy26_note"}},
            {"key": "other_multifamily", "fy2025_units": 557, "fy2025_amount": 38460387,
             "color_group": "capital",
             "fund_type": "mixed", "fund_name": None,
             "fy2026": {"value": None, "amount": None, "closed": False,
                        "note_key": "il_othermf_fy26_note"}},
        ],
    },
    {
        "key": "homebuyer_loans",
        "unit_type": "households",
        "fy2025_actual": 4915,
        "fy2025_source_quote": (
            "Under its homeownership programs, IHDA financed $971,134,438 in first "
            "mortgage purchases for 4,915 loans, paired with $52,319,641 in second "
            "mortgages for down payment and/or closing cost assistance for 4,911 "
            "homebuyers."
        ),
        "fy2025_amounts": [
            {"label_key": "il_amt_first_mortgage", "amount": 971134438},
            {"label_key": "il_amt_second_mortgage", "amount": 52319641},
        ],
        "additive": True,
        # Complete sum of the 3 still-active subprograms' FY2026 second-mortgage
        # assistance projections (SmartBuy is closed, contributes $0).
        "fy2026": {"value": None, "amount": 42382181, "closed": False,
                   "note_key": "il_fy26_note_homebuyer"},
        "subprograms": [
            {"key": "access_4", "fy2025_units": 939, "fy2025_amount": 148094760,
             "color_group": "credit",
             "fund_type": "proprietary", "fund_name": "Single Family Program Fund",
             "fy2026": {"value": None, "amount": 7439400, "closed": False,
                        "note_key": "il_access4_fy26_note"}},
            {"key": "access_5", "fy2025_units": 1705, "fy2025_amount": 356672834,
             "color_group": "credit",
             "fund_type": "proprietary", "fund_name": "Single Family Program Fund",
             "fy2026": {"value": None, "amount": 14736281, "closed": False,
                        "note_key": "il_access5_fy26_note"}},
            {"key": "access_10", "fy2025_units": 1729, "fy2025_amount": 342707251,
             "color_group": "credit",
             "fund_type": "proprietary", "fund_name": "Single Family Program Fund",
             "fy2026": {"value": None, "amount": 20206500, "closed": False,
                        "note_key": "il_access10_fy26_note"}},
            {"key": "smartbuy", "fy2025_units": 542, "fy2025_amount": 123659593,
             "color_group": "credit",
             "fund_type": "governmental", "fund_name": "Build Illinois Bond Program Fund (inferred)",
             "fy2026": {"value": None, "amount": None, "closed": True,
                        "note_key": "il_smartbuy_fy26_note"}},
        ],
    },
    {
        "key": "repair_counseling",
        "unit_type": "households",
        "fy2025_actual": 9324,
        "fy2025_source_quote": (
            "HRAP 251 households + HAFHR 126 properties + CCMFMP 146 households + "
            "HCRP 8,801 households counseled (Section I.B.1, I.B.2, I.E.1, I.E.2)."
        ),
        # Sum of the 4 subprograms' own disbursement figures -- non-overlapping.
        "fy2025_amounts": [
            {"label_key": "il_amt_disbursed", "amount": 17454175},
        ],
        "additive": True,
        # HCRP does not disclose an FY2026 dollar figure, so no category-level
        # amount is shown here (would understate the true total) -- only the
        # complete, all-4-subprograms-accounted-for unit total is shown.
        "fy2026": {"value": 15086, "amount": None, "closed": False,
                   "note_key": "il_fy26_note_repair"},
        "subprograms": [
            {"key": "hrap", "fy2025_units": 251, "fy2025_amount": 8778134,
             "color_group": "amber",
             "fund_type": "governmental", "fund_name": "Illinois Affordable Housing Trust Fund",
             "fy2026": {"value": 181, "amount": 6300000, "closed": False,
                        "note_key": "il_hrap_fy26_note"}},
            {"key": "hafhr", "fy2025_units": 126, "fy2025_amount": 6860258,
             "color_group": "amber",
             "fund_type": "governmental", "fund_name": "COVID-19 Homeowner Assistance Fund (nonmajor)",
             "fy2026": {"value": 184, "amount": 10000000, "closed": False,
                        "note_key": "il_hafhr_fy26_note"}},
            {"key": "ccmfmp", "fy2025_units": 146, "fy2025_amount": 37400,
             "color_group": "amber",
             "fund_type": "governmental", "fund_name": "Cook County Mortgage Foreclosure Mediation Program Fund (nonmajor)",
             "fy2026": {"value": 121, "amount": 50000, "closed": False,
                        "note_key": "il_ccmfmp_fy26_note"}},
            {"key": "hcrp", "fy2025_units": 8801, "fy2025_amount": 1778383,
             "color_group": "amber",
             "fund_type": "governmental", "fund_name": "Housing Counseling Resource Program Fund (nonmajor)",
             "fy2026": {"value": 14600, "amount": None, "closed": False,
                        "note_key": "il_hcrp_fy26_note"}},
        ],
    },
    {
        "key": "covid_emergency",
        "unit_type": "households",
        "fy2025_actual": 7720,
        "fy2025_source_quote": (
            "Additionally, the Authority financed three COVID-19 emergency rental "
            "and mortgage assistance programs which disbursed approximately "
            "$64,212,255 to 7,720 approved applicants."
        ),
        "fy2025_amounts": [
            {"label_key": "il_amt_disbursed", "amount": 64212255},
        ],
        "additive": True,
        # Complete: State CBRAP $50M + ILHAF2/ASERAP closed ($0 each).
        "fy2026": {"value": 6500, "amount": 50000000, "closed": False,
                   "note_key": "il_fy26_note_covid"},
        "subprograms": [
            {"key": "ilhaf2", "fy2025_units": 35, "fy2025_amount": 451201,
             "color_group": "rose",
             "fund_type": "governmental", "fund_name": "COVID-19 Homeowner Assistance Fund (nonmajor)",
             "fy2026": {"value": None, "amount": None, "closed": True,
                        "note_key": "il_ilhaf2_fy26_note"}},
            {"key": "state_cbrap", "fy2025_units": 7683, "fy2025_amount": 63749173,
             "color_group": "rose",
             "fund_type": "governmental", "fund_name": "Illinois General Revenue Fund",
             "fy2026": {"value": 6500, "amount": 50000000, "closed": False,
                        "note_key": "il_cbrap_fy26_note"}},
            {"key": "aserap", "fy2025_units": 2, "fy2025_amount": 11881,
             "color_group": "rose",
             "fund_type": "governmental", "fund_name": None,
             "fy2026": {"value": None, "amount": None, "closed": True,
                        "note_key": "il_aserap_fy26_note"}},
        ],
    },
]

# ---------------------------------------------------------------------------
# Category 1 project-level detail (Appendix II, Exhibits XIV-XIX, XXII, XXIII)
# Manually transcribed; "units" uses the largest unit count reported for that
# project across the exhibits it appears in (a project's *unit* figure can
# differ slightly by exhibit -- e.g. a listing may report only the subset of
# units tied to a specific credit type -- so the max is the best single
# estimate of the physical development's size for bubble sizing).
# ---------------------------------------------------------------------------

# Casa Yucatan is reported with genuinely different unit counts in different
# exhibits (its LIHTC 9% allocation and the IAHTF/Trust Fund listing cover a
# 32-unit subset, while the Bonds/4%/HOME/Other-Multifamily listings cover
# the full 70-unit development) -- this per-exhibit override map lets the
# verification sums use each exhibit's own reported figure while the bubble
# map still displays the project's full 70-unit size.
UNIT_OVERRIDES = {
    "Casa Yucatan": {"lihtc_9": 32, "trust_fund": 32},
}

# (name, address, city, units, [funding source keys])
RAW_PROJECTS = [
    ("Buena Vista Apartments", "1285 Fleetwood Dr", "Elgin", 231,
     ["bonds", "lihtc_4"]),
    ("Leyden Apartments", "2506-2516 N Mannheim Rd", "Franklin Park", 80,
     ["bonds", "lihtc_4", "home", "iahtc"]),
    ("Ravine Terrace", "200 S Martin Luther King Jr Ave", "Waukegan", 98,
     ["bonds", "lihtc_4", "iahtc"]),
    ("The Villager & Briarwood West", "77 S Williams St", "Crystal Lake", 116,
     ["bonds", "lihtc_4"]),
    ("Walden Oaks", "1155 Walden Oaks Dr", "Woodstock", 191,
     ["bonds", "lihtc_4", "trust_fund"]),
    ("Willa Rawls Manor", "4120 S Indiana Ave", "Chicago", 123,
     ["bonds", "lihtc_4"]),
    ("Casa Yucatan", "2136 S Ashland Ave", "Chicago", 70,
     ["bonds", "lihtc_9", "lihtc_4", "home", "trust_fund", "other_multifamily"]),
    ("Access South Cook", "364 S Orchard Dr", "Park Forest", 44,
     ["lihtc_9", "nhtf"]),
    ("Addison Horizon Senior Living Community", "150 Green Meadow Dr", "Addison", 62,
     ["lihtc_9", "other_multifamily"]),
    ("Bristol Place Senior Residences", "121 Tower St", "Champaign", 60,
     ["lihtc_9", "other_multifamily"]),
    ("Churchview Garden Homes", "909 S Sumner Ave", "Peoria", 47,
     ["lihtc_9", "home"]),
    ("Earle School Family Residences", "1711 W 61st St", "Chicago", 50,
     ["lihtc_9", "other_multifamily"]),
    ("Eve B. Lee Place", "500 Peterson Rd", "Libertyville", 34,
     ["lihtc_9", "iahtc", "other_multifamily"]),
    ("Fox Hill Senior Living", "1536 Sycamore Rd", "Yorkville", 48,
     ["lihtc_9", "home"]),
    ("Gifford's Crossing", "36W380 Big Timber Rd", "Elgin", 36,
     ["lihtc_9", "home"]),
    ("Hillside Senior Apartments", "5207 Ridge Ave", "Hillside", 42,
     ["lihtc_9", "home", "iahtc"]),
    ("Humboldt Park Passive Living", "3831 W Chicago Ave", "Chicago", 60,
     ["lihtc_9"]),
    ("Lincoln Senior Flats", "1405 Castle Manor Dr", "Lincoln", 57,
     ["lihtc_9", "trust_fund", "other_multifamily"]),
    ("McHenry Senior Commons", "3717 Municipal Dr", "McHenry", 40,
     ["lihtc_9", "iahtc"]),
    ("North Bend Fairview Heights Residences", "301 N Monticello Pl", "Fairview Heights", 60,
     ["lihtc_9", "other_multifamily"]),
    ("OC Living Phase A-2", "1301 S Washtenaw Ave", "Chicago", 75,
     ["lihtc_9", "iahtc"]),
    ("Parker Glen II", "2617 JT Coffman Dr", "Champaign", 56,
     ["lihtc_9", "home"]),
    ("Poupard Place", "1657 Shermer Rd", "Northbrook", 48,
     ["lihtc_9", "iahtc", "trust_fund"]),
    ("Rimini Place", "600 Rimini Dr", "Virden", 28,
     ["lihtc_9", "other_multifamily"]),
    ("Starling Senior Apartments", "0 Deep Lake Rd", "Lake Villa", 40,
     ["lihtc_9", "other_multifamily"]),
    ("Steer Place Apartments", "1202 E Harding Dr", "Urbana", 108,
     ["lihtc_9", "iahtc"]),
    ("Stevens Apartments", "118 N Haller St", "Wood River", 46,
     ["lihtc_9", "other_multifamily"]),
    ("Taylor Place Apartments", "4103 W Crystal Lake Rd", "McHenry", 50,
     ["lihtc_9", "other_multifamily"]),
    ("Timber Trails Apartments", "50 Small St", "Harrisburg", 50,
     ["lihtc_9", "home"]),
    ("Brainerd Senior Preservation", "8915 S Loomis St", "Chicago", 60,
     ["lihtc_4", "trust_fund"]),
    ("Deerfield Supportive Living", "1101 Lake Cook Rd", "Deerfield", 147,
     ["lihtc_4", "iahtc"]),
    ("Heart of Uptown Apartments", "Multiple Addresses", "Chicago", 103,
     ["lihtc_4", "trust_fund"]),
    ("Lincoln Terrace", "2825 W Ann St", "Peoria", 92,
     ["lihtc_4"]),
    ("Lincoln Towers Bloomington & Downtowner", "109 W Market St", "Bloomington", 137,
     ["lihtc_4"]),
    ("Lincoln Towers Freeport", "320 N Harlem Ave", "Freeport", 101,
     ["lihtc_4"]),
    ("New Holland Apartments", "324 N Vermilion St", "Danville", 44,
     ["lihtc_4", "trust_fund", "iahtc"]),
    ("Building Communities 2024", "2004 Herbert Dr", "Waukegan", 5,
     ["iahtc"]),
    ("EAP Phase XII", "Scattered Site", "Rock Island", 0,
     ["iahtc"]),
    ("Evanston Community Land Trust", "1808 Hovland Ct", "Evanston", 1,
     ["iahtc"]),
    ("Expansion of Hope", "1308 Sunset Dr", "Rantoul", 8,
     ["iahtc"]),
    ("Forest Downs", "", "Harvard", 4,
     ["iahtc"]),
    ("Garden Apartments", "7019 W Crandall Ave", "Worth", 16,
     ["iahtc", "nhtf", "trust_fund"]),
    ("HODC LCHA Preservation", "212 E IL Route 22", "Lake Zurich", 10,
     ["iahtc"]),
    ("Parkside Phase III", "500-520 W Hobbie St", "Chicago", 99,
     ["iahtc"]),
    ("Providing Stable Foundations 2025", "825 Pleasant St", "DeKalb", 1,
     ["iahtc"]),
    ("Reclaiming Chicago", "Scattered Sites", "Chicago", 25,
     ["iahtc"]),
    ("Unlocking Doors 2024", "733 Eletson Dr", "Crystal Lake", 3,
     ["iahtc"]),
    ("Woodland Court", "Main St and Woodland Ct", "West Chicago", 14,
     ["iahtc"]),
    ("Hamlin Avenue Apartments", "12000 S Hamlin Ave", "Alsip", 25,
     ["nhtf", "trust_fund"]),
    ("Vivian's Village PSH", "5708 Bond Ave", "Cahokia Heights", 16,
     ["nhtf", "trust_fund"]),
    ("1237 N California Avenue Family Apartments", "1237 N California Ave", "Chicago", 40,
     ["trust_fund"]),
    ("Sacred Apts", "3211-3227 E 92nd St", "Chicago", 81,
     ["trust_fund"]),
    ("Mason Street Apartments", "229 W Mason St", "Springfield", 23,
     ["home", "trust_fund"]),
    ("CIIC Empowerment Estates Site 2", "214 Gale St", "Aurora", 1,
     ["capital_bill"]),
    ("Southwest Reentry Expansion", "", "Chicago Ridge", 4,
     ["capital_bill"]),
    ("YWCA Justice Project 2", "428 Maine St", "Quincy", 1,
     ["capital_bill"]),
    ("Hope Village", "1799 Federal Dr", "Urbana", 24,
     ["capital_bill"]),
]

# Per-project, per-funding-source dollar amount, manually transcribed from
# each exhibit's own "Amount" column (for LIHTC 9%/4%, this is the "Equity
# Amount" -- private equity actually raised for the project -- not the
# smaller face-value credit amount, matching how the report's own narrative
# quotes "$298,579,528 in private equity raised" for the 9% program). Unlike
# the unit counts, these dollar figures ARE meant to be summed across a
# project's funding sources -- that sum is the project's total multi-source
# capital stack, not a double-count, since each source contributed distinct
# dollars to the same deal. verify_exhibit_totals() cross-checks the sum of
# each source's column below against that subprogram's fy2025_amount in
# CATEGORIES, so a transcription slip here fails loudly rather than silently.
PROJECT_SOURCE_AMOUNTS = {
    "Buena Vista Apartments": {"bonds": 43083000, "lihtc_4": 25865267},
    "Leyden Apartments": {"bonds": 1960000, "lihtc_4": 13314343, "home": 5982876, "iahtc": 851163},
    "Ravine Terrace": {"bonds": 32500000, "lihtc_4": 24573992, "iahtc": 6700000},
    "The Villager & Briarwood West": {"bonds": 15150000, "lihtc_4": 9354119},
    "Walden Oaks": {"bonds": 13173000, "lihtc_4": 12111191, "trust_fund": 3262000},
    "Willa Rawls Manor": {"bonds": 19840000, "lihtc_4": 15957065},
    "Casa Yucatan": {"bonds": 1845000, "lihtc_9": 13403538, "lihtc_4": 12975000,
                      "home": 10252671, "trust_fund": 1880000, "other_multifamily": 3680123},
    "Access South Cook": {"lihtc_9": 12598740, "nhtf": 5977130},
    "Addison Horizon Senior Living Community": {"lihtc_9": 13573643, "other_multifamily": 3441000},
    "Bristol Place Senior Residences": {"lihtc_9": 11998800, "other_multifamily": 2800000},
    "Churchview Garden Homes": {"lihtc_9": 13198680, "home": 3107076},
    "Earle School Family Residences": {"lihtc_9": 13798620, "other_multifamily": 3253959},
    "Eve B. Lee Place": {"lihtc_9": 12537741, "iahtc": 343331, "other_multifamily": 4924000},
    "Fox Hill Senior Living": {"lihtc_9": 13725000, "home": 4252697},
    "Gifford's Crossing": {"lihtc_9": 13537676, "home": 7085728},
    "Hillside Senior Apartments": {"lihtc_9": 13260030, "home": 1700000, "iahtc": 517500},
    "Humboldt Park Passive Living": {"lihtc_9": 14098500},
    "Lincoln Senior Flats": {"lihtc_9": 12139225, "trust_fund": 670000, "other_multifamily": 3338365},
    "McHenry Senior Commons": {"lihtc_9": 16862315, "iahtc": 209500},
    "North Bend Fairview Heights Residences": {"lihtc_9": 13198680, "other_multifamily": 2842107},
    "OC Living Phase A-2": {"lihtc_9": 14623540, "iahtc": 525000},
    "Parker Glen II": {"lihtc_9": 12346169, "home": 2714096},
    "Poupard Place": {"lihtc_9": 13648635, "iahtc": 1135000, "trust_fund": 3690000},
    "Rimini Place": {"lihtc_9": 7755288, "other_multifamily": 2394470},
    "Starling Senior Apartments": {"lihtc_9": 13648499, "other_multifamily": 3953000},
    "Steer Place Apartments": {"lihtc_9": 12336266, "iahtc": 3190000},
    "Stevens Apartments": {"lihtc_9": 10510060, "other_multifamily": 4063608},
    "Taylor Place Apartments": {"lihtc_9": 13648635, "other_multifamily": 3769755},
    "Timber Trails Apartments": {"lihtc_9": 12131248, "home": 3686963},
    "Brainerd Senior Preservation": {"lihtc_4": 8433162, "trust_fund": 2610000},
    "Deerfield Supportive Living": {"lihtc_4": 22872963, "iahtc": 3550000},
    "Heart of Uptown Apartments": {"lihtc_4": 20693524, "trust_fund": 1772500},
    "Lincoln Terrace": {"lihtc_4": 13218121},
    "Lincoln Towers Bloomington & Downtowner": {"lihtc_4": 13678620},
    "Lincoln Towers Freeport": {"lihtc_4": 6370360},
    "New Holland Apartments": {"lihtc_4": 5248065, "trust_fund": 4776000, "iahtc": 827500},
    "Building Communities 2024": {"iahtc": 539076},
    "EAP Phase XII": {"iahtc": 560000},
    "Evanston Community Land Trust": {"iahtc": 205000},
    "Expansion of Hope": {"iahtc": 903250},
    "Forest Downs": {"iahtc": 314646},
    "Garden Apartments": {"iahtc": 118500, "nhtf": 4172968, "trust_fund": 3674951},
    "HODC LCHA Preservation": {"iahtc": 294800},
    "Parkside Phase III": {"iahtc": 5450000},
    "Providing Stable Foundations 2025": {"iahtc": 276486},
    "Reclaiming Chicago": {"iahtc": 2500000},
    "Unlocking Doors 2024": {"iahtc": 231971},
    "Woodland Court": {"iahtc": 2161351},
    "Hamlin Avenue Apartments": {"nhtf": 7650720, "trust_fund": 4211150},
    "Vivian's Village PSH": {"nhtf": 3433888, "trust_fund": 1516112},
    "1237 N California Avenue Family Apartments": {"trust_fund": 2978954},
    "Sacred Apts": {"trust_fund": 4019153},
    "Mason Street Apartments": {"home": 4363286, "trust_fund": 2111448},
    "CIIC Empowerment Estates Site 2": {"capital_bill": 475000},
    "Southwest Reentry Expansion": {"capital_bill": 475000},
    "YWCA Justice Project 2": {"capital_bill": 475000},
    "Hope Village": {"capital_bill": 7000000},
}

# Each exhibit's unit total, as manually summed from RAW_PROJECTS above,
# must equal the total printed at the foot of that exhibit in the PDF.
# (subprogram_key -> (label, PDF-printed total))
EXHIBIT_CHECK_TOTALS = {
    "bonds": ("Exhibit XIV: Multifamily Bonds -- '7 Developments Closed ... 909'", 909),
    "lihtc_9": ("Exhibit XV (9% LIHTC) -- narrative: '1,173 units'", 1173),
    "lihtc_4": ("Exhibit XV (4% LIHTC) -- narrative: '1,593 units'", 1593),
    "iahtc": ("Exhibit XVI: IAHTC -- '22 Developments Closed ... 902'", 902),
    "home": ("Exhibit XVII: HOME -- '9 Developments Closed ... 452'", 452),
    "nhtf": ("Exhibit XVIII: NHTF -- '4 Developments Closed ... 101'", 101),
    "trust_fund": ("Exhibit XIX: IAHTF -- '13 Developments Closed ... 736'", 736),
    "capital_bill": ("Exhibit XXII: Capital Bill (HJIIP+H3C) -- '4 Projects Closed ... 30'", 30),
    "other_multifamily": ("Exhibit XXIII: Other Multifamily -- '11 Developments Closed ... 557'", 557),
}

FUNDING_COLOR_GROUP = {
    "bonds": "bond",
    "lihtc_9": "credit", "lihtc_4": "credit", "iahtc": "credit",
    "home": "trust", "nhtf": "trust", "trust_fund": "trust",
    "capital_bill": "capital", "other_multifamily": "capital",
}
# priority order for picking a project's single "primary" color when it has
# multiple funding sources (first match wins)
FUNDING_PRIORITY = ["bonds", "lihtc_9", "lihtc_4", "iahtc", "home", "nhtf",
                     "trust_fund", "capital_bill", "other_multifamily"]


def units_for_source(name, units, source):
    return UNIT_OVERRIDES.get(name, {}).get(source, units)


def verify_exhibit_totals():
    sums = {}
    for name, _addr, _city, units, sources in RAW_PROJECTS:
        for src in sources:
            sums[src] = sums.get(src, 0) + units_for_source(name, units, src)
    errors = []
    for key, (label, expected) in EXHIBIT_CHECK_TOTALS.items():
        got = sums.get(key, 0)
        if got != expected:
            errors.append(f"{label} (units): expected {expected}, got {got}")
    if errors:
        raise SystemExit("Exhibit total mismatch(es):\n" + "\n".join(errors))
    print("All 9 exhibit unit subtotals verified against PDF-printed totals.")


# subprogram-level fy2025_amount in CATEGORIES intentionally stores the
# smaller face-value LIHTC *credit* amount (matching the category's own
# "88,757,727 in state and federal tax credits" headline figure), while the
# per-project amounts above use the larger *equity raised* figure (the
# actual cash into each project, matching the report's separately quoted
# "$298,579,528"/"$204,665,792 in private equity raised" for 9%/4% credits
# respectively) -- these overrides let the two be checked against their own,
# differently-sourced, correct totals instead of against each other.
AMOUNT_CHECK_OVERRIDES = {
    "lihtc_9": 298579528,
    "lihtc_4": 204665792,
}


def verify_amount_totals():
    mf_category = next(c for c in CATEGORIES if c["key"] == "multifamily_new_preserve")
    expected_by_source = {sp["key"]: sp["fy2025_amount"] for sp in mf_category["subprograms"]}
    expected_by_source.update(AMOUNT_CHECK_OVERRIDES)
    sums = {}
    for name, _addr, _city, _units, sources in RAW_PROJECTS:
        amounts = PROJECT_SOURCE_AMOUNTS.get(name)
        if amounts is None:
            raise SystemExit(f"No PROJECT_SOURCE_AMOUNTS entry for {name!r}")
        missing = [s for s in sources if s not in amounts]
        if missing:
            raise SystemExit(f"{name!r} is missing amounts for source(s) {missing}")
        for src, amt in amounts.items():
            sums[src] = sums.get(src, 0) + amt
    errors = []
    for key, expected in expected_by_source.items():
        got = sums.get(key, 0)
        if got != expected:
            errors.append(f"{key} (amount): expected {expected}, got {got}")
    if errors:
        raise SystemExit("Amount total mismatch(es):\n" + "\n".join(errors))
    print("All 9 exhibit dollar-amount subtotals verified against PDF-printed/quoted totals.")


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
        query = f"{address}, {city}, IL" if address else f"{city}, IL"
        coords = geocode(query, cache)
        status = "ok"
        if coords is None:
            coords = geocode(f"{city}, IL", cache)
            status = "city_center" if coords else "unresolved"
        primary = next((s for s in FUNDING_PRIORITY if s in sources), sources[0])
        source_amounts = PROJECT_SOURCE_AMOUNTS.get(name, {})
        projects.append({
            "id": name.lower().replace(" ", "-").replace("'", "").replace(".", ""),
            "name": name,
            "address": address or None,
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
    verify_exhibit_totals()
    verify_amount_totals()
    print("Geocoding project addresses via US Census Geocoder...")
    projects = build_projects()
    unresolved = [p["name"] for p in projects if p["geocode_status"] == "unresolved"]
    if unresolved:
        print(f"  {len(unresolved)} project(s) could not be geocoded: {unresolved}")

    payload = {
        "IL": {
            "hfa_name": "Illinois Housing Development Authority",
            "hfa_abbr": "IHDA",
            "fiscal_year": "FY2025",
            "source_title": "Report of Activities for FY 2025 and Projected Activities for FY 2026",
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
