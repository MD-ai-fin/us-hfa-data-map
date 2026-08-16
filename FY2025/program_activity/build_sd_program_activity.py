"""
Builds docs/sd_program_activity.json from South Dakota Housing's (South Dakota
Housing Development Authority, "SD Housing") "SD Housing Annual Report"
(FY2025) plus South Dakota Housing's own FY2025 audited financial report (for
GASB fund-type classification and one external cross-check). This is a
KPI-layer-only build, like VA -- see "Why RAW_PROJECTS is empty" below.

Source
------------------------------------------------------------------------
"SD Housing Annual Report" (2025 / FY2025), South Dakota Housing, served from
the SD Housing "Financials & Reports" investor page:
    https://www.sdhousing.org/housing-partners/investors/financials-reports
    (the task brief's catalog URL https://www.sdhda.org/about/financial-reports/
    is a legacy domain that 301-redirects to sdhousing.org; the report list
    lives at the "Financials & Reports" URL above).
Annual Report PDF (direct static URL):
    https://www.sdhousing.org/s/SDH_AnnualReport_2025_V4.pdf
Local copy, downloaded and archived per this build's task briefing (verified
live 2026-08-16: HTTP 200, 3,454,227 bytes, 42 pages):
    FY2025/program_activity/pdf/SD_SDHousing_AnnualReport_2025.pdf

FY2025 = South Dakota Housing's fiscal year, July 1, 2024 - June 30, 2025.
The annual report's "A Year-in-Review" chapter runs "JULY 2024" through "JUNE
2025", and the report's own "FY25 At-A-Glance" table and "FY25" labels tie it
to the same fiscal year as SD Housing's audited financial report, which is for
"the years ended June 30, 2025 and 2024" (title page). No content-year
ambiguity: the homeownership totals below are labeled "FY25" in the report.

Every figure below is transcribed directly from this build's own local PDF
extraction (pypdf, page-by-page), not from memory or a secondary source:

  - HOMEOWNERSHIP PROGRAMS (printed page 16, pypdf index 15):
      "$587,214,365 -- Mortgage loan funds provided for first-time and repeat
      homebuyers."  "2,502 -- First-time or repeat homebuyers received loans
      from SD Housing."  "2,096 -- Loans for first-time homebuyers totaling
      $480,451,950."  "389 -- Loans for repeat homebuyers totaling
      $104,123,296."  "17 -- Loans for Mortgage Credit Certificate Program
      totaling $2,639,119."  "58 -- Loans for Home Improvement totaling
      $1,282,903 [separate program, see below]."  "807 -- Homebuyers received
      $7,884,841 in downpayment assistance [second-mortgage DPA, separate]."
      "956 -- Grants received from SD Housing totaling $11,528,507 for
      downpayment assistance [grant DPA, separate]."
      2,096 + 389 + 17 = 2,502 loans and $480,451,950 + $104,123,296 +
      $2,639,119 = $587,214,365, both EXACT partitions of the headline
      (verified in verify_category_consistency()). The "2,502 first-time or
      repeat homebuyers" headline therefore includes the 17 MCC loans (MCC
      recipients are also first-time/repeat homebuyers); the 58 Home
      Improvement loans are a distinct program and are NOT part of this
      headline (2,096 + 389 + 17 + 58 = 2,560 would over-count).

  - RENTAL HOUSING DEVELOPMENT (printed page 22, pypdf index 21):
      "South Dakota Housing awarded $109,845,684 to develop or preserve 2,331
      units of affordable housing. These projects will result in new
      construction of 546 multifamily rental units, 4 single-family rental
      units and 43 single-family homes; rehabilitation of 91 multifamily
      rental units; infrastructure for 797 new single-family lots and 722
      multifamily lots; homebuyer assistance for 25 homebuyers; rehab
      assistance for 36 homeowners and homelessness prevention assistance for
      67 individuals/families."  Stat cards: "2,331 Total Units Created",
      "$109,845,684 Total Financing Awarded", "$243,908,240 Total Development
      Costs", "33 Total Developments Funded", "9 Total Programs Funded".
      Program Financing (printed page 23): "$15.1M Housing Infrastructure
      Financing; $2.7M Housing Opportunity Fund; $2.9M Housing Trust Fund;
      $4.3M HOME Investment Partnership; $81.5M Bond; $3.3M Housing Tax
      Credits."  The unit composition (593 new construction + 91 rehab +
      1,519 infrastructure lots + 25 + 36 + 67 = 2,331) is an EXACT partition
      of SD Housing's own "Total Units Created" headline (verified). The six
      program-financing figures sum to $109.8M, consistent with the printed
      $109,845,684 total within the report's own $0.1M rounding (not hard-
      asserted, since the source itself printed the components only to $0.1M).

  - RENTAL HOUSING MANAGEMENT / SECTION 8 (printed page 25, pypdf index 24):
      "SD Housing provided $229,855,780 in Section 8 housing assistance
      payments for affordable housing."  Detail box: "Section 8 and 811 PRA:
      Total Assistance Paid $29,855,780; Total Number of Units 4,863."
      IMPORTANT: the narrative "$229,855,780" contains a spurious leading "2"
      (a typo). Both the same page's own detail box ($29,855,780) and SD
      Housing's FY2025 audited Statement of Revenues ("HUD housing assistance
      payments 29,855,780", ACFR p.13 / .txt line 507) confirm $29,855,780 --
      an exact external cross-check against the audited ACFR (verified). This
      build uses $29,855,780, never the typo'd figure.

IMPORTANT -- figures explicitly excluded (never used as a fy2025_* value)
------------------------------------------------------------------------
  - "Housing Infrastructure Financing Program ... creating 4,893 multifamily
    units and 6,637 single-family lots, as of July 2024" (Year-in-Review,
    July 2024) -- a CUMULATIVE "as of" total, not FY2025 activity.
  - Grants for Grads: "$14 million ... supported over 1,100 recent graduates
    ... between May 2024 and May 2025" (Year-in-Review, May 2025) and
    "More than 1,100 college graduates" (Executive Director message) -- both
    rounded/approximate ("over 1,100", "$14 million") and the program
    "officially concluded", so they are not exact enough to be a KPI.
  - The downpayment-assistance figures (807 homebuyers / $7,884,841 second
    mortgages; 956 grants / $11,528,507) and Home Improvement loans (58 /
    $1,282,903) are disclosed on the same Homeownership Programs page but are
    distinct programs layered on / alongside the 2,502-loan headline, so they
    are not modeled as subprograms of homeownership_loans (see below).

Why RAW_PROJECTS is empty ([])
------------------------------------------------------------------------
SD Housing's Annual Report contains no complete per-development cohort list.
The only project-level content is (a) four editorially-selected "Testimonials"
case studies (FortyOne Flats, Timber Lake DakotaPlex, a Grants for Grads
purchase, and Weinberg Property Management's six-property portfolio) and
(b) the "FY25 At-A-Glance" city-by-city tables (printed pages 25-34), which
aggregate loan/assistance totals per CITY, not per named development. Neither
is a full-year, complete list of every individual development financed in
FY2025 (the Rental Housing Development chapter's own 33-developments/2,331-unit
headline implies a much larger population than the 4 testimonials). RAW_PROJECTS
is therefore [] and the `projects` array in the output JSON is empty -- an
honest reflection of what the source discloses at project level. The frontend
(docs/program_activity.js) renders the KPI cards normally and the bubble map
with 0 markers.

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
Source: FY2025/txt/SD_SDHDA_FY2025_ACFR.txt. VERIFIED before use: title page
reads "South Dakota Housing Development Authority (A Component Unit of the
State of South Dakota) Financial Report June 30, 2025 and 2024"; the
Independent Auditor's Report (.txt line 37) covers "the business-type
activities of the South Dakota Housing Development Authority"; and the program
descriptions throughout match this Annual Report's entity and fiscal year-end.
Unambiguously the correct entity, no substitution needed.

Unlike IHDA's mixed governmental+proprietary structure, South Dakota Housing is
a SINGLE business-type/proprietary enterprise fund: "The activity of the
Authority is accounted for as a proprietary-type fund" (.txt line 166) and "The
Authority is considered a single enterprise fund" (.txt line 595). Every
program below is therefore classified "proprietary" (HIGH confidence), with
fund_name drawn from the ACFR's own indenture descriptions (lines 597-624):

  - homeownership_loans (first_time_homebuyer, repeat_homebuyer,
    mortgage_credit_certificate): the ACFR's "Homeownership Mortgage Bonds"
    indenture (lines 613-623) "accounts for ... the Single Family Housing
    Program, and mortgage loans on eligible single family residential housing
    disbursed from bond proceeds." The transcribed dollar figures are
    first-mortgage loan principal -- SD Housing's own lending -- not tax-credit
    allocations. (For the MCC subprogram, the MCC federal income-tax credit
    itself is off-balance-sheet, but the transcribed $2,639,119 is loan
    principal, so the subprogram is proprietary.) Confidence: high.
  - rental_housing_development (new_construction, rehabilitation,
    infrastructure, homebuyer_assistance, homeowner_rehab,
    homelessness_prevention): the MD&A (.txt lines 182-184) describes the
    Authority's "primary business of construction, preservation, rehabilitation,
    purchase, and development of affordable single family and multifamily
    housing"; the program financing mix (bond proceeds + HIFP/HOF/HTF/HOME/HTC)
    flows through the same enterprise fund. The grant-funded subprograms
    (HOME/HTF/HOF/ESG) are federal/state pass-through grants, but the ACFR
    recognizes "HUD contributions" and "Fee, grant and other income" as
    operating revenues of the enterprise fund (lines 501-503), so "proprietary"
    is correct for SD's single-fund structure. Confidence: high.
  - rental_assistance (section_8_pra): the ACFR's General Operating Account
    note (.txt lines 607-609) states the account "include[s] the activities of
    statewide Section 8 Housing Assistance Payments Programs which the
    Authority administers on behalf of the U.S. Department of Housing and Urban
    Development (HUD). Under these programs, the Authority distributes housing
    assistance payments received from HUD," and the Statement of Revenues
    recognizes "HUD housing assistance payments 29,855,780" as an operating
    expense of the enterprise fund (.txt line 507). So the Section 8 HAP is a
    federal pass-through that SD Housing recognizes within its own proprietary
    fund. Confidence: high.

Category-level methodology
------------------------------------------------------------------------
homeownership_loans: additive=True. The three subprograms (first-time 2,096,
repeat 389, MCC 17) are a true, exact partition of the 2,502-loan /
$587,214,365 headline (both unit and dollar sums verified). The report's
downpayment-assistance (807/$7,884,841 second mortgages) and Home Improvement
(58/$1,282,903) figures are separate, layered products not part of this
headline, so they are documented in the source_quote/docstring but not modeled
as subprograms (adding them would break the exact partition).

rental_housing_development: additive=True. The six subprograms are SD Housing's
own unit composition of the "2,331 Total Units Created" headline (an exact
partition). NOTE: the report's "units" is heterogeneous -- it mixes rental
units, single-family homes, infrastructure LOTS, and assisted households -- per
the report's own "Total Units Created" definition, which this build mirrors
verbatim rather than silently redefining. No per-subprogram dollar amount is
disclosed (only the $109,845,684 category total and the separately-rounded
program-financing mix), so fy2025_amount is None on every subprogram.

rental_assistance: additive=True with a single subprogram exactly equal to the
category headline (same pattern as VA's federal_assistance) -- the report
discloses one Section 8/811 PRA total (4,863 units / $29,855,780), no further
breakdown.

fy2026
------------------------------------------------------------------------
The 2025 Annual Report is a backward-looking annual report with no
forward-looking/projected-activity section (checked: the string "2026" appears
only in the Year-in-Review's "SD Housing presented the 2026 budget" and the
report does not project program-level activity). Every fy2026 field below is
therefore {value: None, amount: None, closed: False, note_key:
"sdFy26NotePending"}.
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "sd_program_activity.json"

SOURCE_URL = "https://www.sdhousing.org/housing-partners/investors/financials-reports"
SOURCE_FILE = (
    "SD_SDHousing_AnnualReport_2025.pdf (downloaded from "
    "https://www.sdhousing.org/s/SDH_AnnualReport_2025_V4.pdf, listed on the "
    "SD Housing \"Financials & Reports\" page above; verified live 2026-08-16, "
    "HTTP 200, 3,454,227 bytes, 42 pages)"
)
RETRIEVED = "2026-08-16"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                 "note_key": "sdFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data (SD Housing 2025 Annual Report, printed pp. 16, 22, 25)
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "homeownership_loans",
        "unit_type": "households",
        "fy2025_actual": 2502,
        "fy2025_source_quote": (
            "\"HOMEOWNERSHIP PROGRAMS: $587,214,365 -- Mortgage loan funds "
            "provided for first-time and repeat homebuyers. 2,502 -- First-time "
            "or repeat homebuyers received loans from SD Housing. 2,096 -- Loans "
            "for first-time homebuyers totaling $480,451,950. 389 -- Loans for "
            "repeat homebuyers totaling $104,123,296. 17 -- Loans for Mortgage "
            "Credit Certificate Program totaling $2,639,119. 58 -- Loans for Home "
            "Improvement totaling $1,282,903 [separate program, not part of the "
            "2,502-loan headline]. 807 -- Homebuyers received $7,884,841 in "
            "downpayment assistance [second-mortgage DPA, separate]. 956 -- Grants "
            "received from SD Housing totaling $11,528,507 for downpayment "
            "assistance [grant DPA, separate].\" (SD Housing 2025 Annual Report, "
            "\"Homeownership Programs\", p.16). 2,096 + 389 + 17 = 2,502 loans and "
            "$480,451,950 + $104,123,296 + $2,639,119 = $587,214,365, an exact "
            "partition of the headline (verified in verify_category_consistency()). "
            "The 58 Home Improvement loans and the two downpayment-assistance "
            "figures are separate programs layered on/alongside this headline and "
            "are not modeled as subprograms."
        ),
        "fy2025_amounts": [
            {"label_key": "sd_amt_home_loans", "amount": 587214365},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "first_time_homebuyer", "fy2025_units": 2096, "fy2025_amount": 480451950,
             "color_group": "bond",
             # ACFR "Homeownership Mortgage Bonds" indenture (single-family
             # mortgage loans from bond proceeds); proprietary enterprise fund.
             "fund_type": "proprietary", "fund_name": "Homeownership Mortgage Bonds (Single Family Housing Program)",
             "fy2026": _FY26_PENDING},
            {"key": "repeat_homebuyer", "fy2025_units": 389, "fy2025_amount": 104123296,
             "color_group": "bond",
             "fund_type": "proprietary", "fund_name": "Homeownership Mortgage Bonds (Single Family Housing Program)",
             "fy2026": _FY26_PENDING},
            {"key": "mortgage_credit_certificate", "fy2025_units": 17, "fy2025_amount": 2639119,
             "color_group": "credit",
             # $2,639,119 is first-mortgage loan principal (proprietary), not
             # the off-balance-sheet MCC federal income-tax credit itself.
             "fund_type": "proprietary", "fund_name": "Mortgage Credit Certificate Program (homeownership mortgage loans)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "rental_housing_development",
        "unit_type": "units",
        "fy2025_actual": 2331,
        "fy2025_source_quote": (
            "\"RENTAL HOUSING DEVELOPMENT: South Dakota Housing awarded "
            "$109,845,684 to develop or preserve 2,331 units of affordable "
            "housing. These projects will result in new construction of 546 "
            "multifamily rental units, 4 single-family rental units and 43 "
            "single-family homes; rehabilitation of 91 multifamily rental units; "
            "infrastructure for 797 new single-family lots and 722 multifamily "
            "lots; homebuyer assistance for 25 homebuyers; rehab assistance for "
            "36 homeowners and homelessness prevention assistance for 67 "
            "individuals/families.\" (SD Housing 2025 Annual Report, \"Rental "
            "Housing Development\", p.22; stat cards \"2,331 Total Units Created\" "
            "and \"$109,845,684 Total Financing Awarded\"). 593 (new construction) "
            "+ 91 (rehab) + 1,519 (infrastructure lots) + 25 + 36 + 67 = 2,331, an "
            "exact partition of the \"Total Units Created\" headline (verified). "
            "NOTE: the report's own \"2,331 units\" is a heterogeneous count "
            "(rental units + single-family homes + infrastructure lots + assisted "
            "households), mirrored verbatim rather than redefined. Program "
            "financing (p.23) is disclosed separately as $15.1M HIFP + $2.7M HOF + "
            "$2.9M HTF + $4.3M HOME + $81.5M Bond + $3.3M HTC = $109.8M, "
            "consistent with the $109,845,684 total within the report's own $0.1M "
            "rounding."
        ),
        "fy2025_amounts": [
            {"label_key": "sd_amt_rental_development", "amount": 109845684},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "new_construction", "fy2025_units": 593, "fy2025_amount": None,
             "color_group": "bond",
             "fund_type": "proprietary", "fund_name": "Multifamily Housing Revenue Bonds / development financing (enterprise fund)",
             "fy2026": _FY26_PENDING},
            {"key": "rehabilitation", "fy2025_units": 91, "fy2025_amount": None,
             "color_group": "bond",
             "fund_type": "proprietary", "fund_name": "Multifamily Housing Revenue Bonds / development financing (enterprise fund)",
             "fy2026": _FY26_PENDING},
            {"key": "infrastructure", "fy2025_units": 1519, "fy2025_amount": None,
             "color_group": "capital",
             "fund_type": "proprietary", "fund_name": "Housing Infrastructure Financing Program (HIFP)",
             "fy2026": _FY26_PENDING},
            {"key": "homebuyer_assistance", "fy2025_units": 25, "fy2025_amount": None,
             "color_group": "trust",
             "fund_type": "proprietary", "fund_name": "HOME / HTF / HOF federal & state grants (enterprise fund)",
             "fy2026": _FY26_PENDING},
            {"key": "homeowner_rehab", "fy2025_units": 36, "fy2025_amount": None,
             "color_group": "trust",
             "fund_type": "proprietary", "fund_name": "HOME / HTF / HOF federal & state grants (enterprise fund)",
             "fy2026": _FY26_PENDING},
            {"key": "homelessness_prevention", "fy2025_units": 67, "fy2025_amount": None,
             "color_group": "trust",
             "fund_type": "proprietary", "fund_name": "Emergency Solutions Grants (ESG) / federal & state grants (enterprise fund)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "rental_assistance",
        "unit_type": "units",
        "fy2025_actual": 4863,
        "fy2025_source_quote": (
            "\"RENTAL HOUSING MANAGEMENT: SD Housing provided $229,855,780 in "
            "Section 8 housing assistance payments for affordable housing. Section "
            "8 and 811 PRA: Total Assistance Paid $29,855,780; Total Number of "
            "Units 4,863.\" (SD Housing 2025 Annual Report, \"Rental Housing "
            "Management\", p.25). The narrative \"$229,855,780\" carries a "
            "spurious leading \"2\" (a typo) -- both this page's own detail box "
            "($29,855,780) and SD Housing's FY2025 audited Statement of Revenues "
            "(\"HUD housing assistance payments 29,855,780\", ACFR p.13) confirm "
            "$29,855,780, an exact external cross-check (verified in "
            "verify_category_consistency()). This build uses $29,855,780, never the "
            "typo'd figure."
        ),
        "fy2025_amounts": [
            {"label_key": "sd_amt_rental_assistance", "amount": 29855780},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "section_8_pra", "fy2025_units": 4863, "fy2025_amount": 29855780,
             "color_group": "trust",
             # ACFR General Operating Account note: statewide Section 8 HAP
             # "administered on behalf of HUD", recognized as operating expense
             # ($29,855,780) of the proprietary enterprise fund. High confidence.
             "fund_type": "proprietary", "fund_name": "Section 8 Housing Assistance Payments (federal pass-through administered on behalf of HUD)",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# SD Housing's Annual Report has no complete per-development cohort list (only
# 4 editorial testimonials and per-city aggregates in the FY25 At-A-Glance
# tables). RAW_PROJECTS is therefore intentionally empty; see module docstring
# "Why RAW_PROJECTS is empty". This is the allowed, honest outcome: the
# frontend renders the bubble map with 0 markers when this is empty.
RAW_PROJECTS = []

# FY2025 audited ACFR cross-check value for the Section 8 housing assistance
# payment (Statement of Revenues, "HUD housing assistance payments", ACFR p.13
# / FY2025/txt/SD_SDHDA_FY2025_ACFR.txt line 507). This is an independent
# second document used to confirm the Annual Report's own detail-box figure and
# to expose the "$229,855,780" typo.
_ACFR_HUD_HAP_FY2025 = 29855780


def verify_category_consistency():
    errors = []

    # homeownership_loans: first_time + repeat + MCC must equal the 2,502-loan
    # headline AND the $587,214,365 dollar headline exactly (a true partition).
    ho = next(c for c in CATEGORIES if c["key"] == "homeownership_loans")
    ho_units = sum(sp["fy2025_units"] for sp in ho["subprograms"])
    if ho_units != ho["fy2025_actual"]:
        errors.append(
            f"homeownership_loans: subprogram units sum to {ho_units}, expected "
            f"{ho['fy2025_actual']} (2,096 first_time + 389 repeat + 17 MCC)"
        )
    ho_amt = ho["fy2025_amounts"][0]["amount"]
    ho_amt_sum = sum(sp["fy2025_amount"] for sp in ho["subprograms"])
    if ho_amt_sum != ho_amt:
        errors.append(
            f"homeownership_loans: subprogram dollars sum to {ho_amt_sum}, expected "
            f"{ho_amt} ($480,451,950 + $104,123,296 + $2,639,119)"
        )

    # rental_housing_development: 6 subprogram units must equal the 2,331
    # "Total Units Created" headline exactly.
    rd = next(c for c in CATEGORIES if c["key"] == "rental_housing_development")
    rd_units = sum(sp["fy2025_units"] for sp in rd["subprograms"])
    if rd_units != rd["fy2025_actual"]:
        errors.append(
            f"rental_housing_development: subprogram units sum to {rd_units}, "
            f"expected {rd['fy2025_actual']} (593 + 91 + 1,519 + 25 + 36 + 67)"
        )

    # rental_assistance: single subprogram must exactly equal the category
    # headline, and the dollar figure must equal the FY2025 ACFR's audited
    # "HUD housing assistance payments" (external cross-check).
    ra = next(c for c in CATEGORIES if c["key"] == "rental_assistance")
    if len(ra["subprograms"]) != 1:
        errors.append(f"rental_assistance: expected exactly 1 subprogram, got {len(ra['subprograms'])}")
    else:
        sp = ra["subprograms"][0]
        if sp["fy2025_units"] != ra["fy2025_actual"]:
            errors.append(f"rental_assistance: subprogram units {sp['fy2025_units']} != category fy2025_actual {ra['fy2025_actual']}")
        cat_amt = ra["fy2025_amounts"][0]["amount"]
        if sp["fy2025_amount"] != cat_amt:
            errors.append(f"rental_assistance: subprogram amount {sp['fy2025_amount']} != category fy2025_amounts[0].amount {cat_amt}")
        if sp["fy2025_amount"] != _ACFR_HUD_HAP_FY2025:
            errors.append(
                f"rental_assistance: amount {sp['fy2025_amount']} != FY2025 ACFR "
                f"\"HUD housing assistance payments\" {_ACFR_HUD_HAP_FY2025} "
                f"(external cross-check failed)"
            )

    if RAW_PROJECTS:
        errors.append(
            "RAW_PROJECTS is expected to be empty for SD -- see module docstring; "
            "if a complete project-level list has since become available, update "
            "the docstring before populating this list."
        )

    if errors:
        raise SystemExit("Category consistency mismatch(es):\n" + "\n".join(errors))
    print("Category headline vs. subprogram consistency verified for all 3 categories "
          "(homeownership_loans: 2,096+389+17=2,502 loans and "
          "$480,451,950+$104,123,296+$2,639,119=$587,214,365; "
          "rental_housing_development: 593+91+1,519+25+36+67=2,331 units; "
          "rental_assistance: single subprogram = 4,863 units/$29,855,780, "
          "external ACFR cross-check $29,855,780 exact); RAW_PROJECTS confirmed "
          "empty as expected.")


def main():
    verify_category_consistency()
    payload = {
        "SD": {
            "hfa_name": "South Dakota Housing",
            "hfa_abbr": "South Dakota Housing",
            "fiscal_year": "FY2025",
            "source_title": "South Dakota Housing 2025 Annual Report -- "
                             "Homeownership Programs, Rental Housing Development, "
                             "and Rental Housing Management (Section 8/811 PRA)",
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
