"""
Builds docs/me_program_activity.json for MaineHousing (Maine State Housing
Authority) from its FY2025 "By the Numbers" accomplishments page plus the
three FY2025 affordable-rental award-round announcements (which together
supply the per-development project list for the bubble map), cross-referenced
against MaineHousing's own FY2025 audited financial statements for GASB
fund-type classification.

Fiscal-year discipline
------------------------------------------------------------------------
MaineHousing's fiscal year ENDS DECEMBER 31 (a calendar-year fiscal year), so
the accomplishments page's own "2025" data *is* FY2025 -- there is no
July-June vs. January-December mismatch to correct. The page itself says
"On this page we have summarized the work MaineHousing completed in 2025".
fiscal_year is therefore recorded honestly as "FY2025" with no caveat needed
(unlike, e.g., HI's mixed calendar/fiscal-year report in this same series).

Sources (all FY2025 = MaineHousing's January 1 - December 31, 2025 fiscal year)
------------------------------------------------------------------------
1. "BY THE NUMBERS: HOW MAINEHOUSING SERVED MAINE IN 2025" (accomplishments
   page):
     https://mainehousing.org/about/accomplishments
   Local copy: FY2025/program_activity/pdf/ME_MaineHousing_Accomplishments_2025.html
   Supplies every KPI number below (homeownership, development production,
   HCV, HEAP/energy, home repair). NOTE: this page discloses unit/household
   counts but NO dollar figures for the energy/repair programs (dollars appear
   only for homeownership total loans and warming-shelter funding), so those
   categories carry no fy2025_amounts.

2. The three FY2025 affordable-RENTAL award-round announcements, which give
   the name + city + unit count per development (the bubble-map project list):
   a. Rural Affordable Rental Housing Program round (April 10, 2025):
        https://mainehousing.org/news/news-detail/2025/04/10/mainehousing-awards--24.5-million-in-rural-affordable-rental-housing-for-137-new-rental-units
      Local copy: FY2025/program_activity/pdf/ME_MaineHousing_RuralAwardTable_2025.jpg
      (the per-project table is an embedded image, "2025ruralawardstable.jpg";
      its 9 rows were transcribed via Windows OCR -- see methodology below).
      9 developments / 137 units, $23.5M state subsidy + $17.4M MaineHousing loans.
   b. Urban state-subsidy round (June 17, 2025):
        https://mainehousing.org/news/news-detail/2025/06/17/mainehousing-awards--13.9-million-in-state-funding-for-129-new-affordable-housing-units-in-lewiston-and-portland
      Local copy: FY2025/program_activity/pdf/ME_june_2025.html
      3 developments / 129 units, $13.4M state subsidy (per-project amounts
      disclosed: Martel II $5,400,000; Soleil I $5,400,000; Time and Temp
      Annex $2,593,908).
   c. Tax-credit round (November 21, 2025):
        https://mainehousing.org/news/news-detail/2025/11/21/governor-mills--mainehousing-announce-300--new-affordable-apartments-in-cities-across-maine
      Local copy: FY2025/program_activity/pdf/ME_nov_2025.html
      8 developments / 311 units, $14.3M federal + state affordable-housing
      tax credits (combined figure only -- no per-project credit split).

   The November release independently re-states the other two rental rounds'
   totals ("$13.4 million to create 129 new apartments in Portland and
   Lewiston"; "$23.5 million to build 137 apartments in 9 communities
   through ... the Rural Affordable Rental Housing Program"), which is used
   here as the EXTERNAL cross-check for the rural and June rounds.

3. MaineHousing's own FY2025 audited financial statements (used ONLY for GASB
   fund-type classification):
     FY2025/txt/ME_MaineHousing_FY2025_ACFR.txt
   This IS the correct, MaineHousing-scoped document: its title page reads
   "Maine State Housing Authority ... For the Year Ended December 31, 2025"
   and its Notes describe MaineHousing's own fund structure. Unlike the
   pre-existing PA .txt/.pdf mismatch flagged in build_pa_program_activity.py,
   there is no provenance problem here.

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
MaineHousing reports BOTH proprietary and governmental funds -- unlike the
"business-type only" HFAs (PA/PHFA) in this series, it is a special-purpose
government whose MD&A (p.3) splits activities as follows:
  - "Business-type activities -- consist of mortgage financing on single
    family and multifamily residential properties. These activities are
    funded primarily through the issuance of bonds."
  - "Governmental activities -- consist of the administration of state and
    federal housing and energy-related programs. These activities are
    supported through federal grants and program agreements, as well as
    appropriations provided by the Maine State Legislature."
The Notes ("Fund Structure", pp.18-20) then name the proprietary funds
(Mortgage Purchase Fund, Bondholder Reserve Fund, General Administrative
Fund) and the governmental funds (Home Fund, Section 8 Housing Programs,
Low Income Home Energy Assistance Program, Maine Energy/Housing/Economic
Recovery Fund, and Other Federal and State Programs -- the last of which
explicitly lists, under its "State of Maine" sub-list, the "Rural Affordable
Rental Housing Program", "Affordable Homeownership Program", "Weatherization",
"Lead Abatement", "Well Water Treatment", and "Emergency Shelter ... Program").
Classification used here (confidence documented per subprogram):
  - "proprietary": single-family first mortgages -> the Mortgage Purchase Fund
    ("purchase or originate first lien mortgages on single-family and
    multi-family residential properties", p.18). Confidence: high, verbatim.
  - "governmental": every state/federal grant-and-program activity -- the
    Rural Affordable Rental Housing Program (verbatim in the ACFR's State of
    Maine program list), the urban rental state subsidy (state money, by
    program description -- the release names no separate fund, confidence
    medium), Section 8 HCV (the "Section 8 Housing Programs" fund, verbatim),
    HEAP/ECIP/CHIP/Heat Pump (LIHEAP + related DHHS/DOE energy programs,
    verbatim "Low Income Home Energy Assistance Program" fund), and the four
    home-repair programs (HUD/DOE/State of Maine programs under "Other
    Federal and State Programs").
  - "off_balance_sheet": the federal LIHTC and Maine's State Affordable
    Housing Tax Credit allocated in the November round -- credits flow
    directly to developers and their investors, never booked as a MaineHousing
    fund asset (same logic as IL/PA/HI's LIHTC classification).
  - "mixed": the "completed"/"under construction" production-status buckets
    -- each aggregates projects financed by a mix of proprietary multifamily
    loans (Mortgage Purchase Fund), LIHTC, and governmental grants, so no
    single fund type applies.

Methodology -- the two development lenses (awards vs. production)
------------------------------------------------------------------------
MaineHousing discloses its development work two DIFFERENT ways, and this
script keeps them as two separate categories rather than force a merge:
  - "multifamily_rental_awards" = the financing committed DURING FY2025, i.e.
    the three rental award rounds (Rural April + urban June + tax-credit
    November) = 20 developments / 577 units. This is the category that carries
    the per-development RAW_PROJECTS list (name + city + units are disclosed
    per development in the round announcements), so it is the bubble-map
    ("map") category. 577 is this script's own computed cross-round sum --
    none of the three releases prints a combined "577"; each round's own
    printed total (137 / 129 / 311) is asserted in verify_rental_awards() and
    the Nov release's recap cross-checks the other two.
  - "multifamily_production" = the accomplishments page's Production Status
    ("21 Projects Completed / 656 Units Completed" + "34 Projects Under
    Construction/In Underwriting / 1,597 Units ...") = 55 projects / 2,253
    units. No name+city+unit list is disclosed for these 55 projects anywhere,
    so this category carries NO RAW_PROJECTS (honest "no project list"
    result, not a fabricated mapping).

The accomplishments page's own "21 completed / 34 under construction" figures
are a different population from the 20 award-round projects (completions and
the in-underwriting pipeline are largely projects FINANCED IN PRIOR YEARS,
while the 20 awards are this year's new financing), so the two categories are
deliberately NOT made to reconcile.

Rural award-table transcription (image OCR) + its limits
------------------------------------------------------------------------
The April 10 rural release's per-project table is an embedded JPEG
("2025ruralawardstable.jpg"), not HTML text. Its 9 rows (Development Name,
Town, Developer, Units, Subsidy, Loan) were read via Windows built-in OCR.
The 9 name/town/units triplets transcribed below are reliable (the town list
matches the newscentermaine.com account's own "Skowhegan, Yarmouth, Rangeley,
Rockland, Poland, Thomaston, Madison, Brunswick, Winslow", and the units sum
5+18+18+12+18+16+18+14+18 = 137 = the release's own printed total). The
per-project SUBSIDY/LOAN dollar columns, however, did not OCR reliably (only
the first two subsidy values -- $749,965 and $2,874,948 -- came out clean),
so rural projects carry source_amounts = {} rather than half-transcribed
per-project dollars; the round-level $23.5M subsidy / $17.4M loan totals are
used instead (from the release's own text, cross-checked by the Nov recap).
The "55 Weston Avenue" project prints its phase as "Phase 11" in the image's
small font; this is transcribed as "Phase II" (Roman numeral 2), the
unambiguous reading given the developer name "55 Weston Avenue, LLC".

Excluded (disclosed but not built as categories -- honest gaps)
------------------------------------------------------------------------
- AHOP (Affordable Homeownership Program, May 2025 round: 11 single-family
  developments / $9.3M / 125 directly-subsidized homes) is single-family
  FOR-SALE production, a different population from both the rental bubble map
  and the 1,274 first-mortgage homebuyers, so it is documented here but not
  made a category (its 11 development names/locations are not disclosed in
  text form either).
- Homelessness/HPS and emergency-shelter figures (843 HPS households, 46
  shelters, 4,972 shelter/navigator clients, 12 warming shelters / $2,302,576)
  are disclosed on the accomplishments page but are a heterogeneous mix of
  households/shelters/clients/dollars with no clean single unit_type, so they
  are omitted rather than force-fit.
- Home-repair and energy program dollar figures are not disclosed anywhere on
  the source page (household counts only), so those categories' amounts are
  empty (never invented).

fy2026: none of these sources discloses any forward-looking projection, so
every fy2026 field is {value: None, amount: None, closed: False,
note_key: "meFy26NotePending"} -- nothing is invented.
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "me_program_activity.json"

SOURCE_URL = "https://mainehousing.org/about/accomplishments"
SOURCE_FILE = ("ME_MaineHousing_Accomplishments_2025.html (+ ME_june_2025.html, "
               "ME_nov_2025.html, ME_MaineHousing_RuralAwardTable_2025.jpg)")
RETRIEVED = "2026-08-16"

# Authoritative town/city points (INTPTLAT/INTPTLONG) from the U.S. Census
# Bureau 2024 Gazetteer place file for Maine (2024_gaz_place_23.txt; Poland is
# an MCD, from 2024_gaz_cousubs_23.txt). These are the official Census internal
# points for each municipality, so the bubble-map geocoding is deterministic
# (no network call) and reproducible across re-runs. No street address is
# disclosed in any of the three award announcements, so every project is
# placed at its town/city centre -> geocode_status "city_center".
ME_CITY_COORDS = {
    "Skowhegan": (44.778149, -69.712196),
    "Yarmouth": (43.803815, -70.188580),
    "Rangeley": (44.965902, -70.652146),
    "Rockland": (44.123883, -69.130452),
    "Poland": (44.048106, -70.393563),
    "Thomaston": (44.081867, -69.179452),
    "Madison": (44.807789, -69.850366),
    "Brunswick": (43.887452, -69.942623),
    "Winslow": (44.553429, -69.608450),
    "Lewiston": (44.089513, -70.172095),
    "Portland": (43.633157, -70.185305),
    "Belfast": (44.425874, -69.026418),
    "Biddeford": (43.438733, -70.392943),
    "South Portland": (43.631402, -70.285989),
}

# ---------------------------------------------------------------------------
# Category-level data
# ---------------------------------------------------------------------------
# fy2026 uniform shape: {value, amount, closed, note_key} -- see docstring.
_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                 "note_key": "meFy26NotePending"}

CATEGORIES = [
    {
        # First-time homebuyer mortgages (MaineHousing's single-family lending).
        "key": "homeownership_loans",
        "unit_type": "households",
        "fy2025_actual": 1274,
        "fy2025_source_quote": (
            "\"In 2025, our Homeownership Department, in partnership with "
            "financial institutions across the state, helped 1,274 buyers "
            "purchase a first home - including 92 veteran households and 256 "
            "First Generation Program borrowers.\" Accomplishments page stat "
            "block: \"$321,778,689 TOTAL LOANS\" / \"1,274 TOTAL LOANS\" / "
            "\"$252,574 AVERAGE MORTGAGE\". The 92 veteran and 256 First "
            "Generation households are SUBSETS of the 1,274 (not a partition), "
            "so the category carries a single additive subprogram for the "
            "headline total."
        ),
        "fy2025_amounts": [
            {"label_key": "me_amt_total_loans", "amount": 321778689},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "first_home", "fy2025_units": 1274, "fy2025_amount": 321778689,
             "color_group": "bond",
             # Single-family first mortgages are a business-type activity:
             # the Mortgage Purchase Fund "purchase[s] or originate[s] first
             # lien mortgages on single-family and multi-family residential
             # properties" (Notes, Fund Structure, p.18) -- funded by mortgage
             # revenue bonds.
             "fund_type": "proprietary", "fund_name": "Mortgage Purchase Fund",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        # The FY2025 affordable-RENTAL financing awards (the bubble-map
        # category: RAW_PROJECTS below = the 20 awarded developments).
        "key": "multifamily_rental_awards",
        "unit_type": "units",
        "fy2025_actual": 577,
        "fy2025_source_quote": (
            "Three FY2025 rental award rounds, summed by this script to 20 "
            "developments / 577 units (no single source prints 577): (1) Rural "
            "Affordable Rental Housing Program, April 10, 2025 -- \"137 new "
            "rental apartment units in nine Maine communities\", \"$23.5 million "
            "in funding from the Rural Affordable Rental Housing Program\" plus "
            "\"$17.4 million in loans from MaineHousing\"; (2) urban state-subsidy "
            "round, June 17, 2025 -- \"awarded $13.4 million in state subsidies "
            "that will help create 129 new affordable rental homes in Lewiston "
            "and Portland\" (Martel II $5,400,000; Soleil I $5,400,000; Time and "
            "Temp Annex $2,593,908); (3) tax-credit round, Nov 21, 2025 -- \"the "
            "financing for 311 affordable apartments at eight development sites\", "
            "\"supported by $14.3 million in Federal and State affordable housing "
            "tax credits\". The Nov release independently re-states rounds 1-2 "
            "(\"$23.5 million to build 137 apartments ... through ... the Rural "
            "Affordable Rental Housing Program\"; \"$13.4 million to create 129 "
            "new apartments in Portland and Lewiston\"), the external cross-check "
            "for this category."
        ),
        "fy2025_amounts": [
            {"label_key": "me_amt_state_subsidy", "amount": 36900000},
            {"label_key": "me_amt_tax_credits", "amount": 14300000},
            {"label_key": "me_amt_rural_loans", "amount": 17400000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "rural_rental", "fy2025_units": 137, "fy2025_amount": 23500000,
             "color_group": "capital",
             # "Rural Affordable Rental Housing Program" appears verbatim in the
             # ACFR's governmental-fund program list ("Other Federal and State
             # Programs" -> "State of Maine", p.20) -- a state-subsidy program.
             "fund_type": "governmental",
             "fund_name": "Other Federal and State Programs - Rural Affordable Rental Housing Program",
             "fy2026": _FY26_PENDING},
            {"key": "state_subsidy", "fy2025_units": 129, "fy2025_amount": 13400000,
             "color_group": "capital",
             # State rental-development subsidy ("state subsidies ... resources
             # approved by the Legislature are now exhausted", June release).
             # The release names no separate fund; classified governmental by
             # program description (state money, not bond/tax-credit).
             # Confidence: medium.
             "fund_type": "governmental",
             "fund_name": "State rental development subsidy (inferred)",
             "fy2026": _FY26_PENDING},
            {"key": "tax_credit", "fy2025_units": 311, "fy2025_amount": 14300000,
             "color_group": "credit",
             # Federal LIHTC + Maine's State Affordable Housing Tax Credit (the
             # Nov release notes the $80M state credit, of which $65.5M has been
             # allocated since 2020). Credits flow to developers/investors, not
             # booked as a MaineHousing fund asset.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        # Development production status (accomplishments page) -- completed +
        # under construction. KPI-only; no per-project name+city list exists.
        "key": "multifamily_production",
        "unit_type": "units",
        "fy2025_actual": 2253,
        "fy2025_source_quote": (
            "Accomplishments page \"DEVELOPING AFFORDABLE HOUSING\" stat blocks: "
            "\"21 Projects Completed / 656 Units Completed\" and \"34 Projects "
            "Under Construction/In Underwriting / 1,597 Units Under "
            "Construction/In Underwriting\". 2,253 = 656 + 1,597 is this script's "
            "own sum (the page prints no combined total). No name/city/unit "
            "breakdown is disclosed for these 55 projects, so this category has "
            "no bubble-map projects of its own -- distinct from the 20 award "
            "developments in multifamily_rental_awards (see module docstring)."
        ),
        "fy2025_amounts": [],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "completed", "fy2025_units": 656, "fy2025_amount": None,
             "color_group": "capital",
             # Production aggregates every financing source (proprietary
             # multifamily loans + LIHTC + governmental grants) -- no single
             # fund type applies to a completion-status bucket.
             "fund_type": "mixed", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "under_construction", "fy2025_units": 1597, "fy2025_amount": None,
             "color_group": "capital",
             "fund_type": "mixed", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        # Section 8 Housing Choice Voucher program (ongoing rental assistance).
        "key": "rental_assistance_hcv",
        "unit_type": "households",
        "fy2025_actual": 3525,
        "fy2025_source_quote": (
            "Accomplishments page \"rental programs\" stat block: \"3,525 AVG "
            "HOUSEHOLDS SERVED PER MONTH -- Housing Choice Vouchers Program\" "
            "(plus \"96 ACTIVE PARTICIPANTS -- ReStart/Family Self Sufficiency "
            "Program\"). This is an average monthly household count, not a "
            "construction total; no dollar figure is disclosed on the page."
        ),
        "fy2025_amounts": [],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "hcv", "fy2025_units": 3525, "fy2025_amount": None,
             "color_group": "trust",
             # "Section 8 Housing Programs" is an explicit governmental fund
             # (Notes, Fund Structure, p.19): "Housing Choice Voucher" is one
             # of its listed programs.
             "fund_type": "governmental", "fund_name": "Section 8 Housing Programs",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        # Energy assistance (HEAP and the related DHHS/DOE heating programs).
        # Non-additive: these are separate "households helped" counts and a
        # household can receive more than one (e.g. HEAP + ECIP crisis aid),
        # so the subprogram counts are reference chips, not a partition.
        "key": "energy_assistance",
        "unit_type": "households",
        "fy2025_actual": 45345,
        "fy2025_source_quote": (
            "Accomplishments page \"heating assistance programs\" stat blocks: "
            "\"45,345 HOUSEHOLDS HELPED -- Home Energy Assistance Program (HEAP)\"; "
            "\"7,200 HOUSEHOLDS HELPED -- Energy Crisis Intervention Program "
            "(ECIP)\"; \"197 HOUSEHOLDS HELPED -- Central Heating Improvement "
            "Program (CHIP)\"; \"94 HOUSEHOLDS HELPED -- Heat Pump Program\". "
            "No dollar figure is disclosed for any of these on the page."
        ),
        "fy2025_amounts": [],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "heap", "fy2025_units": 45345, "fy2025_amount": None,
             "color_group": "trust",
             # "Low Income Home Energy Assistance Program" is an explicit
             # governmental fund (Notes, Fund Structure, p.19) -- federally
             # funded through HHS.
             "fund_type": "governmental", "fund_name": "Low Income Home Energy Assistance Program",
             "fy2026": _FY26_PENDING},
            {"key": "ecip", "fy2025_units": 7200, "fy2025_amount": None,
             "color_group": "trust",
             "fund_type": "governmental", "fund_name": "Low Income Home Energy Assistance Program",
             "fy2026": _FY26_PENDING},
            {"key": "chip", "fy2025_units": 197, "fy2025_amount": None,
             "color_group": "trust",
             "fund_type": "governmental", "fund_name": "Low Income Home Energy Assistance Program",
             "fy2026": _FY26_PENDING},
            {"key": "heat_pump", "fy2025_units": 94, "fy2025_amount": None,
             "color_group": "trust",
             "fund_type": "governmental", "fund_name": "Low Income Home Energy Assistance Program",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        # Health/safety home-repair programs (separate from energy assistance).
        "key": "home_repair",
        "unit_type": "households",
        "fy2025_actual": 465,
        "fy2025_source_quote": (
            "Accomplishments page \"home repair programs\" stat blocks: \"236 "
            "HOUSEHOLDS HELPED -- Home Repair Program\"; \"125 HOUSEHOLDS HELPED "
            "-- Weatherization Program\"; \"90 HOUSEHOLDS HELPED -- Lead Hazard "
            "Repair Program\"; \"14 HOUSEHOLDS HELPED -- Well Water Abatement "
            "Program\". 465 = 236 + 125 + 90 + 14 is this script's own sum (the "
            "page prints no combined total). No dollar figure is disclosed for "
            "any of these on the page."
        ),
        "fy2025_amounts": [],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "home_repair_program", "fy2025_units": 236, "fy2025_amount": None,
             "color_group": "capital",
             # Home Repair Program: a health/safety repair grant/loan program
             # administered under MaineHousing's governmental "Other Federal
             # and State Programs" (State of Maine) umbrella.
             "fund_type": "governmental", "fund_name": "Other Federal and State Programs",
             "fy2026": _FY26_PENDING},
            {"key": "weatherization", "fy2025_units": 125, "fy2025_amount": None,
             "color_group": "trust",
             # "Weatherization Assistance Program" is listed verbatim under the
             # ACFR's U.S. Department of Energy programs (Notes, p.20).
             "fund_type": "governmental", "fund_name": "Other Federal and State Programs",
             "fy2026": _FY26_PENDING},
            {"key": "lead_repair", "fy2025_units": 90, "fy2025_amount": None,
             "color_group": "trust",
             # "Lead-Based Paint Hazard Control Program" / "Lead Abatement
             # Program" (HUD + State of Maine) under Other Federal and State
             # Programs (Notes, p.20).
             "fund_type": "governmental", "fund_name": "Other Federal and State Programs",
             "fy2026": _FY26_PENDING},
            {"key": "well_water", "fy2025_units": 14, "fy2025_amount": None,
             "color_group": "capital",
             # "Well Water Treatment Program" (State of Maine) under Other
             # Federal and State Programs (Notes, p.20).
             "fund_type": "governmental", "fund_name": "Other Federal and State Programs",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# ---------------------------------------------------------------------------
# Multifamily rental award project-level detail: the three FY2025 rental
# award rounds. One row per development; "units" is each announcement's own
# per-development unit count. No street address is disclosed in any of the
# three releases (city/town only), so address=None throughout and every
# project geocodes to a city/town center (geocode_status="city_center").
#
# (name, city, units, [funding source keys])
# ---------------------------------------------------------------------------
RAW_PROJECTS = [
    # -- Rural Affordable Rental Housing Program, April 10, 2025 (9 / 137) --
    ("The J Palmer Merrill Block", "Skowhegan", 5, ["rural_rental"]),
    ("36 Cleaves Street", "Yarmouth", 18, ["rural_rental"]),
    ("Rangeley Workforce Housing", "Rangeley", 18, ["rural_rental"]),
    ("Rockland's Project Greenhouse", "Rockland", 12, ["rural_rental"]),
    ("Poland Elderly Housing Development", "Poland", 18, ["rural_rental"]),
    ("Clark Street", "Thomaston", 16, ["rural_rental"]),
    ("55 Weston Avenue Phase II", "Madison", 18, ["rural_rental"]),
    ("Rosa's Place", "Brunswick", 14, ["rural_rental"]),
    ("Asher's Village Apartments", "Winslow", 18, ["rural_rental"]),
    # -- Urban state-subsidy round, June 17, 2025 (3 / 129) --
    ("Martel II", "Lewiston", 44, ["state_subsidy"]),
    ("Soleil I", "Lewiston", 44, ["state_subsidy"]),
    ("Time and Temp Annex", "Portland", 41, ["state_subsidy"]),
    # -- Tax-credit round, November 21, 2025 (8 / 311) --
    ("Belfast Birches", "Belfast", 24, ["tax_credit"]),
    ("Quebec Commons", "Biddeford", 45, ["tax_credit"]),
    ("The Rochambeau", "Biddeford", 46, ["tax_credit"]),
    ("Soleil Apartments 2", "Lewiston", 28, ["tax_credit"]),
    ("The Woodbury", "Portland", 51, ["tax_credit"]),
    ("Cumberland Housing", "Portland", 50, ["tax_credit"]),
    ("Landry Heights", "South Portland", 38, ["tax_credit"]),
    ("McLain School Housing", "Rockland", 29, ["tax_credit"]),
]

# Per-project, per-funding-source dollar amount. Only the June round discloses
# per-project dollars (its release prints each subsidy). The Nov round gives a
# combined $14.3M credit figure (no per-project split), and the Rural round's
# per-project split is inside an image whose dollar columns did not OCR
# reliably -- so rural and Nov projects carry {} rather than half-transcribed
# per-project dollars (never fabricated). See module docstring.
PROJECT_SOURCE_AMOUNTS = {
    "Martel II": {"state_subsidy": 5400000},
    "Soleil I": {"state_subsidy": 5400000},
    "Time and Temp Annex": {"state_subsidy": 2593908},
}

# The three rounds' own printed unit totals (each asserted in
# verify_rental_awards), plus the expected cross-round sum.
EXPECTED_ROUND_UNITS = {"rural_rental": 137, "state_subsidy": 129, "tax_credit": 311}
EXPECTED_TOTAL_PROJECTS = 20
EXPECTED_TOTAL_UNITS = 577

FUNDING_COLOR_GROUP = {
    "rural_rental": "capital", "state_subsidy": "capital", "tax_credit": "credit",
}
FUNDING_PRIORITY = ["tax_credit", "state_subsidy", "rural_rental"]


def verify_project_count_and_units():
    errors = []
    if len(RAW_PROJECTS) != EXPECTED_TOTAL_PROJECTS:
        errors.append(f"project count: expected {EXPECTED_TOTAL_PROJECTS}, got {len(RAW_PROJECTS)}")
    total_units = sum(u for _n, _c, u, _s in RAW_PROJECTS)
    if total_units != EXPECTED_TOTAL_UNITS:
        errors.append(f"total units: expected {EXPECTED_TOTAL_UNITS}, got {total_units}")
    for source, expected in EXPECTED_ROUND_UNITS.items():
        got = sum(u for _n, _c, u, srcs in RAW_PROJECTS if source in srcs)
        if got != expected:
            errors.append(f"{source} units: expected {expected}, got {got}")
    # June round dollar split must reproduce its own $13.4M headline.
    june_sum = sum(PROJECT_SOURCE_AMOUNTS[n]["state_subsidy"]
                   for n in ("Martel II", "Soleil I", "Time and Temp Annex"))
    if round(june_sum / 1e6, 1) != 13.4:
        errors.append(f"June round subsidy sum ${june_sum:,} does not round to $13.4M")
    if errors:
        raise SystemExit("Project count/unit mismatch(es):\n" + "\n".join(errors))
    print("Rental-award verification passed: 20 projects; 137 rural + 129 state "
          "+ 311 tax-credit = 577 units; June round $13.4M subsidy reproduces "
          "the release's own headline.")


def verify_category_headlines():
    """Cross-check the accomplishments-page KPIs against their own printed
    numbers (each is transcribed verbatim; the only computed sums are the ones
    the page itself does not print)."""
    errors = []
    def cat(key):
        return next(c for c in CATEGORIES if c["key"] == key)
    if cat("homeownership_loans")["fy2025_actual"] != 1274:
        errors.append("homeownership headline != 1274")
    if cat("homeownership_loans")["fy2025_amounts"][0]["amount"] != 321778689:
        errors.append("homeownership loans != 321778689")
    prod = cat("multifamily_production")
    completed = next(s for s in prod["subprograms"] if s["key"] == "completed")
    under = next(s for s in prod["subprograms"] if s["key"] == "under_construction")
    if completed["fy2025_units"] + under["fy2025_units"] != prod["fy2025_actual"]:
        errors.append("multifamily_production headline != completed + under_construction sum")
    if completed["fy2025_units"] != 656 or under["fy2025_units"] != 1597:
        errors.append("completed/under_construction units != 656 / 1597")
    if cat("rental_assistance_hcv")["fy2025_actual"] != 3525:
        errors.append("HCV headline != 3525")
    eng = cat("energy_assistance")
    heap = next(s for s in eng["subprograms"] if s["key"] == "heap")
    if heap["fy2025_units"] != 45345:
        errors.append("HEAP != 45345")
    rep = cat("home_repair")
    if sum(s["fy2025_units"] for s in rep["subprograms"]) != rep["fy2025_actual"]:
        errors.append("home_repair headline != sum of its 4 programs")
    if errors:
        raise SystemExit("Category headline mismatch(es):\n" + "\n".join(errors))
    print("Category headlines verified against the accomplishments page's own "
          "printed figures (656+1597=2253, 236+125+90+14=465 are computed sums "
          "the page does not print).")


def build_projects():
    projects = []
    for name, city, units, sources in RAW_PROJECTS:
        coords = ME_CITY_COORDS.get(city)
        status = "city_center" if coords else "unresolved"
        source_amounts = PROJECT_SOURCE_AMOUNTS.get(name, {})
        projects.append({
            "id": name.lower().replace(" ", "-").replace("'", "")
                      .replace(".", "").replace("&", "and").replace("+", "plus"),
            "name": name,
            "address": None,
            "city": city,
            "lat": round(coords[0], 5) if coords else None,
            "lon": round(coords[1], 5) if coords else None,
            "units": units,
            "funding_sources": sources,
            "source_amounts": source_amounts,
            "total_amount": sum(source_amounts.values()) if source_amounts else None,
            "primary_color_group": FUNDING_COLOR_GROUP[sources[0]],
            "overlaps": len(sources) > 1,
            "geocode_status": status,
        })
    return projects


def main():
    verify_project_count_and_units()
    verify_category_headlines()
    print("Placing project towns/cities via Census 2024 Gazetteer points...")
    projects = build_projects()
    unresolved = [p["name"] for p in projects if p["geocode_status"] == "unresolved"]
    if unresolved:
        print(f"  {len(unresolved)} project(s) could not be placed: {unresolved}")
    city_center = [p["name"] for p in projects if p["geocode_status"] == "city_center"]
    print(f"  {len(city_center)}/20 project(s) placed at a town/city centre "
          f"(no street address disclosed).")

    payload = {
        "ME": {
            "hfa_name": "Maine State Housing Authority",
            "hfa_abbr": "MaineHousing",
            "fiscal_year": "FY2025",
            "source_title": ("MaineHousing 2025 Accomplishments (By the Numbers) + "
                             "FY2025 rental award announcements (Rural / June / November)"),
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
