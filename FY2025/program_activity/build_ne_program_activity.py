"""
Builds docs/ne_program_activity.json from the Nebraska Investment Finance
Authority's (NIFA) "Fiscal Year 2025 Impact Report: From Vision to Action",
plus NIFA's own FY2025 audited financial statements (for GASB fund-type
classification). This is a KPI-layer-only build, like VA/MA -- see "Why
RAW_PROJECTS is empty" below.

Source
------------------------------------------------------------------------
Landing page (report is also linked from the catalog URL
https://www.nifa.org/about/financials/):
    https://www.nifa.org/annual-report
Direct PDF (S3 asset served by NIFA's CMS, downloaded and archived per this
build's task briefing; verified live 2026-08-16, HTTP 200, 6,853,615 bytes,
20 pages, pypdf-extracted text confirms the "Affordable Rental Housing",
"Affordable Homeownership", "Workforce Housing", and "Emergency Rental
Assistance" sections and their "FY25 IMPACT" figures):
    https://www-nifa-org-files.s3.amazonaws.com/88a4-06737177-2025_NIFAImpactReport_FINAL_4.pdf
Local copy:
    FY2025/program_activity/pdf/NE_NIFA_AnnualImpactReport_FY2025.pdf

Fiscal year: FY2025 = NIFA's fiscal year, July 1, 2024 - June 30, 2025. The
report is titled "Fiscal Year 2025 Impact Report" and its cumulative
"since inception" figures are all stated "through June 30, 2025", matching
NIFA's ACFR fiscal year end of June 30, 2025 (the archived
FY2025/txt/NE_NIFA_FY2025_ACFR.txt contains the same annual-report front
matter plus the audited financial statements "June 30, 2025 and 2024").
No calendar-year ambiguity: every "FY25 IMPACT" figure below is a fiscal-year
figure.

Every figure below is transcribed directly from this build's own local PDF
extraction (pypdf, page-by-page), not from memory or a secondary source.
PDF page numbers below are the printed page numbers; pypdf 0-indexed pages
are one less.

  - AFFORDABLE RENTAL HOUSING (printed PDF p.7): "Since inception, NIFA has
    allocated $2 billion of federal LIHTC and $385.4 million of Nebraska
    AHTC." [historical cumulative, NOT used]. "FY25 IMPACT: $213.8M awarded
    in federal LIHTC and Nebraska's AHTC for 1,237 units. $372.2M stimulated
    by production of affordable units. 17 affordable rental developments
    awarded, including: 155 special needs units, 185 elderly units, 897
    family units (Note: Some units count in more than one category.) 391
    developments (13,798 units) under compliance."
  - AFFORDABLE HOMEOWNERSHIP (printed PDF p.8): "Since inception, NIFA has
    helped 104,501 Nebraska households achieve homeownership, financing
    nearly $9 billion and providing over $128 million in down payment
    assistance." [historical cumulative, NOT used]. "FY25 IMPACT: 2,976
    first mortgage loans ($648M), including: 2,319 First Home loans ($480M),
    657 Welcome Home loans ($168M) - including 150 repeat NIFA buyers.
    ... 1,756 second mortgage loans ($18.2M), including: 1,238 Homebuyer
    Assistance ($12M), 518 Welcome Home Assistance ($6.2M). ... 302 loans to
    households at or below 50% AMI. 76 counties served."
  - WORKFORCE HOUSING (printed PDF p.13): "FY25 IMPACT: $349,347 Rural
    Workforce Housing NIFA match funds invested; 8 Rural Workforce Housing
    units created that meet NIFA's moderate income requirements. $1.2M Urban
    Workforce Housing NIFA match funds invested; 22 Urban Workforce Housing
    units created that meet NIFA's moderate income requirements."
  - EMERGENCY RENTAL ASSISTANCE (printed PDF p.14): "FY25 IMPACT: 2,517
    applications approved; $17.9M in assistance distributed; 70 Nebraska
    counties served; 1,433 applications approved for households with incomes
    below 50% AMI." (The PDF's raw text prints the figure as "$17. 9M" with
    a stray internal space -- an extraction/kerning artifact of the source's
    own number formatting, not a transcription choice; the value is $17.9M.)

IMPORTANT -- historical-cumulative figures explicitly excluded
------------------------------------------------------------------------
Per this build's task briefing, the following "since inception" figures
appear adjacent to the FY2025 figures above but are NOT FY2025 activity and
are never used as a fy2025_actual/fy2025_amount/fy2025_amounts value anywhere
in this script: $2 billion federal LIHTC allocated since inception; $385.4
million Nebraska AHTC allocated since inception; 104,501 households helped
into homeownership (cumulative); "nearly $9 billion" financed (cumulative);
"over $128 million in down payment assistance" (cumulative); 25,298
second-time borrowers served (cumulative, not in the extracted page but a
well-known cumulative figure); 1,085 beginning farmer/rancher loans / "over
$143 million in tax-exempt financing" (cumulative). Only figures the report
frames as "FY25 IMPACT" (this fiscal year) are used.

Why RAW_PROJECTS is empty ([]) -- the report discloses no complete
per-project cohort list
------------------------------------------------------------------------
The Affordable Rental Housing section reports "17 affordable rental
developments awarded" but never names or itemizes those 17 developments with
per-project units, dollars, cities, or addresses (the only project-level
narratives are three editorially-selected human-interest case studies --
Founders Row West, a Grand Island CROWN home, and one property-manager
profile -- not a machine-readable, complete list of all 17). Transcribing
aggregate "17 developments / 1,237 units" as if it were a complete
per-project dataset would misrepresent NIFA's disclosure, which this
project's methodology (see build_ma_program_activity.py / build_va_program_
activity.py docstrings) explicitly prohibits. RAW_PROJECTS is therefore []
and the output `projects` array is empty -- an honest reflection of what the
FY2025 Impact Report discloses at project level, not a placeholder for
missing work. The frontend renders the KPI cards normally and the bubble map
with 0 markers.

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
Source: FY2025/txt/NE_NIFA_FY2025_ACFR.txt. VERIFIED before use: the file
contains the same "From Vision to Action" annual-report front matter plus
"Financial Statements and Supplemental Data June 30, 2025 and 2024 Nebraska
Investment Finance Authority" and an Independent Auditor's Report whose
qualified opinion covers "the financial statements of the business-type
activities of the Nebraska Investment Finance Authority (the Authority), as
of and for the years ended June 30, 2025 and 2024". The Notes state the
"Authority is a self-supporting entity and follows enterprise fund
accounting." Unambiguously the correct entity; NIFA has business-type
(proprietary/enterprise) activities only -- NO governmental funds, NO
fiduciary funds. Classification therefore reduces to three cases:

  - "proprietary", HIGH confidence (NIFA's own enterprise-fund business):
      * homeownership_loans (first_home / welcome_home subprograms) -- NIFA's
        "Single Family Program" originates these first mortgages, funded by
        the Authority's own tax-exempt/taxable single-family bond issuance
        (the report's "Funding Growth and Development" section: "$744.4M
        issued to fund loans for low- to moderate-income homebuyers").
      * downpayment_assistance (homebuyer_assistance /
        welcome_home_assistance subprograms) -- second-mortgage loans; the
        ACFR loan-portfolio note lists "Second mortgage (Homebuyer
        Assistance) loans" among the Authority's own loan receivables.
      * workforce_housing_grant (rural_workforce / urban_workforce
        subprograms) -- NIFA "match funds" granted to nonprofit developers
        (the Rural Workforce Housing Fund, LB518, and Middle Income Workforce
        Housing Fund, LB866); with no governmental fund in NIFA's structure,
        these match funds are held/expended within the enterprise fund.
      * emergency_rental_assistance (era2 subprogram) -- the ACFR's "Grant
        Revenue and Expense" note states "The Authority is a subrecipient of
        grant funds in connection with the federal ... Emergency Rental
        Assistance Fund ..." -- i.e. the federal ERA2 pass-through is
        recognized as grant revenue/expense within NIFA's own enterprise
        fund, not as a separate governmental fund. Confidence: high.
  - "off_balance_sheet", HIGH confidence:
      * multifamily_lihtc (special_needs / elderly / family subprograms) --
        the ACFR states "The Authority has been designated as the allocating
        agency for the Federal Low Income Housing Tax Credit Program (the
        LIHTC Program) and the Nebraska Affordable Housing Tax Credit Program
        (the AHTC Program)"; the credits themselves flow to developers and
        investors, and NIFA only earns a compliance-monitoring fee amortized
        over the 15-year compliance period. Same off-balance-sheet logic as
        every other pilot state's LIHTC treatment.

Category-level methodology
------------------------------------------------------------------------
multifamily_lihtc: additive=False. The three subprograms (special_needs 155,
elderly 185, family 897) sum to 1,237 -- exactly the headline -- but the
source explicitly states "Note: Some units count in more than one category",
so they are NOT a true partition (a unit may be both "elderly" and "special
needs"). additive=False (reference chips, not a stacked bar) is therefore
the honest display, even though the transcribed numbers coincidentally sum
to the headline (verified in verify_category_consistency() as a transcription
check only). The headline amount is $213.8M of LIHTC/AHTC tax credits
(off_balance_sheet); "$372.2M stimulated by production" is shown only as a
reference chip, not as a modeled subprogram, because it is a derived
total-development-cost figure with no paired unit count.

homeownership_loans: additive=True. first_home (2,319 / $480M) +
welcome_home (657 / $168M) = 2,976 / $648M exactly -- a true partition of the
report's own headline (verified). The "150 repeat NIFA buyers" is a subset of
welcome_home, not an additional line.

downpayment_assistance: additive=True. homebuyer_assistance (1,238 / $12M) +
welcome_home_assistance (518 / $6.2M) = 1,756 / $18.2M exactly -- a true
partition (verified). These are the report's "second mortgage loans" (down
payment assistance), distinct from the first-mortgage category above.

workforce_housing_grant: additive=True. rural_workforce (8 / $349,347) +
urban_workforce (22 / $1.2M) = 30 units. The report prints no combined total
for workforce housing (it lists rural and urban as separate bullets), so the
30-unit headline is computed here (8 + 22) and asserted in
verify_category_consistency() -- the PA "compute the column sum yourself"
pattern. The category-level fy2025_amounts is empty because no combined
dollar total is printed and the urban figure is rounded ("$1.2M"); each
subprogram carries its own disclosed amount. The urban "$1.2M" is NIFA's own
rounded phrasing (no more precise figure is disclosed), expanded to
1,200,000 here consistent with the report's rounding, matching VA's "$1.4B"
-> 1,400,000,000 precedent.

emergency_rental_assistance: additive=True with a single subprogram exactly
equal to the category headline (same pattern as VA's federal_assistance and
MA's categories). The report discloses only one ERA2 total (2,517
applications approved / $17.9M distributed); the "1,433 applications ...
below 50% AMI" is a subset, not a separate partition.

Dual verification gate
------------------------------------------------------------------------
The transcribed unit/dollar sums reproduce the source document's own printed
totals (internal), asserted in verify_category_consistency(): 155+185+897 =
1,237; 2,319+657 = 2,976 and $480M+$168M = $648M; 1,238+518 = 1,756 and
$12M+$6.2M = $18.2M; 8+22 = 30; ERA2 single subprogram = 2,517/$17.9M. No
second, independent external number exists for these exact FY2025 figures:
the only other NIFA FY2025-affordable-housing numbers in the public record
are a December 2025 press release announcing a *subsequent* round of 4% LIHTC
awards ("more than $13 million ... 828 new ... 346 preserved units"), which
covers a different award round and is not a cross-check of these figures.
That gap is documented here rather than papered over.

fetched_retrieved
------------------------------------------------------------------------
`retrieved` is fixed to the task briefing's date string; not a live
timestamp.
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "ne_program_activity.json"

SOURCE_URL = "https://www.nifa.org/annual-report"
SOURCE_FILE = (
    "NE_NIFA_AnnualImpactReport_FY2025.pdf (downloaded from "
    "https://www-nifa-org-files.s3.amazonaws.com/88a4-06737177-"
    "2025_NIFAImpactReport_FINAL_4.pdf; verified live 2026-08-16, "
    "6,853,615 bytes, 20 pages)"
)
RETRIEVED = "2026-08-16"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "neFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data (FY25 IMPACT figures, printed PDF pages 7, 8, 13, 14)
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "multifamily_lihtc",
        "unit_type": "units",
        "fy2025_actual": 1237,
        "fy2025_source_quote": (
            "\"Affordable Rental Housing -- FY25 IMPACT: $213.8M awarded in federal "
            "LIHTC and Nebraska's AHTC for 1,237 units. $372.2M stimulated by production "
            "of affordable units. 17 affordable rental developments awarded, including: "
            "155 special needs units, 185 elderly units, 897 family units (Note: Some "
            "units count in more than one category.) 391 developments (13,798 units) "
            "under compliance.\" (NIFA Fiscal Year 2025 Impact Report, p.7). "
            "\"Since inception, NIFA has allocated $2 billion of federal LIHTC and "
            "$385.4 million of Nebraska AHTC\" is historical-cumulative and NOT used. "
            "155 + 185 + 897 = 1,237, exactly the headline, but additive=False is used "
            "because the source explicitly states some units count in more than one "
            "category (not a true partition) -- see module docstring. The $372.2M "
            "\"stimulated by production\" figure is shown only as a reference amount "
            "below (a derived total-development-cost figure with no paired unit count), "
            "not modeled as its own subprogram."
        ),
        "fy2025_amounts": [
            {"label_key": "ne_amt_lihtc_ahtc", "amount": 213800000},
            {"label_key": "ne_amt_lihtc_production", "amount": 372200000},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "special_needs", "fy2025_units": 155, "fy2025_amount": None,
             "color_group": "credit",
             # ACFR: NIFA is "the allocating agency for the ... LIHTC Program
             # and the ... AHTC Program"; credits flow to developers, NIFA
             # earns only a compliance-monitoring fee.
             "fund_type": "off_balance_sheet",
             "fund_name": "LIHTC / Nebraska AHTC (NIFA is the statutory allocating agency; credits flow to developers)",
             "fy2026": _FY26_PENDING},
            {"key": "elderly", "fy2025_units": 185, "fy2025_amount": None,
             "color_group": "credit",
             "fund_type": "off_balance_sheet",
             "fund_name": "LIHTC / Nebraska AHTC (NIFA is the statutory allocating agency; credits flow to developers)",
             "fy2026": _FY26_PENDING},
            {"key": "family", "fy2025_units": 897, "fy2025_amount": None,
             "color_group": "credit",
             "fund_type": "off_balance_sheet",
             "fund_name": "LIHTC / Nebraska AHTC (NIFA is the statutory allocating agency; credits flow to developers)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "homeownership_loans",
        "unit_type": "households",
        "fy2025_actual": 2976,
        "fy2025_source_quote": (
            "\"Affordable Homeownership -- FY25 IMPACT: 2,976 first mortgage loans "
            "($648M), including: 2,319 First Home loans ($480M), 657 Welcome Home loans "
            "($168M) - including 150 repeat NIFA buyers.\" (NIFA Fiscal Year 2025 Impact "
            "Report, p.8). \"Since inception, NIFA has helped 104,501 Nebraska households "
            "achieve homeownership, financing nearly $9 billion and providing over $128 "
            "million in down payment assistance\" is historical-cumulative and NOT used. "
            "2,319 + 657 = 2,976 loans and $480M + $168M = $648M, an exact partition of "
            "the report's own headline (verified in verify_category_consistency()); the "
            "150 repeat NIFA buyers are a subset of Welcome Home, not an additional line."
        ),
        "fy2025_amounts": [
            {"label_key": "ne_amt_first_mortgage_total", "amount": 648000000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "first_home", "fy2025_units": 2319, "fy2025_amount": 480000000,
             "color_group": "bond",
             # ACFR: business-type/enterprise fund only; the Single Family
             # Program's first mortgages are funded by the Authority's own
             # single-family bond issuance.
             "fund_type": "proprietary",
             "fund_name": "Single Family Program (tax-exempt/taxable bond-financed first mortgages)",
             "fy2026": _FY26_PENDING},
            {"key": "welcome_home", "fy2025_units": 657, "fy2025_amount": 168000000,
             "color_group": "bond",
             "fund_type": "proprietary",
             "fund_name": "Single Family Program (tax-exempt/taxable bond-financed first mortgages)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "downpayment_assistance",
        "unit_type": "households",
        "fy2025_actual": 1756,
        "fy2025_source_quote": (
            "\"Affordable Homeownership -- FY25 IMPACT: 1,756 second mortgage loans "
            "($18.2M), including: 1,238 Homebuyer Assistance ($12M), 518 Welcome Home "
            "Assistance ($6.2M).\" (NIFA Fiscal Year 2025 Impact Report, p.8). These are "
            "the report's down-payment-assistance second-mortgage products (the same "
            "page's cumulative line frames the program as \"over $128 million in down "
            "payment assistance\" since inception). 1,238 + 518 = 1,756 loans and $12M + "
            "$6.2M = $18.2M, an exact partition of the report's own headline (verified in "
            "verify_category_consistency())."
        ),
        "fy2025_amounts": [
            {"label_key": "ne_amt_second_mortgage_total", "amount": 18200000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "homebuyer_assistance", "fy2025_units": 1238, "fy2025_amount": 12000000,
             "color_group": "capital",
             # ACFR loan-portfolio note lists "Second mortgage (Homebuyer
             # Assistance) loans" among the Authority's own loan receivables.
             "fund_type": "proprietary",
             "fund_name": "Single Family Program (second-mortgage down payment assistance loans)",
             "fy2026": _FY26_PENDING},
            {"key": "welcome_home_assistance", "fy2025_units": 518, "fy2025_amount": 6200000,
             "color_group": "capital",
             # Same second-mortgage structure as Homebuyer Assistance,
             # disclosed on the same "Affordable Homeownership" page.
             "fund_type": "proprietary",
             "fund_name": "Single Family Program (second-mortgage down payment assistance loans)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "workforce_housing_grant",
        "unit_type": "units",
        "fy2025_actual": 30,
        "fy2025_source_quote": (
            "\"Workforce Housing -- FY25 IMPACT: $349,347 Rural Workforce Housing NIFA "
            "match funds invested; 8 Rural Workforce Housing units created that meet "
            "NIFA's moderate income requirements. $1.2M Urban Workforce Housing NIFA "
            "match funds invested; 22 Urban Workforce Housing units created that meet "
            "NIFA's moderate income requirements.\" (NIFA Fiscal Year 2025 Impact Report, "
            "p.13). The report prints no combined workforce-housing total (rural and "
            "urban are separate bullets), so the 30-unit headline is computed here as "
            "8 + 22 and asserted in verify_category_consistency(); the category-level "
            "fy2025_amounts is empty because no combined dollar total is printed and the "
            "urban figure is rounded (\"$1.2M\", NIFA's own phrasing, expanded to "
            "1,200,000 here)."
        ),
        "fy2025_amounts": [],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "rural_workforce", "fy2025_units": 8, "fy2025_amount": 349347,
             "color_group": "capital",
             # ACFR: NIFA is enterprise-fund only; the Rural Workforce Housing
             # Fund (LB518) match funds are expended within that fund.
             "fund_type": "proprietary",
             "fund_name": "Rural Workforce Housing Fund match funds (LB518; enterprise fund)",
             "fy2026": _FY26_PENDING},
            {"key": "urban_workforce", "fy2025_units": 22, "fy2025_amount": 1200000,
             "color_group": "capital",
             # ACFR: enterprise fund only; Middle Income Workforce Housing
             # Fund (LB866) match funds. Urban amount is the source's rounded
             # "$1.2M".
             "fund_type": "proprietary",
             "fund_name": "Middle Income Workforce Housing Fund match funds (LB866; enterprise fund; source prints rounded \"$1.2M\")",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "emergency_rental_assistance",
        "unit_type": "households",
        "fy2025_actual": 2517,
        "fy2025_source_quote": (
            "\"Emergency Rental Assistance -- FY25 IMPACT: 2,517 applications approved; "
            "$17.9M in assistance distributed; 70 Nebraska counties served; 1,433 "
            "applications approved for households with incomes below 50% AMI.\" (NIFA "
            "Fiscal Year 2025 Impact Report, p.14). The report's raw text prints the "
            "amount as \"$17. 9M\" with a stray internal space (an extraction artifact "
            "of the source's own number formatting), read as $17.9M. The \"1,433 ... "
            "below 50% AMI\" is a subset of the 2,517, not a separate partition; no "
            "further breakdown by county or source is disclosed. \"Applications "
            "approved\" is used as the household proxy (each application is a renter "
            "household); unit_type is \"households\"."
        ),
        "fy2025_amounts": [
            {"label_key": "ne_amt_era2_distributed", "amount": 17900000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "era2", "fy2025_units": 2517, "fy2025_amount": 17900000,
             "color_group": "trust",
             # ACFR "Grant Revenue and Expense" note: "The Authority is a
             # subrecipient of grant funds in connection with the federal ...
             # Emergency Rental Assistance Fund ..." -- recognized as grant
             # revenue/expense within NIFA's enterprise fund.
             "fund_type": "proprietary",
             "fund_name": "Emergency Rental Assistance Fund (federal ERA2 subrecipient grant, recognized in the enterprise fund)",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# Per this build's task briefing and the "Why RAW_PROJECTS is empty" section
# of the module docstring: NIFA's FY2025 Impact Report discloses "17
# affordable rental developments awarded" only in aggregate, never as a
# complete, named, machine-readable per-project list with units/dollars/
# cities/addresses. RAW_PROJECTS is therefore intentionally empty -- the
# allowed, honest outcome for a KPI-only state (not a placeholder for missing
# work).
RAW_PROJECTS = []


def verify_category_consistency():
    errors = []

    # multifamily_lihtc: 155 + 185 + 897 must equal the 1,237-unit headline
    # (transcription check). additive=False is a DISPLAY decision because the
    # source says "some units count in more than one category"; the arithmetic
    # summing exactly to the headline is still asserted so a transcription
    # error cannot silently pass.
    mf = next(c for c in CATEGORIES if c["key"] == "multifamily_lihtc")
    mf_sum = sum(sp["fy2025_units"] for sp in mf["subprograms"])
    if mf_sum != mf["fy2025_actual"]:
        errors.append(
            f"multifamily_lihtc: subprogram units sum to {mf_sum}, expected "
            f"{mf['fy2025_actual']} (155 special_needs + 185 elderly + 897 family)"
        )

    # homeownership_loans: first_home + welcome_home must equal 2,976 loans
    # and $480M + $168M must equal $648M (true partition, additive=True).
    ho = next(c for c in CATEGORIES if c["key"] == "homeownership_loans")
    ho_units = sum(sp["fy2025_units"] for sp in ho["subprograms"])
    ho_amt = sum(sp["fy2025_amount"] for sp in ho["subprograms"])
    if ho_units != ho["fy2025_actual"]:
        errors.append(f"homeownership_loans: subprogram units sum to {ho_units}, expected {ho['fy2025_actual']}")
    if ho_amt != 648000000:
        errors.append(f"homeownership_loans: subprogram amounts sum to {ho_amt}, expected 648000000")

    # downpayment_assistance: 1,238 + 518 = 1,756; $12M + $6.2M = $18.2M.
    dpa = next(c for c in CATEGORIES if c["key"] == "downpayment_assistance")
    dpa_units = sum(sp["fy2025_units"] for sp in dpa["subprograms"])
    dpa_amt = sum(sp["fy2025_amount"] for sp in dpa["subprograms"])
    if dpa_units != dpa["fy2025_actual"]:
        errors.append(f"downpayment_assistance: subprogram units sum to {dpa_units}, expected {dpa['fy2025_actual']}")
    if dpa_amt != 18200000:
        errors.append(f"downpayment_assistance: subprogram amounts sum to {dpa_amt}, expected 18200000")

    # workforce_housing_grant: 8 rural + 22 urban = 30 units (computed headline).
    wf = next(c for c in CATEGORIES if c["key"] == "workforce_housing_grant")
    wf_sum = sum(sp["fy2025_units"] for sp in wf["subprograms"])
    if wf_sum != wf["fy2025_actual"]:
        errors.append(f"workforce_housing_grant: subprogram units sum to {wf_sum}, expected {wf['fy2025_actual']}")

    # emergency_rental_assistance: single subprogram must exactly equal the
    # category headline (additive=True with 1 subprogram is only meaningful
    # if the subprogram *is* the headline).
    era = next(c for c in CATEGORIES if c["key"] == "emergency_rental_assistance")
    if len(era["subprograms"]) != 1:
        errors.append(f"emergency_rental_assistance: expected exactly 1 subprogram, got {len(era['subprograms'])}")
    else:
        sp = era["subprograms"][0]
        if sp["fy2025_units"] != era["fy2025_actual"]:
            errors.append(f"emergency_rental_assistance: subprogram units {sp['fy2025_units']} != category fy2025_actual {era['fy2025_actual']}")
        cat_amt = era["fy2025_amounts"][0]["amount"] if era["fy2025_amounts"] else None
        if cat_amt is not None and sp["fy2025_amount"] != cat_amt:
            errors.append(f"emergency_rental_assistance: subprogram amount {sp['fy2025_amount']} != category fy2025_amounts[0].amount {cat_amt}")

    if RAW_PROJECTS:
        errors.append(
            "RAW_PROJECTS is expected to be empty for NE -- see module docstring; "
            "if a complete project-level list has since become available, update "
            "the docstring before populating this list."
        )

    if errors:
        raise SystemExit("Category consistency mismatch(es):\n" + "\n".join(errors))
    print("Category headline vs. subprogram consistency verified for all 5 categories "
          "(multifamily_lihtc: 155+185+897=1,237 units; homeownership_loans: "
          "2,319+657=2,976 / $480M+$168M=$648M; downpayment_assistance: "
          "1,238+518=1,756 / $12M+$6.2M=$18.2M; workforce_housing_grant: 8+22=30; "
          "emergency_rental_assistance: single subprogram = 2,517/$17.9M); RAW_PROJECTS "
          "confirmed empty as expected.")


def main():
    verify_category_consistency()
    payload = {
        "NE": {
            "hfa_name": "Nebraska Investment Finance Authority",
            "hfa_abbr": "NIFA",
            "fiscal_year": "FY2025",
            "source_title": "NIFA Fiscal Year 2025 Impact Report -- \"From Vision to "
                             "Action\" (Affordable Rental Housing, Affordable Homeownership, "
                             "Workforce Housing, and Emergency Rental Assistance sections)",
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
