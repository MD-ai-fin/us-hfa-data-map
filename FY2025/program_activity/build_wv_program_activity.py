"""
Builds docs/wv_program_activity.json for the West Virginia Housing Development
Fund ("WVHDF") from its FY2025 Annual Report (an interactive, server-rendered
web report -- there is no single downloadable PDF), plus WVHDF's own FY2025
audited financial statements (for GASB fund-type classification). This is a
KPI-layer-only build (RAW_PROJECTS=[], projects:[]) -- see "Why RAW_PROJECTS
is empty" below.

Source
------------------------------------------------------------------------
WVHDF FY2025 Annual Report, an interactive web report (not a downloadable
PDF; figures below were transcribed from the report's own server-rendered
HTML pages, verified live 2026-08-16):
    https://www.wvhdf.com/annual-report-2025/
    (pages fetched with ?ar-page=home / about / single-family-programs-
    overview / multi-family-programs-overview)

Because the primary source is an interactive web report rather than a PDF,
there is nothing to archive under FY2025/program_activity/pdf/WV_*.pdf; the
URL above is recorded in source_url, and the specific page slugs are cited in
each quote. (The report's own "Audited Financial Statements (PDF)" and
"Comprehensive Financial Report (PDF)" links point to the ACFR -- a separate
document used only for fund-type classification, below -- whose text is
already archived in the repo at FY2025/txt/WV_WVHDF_FY2025_ACFR.txt.)

Fiscal-year coverage
------------------------------------------------------------------------
The report is titled "FY2025 Annual Report" and repeatedly frames figures as
"FY25"/"fiscal year 2025". WVHDF's fiscal year ends June 30 (confirmed by the
ACFR title page: "Fiscal Years Ended June 30, 2025 and June 30, 2024"). The
Veterans' program is described as having "operated from September 2024 to
February 2025" (inside FY2025), and the rental-assistance narrative states the
FY2025 activity "sunset on September 30, 2025" (after FY2025's June 30 close
but still described as the FY2025 figure). fiscal_year is therefore "FY2025".

Headline figures transcribed verbatim
------------------------------------------------------------------------
Landing page (ar-page=home, "Welcome from WVHDF"):
  - Single-Family: "$254,382,975 Mortgage Loans"; "$233,339,147 Loaned through
    the Homeownership Program"; "$4,204,020 Loaned through the Movin' Up
    Program"; "$9,076,415 In down payment assistance through the Low Down Home
    Loan"; "In fiscal year 2025, we loaned more than $254 million and helped
    nearly 1,400 West Virginians become first-time homeowners."
  - Multifamily: "55 Loans and Awards Through Multifamily Programs";
    "$108,631,601 Total amount loaned and awarded through Multifamily
    Programs"; "781 Total Multifamily units produced"; "This work resulted in
    781 new or rehabilitated rental units financed through our Multifamily
    Division in fiscal year 2025."

Welcome letter (ar-page=about, "Welcome from WVHDF"):
  - Single-Family stat cards: "Single-Family Production $254,382,975" and
    "Production 1,414 Single-Family Loans".
  - Multifamily stat cards: "Multifamily Production $94,271,508 Including
    Private Investment"; "Multifamily Lending Program $88,383,000 Construction
    and Permanent Loans".
  - "Nearly 1,400 borrowers purchased their first home through our programs,
    with 86% taking advantage of down payment and closing cost assistance."
  - "In FY25, we committed roughly $110.4 million in funding to these projects
    through our slate of housing programs, resulting in 781 safe, affordable
    rental units in communities across the state."
  - "In FY25, we provided 2,634 at-risk households with more than $9.2 million
    in direct rental and utility assistance."

Single-Family Programs page (ar-page=single-family-programs-overview):
  - Homeownership Program: "In FY25, the Fund loaned more than $233 million to
    1,347 first-time home buyers through the Homeownership Program."
  - Movin' Up: "In FY25, the Fund loaned $4.2 million to 21 borrowers through
    the Movin' Up Program."
  - Low Down Home Loan: "The Fund loaned $9 million to 1,192 borrowers through
    the Low Down Home Loan." (also "About 86 percent of borrowers took
    advantage of this loan in FY25.")
  - Veterans: "This special program received $8 million in funding ... operated
    from September 2024 to February 2025. This program helped 32 veterans
    achieve their dreams of affordable homeownership."
  - On-Site Systems (OSLP): "In FY25, the program loaned $145,129 to 14
    property owners across the state."

IMPORTANT -- historical-cumulative figures explicitly excluded
------------------------------------------------------------------------
The report and its "Mission & Board" page also print the following "to
date"/"since inception" cumulative figures, which are NOT FY2025 activity and
are never used as a fy2025_* value anywhere in this script: "$4.5 billion in
bonds" (to date), "more than 170,000 housing units" (financed since 1969), and
the ACFR's cumulative "Total Units 176,413" / "176,000+ housing or
housing-related units" (through June 30, 2025). Only figures the source frames
as this fiscal year's own ("In FY25"/"fiscal year 2025") are used.

Category methodology and verification
------------------------------------------------------------------------
single_family_homeownership (additive=True): the report's own four disclosed
single-family loan programs sum to the headline exactly -- Homeownership
1,347 + Movin' Up 21 + Veterans 32 + On-Site Systems 14 = 1,414 single-family
loans (asserted in verify_category_consistency()). The Low Down Home Loan
(1,192 borrowers / $9,076,415) is a SECOND-position down-payment/closing-cost
assistance loan layered on a subset of the first mortgages (86% of borrowers;
1,192 < 1,347 + 21), so it is NOT part of the 1,414-loan partition and is
shown only as an fy2025_amounts reference chip, mirroring VA's handling of its
assistance products. The dollar total ($254,382,975) is the report's own
headline and is NOT fully itemized by the subprograms: the two disclosed loan
amounts sum to $233,339,147 + $4,204,020 = $237,543,167, with the Veterans'
loan dollars not disclosed (only the $8M State funding transfer) -- the
remainder (which includes the Veterans loans and any Secondary Market /
other activity) is not broken out. This is documented, not reconciled by
invention.

multifamily_rental_production (additive=True, single aggregate subprogram):
the report does not give a clean per-program partition of the 781 units (the
interactive Multifamily Programs page's per-program impact cards are
duplicated/ambiguous in the raw HTML -- e.g. the same "76 Units Renovated" /
"108 Senior Housing Units" cards recur under several programs), so the
category is modeled as one aggregate subprogram equal to the headline, like
VA's federal_assistance. The primary amount is $108,631,601 ("Total amount
loaned and awarded through Multifamily Programs", grouped on the landing page
directly with "781 Total Multifamily units produced"). Two other precisely
printed multifamily dollar figures exist -- $94,271,508 ("Multifamily
Production, including private investment") and $88,383,000 ("Multifamily
Lending Program construction and permanent loans") -- plus a narrative
"roughly $110.4 million committed"; all are noted in the quote but only
$108,631,601 is used as the category amount.

rental_assistance (additive=True, single aggregate subprogram): "2,634
at-risk households" with "more than $9.2 million in direct rental and utility
assistance" from remaining Emergency Rental Assistance (ERA) funds. The source
prints only the rounded "more than $9.2 million" -- no more precise figure is
disclosed -- so 9,200,000 is used as-is (a floor), the same way VA used the
report's own rounded "$1.4B".

Why RAW_PROJECTS is empty ([]) -- no complete per-project cohort list
------------------------------------------------------------------------
The WVHDF FY2025 Annual Report discloses aggregate KPI figures and a handful
of editorially selected narrative "Building Home, Together" case studies
(e.g. Broad Street Manor, Prichard Hotel) but NO complete, extractable
list of every single-family loan or multifamily development financed in
FY2025. Transcribing a few hand-picked case studies as RAW_PROJECTS would
misrepresent them as a complete per-project dataset, which this project's
methodology prohibits. RAW_PROJECTS is therefore [] and the output `projects`
array is empty -- an honest reflection of what the report discloses, not a
placeholder. The frontend (docs/program_activity.js) renders the KPI cards
normally and the bubble map with 0 markers.

External cross-check caveat
------------------------------------------------------------------------
WVHDF's own ACFR (FY2025/txt/WV_WVHDF_FY2025_ACFR.txt) contains a "Housing
Unit Production Report" statistical schedule (p.72) with a "Net Units"
footnote ("units that are counted only once, even if they have more than one
source of program financing") that reports FY2025 totals (e.g. MRB 1,348;
Development Financing Programs 514; Emergency Rental Assistance 2,252) and a
grand "Total Units 4,619". These use a different measurement convention (net
units, deduplicated across financing sources, and counting federal/special
program units the Annual Report's "loans"/"households" headlines do not), so
they do NOT reconcile to the Annual Report's 1,414 loans / 781 units / 2,634
households and are not used as a numeric cross-check. The only hard external
checks used here are the report's own cross-page rounded-vs-exact figures
("more than $254 million" == $254,382,975; "more than $233 million" ==
$233,339,147), which are asserted in verify_category_consistency().

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
Source: FY2025/txt/WV_WVHDF_FY2025_ACFR.txt. VERIFIED before use: title page
reads "WEST VIRGINIA HOUSING DEVELOPMENT FUND (A Component Unit of the State
of West Virginia) ... For the years ended June 30, 2025 and June 30, 2024";
the Table of Contents lists "Proprietary Fund Type - Enterprise Fund" and a
"Fiduciary Fund Type - Welfare Benefit Plan". Note 1 (txt lines 1017-1053)
names the Fund's internal program accounts, all within the single enterprise
fund: the "General Account", "Bond Programs", "Other Loan Programs", "Land
Development Program", "Bond Insurance Account", and "Federal Programs".
Unambiguously the correct entity, no substitution needed.

  - "proprietary", HIGH confidence (program named verbatim in ACFR Note 1):
      * single_family_homeownership's homeownership_program -- Note 1:
        "The Bond Programs include the activities of the single-family bond
        programs under the Housing Finance Bond Program resolution..." (the
        MRB Homeownership Program). The MD&A confirms "The Fund's Bond
        Programs are the core-housing programs and the primary source of
        income for the Fund."
      * movin_up -- Note 1 "Other Loan Programs" list; MD&A "The Fund's Movin'
        Up program is ... a self-funding lending program".
      * veterans -- Note 1: "The Veteran's Home Loan Mortgage Program is also
        part of the Other Loan Programs. The Fund received $8,000,000 from the
        State during fiscal year 2025 to administer the Veteran's Home Loan
        Mortgage Program..."
      * onsite_systems -- Note 1 "Other Loan Programs" names the "On-Site
        Septic Systems Loan Program".
  - "mixed", MEDIUM confidence (aggregate category spanning loan + award
    activity): multifamily_rental_production's single aggregate subprogram.
    The $108,631,601 "total amount loaned AND AWARDED" spans Multifamily
    Lending Program loans (proprietary, Note 1 "Other Loan Programs") plus
    LIHTC tax-credit awards (off-balance-sheet -- the credits flow to
    developers; Note 1 "General Account" records only "fee income related to
    the administration of the ... Low-Income Housing Tax Credit Program") and
    HOME/NHTF/AHF/Home4Good grants ("Federal Programs ... funded solely
    through federal monies", "program administrator"). The exact split is not
    disclosed, hence "mixed".
  - "proprietary", MEDIUM-HIGH confidence (federal pass-through recognized
    within the enterprise fund): rental_assistance's single aggregate
    subprogram. MD&A "COVID Relief Programs" and Note 1 state the Emergency
    Rental Assistance (ERA1/ERA2, locally the "Mountaineer Rental Assistance
    Program") funds "are included in pass through grant revenue and pass
    through grant expense and in restricted cash and cash equivalents" -- i.e.
    recognized within the enterprise fund's own statement of revenues/
    expenses (the same structure VA classified as proprietary for its federal
    Section 8 pass-through).

fy2026
------------------------------------------------------------------------
The FY2025 Annual Report is a backward-looking report with no
forward-looking/projected-activity section. Every fy2026 field below is
{value: None, amount: None, closed: False, note_key: "wvFy26NotePending"}.
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "wv_program_activity.json"

SOURCE_URL = "https://www.wvhdf.com/annual-report-2025/"
SOURCE_FILE = (
    "Interactive web report (no single downloadable PDF) -- figures "
    "transcribed from server-rendered HTML pages under "
    "https://www.wvhdf.com/annual-report-2025/ (?ar-page=home / about / "
    "single-family-programs-overview / multi-family-programs-overview). "
    "Fund-type classification cross-referenced against the Fund's own ACFR, "
    "already archived at FY2025/txt/WV_WVHDF_FY2025_ACFR.txt (fiscal year "
    "ended June 30, 2025)."
)
RETRIEVED = "2026-08-16"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "wvFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data (WVHDF FY2025 Annual Report)
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "single_family_homeownership",
        "unit_type": "households",
        "fy2025_actual": 1414,
        "fy2025_source_quote": (
            "\"Single-Family Production $254,382,975\" / \"Production 1,414 "
            "Single-Family Loans\" (Welcome-from-WVHDF stat cards, "
            "ar-page=about); \"$254,382,975 Mortgage Loans\", \"$233,339,147 "
            "Loaned through the Homeownership Program\", \"$4,204,020 Loaned "
            "through the Movin' Up Program\", \"$9,076,415 In down payment "
            "assistance through the Low Down Home Loan\" (landing-page cards, "
            "ar-page=home). Single-Family Programs page: \"In FY25, the Fund "
            "loaned more than $233 million to 1,347 first-time home buyers "
            "through the Homeownership Program.\" \"In FY25, the Fund loaned "
            "$4.2 million to 21 borrowers through the Movin' Up Program.\" "
            "\"This program helped 32 veterans achieve their dreams of "
            "affordable homeownership.\" \"In FY25, the program loaned "
            "$145,129 to 14 property owners across the state.\" 1,347 + 21 + "
            "32 + 14 = 1,414, an exact partition of the headline (verified in "
            "verify_category_consistency()). The Low Down Home Loan (1,192 "
            "borrowers / $9,076,415) is a second-position down-payment/"
            "closing-cost assistance loan layered on a subset of these first "
            "mortgages ('About 86 percent of borrowers took advantage of this "
            "loan'), so it is shown only as a reference amount, not part of "
            "the 1,414-loan partition. The $254,382,975 total is the report's "
            "own headline and is not fully itemized by the subprograms "
            "(Veterans loan dollars are not disclosed; only the $8M State "
            "funding transfer is), so the subprogram dollar amounts are a "
            "partial, non-exhaustive itemization."
        ),
        "fy2025_amounts": [
            {"label_key": "wv_amt_single_family_total", "amount": 254382975},
            {"label_key": "wv_amt_low_down_assistance", "amount": 9076415},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "homeownership_program", "fy2025_units": 1347, "fy2025_amount": 233339147,
             "color_group": "bond",
             # ACFR Note 1: "The Bond Programs include the activities of the
             # single-family bond programs under the Housing Finance Bond
             # Program resolution..." -- the MRB Homeownership Program.
             "fund_type": "proprietary", "fund_name": "Bond Programs (single-family Housing Finance Bond Program / MRB)",
             "fy2026": _FY26_PENDING},
            {"key": "movin_up", "fy2025_units": 21, "fy2025_amount": 4204020,
             "color_group": "capital",
             # ACFR Note 1 "Other Loan Programs"; MD&A "The Fund's Movin' Up
             # program is ... a self-funding lending program".
             "fund_type": "proprietary", "fund_name": "Other Loan Programs (Movin' Up Program, self-funding)",
             "fy2026": _FY26_PENDING},
            {"key": "veterans", "fy2025_units": 32, "fy2025_amount": None,
             "color_group": "capital",
             # ACFR Note 1: "The Veteran's Home Loan Mortgage Program is also
             # part of the Other Loan Programs. The Fund received $8,000,000
             # from the State during fiscal year 2025..." Loan DOLLARS not
             # disclosed (only the $8M State funding transfer), so
             # fy2025_amount is None.
             "fund_type": "proprietary", "fund_name": "Other Loan Programs (Veteran's Home Loan Mortgage Program; $8M State funding)",
             "fy2026": _FY26_PENDING},
            {"key": "onsite_systems", "fy2025_units": 14, "fy2025_amount": 145129,
             "color_group": "capital",
             # ACFR Note 1 "Other Loan Programs" names the "On-Site Septic
             # Systems Loan Program" (the annual report calls it the On-Site
             # Systems Loan Program / OSLP, a WV DEP partnership).
             "fund_type": "proprietary", "fund_name": "Other Loan Programs (On-Site Septic Systems Loan Program)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "multifamily_rental_production",
        "unit_type": "units",
        "fy2025_actual": 781,
        "fy2025_source_quote": (
            "\"781 Total Multifamily units produced\", \"$108,631,601 Total "
            "amount loaned and awarded through Multifamily Programs\", \"55 "
            "Loans and Awards Through Multifamily Programs\" (landing-page "
            "cards, ar-page=home); \"This work resulted in 781 new or "
            "rehabilitated rental units financed through our Multifamily "
            "Division in fiscal year 2025.\" (ar-page=home). Welcome letter: "
            "\"In FY25, we committed roughly $110.4 million in funding to "
            "these projects through our slate of housing programs, resulting "
            "in 781 safe, affordable rental units in communities across the "
            "state.\" (ar-page=about). $108,631,601 is used as the primary "
            "amount because it is the precise 'total amount loaned and "
            "awarded' and is grouped directly with the '781 Total Multifamily "
            "units produced' headline. Two other precisely printed dollar "
            "figures exist -- \"Multifamily Production $94,271,508 Including "
            "Private Investment\" and \"Multifamily Lending Program "
            "$88,383,000 Construction and Permanent Loans\" (ar-page=about) "
            "-- plus the narrative 'roughly $110.4 million committed'; all "
            "are noted here but not used as the category amount. The report "
            "does not provide a clean per-program partition of the 781 units "
            "(the interactive Multifamily Programs page's per-program impact "
            "cards are ambiguous/duplicated in raw HTML), so this is modeled "
            "as a single aggregate subprogram equal to the headline."
        ),
        "fy2025_amounts": [
            {"label_key": "wv_amt_multifamily_total", "amount": 108631601},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "multifamily_total", "fy2025_units": 781, "fy2025_amount": 108631601,
             "color_group": "bond",
             # $108,631,601 spans Multifamily Lending Program loans
             # (proprietary, Note 1 "Other Loan Programs") plus LIHTC
             # tax-credit awards (off-balance-sheet) and HOME/NHTF/AHF/
             # Home4Good grants (federally administered "Federal Programs").
             # Exact split not disclosed -> "mixed". Confidence: medium.
             "fund_type": "mixed", "fund_name": "Multifamily Lending Program loans (proprietary) + LIHTC/HOME/NHTF/AHF/Home4Good awards (off-balance-sheet credits and federally-administered grants)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "rental_assistance",
        "unit_type": "households",
        "fy2025_actual": 2634,
        "fy2025_source_quote": (
            "\"In FY25, we provided 2,634 at-risk households with more than "
            "$9.2 million in direct rental and utility assistance. This "
            "program, which sunset on September 30, 2025, has been vital to "
            "providing housing stability for at-risk West Virginia renters.\" "
            "(Welcome letter, ar-page=about). The source prints only the "
            "rounded 'more than $9.2 million' -- no more precise figure is "
            "disclosed -- so 9,200,000 is used as-is (a floor), the same way "
            "VA used the report's own rounded '$1.4B'. Funded from remaining "
            "Emergency Rental Assistance (ERA1/ERA2, locally the Mountaineer "
            "Rental Assistance Program) funds, a federal pass-through the "
            "ACFR recognizes as 'pass through grant revenue and pass through "
            "grant expense' within the enterprise fund."
        ),
        "fy2025_amounts": [
            {"label_key": "wv_amt_rental_assistance", "amount": 9200000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "rental_assistance_total", "fy2025_units": 2634, "fy2025_amount": 9200000,
             "color_group": "trust",
             # MD&A "COVID Relief Programs" / Note 1: ERA1/ERA2 funds "are
             # included in pass through grant revenue and pass through grant
             # expense and in restricted cash and cash equivalents" -- i.e.
             # recognized within the enterprise fund (federal pass-through,
             # not the Fund's own lending). Confidence: medium-high.
             "fund_type": "proprietary", "fund_name": "Emergency Rental Assistance (ERA1/ERA2 - 'Mountaineer Rental Assistance Program'), federal pass-through recognized in the enterprise fund",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# WVHDF's FY2025 Annual Report discloses aggregate KPI figures and a few
# editorially selected narrative case studies but NO complete, extractable
# per-project cohort list (see module docstring "Why RAW_PROJECTS is empty").
RAW_PROJECTS = []


def verify_category_consistency():
    errors = []

    # single_family_homeownership: the four disclosed single-family loan
    # programs must sum to the 1,414-loan headline exactly (an exact
    # partition of the report's own headline).
    sf = next(c for c in CATEGORIES if c["key"] == "single_family_homeownership")
    sf_sum = sum(sp["fy2025_units"] for sp in sf["subprograms"])
    if sf_sum != sf["fy2025_actual"]:
        errors.append(
            f"single_family_homeownership: subprogram units sum to {sf_sum}, "
            f"expected {sf['fy2025_actual']} (1,347 homeownership + 21 movin_up "
            f"+ 32 veterans + 14 onsite_systems)"
        )

    # Cross-page rounded-vs-exact dollar sanity (internal, second phrasing):
    # landing page "more than $254 million" and "more than $233 million"
    # must be consistent with the exact stat-card figures.
    sf_total = sf["fy2025_amounts"][0]["amount"]
    ho = next(sp for sp in sf["subprograms"] if sp["key"] == "homeownership_program")
    mu = next(sp for sp in sf["subprograms"] if sp["key"] == "movin_up")
    if sf_total < 254000000:
        errors.append(f"single_family_homeownership: total ${sf_total} < 'more than $254 million'")
    if ho["fy2025_amount"] < 233000000:
        errors.append(f"single_family_homeownership: homeownership ${ho['fy2025_amount']} < 'more than $233 million'")
    if ho["fy2025_amount"] + mu["fy2025_amount"] > sf_total:
        errors.append(
            f"single_family_homeownership: disclosed loan amounts "
            f"${ho['fy2025_amount']} + ${mu['fy2025_amount']} exceed the "
            f"${sf_total} headline"
        )

    # multifamily_rental_production: single subprogram must exactly equal the
    # category headline (additive=True with 1 subprogram is only meaningful
    # if the subprogram *is* the headline).
    mf = next(c for c in CATEGORIES if c["key"] == "multifamily_rental_production")
    if len(mf["subprograms"]) != 1:
        errors.append(f"multifamily_rental_production: expected exactly 1 subprogram, got {len(mf['subprograms'])}")
    else:
        sp = mf["subprograms"][0]
        if sp["fy2025_units"] != mf["fy2025_actual"]:
            errors.append(f"multifamily_rental_production: subprogram units {sp['fy2025_units']} != category fy2025_actual {mf['fy2025_actual']}")
        cat_amt = mf["fy2025_amounts"][0]["amount"] if mf["fy2025_amounts"] else None
        if cat_amt is not None and sp["fy2025_amount"] != cat_amt:
            errors.append(f"multifamily_rental_production: subprogram amount {sp['fy2025_amount']} != category fy2025_amounts[0].amount {cat_amt}")

    # rental_assistance: single subprogram must exactly equal the category
    # headline (same single-subprogram pattern).
    ra = next(c for c in CATEGORIES if c["key"] == "rental_assistance")
    if len(ra["subprograms"]) != 1:
        errors.append(f"rental_assistance: expected exactly 1 subprogram, got {len(ra['subprograms'])}")
    else:
        sp = ra["subprograms"][0]
        if sp["fy2025_units"] != ra["fy2025_actual"]:
            errors.append(f"rental_assistance: subprogram units {sp['fy2025_units']} != category fy2025_actual {ra['fy2025_actual']}")
        cat_amt = ra["fy2025_amounts"][0]["amount"] if ra["fy2025_amounts"] else None
        if cat_amt is not None and sp["fy2025_amount"] != cat_amt:
            errors.append(f"rental_assistance: subprogram amount {sp['fy2025_amount']} != category fy2025_amounts[0].amount {cat_amt}")

    if RAW_PROJECTS:
        errors.append(
            "RAW_PROJECTS is expected to be empty for WV -- see module docstring; "
            "if a complete project-level list has since become available, update "
            "the docstring before populating this list."
        )

    if errors:
        raise SystemExit("Category consistency mismatch(es):\n" + "\n".join(errors))
    print("Category headline vs. subprogram consistency verified for all 3 categories "
          "(single_family_homeownership: 1,347+21+32+14=1,414 loans; "
          "multifamily_rental_production: single subprogram = 781 units/$108,631,601; "
          "rental_assistance: single subprogram = 2,634 households/$9,200,000); "
          "cross-page dollar sanity passed; RAW_PROJECTS confirmed empty as expected.")


def main():
    verify_category_consistency()
    payload = {
        "WV": {
            "hfa_name": "West Virginia Housing Development Fund",
            "hfa_abbr": "WVHDF",
            "fiscal_year": "FY2025",
            "source_title": "West Virginia Housing Development Fund FY2025 Annual "
                             "Report -- \"Welcome from WVHDF\" summary, Single-Family "
                             "Programs, Multifamily Programs, and Production Snapshot",
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
