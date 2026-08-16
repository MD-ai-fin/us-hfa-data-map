"""
Builds docs/nd_program_activity.json from the North Dakota Housing Finance
Agency's (NDHFA, a department of the State of North Dakota) Consolidated
Annual Performance and Evaluation Report (CAPER). This is a KPI-layer-only
build (RAW_PROJECTS=[]), like MA/VA -- see "Why RAW_PROJECTS is empty" below.

Source
------------------------------------------------------------------------
"FY2024 Draft -- North Dakota Consolidated Annual Performance and Evaluation
Report (CAPER) -- July 1, 2024 - June 30, 2025", North Dakota Department of
Commerce / NDHFA. Landing page (the CAPER section titled "Annual Reports"):
    https://www.ndhousing.nd.gov/consolidated-plan/
Direct PDF URL (downloaded and archived per this build's task briefing):
    https://www.ndhousing.nd.gov/sites/www/files/documents/Plans/2024DraftforPublicCommentPeriod.pdf
Local copy: FY2025/program_activity/pdf/ND_NDHFA_CAPER_2024.pdf (verified live
2026-08-16: HTTP 200, 16,655,160 bytes, 67 pages; cover page reads "FY2024
Draft ... July 1, 2024 - June 30, 2025").

TITLE-YEAR / CONTENT-YEAR MISMATCH (honest fiscal_year handling)
------------------------------------------------------------------------
The cover of this document prints "FY2024 Draft" and the pages are stamped
"CAPER N" with "OMB Control No: 2506-0117". But the cover itself also prints
the coverage span "July 1, 2024 - June 30, 2025", and the body refers to the
program year as "FY2024" / "FY24" throughout. In HUD parlance the "2024
program year" (PY2024) IS July 1, 2024 - June 30, 2025. NDHFA's audited
financial statements (FY2025/txt/ND_NDHFA_FY2025_ACFR.txt) are for "the year
ended June 30, 2025" -- the same July 1 - June 30 fiscal year. The content of
this CAPER therefore corresponds to NDHFA's FY2025, and `fiscal_year` is set
to "FY2025" (NOT "FY2024", which would be a title-year, not a content-year).
Every figure below is the CAPER's own "program year" / "In FY24" figure, never
a "strategic plan to date" cumulative.

Historical/cumulative figures explicitly excluded
------------------------------------------------------------------------
The CAPER's performance tables print two columns side by side: "Expected /
Actual - Strategic Plan" (cumulative since the 2020-2024 plan began) and
"Expected / Actual - Program Year" (this year only). The following cumulative
("to date") figures appear adjacent to the program-year figures below but are
NOT FY2025 activity and are never used as a fy2025_* value: 105 rental units
constructed to date, 386 rental units rehabilitated to date, 82 homeowner
units rehabilitated to date, 11,735 persons in overnight shelter to date,
1,818 homelessness-prevention persons to date, and 362 TBRA/Rapid Rehousing
households to date. Only the program-year column and the "In FY24" narrative
totals are transcribed.

Program figures used (all transcribed from the local PDF, not memory)
------------------------------------------------------------------------
  - HOME (CR-05 p.2, CR-20 p.17-18, CR-15 Table 3 p.11):
    "During the program year, a total of $6,433,618.82 was expended for
    HOME ... on housing activities." "A total of 54 HOME-assisted units were
    completed in FY2024" (CR-20 p.18, confirmed by CR-20 Table 13 "HOME
    Actual ... Total 54"). Components: three multifamily projects (Prairie
    Ridge Residences 11 HOME-assisted; Century View Apartments 10
    HOME-assisted; Lantern Light 23 HOME-assisted = 44), plus 5 HOME
    Homeowner Rehabilitation units, plus 5 HOME Community Land Trust Housing
    Assistance (HOME CHAP) / down-payment-assistance units. 44 + 5 + 5 = 54.
  - Housing Trust Fund / HTF (CR-56 p.33, CR-20 p.18, CR-15 Table 3 p.11):
    "One project was completed during the program year, Lantern Light, a
    23-unit (23 HTF assisted) development ... located in Fargo, ND." CR-56
    Table 15 prints 23 rental units completed; CR-20 prints "1 HTF-assisted
    project completed/23 HTF-assisted units." "a total of ... $7,088,068.01
    for Housing Trust fund on housing activities" (CR-05 p.2). NOTE -- source
    internal discrepancy flagged: the CR-05 narrative overview prints "One
    project was fully completed under the Housing Trust Fund program, Lantern
    Light, 23 units (9 HTF assisted)" -- i.e. "9 HTF assisted" -- whereas the
    HTF-specific CR-56 section, CR-56 Table 15, and CR-20's own summary all
    state 23 HTF-assisted units. This build uses 23 (the HTF-specific figure,
    corroborated in three places) and records the CR-05 "9" as a
    source-internal inconsistency, not a transcription choice.
  - Emergency Solutions Grant / homeless assistance (CR-05 p.2, CR-15 p.11,
    CR-25 p.20-21):
    "With the combined Federal, State, and previous year's funding carry
    over, ESG $364,469 and assisted 186 households/488 persons with rapid
    rehousing and homeless prevention tenant based rental assistance,
    utilities, and security deposits, $339,181 for overnight shelter,
    assisting 987 persons ..." (CR-15 p.11). CR-25 splits the TBRA headline:
    "ESG and ESG State funds assisted 431 persons/145 households ... for a
    total of $299,451.87 expended under homeless prevention component
    activities" (p.20) and "ESG and State funds assisted 57 persons/41
    households ... for a total of $65,017.70" rapid rehousing (p.21).
    145 + 41 = 186 households and 431 + 57 = 488 persons (exact). The dollar
    components sum to $299,451.87 + $65,017.70 = $364,469.57, which the CAPER
    itself prints as the rounded headline "$364,469" -- a 57-cent
    source-internal rounding, verified with a <$1 tolerance (see
    verify_category_consistency()). The overnight-shelter figure (987 persons
    / $339,181) is a "persons" count (not units or households), so per this
    project's schema it is recorded only as a reference amount chip, not a
    subprogram.

Why RAW_PROJECTS is empty ([]) -- no complete per-project cohort list
------------------------------------------------------------------------
The CAPER names individual HOME/HTF multifamily developments in prose (Prairie
Ridge Residences, Century View Apartments, Lantern Light, and the under-
construction Nex Senior / Pleasant Valley / Lashkowitz Riverfront Four /
Dakota II / Jewel City I), but these are narrative mentions with partial
assisted-unit and dollar detail, NOT a complete, consistently-fielded
per-project cohort list (no per-project HOME/HTF dollar splits, no addresses,
no coordinates, and the "currently under construction" projects are not
completions). Transcribing a handful of named developments as RAW_PROJECTS
would misrepresent an editorial narrative as a complete per-development
dataset, which this project's methodology explicitly prohibits (see the MA/VA
build docstrings). RAW_PROJECTS is therefore [] and the output `projects`
array is empty -- the honest reflection of what this CAPER discloses at
project level. The frontend renders KPI cards normally and a 0-marker bubble
map for this state.

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
Source: FY2025/txt/ND_NDHFA_FY2025_ACFR.txt. VERIFIED before use: the title
page reads "NORTH DAKOTA HOUSING FINANCE AGENCY ... AUDITED FINANCIAL
STATEMENTS FOR THE YEAR ENDED JUNE 30, 2025 AND 2024"; the Independent
Auditor's Report (.txt lines 42-44) covers "the business-type activities of
the North Dakota Housing Finance Agency, a department of the State of North
Dakota"; this matches the CAPER's own entity, fiscal-year end (June 30,
2025), and program descriptions (HOME, HTF, ESG / ND Homeless Grant). The
correct entity, no substitution needed.

NDHFA is a proprietary (business-type) only entity -- there are NO
governmental funds. The Auditor's Report covers only "business-type
activities"; Note 1 "Fund Accounting" (.txt lines 678-692) lists exactly two
funds: "Agency Operating Funds" ("account for (1) activities related to the
development and administration of Agency financial programs, (2) HUD Section
8 Housing Assistance Payment programs, (3) Agency owned assets and (4) any
activities of the Agency not applicable to the other funds") and
"Homeownership Bond Funds" (bond-financed single-family homeownership). All
three CAPER programs are federal grant/pass-through programs NDHFA
administers within its Agency Operating Funds:

  * HOME -- "proprietary", MEDIUM-HIGH confidence. The ACFR's Note 5 "Mortgage
    Loans Receivable" (.txt lines 1024-1028) records HOME loans ("$3,000 of
    HOME ARP loans and $23,354 of HOME loans") as assets on the Agency's
    statement of net position, and the MD&A (.txt lines 210-211, 232-233)
    refers to "Agency grants" as operating expenses -- i.e. HOME lending is
    booked inside the Agency's own proprietary operating fund, not
    off-balance-sheet.
  * HTF -- "proprietary", MEDIUM confidence. The ACFR has no separate HTF
    fund; HTF is one of the "development and administration of Agency
    financial programs" activities of the Agency Operating Funds. Classified
    by program description (federal grant administered by NDHFA), not a
    literal dedicated HTF line item.
  * ESG / ND Homeless Grant -- "proprietary", MEDIUM confidence. The MD&A
    (.txt lines 375-376) states "In FY2023, the Agency took over the
    administration of the HUD Emergency Solutions Grant and the North Dakota
    Homeless Grant." These are federal/state pass-through grants administered
    within the Agency Operating Funds; like VA's Section 8 pass-through, they
    are not a separate governmental fund, and NDHFA has no governmental funds
    at all. Classified by program description.

No LIHTC category: the CAPER mentions Low-Income Housing Tax Credits only in
passing (coordination with HOME/HTF scoring; under-construction projects that
"also have allocations of Low-Income Housing Tax Credits"), and discloses no
LIHTC allocation total or LIHTC unit count for the program year, so there is
no honest LIHTC KPI to build here.

fy2026
------------------------------------------------------------------------
This CAPER is a backward-looking HUD compliance report with no forward-looking
activity section; the string "2026" does not appear as a program-year
projection anywhere in the 67-page extraction. Every fy2026 field is
{value: None, amount: None, closed: False, note_key: "ndFy26NotePending"}.
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "nd_program_activity.json"

SOURCE_URL = (
    "https://www.ndhousing.nd.gov/sites/www/files/documents/Plans/"
    "2024DraftforPublicCommentPeriod.pdf"
)
SOURCE_FILE = (
    "ND_NDHFA_CAPER_2024.pdf (downloaded 2026-08-16, HTTP 200, 16,655,160 "
    "bytes, 67 pages; listed as 'FY 2024 CAPER Draft for Comment' on the "
    "consolidated-plan landing page https://www.ndhousing.nd.gov/"
    "consolidated-plan/)"
)
RETRIEVED = "2026-08-16"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                 "note_key": "ndFy26NotePending"}

# Exact-cent values transcribed from the source, kept separate from the
# whole-dollar JSON amounts so verify_category_consistency() can reconcile the
# ESG TBRA components against the CAPER's own rounded headline.
_ESG_RAPID_REHOUSING_EXACT = 65017.70
_ESG_HOMELESS_PREVENTION_EXACT = 299451.87
_ESG_TBRA_HEADLINE = 364469  # the CAPER's own printed "ESG $364,469"

# ---------------------------------------------------------------------------
# Category-level data (CAPER: CR-05 p.2, CR-15 p.11, CR-20 p.17-18,
# CR-25 p.20-21, CR-56 p.33)
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "home_program",
        "unit_type": "units",
        "fy2025_actual": 54,
        "fy2025_source_quote": (
            "\"A total of 54 HOME-assisted units were completed in FY2024.\" "
            "(North Dakota CAPER, CR-20 Affordable Housing, p.18; confirmed by "
            "CR-20 Table 13 'Number of Households Served -- HOME Actual ... "
            "Total 54'). Components (CR-05 Goals and Outcomes, p.2): \"Three "
            "multi-family projects were fully completed under the HOME "
            "program, Prairie Ridge Residences 120 units (11 HOME Assisted) "
            "... Century View Apartments, 40 units (10 HOME-assisted) ... and "
            "Lantern Light a 23 units (23 Home-Assisted) ... A total of 5 "
            "units were completed under the HOME Homeowner Rehabilitation "
            "program ... A total of 5 units were completed under the HOME "
            "Community Land Trust Housing Assistance Program (HOME CHAP).\" "
            "11 + 10 + 23 (multifamily) + 5 (homeowner rehab) + 5 (down-"
            "payment/CHAP) = 54 (verified in verify_category_consistency()). "
            "\"During the program year, a total of $6,433,618.82 was expended "
            "for HOME ... on housing activities\" (CR-05 p.2; CR-15 Table 3 "
            "prints 'HOME ... Amount Expended During Program Year 6,433,618')."
        ),
        "fy2025_amounts": [
            {"label_key": "nd_amt_home_total", "amount": 6433619},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "multifamily_rental", "fy2025_units": 44, "fy2025_amount": None,
             "color_group": "trust",
             # 11 (Prairie Ridge) + 10 (Century View) + 23 (Lantern Light)
             # HOME-assisted multifamily units; HOME loans are on the Agency's
             # statement of net position (ACFR Note 5). See module docstring.
             "fund_type": "proprietary",
             "fund_name": "Agency Operating Funds (HOME federal grant; HOME loans on the Agency's statement of net position, ACFR Note 5)",
             "fy2026": _FY26_PENDING},
            {"key": "homeowner_rehabilitation", "fy2025_units": 5, "fy2025_amount": None,
             "color_group": "trust",
             "fund_type": "proprietary",
             "fund_name": "Agency Operating Funds (HOME federal grant program)",
             "fy2026": _FY26_PENDING},
            {"key": "homebuyer_assistance", "fy2025_units": 5, "fy2025_amount": None,
             "color_group": "trust",
             # 5 households (down-payment/CLT assistance), not 5 housing units
             # -- see source_quote. Counted against the 54 HOME-assisted total.
             "fund_type": "proprietary",
             "fund_name": "Agency Operating Funds (HOME CHAP / down-payment assistance grant program)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "housing_trust_fund",
        "unit_type": "units",
        "fy2025_actual": 23,
        "fy2025_source_quote": (
            "\"One project was completed during the program year, Lantern "
            "Light, a 23-unit (23 HTF assisted) development for individuals "
            "experiencing homelessness located in Fargo, ND.\" (North Dakota "
            "CAPER, CR-56 HTF, p.33; CR-56 Table 15 prints 'Rental ... Total "
            "Completed Units 23'). CR-20 (p.18) confirms: \"There was 1 "
            "HTF-assisted project completed/23 HTF-assisted units.\" \"... a "
            "total of $7,088,068.01 for Housing Trust fund on housing "
            "activities\" (CR-05 p.2; CR-15 Table 3 prints 'HTF ... Amount "
            "Expended During Program Year 7,088,068'). NOTE -- source-internal "
            "discrepancy flagged: CR-05's narrative overview prints \"One "
            "project was fully completed under the Housing Trust Fund program, "
            "Lantern Light, 23 units (9 HTF assisted)\" (i.e. 9 HTF-assisted), "
            "but the HTF-specific CR-56 section, CR-56 Table 15, and CR-20's "
            "own summary all state 23 HTF-assisted units; this build uses 23 "
            "and records the CR-05 '9' as a source inconsistency, not a "
            "transcription choice."
        ),
        "fy2025_amounts": [
            {"label_key": "nd_amt_htf_total", "amount": 7088068},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "htf", "fy2025_units": 23, "fy2025_amount": 7088068,
             "color_group": "trust",
             "fund_type": "proprietary",
             "fund_name": "Agency Operating Funds (HTF federal grant; administered by NDHFA, no separate HTF fund in the ACFR)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "homeless_assistance",
        "unit_type": "households",
        "fy2025_actual": 186,
        "fy2025_source_quote": (
            "\"With the combined Federal, State, and previous year's funding "
            "carry over, ESG $364,469 and assisted 186 households/488 persons "
            "with rapid rehousing and homeless prevention tenant based rental "
            "assistance, utilities, and security deposits, $339,181 for "
            "overnight shelter, assisting 987 persons ...\" (North Dakota "
            "CAPER, CR-15 p.11; same text at CR-05 p.2). CR-25 splits the "
            "TBRA headline: \"ESG and ESG State funds assisted 431 persons/"
            "145 households ... for a total of $299,451.87 expended under "
            "homeless prevention component activities\" (p.20) and \"ESG and "
            "State funds assisted 57 persons/41 households ... for a total of "
            "$65,017.70\" rapid rehousing (p.21). 145 + 41 = 186 households "
            "and 431 + 57 = 488 persons (exact, verified). The two dollar "
            "components sum to $299,451.87 + $65,017.70 = $364,469.57, which "
            "the CAPER itself prints as the rounded headline \"$364,469\" -- "
            "a 57-cent source-internal rounding (verified with a <$1 "
            "tolerance in verify_category_consistency()). The overnight "
            "shelter figure (987 persons / $339,181) is a 'persons' count, "
            "not units or households, so it is recorded only as the "
            "reference amount chip below, not a subprogram."
        ),
        "fy2025_amounts": [
            {"label_key": "nd_amt_esg_tbra", "amount": _ESG_TBRA_HEADLINE},
            {"label_key": "nd_amt_esg_shelter", "amount": 339181},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "rapid_rehousing", "fy2025_units": 41, "fy2025_amount": 65018,
             "color_group": "trust",
             # "$65,017.70" rounded to whole dollars; see source_quote.
             "fund_type": "proprietary",
             "fund_name": "Agency Operating Funds (ESG / ND Homeless Grant federal-state pass-through; MD&A notes FY2023 takeover of administration)",
             "fy2026": _FY26_PENDING},
            {"key": "homeless_prevention", "fy2025_units": 145, "fy2025_amount": 299452,
             "color_group": "trust",
             # "$299,451.87" rounded to whole dollars; see source_quote.
             "fund_type": "proprietary",
             "fund_name": "Agency Operating Funds (ESG / ND Homeless Grant federal-state pass-through; MD&A notes FY2023 takeover of administration)",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# Per this build's explicit task briefing: ND is a KPI-ONLY verdict -- the
# CAPER discloses solid multi-category KPI figures (unit/household counts +
# dollar amounts) but NO complete per-project cohort list (only narrative
# project mentions with partial detail). RAW_PROJECTS is intentionally empty;
# see module docstring "Why RAW_PROJECTS is empty".
RAW_PROJECTS = []


def verify_category_consistency():
    errors = []

    # home_program: 44 (multifamily) + 5 (homeowner rehab) + 5 (down-payment/
    # CHAP) must equal the 54-unit headline exactly (an exact partition).
    hp = next(c for c in CATEGORIES if c["key"] == "home_program")
    hp_sum = sum(sp["fy2025_units"] for sp in hp["subprograms"])
    if hp_sum != hp["fy2025_actual"]:
        errors.append(
            f"home_program: subprogram units sum to {hp_sum}, expected "
            f"{hp['fy2025_actual']} (44 multifamily + 5 homeowner rehab + 5 homebuyer)"
        )
    # Internal check of the multifamily subprogram's own 11+10+23 composition.
    _MF_SUBUNITS = [11, 10, 23]
    if sum(_MF_SUBUNITS) != 44:
        errors.append(f"home_program.multifamily_rental: 11+10+23 = {sum(_MF_SUBUNITS)}, expected 44")

    # housing_trust_fund: single subprogram must exactly equal the category
    # headline (additive=True with 1 subprogram is only meaningful if the
    # subprogram *is* the headline).
    htf = next(c for c in CATEGORIES if c["key"] == "housing_trust_fund")
    if len(htf["subprograms"]) != 1:
        errors.append(f"housing_trust_fund: expected exactly 1 subprogram, got {len(htf['subprograms'])}")
    else:
        sp = htf["subprograms"][0]
        if sp["fy2025_units"] != htf["fy2025_actual"]:
            errors.append(f"housing_trust_fund: subprogram units {sp['fy2025_units']} != category fy2025_actual {htf['fy2025_actual']}")
        cat_amt = htf["fy2025_amounts"][0]["amount"] if htf["fy2025_amounts"] else None
        if cat_amt is not None and sp["fy2025_amount"] != cat_amt:
            errors.append(f"housing_trust_fund: subprogram amount {sp['fy2025_amount']} != category fy2025_amounts[0].amount {cat_amt}")

    # homeless_assistance: 41 (rapid rehousing) + 145 (homeless prevention)
    # must equal the 186-household headline exactly; the two dollar components
    # must sum to the CAPER's own "$364,469" headline within $1 (the source
    # itself rounds the exact $364,469.57 down 57 cents).
    ha = next(c for c in CATEGORIES if c["key"] == "homeless_assistance")
    ha_units = sum(sp["fy2025_units"] for sp in ha["subprograms"])
    if ha_units != ha["fy2025_actual"]:
        errors.append(
            f"homeless_assistance: subprogram units sum to {ha_units}, expected "
            f"{ha['fy2025_actual']} (41 rapid rehousing + 145 homeless prevention)"
        )
    exact_sum = _ESG_RAPID_REHOUSING_EXACT + _ESG_HOMELESS_PREVENTION_EXACT
    if abs(exact_sum - _ESG_TBRA_HEADLINE) >= 1.0:
        errors.append(
            f"homeless_assistance: exact TBRA component sum ${exact_sum:.2f} differs "
            f"from the source's own '$364,469' headline by more than $1"
        )

    if RAW_PROJECTS:
        errors.append(
            "RAW_PROJECTS is expected to be empty for ND -- see module docstring; "
            "if a complete project-level list has since become available, update "
            "the docstring before populating this list."
        )

    if errors:
        raise SystemExit("Category consistency mismatch(es):\n" + "\n".join(errors))
    print(
        "Category headline vs. subprogram consistency verified for all 3 categories "
        "(home_program: 44+5+5=54 units; housing_trust_fund: single subprogram = 23 "
        "units / $7,088,068; homeless_assistance: 41+145=186 households, exact TBRA "
        f"component sum ${exact_sum:.2f} ~ source headline $364,469 within $1); "
        "RAW_PROJECTS confirmed empty as expected."
    )


def main():
    verify_category_consistency()
    payload = {
        "ND": {
            "hfa_name": "North Dakota Housing Finance Agency",
            "hfa_abbr": "NDHFA",
            "fiscal_year": "FY2025",
            "source_title": (
                "North Dakota Consolidated Annual Performance and Evaluation "
                "Report (CAPER) -- \"FY2024 Draft\" covering July 1, 2024 - "
                "June 30, 2025 (HOME, Housing Trust Fund, and Emergency "
                "Solutions Grant / homeless-assistance sections)"
            ),
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
