"""
Builds docs/ks_program_activity.json from the Kansas Housing Resources
Corporation's (KHRC) "2025 Annual Report" -- a KPI-layer-only build (no
per-project cohort), like LA/VA/AK. See "Why RAW_PROJECTS is empty" below.

Source
------------------------------------------------------------------------
"KHRC Annual Report 2025", Kansas Housing Resources Corporation (KHRC):
    https://kshousingcorp.org/wp-content/uploads/2025/12/KHRC-Annual-Report-2025.pdf
Text was extracted from the PDF to a local temp file for this build and every
figure below is transcribed from that extraction (page-by-page), not from
memory or a secondary source.

Fiscal-year discipline
------------------------------------------------------------------------
The report is KHRC's "2025 Annual Report" and its KPI tiles are all labeled
"2025"/"IN 2025" (e.g. "2,178 TOTAL HOMES CREATED IN 2025"). KHRC's state
fiscal year runs July 1 - June 30 (FY2025 = July 1, 2024 - June 30, 2025),
matching every other state in this pilot's Jul-Jun convention; the report
never prints an explicit span, so it is treated as a loose "2025" narrative
and the figures are reported under fiscal_year "FY2025". The one explicit
multi-year figure -- "Federal and state resources funded 7,206 homes from
2022 to 2025" (PDF page 5) -- is a 4-year cumulative total and is EXCLUDED
from every fy2025_* value.

Every figure below is transcribed from this build's own local PDF text
extraction:
  - HOUSING DEVELOPMENT (PDF page 8): "2,178 / TOTAL HOMES CREATED IN 2025"
    is the only text-extractable tile. The accompanying tiles -- "SINGLE-
    FAMILY UNITS CREATED", "MULTIFAMILY UNITS CREATED", "NEW HOMES
    CONSTRUCTED", "HOMES REHABILITATED", "DEVELOPMENTS FUNDED", "COUNTIES
    SERVED" -- are image-rendered in the PDF (their values are not present in
    the extracted text), so the 2,178 total cannot be partitioned and is
    modeled as a single headline with additive=False-like treatment (one
    subprogram equal to the headline; see CATEGORIES).
  - WEATHERIZATION ASSISTANCE (PDF page 7): "785 / HOMES WEATHERIZED" is the
    core output KPI. Supporting tiles (image-mixed layout, extracted as):
    "528 / HEATING SOURCES INSTALLED", "67% / OF WEATHERIZED HOMES RECIEVED
    [sic] A NEW PRIMARY HEATING SOURCE", "770,139 / SQUARE FEET OF INSULATION
    INSTALLED", "7,136 / LED BULBS INSTALLED", "30 / ENERGY STAR
    REFRIGERATORS INSTALLED", "396 / NEW A/Cs OR HEAT PUMPS INSTALLED". These
    are supporting activity metrics with no clean per-home partition, so only
    the 785-home headline is modeled. No dollar amount is disclosed for the
    Weatherization Assistance Program on this page.
  - PROJECT BASED RENTAL ASSISTANCE COMPLIANCE (PDF page 9): "KHRC's Contract
    Administration division administers the state's Project Based Rental
    Assistance contract to ensure that the 10,893 units in 224 properties
    throughout the state are kept in safe, decent, and sanitary conditions."
    Tiles: "$72M / PAID IN HOUSING ASSISTANCE PAYMENTS (HAP) ON BEHALF OF HUD
    TENANTS", "386 / TENANT CONCERNS ADDRESSED, 38 OF WHICH WERE
    LIFE-THREATENING", "133 / MANAGEMENT OCCUPANCY REPORTS COMPLETED", "15 /
    CONTRACT RENEWALS", "210 / RENT ADJUSTMENTS", "522 / SPECIAL CLAIMS
    PROCESSED". The 10,893-unit / $72M-HAP pair is the core PBRA KPI; the
    other tiles are contract-administration activity metrics, not additional
    units or dollars.

Excluded (monitoring/outreach, not housing-production KPI)
------------------------------------------------------------------------
The HOUSING COMPLIANCE section (PDF page 9) prints 171 physical inspections,
148 HOME & Housing Trust Fund rent reviews, 598 annual reports reviewed, 145
tenant file audits, and 124 tenant concerns addressed. These are monitoring/
oversight functions (KHRC's "Housing Compliance division provides monitoring
and oversight of properties"), not housing production or assistance units, so
they are referenced here but not modeled as categories.

Why RAW_PROJECTS is empty ([]) -- no complete per-project cohort list
------------------------------------------------------------------------
KHRC's 2025 Annual Report has NO complete per-project FY2025 cohort list. The
report's project mentions are a handful of editorial case studies with layered
financing (e.g. "Abilene Terrace", "Willow Estates, Colby" 18 townhomes,
"Cottonwood Lofts" 10 apartments, "Union at Tower District" 250 homes) --
illustrative vignettes, not a complete, extractable per-development cohort.
The 2,178-homes headline's single-family/multifamily/rehab sub-numbers are
image-rendered, so no per-project unit detail is recoverable. RAW_PROJECTS is
therefore [] and the output `projects` array is empty -- the honest KPI-only
result, not a placeholder. The frontend (docs/program_activity.js) renders the
KPI cards normally and the bubble map with 0 markers.

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
IMPORTANT: the local ACFR text corpus entry for Kansas
(FY2025/txt/KS_KHRC_FY2025_ACFR.txt) is actually the STATE OF KANSAS's own
government-wide CAFR, NOT KHRC's audited financial statements -- so fund_type
CANNOT be derived from it (no KHRC component-unit fund schedules are present).
This matches the known wrong-document issue flagged in the multistate pilot
memory ("GA & KS txt are the STATE government's CAFR, not the HFA's").

Instead, classification below rests on the annual report's own description of
KHRC's structure plus the conventions already used for peer HFAs, with the
confidence level stated per subprogram:
  - The report (PDF page 4) describes KHRC as "a subsidiary corporation of the
    Kansas Development Finance Authority (KDFA)" and "a self-supporting,
    nonprofit, public corporation" that "does not receive operational revenue
    from the state of Kansas but sustains itself through a State Housing Trust
    Fund (SHTF) funded through fees for services and grant administration cost
    reimbursement." Like LHC (Louisiana) and most self-supporting HFAs, KHRC's
    operations are business-type (proprietary) rather than governmental.
  - "mixed" (LOW confidence) -- housing_solutions/homes_created. The 2,178
    homes are produced across a blended portfolio: LIHTC/KAHTC/KHITC tax
    credits (off-balance-sheet, credits flow to developers), federal
    HOME/NHTF pass-through grants, and state MIH/RLF/PAB programs. The report
    gives no per-program FY2025 unit split, so the single headline cannot be
    classified to one fund type; "mixed" is the honest bucket.
  - "proprietary" (MEDIUM confidence) -- weatherization (federal DOE
    Weatherization Assistance Program pass-through) and PBRA (HUD Project-Based
    Rental Assistance contract administration with HAP pass-through). These are
    federal pass-through programs that KHRC recognizes within its own
    self-supporting corporate fund (same treatment as every other pilot state's
    federal pass-through), but the exact FY2025 dollar amounts are not
    reconciled to a specific financial statement line (no KHRC ACFR available),
    so confidence is medium, not high.
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "ks_program_activity.json"

SOURCE_URL = "https://kshousingcorp.org/wp-content/uploads/2025/12/KHRC-Annual-Report-2025.pdf"
SOURCE_FILE = (
    "KHRC-Annual-Report-2025.pdf (downloaded from the kshousingcorp.org URL "
    "above; text extracted for this build to a local temp file, page-by-page "
    "via pypdf)"
)
RETRIEVED = "2026-08-16"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "ksFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data (KHRC 2025 Annual Report)
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "housing_solutions",
        "unit_type": "units",
        "fy2025_actual": 2178,
        "fy2025_source_quote": (
            "\"2,178 TOTAL HOMES CREATED IN 2025\" (KHRC 2025 Annual Report, "
            "HOUSING DEVELOPMENT, PDF p.8). The page's accompanying KPI tiles -- "
            "\"SINGLE-FAMILY UNITS CREATED\", \"MULTIFAMILY UNITS CREATED\", "
            "\"NEW HOMES CONSTRUCTED\", \"HOMES REHABILITATED\", \"DEVELOPMENTS "
            "FUNDED\", \"COUNTIES SERVED\" -- are image-rendered in the PDF (their "
            "values are not present in the extracted text), so only the 2,178 "
            "total-home headline can be transcribed. The single-family/"
            "multifamily/rehab sub-numbers cannot be partitioned and no "
            "subprogram unit split is asserted (single subprogram = the headline). "
            "No dollar amount is disclosed for this total. NOTE: the report also "
            "prints \"Federal and state resources funded 7,206 homes from 2022 to "
            "2025\" (PDF p.5) -- a 4-year cumulative total, NOT a FY2025 figure, "
            "and therefore excluded."
        ),
        "fy2025_amounts": [],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "homes_created", "fy2025_units": 2178, "fy2025_amount": None,
             "color_group": "capital",
             # No KHRC ACFR available (the local KS txt is the STATE OF KANSAS
             # CAFR). The 2,178 homes span tax credits + federal pass-through +
             # state funds with no per-program split disclosed, so "mixed" is
             # the honest bucket. Confidence: low.
             "fund_type": "mixed",
             "fund_name": "Mixed housing-development portfolio (federal HOME/NHTF pass-through, LIHTC/KAHTC/KHITC tax credits, state MIH/RLF/PAB; no per-program FY2025 unit split disclosed)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "weatherization",
        "unit_type": "units",
        "fy2025_actual": 785,
        "fy2025_source_quote": (
            "\"785 HOMES WEATHERIZED\" (KHRC 2025 Annual Report, WEATHERIZATION "
            "ASSISTANCE, PDF p.7). Accompanying KPI tiles: 528 heating sources "
            "installed, 67% of weatherized homes received a new primary heating "
            "source, 770,139 square feet of insulation installed, 7,136 LED "
            "bulbs installed, 30 ENERGY STAR refrigerators installed, 396 new "
            "A/Cs or heat pumps installed. The 785 homes-weatherized headline is "
            "the core output KPI; the other tiles are supporting activity "
            "metrics with no clean per-home partition, so only the 785-home "
            "figure is modeled. No dollar amount is disclosed for the "
            "Weatherization Assistance Program on this page."
        ),
        "fy2025_amounts": [],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "homes_weatherized", "fy2025_units": 785, "fy2025_amount": None,
             "color_group": "trust",
             # Federal DOE Weatherization Assistance Program pass-through,
             # recognized in KHRC's self-supporting corporate fund (no KHRC
             # ACFR to reconcile against). Confidence: medium.
             "fund_type": "proprietary",
             "fund_name": "Federal Weatherization Assistance Program pass-through (recognized in KHRC's self-supporting corporate fund)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "rental_assistance_pbra",
        "unit_type": "units",
        "fy2025_actual": 10893,
        "fy2025_source_quote": (
            "\"KHRC's Contract Administration division administers the state's "
            "Project Based Rental Assistance contract to ensure that the 10,893 "
            "units in 224 properties throughout the state are kept in safe, "
            "decent, and sanitary conditions.\" (KHRC 2025 Annual Report, "
            "PROJECT BASED RENTAL ASSISTANCE COMPLIANCE, PDF p.9). Accompanying "
            "KPI tiles: \"$72M PAID IN HOUSING ASSISTANCE PAYMENTS (HAP) ON "
            "BEHALF OF HUD TENANTS\", 386 tenant concerns addressed (38 of which "
            "were life-threatening), 133 management occupancy reports completed, "
            "15 contract renewals, 210 rent adjustments, 522 special claims "
            "processed. The 10,893 units / $72M HAP pair is the core PBRA KPI; "
            "the other tiles are contract-administration activity metrics, not "
            "additional units or dollars, and are quoted here for completeness "
            "but not modeled. The separately-listed HOUSING COMPLIANCE figures "
            "(171 inspections, 148 HOME/HTF rent reviews, 598 annual reports, "
            "145 audits, 124 concerns) are a monitoring function, not rental "
            "assistance, and are not modeled."
        ),
        "fy2025_amounts": [
            {"label_key": "ks_amt_hap", "amount": 72000000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "pbra", "fy2025_units": 10893, "fy2025_amount": 72000000,
             "color_group": "trust",
             # HUD Project-Based Rental Assistance contract administration with
             # HAP pass-through, recognized in KHRC's self-supporting corporate
             # fund (no KHRC ACFR to reconcile against). Confidence: medium.
             "fund_type": "proprietary",
             "fund_name": "HUD Project-Based Rental Assistance contract (HAP pass-through, recognized in KHRC's self-supporting corporate fund)",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# Per this build's explicit task briefing: KHRC's 2025 Annual Report has NO
# complete per-project FY2025 cohort list (only scattered editorial case
# studies, and the headline's single-family/multifamily/rehab sub-numbers are
# image-rendered). RAW_PROJECTS is intentionally empty; see module docstring.
RAW_PROJECTS = []


def verify_category_consistency():
    errors = []
    warnings = []

    # housing_solutions: single subprogram must equal the 2,178-home headline
    # (additive=True with 1 subprogram = the headline), and no dollar amount.
    hs = next(c for c in CATEGORIES if c["key"] == "housing_solutions")
    if len(hs["subprograms"]) != 1:
        errors.append(f"housing_solutions: expected 1 subprogram, got {len(hs['subprograms'])}")
    else:
        sp = hs["subprograms"][0]
        if sp["fy2025_units"] != hs["fy2025_actual"]:
            errors.append(f"housing_solutions: subprogram units {sp['fy2025_units']} "
                          f"!= headline {hs['fy2025_actual']}")
    if hs["fy2025_amounts"]:
        errors.append("housing_solutions: no dollar amount is disclosed in the source")

    # weatherization: single subprogram must equal the 785-home headline.
    wz = next(c for c in CATEGORIES if c["key"] == "weatherization")
    if len(wz["subprograms"]) != 1:
        errors.append(f"weatherization: expected 1 subprogram, got {len(wz['subprograms'])}")
    else:
        sp = wz["subprograms"][0]
        if sp["fy2025_units"] != wz["fy2025_actual"]:
            errors.append(f"weatherization: subprogram units {sp['fy2025_units']} "
                          f"!= headline {wz['fy2025_actual']}")
    if wz["fy2025_amounts"]:
        errors.append("weatherization: no dollar amount is disclosed in the source")

    # rental_assistance_pbra: single subprogram must equal the 10,893-unit /
    # $72,000,000-HAP headline.
    pbra = next(c for c in CATEGORIES if c["key"] == "rental_assistance_pbra")
    if len(pbra["subprograms"]) != 1:
        errors.append(f"rental_assistance_pbra: expected 1 subprogram, got {len(pbra['subprograms'])}")
    else:
        sp = pbra["subprograms"][0]
        if sp["fy2025_units"] != pbra["fy2025_actual"]:
            errors.append(f"rental_assistance_pbra: subprogram units {sp['fy2025_units']} "
                          f"!= headline {pbra['fy2025_actual']}")
        if sp["fy2025_amount"] != pbra["fy2025_amounts"][0]["amount"]:
            errors.append(f"rental_assistance_pbra: subprogram amount {sp['fy2025_amount']} "
                          f"!= headline amount {pbra['fy2025_amounts'][0]['amount']} ($72M)")

    # The report's 7,206-homes figure is 2022-2025 cumulative -- must NOT appear
    # anywhere in a fy2025_* value (sanity guard against the recurring trap).
    for c in CATEGORIES:
        if c["fy2025_actual"] == 7206:
            errors.append(f"{c['key']}: fy2025_actual is 7,206 (the 4-year cumulative, not FY2025)")

    if RAW_PROJECTS:
        errors.append(
            "RAW_PROJECTS is expected to be empty for KS -- see module docstring; "
            "if a complete per-project cohort list has since become available, "
            "update the docstring before populating this list."
        )

    for w in warnings:
        print(f"WARNING: {w}")
    if errors:
        raise SystemExit("Category consistency mismatch(es):\n" + "\n".join(errors))
    print("Category headline vs. subprogram consistency verified: "
          "housing_solutions (2,178 homes, 1 subprogram), weatherization "
          "(785 homes, 1 subprogram), rental_assistance_pbra (10,893 units / "
          "$72,000,000 HAP, 1 subprogram). RAW_PROJECTS confirmed empty as expected.")


def main():
    verify_category_consistency()
    payload = {
        "KS": {
            "hfa_name": "Kansas Housing Resources Corporation",
            "hfa_abbr": "KHRC",
            "fiscal_year": "FY2025",
            "source_title": "Kansas Housing Resources Corporation 2025 Annual Report -- "
                             "HOUSING DEVELOPMENT / WEATHERIZATION ASSISTANCE / "
                             "PROJECT BASED RENTAL ASSISTANCE chapters (homes created, "
                             "weatherization, PBRA)",
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
