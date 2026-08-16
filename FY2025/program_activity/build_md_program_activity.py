"""
Builds docs/md_program_activity.json from Maryland's "Fiscal Year 2025
Agency Impact Report" (Maryland Department of Housing and Community
Development / DHCD, whose housing-finance arm is the Community Development
Administration / CDA), plus DHCD's own FY2025 official press release
announcing that report, and (for GASB fund-type classification only) the
checked-in FY2025 audited financial statements of the Community Development
Administration Housing Revenue Bonds fund.

This is a KPI-ONLY build (RAW_PROJECTS=[]) -- like VA and MA. Maryland's
impact report discloses solid multi-category KPI figures (unit/household
counts plus per-program dollar funding totals) but NO complete per-project
cohort list, so the `projects` array is empty. See "Why RAW_PROJECTS is
empty" below.

Sources
------------------------------------------------------------------------
1. PRIMARY -- "FY25 DHCD Annual Report" / "Fiscal Year 2025 Agency Impact
   Report", a Framer-hosted web application (NOT a downloadable PDF):
       https://dhcdannualreport.maryland.gov/fy25
   Retrieved 2026-08-16 (HTTP 200). The report is a JavaScript-heavy SPA;
   its server-rendered HTML contains the full "FY25 Program Investments"
   chapter, which this build transcribed directly from a local HTML dump
   (program-by-program dollar funding totals and their sub-item breakdowns,
   all extracted verbatim -- see the "FY25 Program Investments" transcription
   below). It does NOT contain a per-development project list anywhere.

2. DHCD's own official press release announcing the report (published
   February 23, 2026), which states the FY2025 unit/household headline counts
   the report presents as image-rendered "By the Numbers" cards (the SPA's
   big-number cards are image/JS-rendered and do not survive plain-text
   extraction; the press release states the same figures as text):
       https://news.maryland.gov/dhcd/2026/02/23/maryland-department-of-housing-and-community-development-generates-8-5-billion-in-economic-impact-supports-nearly-31000-jobs-in-fiscal-year-2025/
   (also fetched locally 2026-08-16, HTTP 200.)

3. FY2025/txt/MD_CDA_FY2025_ACFR.txt -- "COMMUNITY DEVELOPMENT
   ADMINISTRATION HOUSING REVENUE BONDS, FINANCIAL STATEMENTS, YEARS ENDED
   JUNE 30, 2025 AND 2024" (audited by CliftonLarsonAllen LLP). VERIFIED to
   be the correct entity before use: the Independent Auditors' Report covers
   "the Community Development Administration Housing Revenue Bonds (the
   Fund) of the Department of Housing and Community Development of the State
   of Maryland, as of and for the years ended June 30, 2025 and 2024". This
   is a proprietary/enterprise FUND (single-purpose bond fund), NOT a
   department-wide CAFR, and its "Emphasis of Matter" note states it "presents
   only ... the Fund and do[es] not ... present fairly the financial position
   of the Department" -- see fund-type classification below for the
   consequence of that scoping.

Fiscal year
------------------------------------------------------------------------
DHCD's fiscal year is the State of Maryland's, July 1 - June 30 (the ACFR is
"years ended June 30, 2025 and 2024"; the impact report is titled "FY25").
fiscal_year is therefore "FY2025". No title-year-vs-content-year mismatch:
the press release repeatedly scopes every figure with "In Fiscal Year 2025".

FY25 Program Investments transcription (report HTML, "FY25 Program
Investments" chapter -- every figure below is transcribed from this build's
own local HTML dump, not from memory or a secondary source)
------------------------------------------------------------------------
The report's own chapter text: "The Department's programs have invested
$3,019,620,328 in communities across the state ... (Program totals in
millions)." Then, program-by-program (dollar figures are the report's own
printed, million-rounded program totals, each followed by its printed sub-item
breakdown):

  * Rental Housing Development -- $1.375 billion
      $724M Multifamily Revenue Bond Loan Program; $485M Federal Low Income
      Housing 4% Tax Credit Equity; $78M Federal Low Income Housing 9% Tax
      Credit Equity; $64M Rental Housing Works Program; $11M Rental Housing
      Loan Programs; $6M Federal HOME Investment Partnership Program; $4M
      Shelter and Transitional Housing Program; $2M National Housing Trust
      Fund; $1M Partnership Rental Housing Program.
      (724+485+78+64+11+6+4+2+1 = 1,375 -- exact, verified in
      verify_category_consistency().)
  * Homeownership and Special Needs Housing -- $1.011 billion
      $960M Maryland Mortgage Program Mortgage Backed Securities; $43M
      Downpayment Assistance Programs; $4M Single Family Housing
      Rehabilitation Programs; $2M Federal HOME Investment Partnership
      Program; $1M Housing Programs for Individuals with Disabilities/Home
      Ability Program; $1M Lead Paint Abatement Program (Including HH4Ks).
      (960+43+4+2+1+1 = 1,011 -- exact, verified.)
  * Housing Energy Efficiency -- $70 million
      $39M Multifamily Housing Energy Efficiency Programs; $19M EmPOWER MD
      Single Family Housing Energy Efficiency Programs; $8M Other Single
      Family Housing Energy Efficiency Programs; $4M Federal Single Family
      Housing Weatherization Assistance Program.
      (39+19+8+4 = 70 -- exact, verified.)
  * Homeless Solutions -- $32 million
      $18M Homelessness Solutions Program; $10M Community Services Block
      Grant; $2M Housing Counseling Program (Formerly Foreclosure
      Prevention); $1M Older Adult Home Modification Program (OAHMP); $1M
      Emergency Rental Assistance Program; $200 thousand Neighborhood Housing
      Services (OAG); $100 thousand Youth Homeless Systems Improvement (YSHI).
      (18+10+2+1+1+0.2+0.1 = 32.3 -- the report's own "$32 million" headline
      is a rounded presentation of this $32.3M sum, a source-internal
      rounding reproduced faithfully, asserted not resolved -- verified.)
  * (Not modeled as KPI categories, documented for completeness -- all
    dollar-only or non-housing lines with no paired housing unit/household
    count: Rental Services $304M; Local Government Finance $12M; Division of
    Business Development $21M; Neighborhood Revitalization $180M; Statewide
    Broadband $18M. Broadband's "71,498 households connected" is an
    infrastructure-connectivity metric, not a housing program activity, and
    has no housing-program icon bucket -- excluded by scope.)

FY2025 unit/household headline counts (official DHCD press release,
February 23, 2026 -- transcribed verbatim)
------------------------------------------------------------------------
  * Affordable rental housing: "In Fiscal Year 2025, the Department financed
    3,997 newly constructed or substantially rehabilitated units for
    families, seniors and people at all income levels through 36 projects in
    Maryland."  -> 3,997 units, 36 projects.
  * Homeownership: "The program [Maryland Mortgage Program] averages $1
    billion in mortgage loan reservations annually and provided 3,070
    mortgages for homebuyers in Fiscal Year 2025."  -> 3,070 mortgages.
  * Energy efficiency: "The Department's Energy Efficiency programs provided
    assistance to nearly 3,500 households in Fiscal Year 2025 to make homes
    safer, more comfortable and accessible..."  -> ~3,500 households (the
    source's own "nearly" qualifier is preserved; 3500 is used as the
    headline with that qualifier quoted verbatim, matching VA's use of its
    own rounded "$1.4B" verbatim).
  * Homeless solutions: "In Fiscal Year 2025, the division supported 21,495
    people and 18,423 households."  -> 18,423 households (21,495 people).

EXTERNAL corroboration / one deliberately-noted discrepancy
------------------------------------------------------------------------
DHCD's earlier August 4, 2025 press release ("...Finances Highest Level of
Affordable Housing Production in Nearly a Decade") independently confirms the
3,997-unit / 36-project rental figure (matches the Feb 2026 report exactly).
It also says MMP "provided mortgages to almost 4,300 Marylanders and their
families in the amount exceeding $1 billion" -- but that release scopes it
"based on the numbers to date" (i.e. a mid-year preliminary count before
FY2025 closed). This build uses the impact report's final full-year figure
(3,070 mortgages), records the ~4,300 "numbers to date" phrasing here, and
does NOT conflate the two. No figure is invented.

Why RAW_PROJECTS is empty ([]) -- the report gives aggregates only
------------------------------------------------------------------------
The FY2025 Agency Impact Report discloses program-level aggregates (3,997
rental units across 36 projects; 3,070 MMP mortgages; ~3,500 energy
households; 18,423 homeless-solutions households) and a per-program dollar
funding breakdown, but it does NOT publish a complete, extractable list of the
36 individual multifamily developments (or the individual mortgages). The
"36 projects" is a count, not a roster. There is therefore no honest
per-project cohort to transcribe -- exactly the same situation documented in
VA's and MA's builds. RAW_PROJECTS is [] and the output `projects` array is
empty, an honest reflection of the source, not a placeholder. The frontend
renders the KPI cards normally and the bubble map with 0 markers.

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
Cross-referenced against FY2025/txt/MD_CDA_FY2025_ACFR.txt. CRITICAL SCOPE
LIMITATION, verified in the file itself: that .txt is ONLY the "Community
Development Administration Housing Revenue Bonds" fund -- a single proprietary
(business-type/enterprise) fund whose statements are Statements of Net
Position / Revenues, Expenses and Changes in Net Position / Cash Flows, i.e.
the GASB proprietary-fund format -- and its "Emphasis of Matter" paragraph
says it does "not purport to, and do[es] not, present fairly the financial
position of the Department of Housing and Community Development ... as a
whole". So the ACFR only classifies the CDA's own bond-financed lending; the
grant/assistance programs (HOME, HTF, energy, homeless, state rental
programs) are accounted for elsewhere in the Department and are classified
conservatively by program description below, with confidence documented.
  - "proprietary" (HIGH confidence -- the CDA's own bond-financed lending,
    i.e. the Housing Revenue Bonds fund the checked-in ACFR actually is):
      * multifamily_revenue_bond ($724M) -- the report's own "Multifamily
        Revenue Bond Loan Program"; the ACFR's Note 4 states "All multi-
        family mortgage loans are secured by first liens on the related
        property" and the Statements show Mortgage Loans / Mortgage-Backed
        Securities as the Fund's assets.
      * rental_housing_loans ($11M) and partnership_rental ($1M) -- same
        bond-financed multifamily lending family (the report lists them
        alongside the Revenue Bond program; the ACFR is the fund that holds
        these loans). partnership_rental confidence: medium (a small
        lending/partnership program, classified by description).
      * mmp_mbs ($960M) -- "Maryland Mortgage Program Mortgage Backed
        Securities": single-family mortgage revenue bond activity, the same
        business-type lending structure as the multifamily fund (the ACFR
        covers multifamily MBS specifically, but MMP is the single-family
        analog of the same CDA mortgage-revenue-bond enterprise). Confidence:
        medium-high (by description; the single-family program is not in this
        particular .txt).
  - "off_balance_sheet" (HIGH confidence -- tax-credit equity flows to
    developers/investors, never booked as a CDA/HFA asset; same treatment as
    every other pilot state's LIHTC):
      * lihtc_4pct ($485M) and lihtc_9pct ($78M) -- "Federal Low Income
        Housing 4%/9% Tax Credit Equity" is the equity raised by developers
        from the federal LIHTC; the Department allocates the credits and
        facilitates the equity, but does not carry it as its own asset.
  - "governmental" (MEDIUM confidence -- federal/state grant and
    assistance programs of the Department, accounted for outside the CDA's
    proprietary bond fund, most consistent with special-revenue-fund
    (governmental) treatment; the checked-in .txt does not cover them, so
    this is a conservative classification by program description, not a
    literal ACFR line item):
      * rental_housing_works ($64M) -- state-funded rental gap financing.
      * home_rental ($6M) and nhtf ($2M) -- federal HOME / National Housing
        Trust Fund grants (the .txt makes no mention of either; unlike AR's
        ADFA, whose SEFA carried HOME/NHTF on its own books, there is no
        evidence these sit inside the CDA Housing Revenue Bonds fund).
      * shelter_transitional ($4M), downpayment_assistance ($43M),
        single_family_rehab ($4M), home_homebuyer ($2M),
        disability_homeability ($1M), lead_paint ($1M) -- state/federal
        assistance programs.
      * All four energy_efficiency subprograms and all seven
        homeless_solutions subprograms -- federal/state grant and assistance
        programs (WAP/EmPOWER/weatherization; Homelessness Solutions
        Program/CSBG/ERA/etc.).

Category-level methodology
------------------------------------------------------------------------
Every category is additive=False. The source's dollar figures break down by
FUNDING SOURCE, not by a population partition of the headline unit/household
count -- e.g. the 3,997 rental units cannot be split into "multifamily
revenue bond units" vs "LIHTC units" (a single development typically layers
several of the nine funding sources). A naive stacked bar would therefore
over- or under-count. The subprograms are shown as dollar-only reference
chips (fy2025_units=None on each), exactly like VA's reach_virginia, while
the headline unit/household count carries the KPI. Each category's printed
program-dollar total is carried once as an fy2025_amounts chip and again,
decomposed, as its subprograms -- mirroring how the report itself prints a
headline total above its sub-item list. The Homeless Solutions "$32 million"
headline rounds down its own $32.3M sub-item sum (a source-internal rounding,
documented not resolved).

Excluded historical/cumulative figures
------------------------------------------------------------------------
The report's Broadband section contains "Since 2017, the Office of Statewide
Broadband has invested over $270 million, bringing connectivity to more than
71,000 previously unserved homes and businesses statewide" -- a cumulative
since-2017 figure, NOT FY2025, and in any case broadband is out of scope.
Not used anywhere.

fy2026
------------------------------------------------------------------------
The FY2025 Agency Impact Report is backward-looking with no forward-looking/
projected-activity section for FY2026. Every fy2026 field is therefore
{value: None, amount: None, closed: False, note_key: "mdFy26NotePending"}.
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "md_program_activity.json"

SOURCE_URL = "https://dhcdannualreport.maryland.gov/fy25"
SOURCE_FILE = (
    "FY25 DHCD Annual Report (dhcdannualreport.maryland.gov/fy25) -- a Framer "
    "SPA, not a downloadable PDF; program-dollar figures transcribed from this "
    "build's local HTML dump. Unit/household headline counts transcribed from "
    "DHCD's official press release "
    "news.maryland.gov/dhcd/2026/02/23/maryland-department-of-housing-and-"
    "community-development-generates-8-5-billion-in-economic-impact-supports-"
    "nearly-31000-jobs-in-fiscal-year-2025/ (the report's own By-the-Numbers "
    "cards are image/JS-rendered and do not survive text extraction). Neither "
    "is archived as a PDF under FY2025/program_activity/pdf/ because neither "
    "is a downloadable PDF."
)
RETRIEVED = "2026-08-16"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                 "note_key": "mdFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data. Every dollar figure is the report's own printed,
# million-rounded program-funding number; every unit/household count is the
# press release's own FY2025 headline. See the module docstring for the full
# transcription and the fund-type classification rationale.
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "rental_housing",
        "unit_type": "units",
        "fy2025_actual": 3997,
        "fy2025_source_quote": (
            "\"In Fiscal Year 2025, the Department financed 3,997 newly constructed "
            "or substantially rehabilitated units for families, seniors and people at "
            "all income levels through 36 projects in Maryland.\" (DHCD FY2025 Agency "
            "Impact Report press release, Feb 23, 2026; independently corroborated by "
            "DHCD's Aug 4, 2025 press release, which also reports 3,997 units / 36 "
            "projects.) The report's \"FY25 Program Investments\" chapter prints the "
            "dollar side as \"Rental Housing Development -- $1.375 billion\" with a "
            "nine-item funding-source breakdown (724+485+78+64+11+6+4+2+1 = $1,375M "
            "exactly, verified in verify_category_consistency()). The nine dollar "
            "sub-items are FUNDING SOURCES, not a population partition of the 3,997 "
            "units (a single development layers several of them), so the category is "
            "additive=False and the subprograms are dollar-only reference chips."
        ),
        "fy2025_amounts": [
            {"label_key": "md_amt_rental_total", "amount": 1375000000},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "multifamily_revenue_bond", "fy2025_units": None, "fy2025_amount": 724000000,
             "color_group": "bond",
             # CDA's own bond-financed multifamily lending; the checked-in
             # ACFR IS the "Community Development Administration Housing
             # Revenue Bonds" proprietary fund holding these loans.
             "fund_type": "proprietary", "fund_name": "Community Development Administration Housing Revenue Bonds (proprietary fund)",
             "fy2026": _FY26_PENDING},
            {"key": "lihtc_4pct", "fy2025_units": None, "fy2025_amount": 485000000,
             "color_group": "credit",
             # Federal LIHTC equity flows to developers/investors; never
             # booked as a CDA asset. Same off-balance-sheet treatment as
             # every other pilot state's LIHTC.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "lihtc_9pct", "fy2025_units": None, "fy2025_amount": 78000000,
             "color_group": "credit",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "rental_housing_works", "fy2025_units": None, "fy2025_amount": 64000000,
             "color_group": "capital",
             # State-funded rental gap-financing program; not part of the CDA
             # bond fund (the checked-in .txt does not mention it). Classified
             # conservatively as a Department grant program. Confidence: medium.
             "fund_type": "governmental", "fund_name": "Rental Housing Works Program (state-funded; not in the CDA Housing Revenue Bonds fund)",
             "fy2026": _FY26_PENDING},
            {"key": "rental_housing_loans", "fy2025_units": None, "fy2025_amount": 11000000,
             "color_group": "bond",
             "fund_type": "proprietary", "fund_name": "Community Development Administration Housing Revenue Bonds (proprietary fund)",
             "fy2026": _FY26_PENDING},
            {"key": "home_rental", "fy2025_units": None, "fy2025_amount": 6000000,
             "color_group": "trust",
             # Federal HOME grant. Not mentioned in the checked-in .txt (which
             # covers only the bond fund), so classified by description.
             # Confidence: medium.
             "fund_type": "governmental", "fund_name": "Federal HOME Investment Partnerships Program (not in the CDA Housing Revenue Bonds fund)",
             "fy2026": _FY26_PENDING},
            {"key": "shelter_transitional", "fy2025_units": None, "fy2025_amount": 4000000,
             "color_group": "capital",
             "fund_type": "governmental", "fund_name": "Shelter and Transitional Housing Program (state-funded)",
             "fy2026": _FY26_PENDING},
            {"key": "nhtf", "fy2025_units": None, "fy2025_amount": 2000000,
             "color_group": "trust",
             # Federal National Housing Trust Fund grant; not in the .txt.
             # Confidence: medium.
             "fund_type": "governmental", "fund_name": "National Housing Trust Fund (federal; not in the CDA Housing Revenue Bonds fund)",
             "fy2026": _FY26_PENDING},
            {"key": "partnership_rental", "fy2025_units": None, "fy2025_amount": 1000000,
             "color_group": "bond",
             # Lending/partnership program in the multifamily financing family.
             # Confidence: medium.
             "fund_type": "proprietary", "fund_name": "Partnership Rental Housing Program (CDA multifamily lending)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "homeownership",
        "unit_type": "households",
        "fy2025_actual": 3070,
        "fy2025_source_quote": (
            "\"The program [Maryland Mortgage Program] averages $1 billion in mortgage "
            "loan reservations annually and provided 3,070 mortgages for homebuyers in "
            "Fiscal Year 2025.\" (DHCD FY2025 Agency Impact Report press release, Feb 23, "
            "2026.) DHCD's earlier Aug 4, 2025 press release had said MMP \"provided "
            "mortgages to almost 4,300 Marylanders and their families\" but scoped it "
            "\"based on the numbers to date\" -- a mid-year preliminary count; the impact "
            "report's 3,070 is the final full-year figure and is the one used here. The "
            "report's dollar side is \"Homeownership and Special Needs Housing -- $1.011 "
            "billion\" (960+43+4+2+1+1 = $1,011M exactly, verified) -- note this program "
            "total also includes ~$8M of special-needs items (single-family rehab, HOME "
            "homebuyer, HomeAbility, lead paint) beyond MMP's own $960M mortgage-backed "
            "securities + $43M downpayment assistance; the scope is documented, not hidden."
        ),
        "fy2025_amounts": [
            {"label_key": "md_amt_homeownership_total", "amount": 1011000000},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "mmp_mbs", "fy2025_units": None, "fy2025_amount": 960000000,
             "color_group": "bond",
             # MMP single-family mortgage-revenue-bond activity -- the
             # single-family analog of the CDA's proprietary bond fund.
             # Confidence: medium-high (by description; the checked-in .txt
             # covers the multifamily bond fund, not MMP).
             "fund_type": "proprietary", "fund_name": "Maryland Mortgage Program mortgage revenue bonds (single-family)",
             "fy2026": _FY26_PENDING},
            {"key": "downpayment_assistance", "fy2025_units": None, "fy2025_amount": 43000000,
             "color_group": "capital",
             # DPA layered onto MMP loans; administered with MMP but a grant,
             # not a bond-fund asset. Classified conservatively. Confidence:
             # medium.
             "fund_type": "governmental", "fund_name": "Downpayment Assistance Programs (with Maryland Mortgage Program)",
             "fy2026": _FY26_PENDING},
            {"key": "single_family_rehab", "fy2025_units": None, "fy2025_amount": 4000000,
             "color_group": "capital",
             "fund_type": "governmental", "fund_name": "Single Family Housing Rehabilitation Programs",
             "fy2026": _FY26_PENDING},
            {"key": "home_homebuyer", "fy2025_units": None, "fy2025_amount": 2000000,
             "color_group": "trust",
             "fund_type": "governmental", "fund_name": "Federal HOME Investment Partnerships Program (homebuyer)",
             "fy2026": _FY26_PENDING},
            {"key": "disability_homeability", "fy2025_units": None, "fy2025_amount": 1000000,
             "color_group": "capital",
             "fund_type": "governmental", "fund_name": "Home Ability Program (housing for individuals with disabilities)",
             "fy2026": _FY26_PENDING},
            {"key": "lead_paint", "fy2025_units": None, "fy2025_amount": 1000000,
             "color_group": "capital",
             "fund_type": "governmental", "fund_name": "Lead Paint Abatement Program (incl. HH4Ks)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "energy_efficiency",
        "unit_type": "households",
        "fy2025_actual": 3500,
        "fy2025_source_quote": (
            "\"The Department's Energy Efficiency programs provided assistance to nearly "
            "3,500 households in Fiscal Year 2025 to make homes safer, more comfortable "
            "and accessible to Marylanders.\" (DHCD FY2025 Agency Impact Report press "
            "release, Feb 23, 2026.) The source's own \"nearly\" qualifier is preserved "
            "here (3500 is used as the headline with the qualifier quoted verbatim). The "
            "report's dollar side is \"Housing Energy Efficiency -- $70 million\" "
            "(39+19+8+4 = $70M exactly, verified). Dollar sub-items are funding sources, "
            "not a partition of the household count, so additive=False."
        ),
        "fy2025_amounts": [
            {"label_key": "md_amt_energy_total", "amount": 70000000},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "multifamily_energy", "fy2025_units": None, "fy2025_amount": 39000000,
             "color_group": "capital",
             "fund_type": "governmental", "fund_name": "Multifamily Housing Energy Efficiency Programs",
             "fy2026": _FY26_PENDING},
            {"key": "empower_md", "fy2025_units": None, "fy2025_amount": 19000000,
             "color_group": "capital",
             "fund_type": "governmental", "fund_name": "EmPOWER MD Single Family Energy Efficiency Programs",
             "fy2026": _FY26_PENDING},
            {"key": "other_single_family_energy", "fy2025_units": None, "fy2025_amount": 8000000,
             "color_group": "capital",
             "fund_type": "governmental", "fund_name": "Other Single Family Housing Energy Efficiency Programs",
             "fy2026": _FY26_PENDING},
            {"key": "weatherization_wap", "fy2025_units": None, "fy2025_amount": 4000000,
             "color_group": "capital",
             # Federal Weatherization Assistance Program (WAP) -- a federal
             # pass-through grant program, governmental-type. Confidence:
             # medium.
             "fund_type": "governmental", "fund_name": "Federal Single Family Weatherization Assistance Program (WAP)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "homeless_solutions",
        "unit_type": "households",
        "fy2025_actual": 18423,
        "fy2025_source_quote": (
            "\"In Fiscal Year 2025, the division supported 21,495 people and 18,423 "
            "households.\" (DHCD FY2025 Agency Impact Report press release, Feb 23, 2026, "
            "describing the Division of Homeless Solutions.) The report's dollar side is "
            "\"Homeless Solutions -- $32 million\" with a seven-item breakdown that sums "
            "to $32.3M (18+10+2+1+1+0.2+0.1); the report's own \"$32 million\" headline "
            "rounds that sum down -- a source-internal rounding reproduced faithfully "
            "(asserted in verify_category_consistency, not silently resolved). Sub-items "
            "are funding sources, not a partition of the household count, so additive=False."
        ),
        "fy2025_amounts": [
            {"label_key": "md_amt_homeless_total", "amount": 32000000},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "homelessness_solutions_program", "fy2025_units": None, "fy2025_amount": 18000000,
             "color_group": "capital",
             "fund_type": "governmental", "fund_name": "Homelessness Solutions Program",
             "fy2026": _FY26_PENDING},
            {"key": "csbg", "fy2025_units": None, "fy2025_amount": 10000000,
             "color_group": "trust",
             # Federal Community Services Block Grant pass-through.
             # Confidence: medium.
             "fund_type": "governmental", "fund_name": "Community Services Block Grant (federal pass-through)",
             "fy2026": _FY26_PENDING},
            {"key": "housing_counseling", "fy2025_units": None, "fy2025_amount": 2000000,
             "color_group": "capital",
             "fund_type": "governmental", "fund_name": "Housing Counseling Program (formerly Foreclosure Prevention)",
             "fy2026": _FY26_PENDING},
            {"key": "oahmp", "fy2025_units": None, "fy2025_amount": 1000000,
             "color_group": "capital",
             "fund_type": "governmental", "fund_name": "Older Adult Home Modification Program (OAHMP)",
             "fy2026": _FY26_PENDING},
            {"key": "emergency_rental_assistance", "fy2025_units": None, "fy2025_amount": 1000000,
             "color_group": "capital",
             "fund_type": "governmental", "fund_name": "Emergency Rental Assistance Program",
             "fy2026": _FY26_PENDING},
            {"key": "nhs_oag", "fy2025_units": None, "fy2025_amount": 200000,
             "color_group": "capital",
             "fund_type": "governmental", "fund_name": "Neighborhood Housing Services (OAG)",
             "fy2026": _FY26_PENDING},
            {"key": "yshi", "fy2025_units": None, "fy2025_amount": 100000,
             "color_group": "capital",
             "fund_type": "governmental", "fund_name": "Youth Homeless Systems Improvement (YSHI)",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# Per this build's explicit task briefing (KPI-ONLY): Maryland's impact report
# discloses program-level aggregates and a per-program dollar breakdown but NO
# complete, extractable per-project cohort list (the "36 projects" is a count,
# not a roster). RAW_PROJECTS is intentionally empty; see the module docstring
# "Why RAW_PROJECTS is empty". This is the allowed, honest outcome -- the
# frontend renders the KPI cards normally and the bubble map with 0 markers.
RAW_PROJECTS = []


def verify_category_consistency():
    """Dual-verification gate (hard-error on mismatch).

    Internal: each category's printed sub-item dollar breakdown must reproduce
    the source's own printed program-funding total exactly (the one deliberate
    exception is Homeless Solutions, where the report's own "$32 million"
    headline rounds down its own $32.3M sub-item sum -- asserted, not
    resolved). External: the unit/household headline counts must match the
    independently-recorded FY2025 figures DHCD published across its two press
    releases.
    """
    errors = []

    # --- Internal: sub-item dollar sums vs printed program totals (in $M) ---
    def sub_sum(key):
        cat = next(c for c in CATEGORIES if c["key"] == key)
        return sum(sp["fy2025_amount"] for sp in cat["subprograms"])

    # rental_housing: 724+485+78+64+11+6+4+2+1 = 1,375 (million) exactly.
    rental_sum = sub_sum("rental_housing")
    if rental_sum != 1375000000:
        errors.append(f"rental_housing subprogram dollars sum to ${rental_sum:,}, expected $1,375,000,000")

    # homeownership: 960+43+4+2+1+1 = 1,011 (million) exactly.
    ho_sum = sub_sum("homeownership")
    if ho_sum != 1011000000:
        errors.append(f"homeownership subprogram dollars sum to ${ho_sum:,}, expected $1,011,000,000")

    # energy_efficiency: 39+19+8+4 = 70 (million) exactly.
    ee_sum = sub_sum("energy_efficiency")
    if ee_sum != 70000000:
        errors.append(f"energy_efficiency subprogram dollars sum to ${ee_sum:,}, expected $70,000,000")

    # homeless_solutions: 18+10+2+1+1+0.2+0.1 = 32.3 (million); the report's
    # printed headline is a rounded "$32 million" -- assert both facts.
    hs_sum = sub_sum("homeless_solutions")
    if hs_sum != 32300000:
        errors.append(f"homeless_solutions subprogram dollars sum to ${hs_sum:,}, expected $32,300,000")
    hs = next(c for c in CATEGORIES if c["key"] == "homeless_solutions")
    hs_headline = hs["fy2025_amounts"][0]["amount"]
    if hs_headline != 32000000:
        errors.append(f"homeless_solutions printed headline is ${hs_headline:,}, expected $32,000,000 (the rounded \"$32 million\")")

    # --- Every subprogram key must be globally unique (the i18n mdSub_* keys
    # are global across categories) ---
    all_keys = [sp["key"] for c in CATEGORIES for sp in c["subprograms"]]
    dupes = sorted({k for k in all_keys if all_keys.count(k) > 1})
    if dupes:
        errors.append(f"duplicate subprogram key(s) across categories: {dupes}")

    # --- External: headline unit/household counts vs the independently
    # recorded FY2025 figures ---
    expected_actuals = {
        "rental_housing": 3997,     # "3,997 ... units ... through 36 projects"
        "homeownership": 3070,      # "3,070 mortgages for homebuyers"
        "energy_efficiency": 3500,  # "nearly 3,500 households"
        "homeless_solutions": 18423,  # "18,423 households"
    }
    for key, expected in expected_actuals.items():
        cat = next(c for c in CATEGORIES if c["key"] == key)
        if cat["fy2025_actual"] != expected:
            errors.append(f"{key}: fy2025_actual {cat['fy2025_actual']} != expected {expected}")

    if RAW_PROJECTS:
        errors.append(
            "RAW_PROJECTS is expected to be empty for MD (KPI-only build) -- see "
            "module docstring; if a complete project-level list has since become "
            "available, update the docstring before populating this list."
        )

    if errors:
        raise SystemExit("Category consistency mismatch(es):\n" + "\n".join(errors))

    print("Internal verification: sub-item dollar sums reproduce the report's own "
          "printed program totals -- rental_housing $1.375B, homeownership $1.011B, "
          "energy_efficiency $70M, homeless_solutions $32.3M (printed headline rounds "
          "to $32M).")
    print("External verification: headline counts match DHCD's independently-recorded "
          "FY2025 figures -- 3,997 units / 3,070 mortgages / ~3,500 energy households / "
          "18,423 homeless households.")
    print("RAW_PROJECTS confirmed empty as expected (KPI-only; no per-project roster "
          "in the source).")


def main():
    verify_category_consistency()
    payload = {
        "MD": {
            "hfa_name": "Maryland Community Development Administration (CDA), Department of Housing and Community Development",
            "hfa_abbr": "Maryland CDA",
            "fiscal_year": "FY2025",
            "source_title": "Maryland DHCD Fiscal Year 2025 Agency Impact Report (\"FY25 DHCD Annual Report\") -- FY25 Program Investments chapter + official DHCD press release (unit/household headline counts)",
            "source_url": SOURCE_URL,
            "source_file": SOURCE_FILE,
            "retrieved": RETRIEVED,
            "categories": CATEGORIES,
            "projects": RAW_PROJECTS,
        }
    }
    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT_PATH} ({len(RAW_PROJECTS)} projects, {len(CATEGORIES)} categories)")


if __name__ == "__main__":
    main()
