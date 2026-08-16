"""
Builds docs/al_program_activity.json from the Alabama Housing Finance
Authority's (AHFA) "2025 Annual Report" -- a KPI-layer-only build (no per-project
cohort), like LA, VA and MA. See "Why RAW_PROJECTS is empty" below.

Source
------------------------------------------------------------------------
"2025 Annual Report", Alabama Housing Finance Authority (AHFA), a single-page
Canva-hosted annual report:
    https://ahfa.my.canva.site/annual-report-2025/
Local plain-text extraction (body text, block-separated) archived for this
build at:
    C:/Users/may_d/AppData/Local/Temp/al_body_clean.txt
Verified 2026-08-16: the extraction's opening paragraph reads "FY2025 was a
year of elevated performance for the Alabama Housing Finance Authority. Our
programs turned 2,443 of our state's households into homeowners. We also opened
1,353 units of much-needed multifamily housing for occupancy and fueled the
future construction and repair of 1,890 more." -- the two annual KPIs used here,
verbatim.

Fiscal-year discipline
------------------------------------------------------------------------
AHFA's audited financial statements (FY2025/txt/AL_AHFA_FY2025_ACFR.txt) cover
"the Alabama Housing Finance Authority (a component unit of the State of
Alabama), as of September 30, 2025 and 2024" (title/auditor pages), i.e.
FY2025 (Oct 1, 2024 - Sep 30, 2025). The annual report's opening line labels
the year "FY2025", and its compliance section states "Our team performed 315
inspections in FY2025." fiscal_year is therefore "FY2025".

Excluded as NON-FY2025 / cumulative / future (do NOT model):
  - "fueled the future construction and repair of 1,890 more" -- the report's
    own word "future" flags this as prospective pipeline, not FY2025 realized
    output. Excluded.
  - "Since inception, these initiatives and others have helped more than
    90,000 Alabama families" (Homeownership section) and the closing "Its
    programs have provided opportunities for more than 206,000 families to live
    in homes they can afford" -- cumulative "since inception"/lifetime totals.
    Excluded.
  - Multifamily cumulative block: "AHFA has provided nearly $1.9 billion in
    funding and tax incentives to help build or preserve 1,065 developments
    totaling 65,739 units. Another 87 developments, comprising 5,255 units, are
    in various stages of completion." -- lifetime production + a pipeline, not
    FY2025 output. Excluded.
  - Habitat for Humanity "seven new loans purchased this year, our total rose
    to 599 households helped" -- "total ... since 1992" is cumulative, and the
    seven-loan figure is not an FY2025 homeownership-cohort KPI. Excluded.

Every figure below is transcribed from the local Canva extraction, not from
memory or a secondary source:
  - Opening paragraph (Canva, "Intro"): "Our programs turned 2,443 of our
    state's households into homeowners. We also opened 1,353 units of
    much-needed multifamily housing for occupancy and fueled the future
    construction and repair of 1,890 more." -> homeownership 2,443 households;
    multifamily 1,353 units opened. 1,890 is "future" (excluded above).
  - HOMEOWNERSHIP PROGRAMS section: "The First Step Mortgage Revenue Bond
    (MRB) program provides below-market fixed interest rates and up to $10,000
    in down payment assistance for first-time or repeat buyers. ... Our Step Up
    program is for buyers who can afford a mortgage but need extra lift for the
    down payment. With up to $10,000 in assistance, a competitive 30-year fixed
    rate, and no sales price limits... The Affordable Income Subsidy Grant
    provides an additional boost for our lowest-income borrowers, helping them
    with closing costs when paired with the First Step or Step Up programs."
    The report discloses the three homeownership programs but does NOT split
    the 2,443 households across them, and discloses no FY2025 homeownership
    dollar-production total ("up to $10,000" is a per-borrower cap, not a
    total). So homeownership is a single-subprogram category (subprogram =
    headline), no dollar amount.
  - Multifamily programs section: "AHFA is Alabama's administrator of the
    federal HOME Investment Partnerships Program (HOME) and Low Income Housing
    Tax Credit (LIHTC) program. ... AHFA also administers Alabama's share of
    the National Housing Trust Fund (HTF)... AHFA issues Multifamily Housing
    Revenue Bonds... New this year is AHFA's administration of the Workforce
    Housing Tax Credit enacted by the Alabama Legislature in 2024." Five
    multifamily programs, but the ONLY FY2025 output figure is the aggregate
    "1,353 units ... opened for occupancy"; no per-program unit or dollar split
    is disclosed. So multifamily is also a single-subprogram category
    (subprogram = headline), no dollar amount, fund_type "mixed" (see below).

Compliance (not modeled): "Our team performed 315 inspections in FY2025" is a
monitoring/administration activity, not a housing-production/assistance program
output. Same treatment as LA's PBCA/Section 8 contract-administration figures
(which LA's build explicitly did NOT model): it has no icon-bucket home in the
frontend's CATEGORY_KEYWORD_BUCKETS and is not a unit/household production KPI.
Documented here rather than hard-erroring.

Why RAW_PROJECTS is empty ([]) -- no complete per-project cohort list
------------------------------------------------------------------------
AHFA's report has NO complete per-project FY2025 cohort list. The
"Groundbreakings + Ribbon Cuttings" section is explicitly "a sampling of this
year's accomplishments" -- six editorial case studies, not a full cohort:
  - Columbus Square III (60 units, Montgomery; 9% credits $1.5M)
  - High Point Senior (56 units, Andalusia; $2.2M HOME + $1.3M credits)
  - Southtown Senior (143 units, Birmingham; $1.9M credits)
  - Magnolia Trace (56 units, Montgomery; $14.2M equity + $3.1M HOME)
  - Freedom Village (56 units, Montgomery; $3.1M HOME + $1.5M credits)
  - The Cottages on Georgia Road (8 units, Birmingham; $1,283,200 HTF)
Plus a "Workforce Housing Tax Credits" item (3 applications, an estimated 444
units, "projected"/"estimated" -- a forward-looking pipeline, not completed
units). None of these sums to, or is presented as, AHFA's complete FY2025
multifamily cohort; the report's only complete FY2025 figure is the aggregate
"1,353 units ... opened". RAW_PROJECTS is therefore [] and the output
`projects` array is empty -- the honest KPI-only result, not a placeholder.
The frontend renders the KPI cards normally and the bubble map with 0 markers.

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
Source: FY2025/txt/AL_AHFA_FY2025_ACFR.txt. VERIFIED before use: the auditor's
report and title page read "Alabama Housing Finance Authority ... as of
September 30, 2025 and 2024"; Note 1 states "The Authority is a component unit
of the State of Alabama." (.txt line 521). Note 2 lists the Authority's funds:
"Single Family Mortgage Revenue Bond Programs (Single Family Programs), Federal
Programs, the Housing Assistance Fund, and the General Fund" (.txt lines
525-527), and states they "have been presented on a combined basis, as the
Authority is considered a single enterprise fund for financial reporting
purposes" (.txt lines 531-534) -- i.e. AHFA is a single proprietary/enterprise
fund, with NO governmental funds. Classification follows from this:
  - "proprietary" (HIGH confidence) -- single_family_programs (homeownership).
    "Revenues and expenses from the Single Family Programs, Housing Assistance,
    and General Funds are reported as operating revenues and expenses" (.txt
    lines 537-538). The Single Family MRB program is AHFA's own core lending
    business. fund_name "Single Family Mortgage Revenue Bond Programs".
  - "mixed" (MEDIUM confidence) -- multifamily_units_opened. The 1,353-unit
    aggregate spans several funding types with no disclosed split:
      * HOME & HTF are "Federal Programs": "Federal Program receipts are
        recognized in proportion to Federal Program expenditures as incurred.
        Federal Program activities are reported in nonoperating revenues
        (expenses) ... GASB No. 24" (.txt lines 539-542) -- i.e. recognized
        within AHFA's own enterprise fund (proprietary).
      * LIHTC and the state Workforce Housing Credit are tax credits that flow
        to developers/investors, not onto AHFA's balance sheet; the ACFR
        instead recognizes only "Low-Income Housing Tax Credit fees" (unearned
        compliance/commitment fees, .txt line 272) -- off_balance_sheet.
      * Multifamily Housing Revenue Bonds are conduit debt ("The Authority
        issued approximately $21,000,000 of multifamily bonds as conduit
        debt", .txt line 1530) -- off_balance_sheet.
    Because the aggregate mixes proprietary (HOME/HTF pass-through) and
    off_balance_sheet (LIHTC/credits/conduit bonds) components, and the report
    gives no per-program split to weight them, "mixed" is the honest
    classification; confidence medium (no forced reconciliation to a specific
    ACFR line, per this project's standing rule).
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "al_program_activity.json"

SOURCE_URL = "https://ahfa.my.canva.site/annual-report-2025/"
SOURCE_FILE = (
    "AHFA 2025 Annual Report (Canva, ahfa.my.canva.site/annual-report-2025); "
    "local plain-text extraction archived at "
    "C:/Users/may_d/AppData/Local/Temp/al_body_clean.txt (verified 2026-08-16)"
)
RETRIEVED = "2026-08-16"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "alFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data (AHFA 2025 Annual Report, Intro + program sections)
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "homeownership",
        "unit_type": "households",
        "fy2025_actual": 2443,
        "fy2025_source_quote": (
            "\"Our programs turned 2,443 of our state\u2019s households into "
            "homeowners.\" (AHFA 2025 Annual Report, Canva, opening paragraph -- "
            "\"FY2025 was a year of elevated performance...\"). The report's "
            "HOMEOWNERSHIP PROGRAMS section names the three programs behind this "
            "number: \"The First Step Mortgage Revenue Bond (MRB) program provides "
            "below-market fixed interest rates and up to $10,000 in down payment "
            "assistance... Our Step Up program is for buyers who can afford a "
            "mortgage but need extra lift for the down payment... The Affordable "
            "Income Subsidy Grant provides an additional boost for our "
            "lowest-income borrowers, helping them with closing costs when paired "
            "with the First Step or Step Up programs.\" The report does NOT split "
            "the 2,443 households across the three programs and discloses no "
            "FY2025 homeownership dollar-production total (\"up to $10,000\" is a "
            "per-borrower cap, not a total), so this is a single-subprogram "
            "category (subprogram = headline) with no dollar amount. The "
            "same-section cumulative line (\"Since inception... more than 90,000 "
            "Alabama families\") is excluded per the year-discipline rule."
        ),
        "fy2025_amounts": [],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "single_family_programs", "fy2025_units": 2443, "fy2025_amount": None,
             "color_group": "bond",
             # ACFR: Single Family Programs are the Authority's MRB lending
             # business, reported as OPERATING revenues/expenses within AHFA's
             # single enterprise fund (proprietary). See module docstring.
             "fund_type": "proprietary",
             "fund_name": "Single Family Mortgage Revenue Bond Programs",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "multifamily_development",
        "unit_type": "units",
        "fy2025_actual": 1353,
        "fy2025_source_quote": (
            "\"We also opened 1,353 units of much-needed multifamily housing for "
            "occupancy\" (AHFA 2025 Annual Report, Canva, opening paragraph). The "
            "same paragraph's \"and fueled the future construction and repair of "
            "1,890 more\" is EXCLUDED -- the report's own word \"future\" marks it "
            "as a pipeline, not FY2025 realized output. The multifamily programs "
            "section names the five programs behind the 1,353 units: \"AHFA is "
            "Alabama's administrator of the federal HOME Investment Partnerships "
            "Program (HOME) and Low Income Housing Tax Credit (LIHTC) program... "
            "AHFA also administers Alabama's share of the National Housing Trust "
            "Fund (HTF)... AHFA issues Multifamily Housing Revenue Bonds... New "
            "this year is AHFA's administration of the Workforce Housing Tax "
            "Credit enacted by the Alabama Legislature in 2024.\" The report "
            "discloses NO per-program split of the 1,353 units and no FY2025 "
            "multifamily dollar-production total, so this is a single-subprogram "
            "category (subprogram = headline), no dollar amount. The same-section "
            "cumulative block (\"nearly $1.9 billion... 1,065 developments totaling "
            "65,739 units. Another 87 developments, comprising 5,255 units, are in "
            "various stages of completion\") is lifetime + pipeline and is excluded."
        ),
        "fy2025_amounts": [],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "multifamily_units_opened", "fy2025_units": 1353, "fy2025_amount": None,
             "color_group": "trust",
             # ACFR: HOME/HTF are Federal Programs recognized in AHFA's single
             # enterprise fund as nonoperating (proprietary); LIHTC/Workforce
             # credits are fee-administered (off_balance_sheet); multifamily
             # bonds are conduit debt (off_balance_sheet). The aggregate mixes
             # both, with no disclosed split -> "mixed". See module docstring.
             "fund_type": "mixed",
             "fund_name": "HOME + LIHTC + HTF + Multifamily Revenue Bonds + Workforce Housing Credit (aggregate; no per-program split disclosed)",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# Per this build's explicit task briefing: AHFA's report has NO complete
# per-project FY2025 cohort list (the "Groundbreakings + Ribbon Cuttings"
# section is "a sampling of this year's accomplishments" -- six editorial case
# studies -- and the Workforce Housing Credit item is a forward-looking
# "projected"/"estimated" pipeline). RAW_PROJECTS is intentionally empty; see
# module docstring.
RAW_PROJECTS = []


def verify_category_consistency():
    errors = []
    warnings = []

    # homeownership: single subprogram must equal the 2,443-household headline
    # (additive=True with 1 subprogram = the headline).
    ho = next(c for c in CATEGORIES if c["key"] == "homeownership")
    if len(ho["subprograms"]) != 1:
        errors.append(f"homeownership: expected 1 subprogram, got {len(ho['subprograms'])}")
    else:
        sp = ho["subprograms"][0]
        if sp["fy2025_units"] != ho["fy2025_actual"]:
            errors.append(f"homeownership: subprogram units {sp['fy2025_units']} "
                          f"!= headline {ho['fy2025_actual']}")
        if sp["fy2025_amount"] is not None:
            errors.append("homeownership: no FY2025 dollar total is disclosed; "
                          "subprogram amount must be None")
    if ho["fy2025_amounts"]:
        errors.append("homeownership: no FY2025 dollar total is disclosed; "
                      "fy2025_amounts must be []")

    # multifamily_development: single subprogram must equal the 1,353-unit
    # headline (additive=True with 1 subprogram = the headline).
    mf = next(c for c in CATEGORIES if c["key"] == "multifamily_development")
    if len(mf["subprograms"]) != 1:
        errors.append(f"multifamily_development: expected 1 subprogram, got {len(mf['subprograms'])}")
    else:
        sp = mf["subprograms"][0]
        if sp["fy2025_units"] != mf["fy2025_actual"]:
            errors.append(f"multifamily_development: subprogram units {sp['fy2025_units']} "
                          f"!= headline {mf['fy2025_actual']}")
        if sp["fy2025_amount"] is not None:
            errors.append("multifamily_development: no FY2025 dollar total is disclosed; "
                          "subprogram amount must be None")
    if mf["fy2025_amounts"]:
        errors.append("multifamily_development: no FY2025 dollar total is disclosed; "
                      "fy2025_amounts must be []")

    # The "1,890 more" is the report's OWN "future" figure and must NOT appear
    # as any category's fy2025_actual (year discipline).
    for c in CATEGORIES:
        if c["fy2025_actual"] in (1890, 206000, 90000, 65739, 5255):
            errors.append(f"{c['key']}: fy2025_actual {c['fy2025_actual']} is a "
                          "future/cumulative figure and must be excluded")

    if RAW_PROJECTS:
        errors.append(
            "RAW_PROJECTS is expected to be empty for AL -- see module docstring; "
            "if a complete per-project cohort list has since become available, "
            "update the docstring before populating this list."
        )

    for w in warnings:
        print(f"WARNING: {w}")
    if errors:
        raise SystemExit("Category consistency mismatch(es):\n" + "\n".join(errors))
    print("Category headline vs. subprogram consistency verified: "
          "homeownership (2,443 households = single subprogram), "
          "multifamily_development (1,353 units = single subprogram). "
          "Future figure 1,890 and cumulative 206,000/90,000/65,739/5,255 "
          "confirmed excluded. RAW_PROJECTS confirmed empty as expected.")


def main():
    verify_category_consistency()
    payload = {
        "AL": {
            "hfa_name": "Alabama Housing Finance Authority",
            "hfa_abbr": "AHFA",
            "fiscal_year": "FY2025",
            "source_title": "Alabama Housing Finance Authority 2025 Annual Report "
                             "(Canva) -- Homeownership & Multifamily program KPIs",
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
