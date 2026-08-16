"""
Builds docs/nj_program_activity.json from the New Jersey Housing and Mortgage
Finance Agency's (NJHMFA) "2025 Annual Report" -- a single-page HTML
"Supporting People, Delivering Affordability" microsite. This is a KPI-layer-
only build (RAW_PROJECTS=[]); see "Why RAW_PROJECTS is empty" below.

Source
------------------------------------------------------------------------
NJHMFA "2025 Annual Report" (web page, published for calendar year 2025):
    https://www.nj.gov/dca/hmfa/reports/2025AnnualReport/
The same report is linked from the Agency's Investor Information page:
    https://www.nj.gov/dca/hmfa/about/investorinfo/2025_AnnualReport.shtml
The report is a Mobirise-built single-page HTML microsite (not a downloadable
PDF), so there is NO local PDF archive for this state -- the content was
captured live on 2026-08-16 from the URL above. No other file is produced.

Fiscal year -- CY2025 (not a June-30 "FY2025")
------------------------------------------------------------------------
NJHMFA's audited financial statements carry a DECEMBER 31 year end (the
checked-in ACFR text FY2024/txt/NJ_NJHMFA_FY2024_ACFR.txt is titled
"YEAR ENDED DECEMBER 31, 2024"), i.e. NJHMFA's fiscal year is the calendar
year. The 2025 Annual Report frames every figure in calendar-year terms --
"in 2025", "during 2025", "through the end of 2025" -- and never uses
"fiscal year" language. Per this project's calendar-year convention (FL/CO/
RI/IN/OR), the honest label here is "CY2025", which coincides with NJHMFA's
own December-31 fiscal year.

Every figure below is transcribed verbatim from this build's own live fetch
of the report (curl + HTML text extraction), not from memory or a secondary
source:
  - LIHTC Program ("2025 COMMITMENTS TO FINANCING" section): "In 2025, the
    $323,372,021 in LIHTC allocations spurred the $1.5 billion in development
    or redevelopment across 34 projects. Within these 34 projects were 3,059
    new and rehabilitated units including 196 special-needs beds and 2,087
    units designated for low- to moderate-income households."
  - Opening narrative (independently restates the same cohort): "The Agency
    provided more than $930 million in subsidy and financing to spur $1.45
    billion in residential construction across 34 projects. This supported
    the development and rehabilitation of 3,059 rental housing units, 2,087
    of which are deed restricted for low-to-moderate income families, and the
    creation of an additional 196 housing opportunities for individuals with
    special needs."
  - Down Payment Assistance (DPA) Program: "During 2025, NJHMFA provided
    2,618 DPA loans to help 3,684 individuals across New Jersey achieve
    homeownership."
  - First-Generation DPA Program: "In 2025, this program helped 1,670
    First-Generation homebuyers from 1,216 households purchase their first
    home."
  - Emergency Rescue Mortgage Assistance (ERMA): "In 2025, NJHMFA awarded
    $10,813,490 in ERMA funding to 300 households, with an average award
    amount of $36,045. ... Through the end of 2025, the ERMA program has
    assisted 8,334 households with awards totaling $242,226,072."

IMPORTANT -- historical-cumulative figures explicitly excluded
------------------------------------------------------------------------
The following "through the end of 2025" / "in the past three years" /
"since inception" figures appear in the report but are NOT CY2025 activity
and are never used as a fy2025_actual/fy2025_amount/fy2025_amounts value:
$242,226,072 ERMA awards to 8,334 households (cumulative since Feb 2022),
$2.39 billion residential development "in the past three years", $1.1
billion cumulative equity appreciation (2016-2024 DPA purchases), and the
"half of all DPA in 40-plus years" historical claim. Only figures the
report frames as this year's own ("in 2025", "during 2025") are used.

Why RAW_PROJECTS is empty ([]) -- the report has project case studies, not
a full-year project list
------------------------------------------------------------------------
Per this build's task briefing (already investigated, not re-litigated), NJ
is a KPI-only verdict: solid multi-category KPI figures exist, but there is
no complete per-project cohort list. This build independently confirmed
that: the report's only project-level detail is 4 editorially-selected
"Grand Openings" case studies (West Orange Senior Housing, The Residences
at Choctaw, Oliver Station, Freedom Village at Historic Roebling) plus a
few scattered financing figures -- a hand-picked set of highlight ribbon-
cuttings, not a complete list of every multifamily development NJHMFA
financed in CY2025 (the report's own 3,059-unit/34-project headline implies
a much larger population of developments than 4). Transcribing these 4 as
RAW_PROJECTS would misrepresent hand-picked examples as a complete dataset,
which this project's methodology prohibits. RAW_PROJECTS is therefore []
and the output `projects` array is empty -- an honest reflection of what
the report discloses at project level. The frontend renders the KPI cards
normally and the bubble map with 0 markers.

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
No FY2025 NJHMFA ACFR text exists in this repo's FY2025/txt/ corpus (NJ was
one of the six states with no checked-in FY2025 ACFR). Cross-referenced
against the checked-in FY2024 ACFR instead --
FY2024/txt/NJ_NJHMFA_FY2024_ACFR.txt -- after VERIFYING it is the correct
document (title page: "NEW JERSEY HOUSING AND MORTGAGE FINANCE AGENCY,
Financial Statements and Supplementary Information, Year Ended December 31,
2024"; the independent auditors' report covers "the business-type
activities ... of the [Agency]"). The fund STRUCTURE is stable across
years even though the numbers are FY2024's, so it is a sound basis for
classification (confidence noted below):
  - The ACFR states "The Agency engages only in business-type activities"
    (Note 1) and reports enterprise/proprietary funds (Single Family,
    Multi-Family, General) plus a separate fiduciary OPEB trust -- i.e.
    NJHMFA has NO governmental funds, the standard HFA structure.
  - "off_balance_sheet", HIGH confidence:
      * multifamily_lihtc's two subprograms (low_mod_income,
        special_needs). The 9% federal Low-Income Housing Tax Credit is
        allocated directly to developers/investors and never booked as a
        NJHMFA asset -- the same off-balance-sheet logic as every other
        pilot state's LIHTC subprogram (AR/UT/PA/etc.). The report's own
        "COMMITMENTS TO FINANCING" section frames this category around the
        LIHTC allocation ($323,372,021), and that is the only dollar figure
        surfaced on the category. (The 34 LIHTC projects additionally layer
        NJHMFA's own AHPF/bond subsidy -- the "$930 million in subsidy and
        financing" framing -- but no per-source breakdown is disclosed for
        the 3,059 units, so the units are classified by the financing
        source the report itself attaches to them: LIHTC.)
  - "proprietary", HIGH confidence:
      * homeownership_dpa's first_generation subprogram. The FY2024 ACFR
        MD&A (lines ~320, 690-707) describes the Single Family Program as
        financed with Mortgage Revenue Bond proceeds, and separately notes
        the State DCA's annual cash contribution "for Down Payment
        Assistance Program (DPA)" (line 382) -- DPA is NJHMFA's own
        single-family program, carried on its own business-type books.
  - "proprietary", MEDIUM confidence:
      * emergency_mortgage_assistance's erma subprogram. The FY2024 ACFR
        (lines 392-399) states "Under the American Rescue Plan Act (ARPA)
        of 2021, the Agency received a total allocation of $325,966 of
        Homeowner Assistance Fund (HAF) dollars to develop the Emergency
        Rescue Mortgage Assistance (ERMA) Program and the Housing
        Counseling Program", and the MD&A (line 520) reports "Unearned
        revenue decreased ... due to significant usage of HAF (ERMA)" --
        i.e. ERMA is a federally-funded, pass-through-structured program
        recognized within NJHMFA's own business-type funds (same logic as
        VA's federal pass-through classification). Confidence medium only
        because the exact FY2025 ACFR is unavailable and the ACFR's own
        HAF figure is not reconciled to the report's $10,813,490 (no forced
        reconciliation attempted, per project convention).

Category-level methodology
------------------------------------------------------------------------
multifamily_lihtc: additive=False. The two subprograms (low_mod_income
2,087 units, special_needs 196 units) sum to 2,283, which is LESS than the
3,059-unit headline -- the source's own wording is "including", i.e. a
non-exhaustive income-tier breakdown (the remaining 776 units are not
itemized). A stacked bar would therefore misrepresent the headline, so
additive=False (reference chips). Only the LIHTC allocation
($323,372,021) is surfaced as an amount chip; the report's "$930 million+"
total subsidy and "$1.45B/$1.5B" construction-value figures are rounded or
different concepts (total development value, not a program amount) and are
documented in the source quote rather than surfaced as amounts.

homeownership_dpa: additive=False, no fy2025_amounts. The report discloses
a clean CY2025 household/loan count (2,618 DPA loans helping 3,684
individuals) but NO CY2025 dollar total for DPA -- only a per-homebuyer
"$51,161 average savings over a 30-year mortgage" and a "$1.1 billion
cumulative equity appreciation (2016-2024)" retrospective. Per the build
brief, a dollar-only line without a paired count is at most a reference
chip, but here the reverse holds: a clean count with no dollar total, so
the category is surfaced unit-only (honest null on amounts, documented in
the quote). first_generation (1,216 households / 1,670 homebuyers) is a
subset of the DPA population, not a partition, so additive=False.

emergency_mortgage_assistance: additive=True with a single subprogram
exactly equal to the category headline (the report discloses one ERMA
total, no further breakdown) -- same pattern as VA's federal_assistance.
300 households and $10,813,490 both come from the report's own ERMA
sentence; 300 x the source's rounded $36,045 average = $10,813,500, within
rounding of the stated $10,813,490 (the true average is $36,044.97), which
the verify step checks.

fy2026
------------------------------------------------------------------------
The 2025 Annual Report is a backward-looking annual report with no
forward-looking/projected-activity figure anywhere. Every fy2026 field is
therefore {value: None, amount: None, closed: False, note_key:
"njFy26NotePending"}.
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "nj_program_activity.json"

SOURCE_URL = "https://www.nj.gov/dca/hmfa/reports/2025AnnualReport/"
SOURCE_FILE = (
    "None -- the report is a single-page HTML microsite (Mobirise), not a "
    "downloadable PDF; no local archive exists. Content captured live "
    "2026-08-16 from the URL above (also linked from the Agency's Investor "
    "Information page https://www.nj.gov/dca/hmfa/about/investorinfo/"
    "2025_AnnualReport.shtml)."
)
RETRIEVED = "2026-08-16"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                 "note_key": "njFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data (NJHMFA "2025 Annual Report", HTML microsite)
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "multifamily_lihtc",
        "unit_type": "units",
        "fy2025_actual": 3059,
        "fy2025_source_quote": (
            "\"NJHMFA's Low-Income Housing Tax Credit (LIHTC) Program ... In 2025, the "
            "$323,372,021 in LIHTC allocations spurred the $1.5 billion in development or "
            "redevelopment across 34 projects. Within these 34 projects were 3,059 new and "
            "rehabilitated units including 196 special-needs beds and 2,087 units designated "
            "for low- to moderate-income households.\" (NJHMFA 2025 Annual Report, '2025 "
            "COMMITMENTS TO FINANCING' section). The same 34-project/3,059-unit cohort is "
            "independently restated in the report's opening narrative: \"The Agency provided "
            "more than $930 million in subsidy and financing to spur $1.45 billion in "
            "residential construction across 34 projects ... the development and "
            "rehabilitation of 3,059 rental housing units, 2,087 of which are deed restricted "
            "for low-to-moderate income families, and the creation of an additional 196 "
            "housing opportunities for individuals with special needs.\" 2,087 + 196 = 2,283, "
            "which is less than 3,059 -- the source's own word is 'including', i.e. a "
            "non-exhaustive income-tier breakdown (the remaining 776 units are not itemized "
            "by income tier), so additive=False. Only the exact LIHTC allocation "
            "($323,372,021) is surfaced as an amount; the '$930 million+' total subsidy and "
            "$1.45B/$1.5B construction-value figures are rounded or different concepts and "
            "are documented here rather than surfaced."
        ),
        "fy2025_amounts": [
            {"label_key": "nj_amt_lihtc", "amount": 323372021},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "low_mod_income", "fy2025_units": 2087, "fy2025_amount": None,
             "color_group": "credit",
             # 9% federal LIHTC credits are allocated to developers/investors,
             # never booked as a NJHMFA asset -- off-balance-sheet (same as
             # AR/UT/PA LIHTC subprograms). The units are the report's own
             # income-tier breakdown *within* the 34 LIHTC projects.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "special_needs", "fy2025_units": 196, "fy2025_amount": None,
             "color_group": "credit",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "homeownership_dpa",
        "unit_type": "households",
        "fy2025_actual": 2618,  # 2,618 DPA loans (helping 3,684 individuals)
        "fy2025_source_quote": (
            "\"Down Payment Assistance (DPA) Program ... During 2025, NJHMFA provided 2,618 "
            "DPA loans to help 3,684 individuals across New Jersey achieve homeownership.\" "
            "and \"First-Generation Down Payment Assistance (DPA) Program ... In 2025, this "
            "program helped 1,670 First-Generation homebuyers from 1,216 households purchase "
            "their first home.\" (NJHMFA 2025 Annual Report, 'HOMEOWNERSHIP' section). "
            "2,618 DPA loans is the household-level count (one DPA loan per purchase; the "
            "3,684 figure is individuals, which can exceed loans when a purchase serves more "
            "than one person). first_generation (1,216 households / 1,670 homebuyers) is a "
            "subset of the DPA population, not a partition, so additive=False. The report "
            "discloses NO CY2025 dollar total for DPA -- only a per-homebuyer '$51,161 "
            "average savings over a 30-year mortgage' and a '$1.1 billion cumulative equity "
            "appreciation (2016-2024)' retrospective -- so this category carries no "
            "fy2025_amounts entry (honest null, not a missing figure)."
        ),
        "fy2025_amounts": [],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "first_generation", "fy2025_units": 1216, "fy2025_amount": None,
             "color_group": "capital",
             # FY2024 ACFR: the Single Family Program is financed with Mortgage
             # Revenue Bond proceeds, and the State DCA makes an annual cash
             # contribution "for Down Payment Assistance Program (DPA)" -- DPA
             # is NJHMFA's own single-family (business-type/proprietary) program.
             "fund_type": "proprietary",
             "fund_name": "Single Family Program (Single-Family Housing Revenue Bonds + State DPA contribution)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "emergency_mortgage_assistance",
        "unit_type": "households",
        "fy2025_actual": 300,
        "fy2025_source_quote": (
            "\"Emergency Rescue Mortgage Assistance (ERMA) ... In 2025, NJHMFA awarded "
            "$10,813,490 in ERMA funding to 300 households, with an average award amount of "
            "$36,045. Households that received ERMA assistance made 54% of the area median "
            "income, on average. Through the end of 2025, the ERMA program has assisted 8,334 "
            "households with awards totaling $242,226,072 [historical cumulative since "
            "Feb 2022 -- NOT used as a CY2025 figure].\" (NJHMFA 2025 Annual Report, 'ERMA' "
            "section). The report's opening narrative independently states the 2025 figure as "
            "'approximately $11 million in relief' to 300 households, consistent with the "
            "precise $10,813,490 (300 x the source's rounded $36,045 average = $10,813,500, "
            "within rounding of the stated total). No sub-breakdown of ERMA by funding source "
            "or assistance type is disclosed, so a single subprogram equal to the headline "
            "is used (same pattern as VA's federal_assistance)."
        ),
        "fy2025_amounts": [
            {"label_key": "nj_amt_erma", "amount": 10813490},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "erma", "fy2025_units": 300, "fy2025_amount": 10813490,
             "color_group": "trust",
             # FY2024 ACFR: ERMA is an ARPA/Homeowner Assistance Fund (HAF)
             # program whose federal funds are recognized within NJHMFA's own
             # business-type funds ("Unearned revenue decreased ... due to
             # significant usage of HAF (ERMA)"). Federal pass-through
             # recognized on the HFA's own books => proprietary (medium
             # confidence -- FY2025 ACFR unavailable; no forced reconciliation
             # to the ACFR's own HAF figure).
             "fund_type": "proprietary",
             "fund_name": "Emergency Rescue Mortgage Assistance (ERMA) -- ARPA/HAF federal pass-through",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# Per this build's explicit task briefing: NJ's only project-level detail is 4
# editorially-selected "Grand Openings" case studies (West Orange Senior
# Housing, The Residences at Choctaw, Oliver Station, Freedom Village at
# Historic Roebling) -- not a full-year, extractable, complete list of CY2025
# multifamily activity. RAW_PROJECTS is therefore intentionally empty; see
# module docstring "Why RAW_PROJECTS is empty". This is the allowed, honest
# outcome (not a placeholder for missing work): the frontend renders the
# bubble map with 0 markers when this is empty.
RAW_PROJECTS = []

# Independently-transcribed expected constants -- the dual verification gate
# asserts the CATEGORIES values above against these (and the source's own
# printed arithmetic relationships against the assertions below).
EXPECTED = {
    "multifamily_lihtc": {"actual": 3059, "low_mod_income": 2087, "special_needs": 196,
                          "lihtc": 323372021},
    "homeownership_dpa": {"actual": 2618, "first_generation": 1216},
    "emergency_mortgage_assistance": {"actual": 300, "erma_units": 300, "erma": 10813490,
                                      "erma_avg": 36045},
}


def verify_category_consistency():
    errors = []
    by_key = {c["key"]: c for c in CATEGORIES}

    # --- multifamily_lihtc: transcribed values must match EXPECTED; and the
    # income-tier subprograms must sum to LESS than the headline (the source's
    # own word is "including", i.e. non-exhaustive) ---
    mf = by_key["multifamily_lihtc"]
    if mf["fy2025_actual"] != EXPECTED["multifamily_lihtc"]["actual"]:
        errors.append(f"multifamily_lihtc headline: expected {EXPECTED['multifamily_lihtc']['actual']}, got {mf['fy2025_actual']}")
    mf_sp = {sp["key"]: sp for sp in mf["subprograms"]}
    if mf_sp["low_mod_income"]["fy2025_units"] != EXPECTED["multifamily_lihtc"]["low_mod_income"]:
        errors.append("multifamily_lihtc low_mod_income units mismatch vs EXPECTED")
    if mf_sp["special_needs"]["fy2025_units"] != EXPECTED["multifamily_lihtc"]["special_needs"]:
        errors.append("multifamily_lihtc special_needs units mismatch vs EXPECTED")
    mf_part = mf_sp["low_mod_income"]["fy2025_units"] + mf_sp["special_needs"]["fy2025_units"]
    if mf_part != 2283:
        errors.append(f"multifamily_lihtc: 2,087 + 196 expected 2,283, got {mf_part}")
    if not (mf_part < mf["fy2025_actual"]):
        errors.append("multifamily_lihtc: income-tier subprograms must sum to LESS than the "
                      "3,059 headline (source's 'including' is non-exhaustive)")
    lihtc_amt = mf["fy2025_amounts"][0]["amount"]
    if lihtc_amt != EXPECTED["multifamily_lihtc"]["lihtc"]:
        errors.append(f"multifamily_lihtc LIHTC amount: expected {EXPECTED['multifamily_lihtc']['lihtc']}, got {lihtc_amt}")

    # --- homeownership_dpa: first_generation is a subset (< headline), and
    # the category intentionally has no dollar amounts (source discloses none) ---
    ho = by_key["homeownership_dpa"]
    if ho["fy2025_actual"] != EXPECTED["homeownership_dpa"]["actual"]:
        errors.append("homeownership_dpa headline mismatch vs EXPECTED")
    ho_sp = ho["subprograms"][0]
    if ho_sp["key"] != "first_generation" or ho_sp["fy2025_units"] != EXPECTED["homeownership_dpa"]["first_generation"]:
        errors.append("homeownership_dpa first_generation units mismatch vs EXPECTED")
    if not (ho_sp["fy2025_units"] < ho["fy2025_actual"]):
        errors.append("homeownership_dpa: first_generation (1,216) must be a subset of the "
                      "2,618-loan headline")
    if ho["fy2025_amounts"]:
        errors.append("homeownership_dpa: source discloses no CY2025 dollar total; "
                      "fy2025_amounts must be empty")

    # --- emergency_mortgage_assistance: single subprogram must equal the
    # headline, and 300 x the source's rounded $36,045 average must be within
    # rounding of the stated $10,813,490 total ---
    er = by_key["emergency_mortgage_assistance"]
    if er["fy2025_actual"] != EXPECTED["emergency_mortgage_assistance"]["actual"]:
        errors.append("emergency_mortgage_assistance headline mismatch vs EXPECTED")
    if len(er["subprograms"]) != 1:
        errors.append(f"emergency_mortgage_assistance: expected 1 subprogram, got {len(er['subprograms'])}")
    else:
        sp = er["subprograms"][0]
        if sp["fy2025_units"] != er["fy2025_actual"]:
            errors.append("emergency_mortgage_assistance: subprogram units != headline")
        er_amt = er["fy2025_amounts"][0]["amount"]
        if sp["fy2025_amount"] != er_amt:
            errors.append("emergency_mortgage_assistance: subprogram amount != category amount chip")
        if er_amt != EXPECTED["emergency_mortgage_assistance"]["erma"]:
            errors.append("emergency_mortgage_assistance ERMA amount mismatch vs EXPECTED")
        implied = er["fy2025_actual"] * EXPECTED["emergency_mortgage_assistance"]["erma_avg"]
        if abs(er_amt - implied) > 300:
            errors.append(
                f"emergency_mortgage_assistance: 300 x $36,045 = ${implied:,} should be within "
                f"rounding of the stated ${er_amt:,} (the source's $36,045 average is itself rounded)"
            )

    if RAW_PROJECTS:
        errors.append(
            "RAW_PROJECTS is expected to be empty for NJ -- see module docstring; if a "
            "complete project-level list has since become available, update the docstring "
            "before populating this list."
        )

    if errors:
        raise SystemExit("Category consistency mismatch(es):\n" + "\n".join(errors))
    print(
        "Category headline vs. subprogram consistency verified for all 3 categories:\n"
        "  multifamily_lihtc: 3,059 units headline; 2,087 low_mod + 196 special_needs = "
        "2,283 (non-exhaustive 'including' subset, < 3,059); LIHTC $323,372,021.\n"
        "  homeownership_dpa: 2,618 DPA loans headline; first_generation 1,216 households "
        "(subset); no dollar total disclosed (honest null).\n"
        "  emergency_mortgage_assistance: single subprogram = 300 households / $10,813,490; "
        "300 x $36,045 = $10,813,500 within rounding of stated total.\n"
        "RAW_PROJECTS confirmed empty as expected."
    )


def main():
    verify_category_consistency()
    payload = {
        "NJ": {
            "hfa_name": "New Jersey Housing and Mortgage Finance Agency",
            "hfa_abbr": "NJHMFA",
            "fiscal_year": "CY2025",
            "source_title": "NJHMFA 2025 Annual Report -- \"Supporting People, Delivering "
                             "Affordability\" (LIHTC Program, Homeownership/DPA, and ERMA "
                             "sections)",
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
