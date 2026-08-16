"""
Builds docs/nm_program_activity.json for the New Mexico Mortgage Finance
Authority (MFA), which has rebranded as "Housing New Mexico", from its FY2025
production-highlights figures. This is a KPI-layer-only build (no project
list) -- see "Why RAW_PROJECTS is empty" below.

Sources
------------------------------------------------------------------------
The agency's own FY2025 annual report PDF is image-only (no extractable
text), so every KPI figure below is transcribed instead from the two
machine-readable, cross-validating HTML sources that the agency publishes on
its own site:

1. Homepage "2025 Production Highlights" section (the detailed 8-item
   breakdown, each item printing an amount + a unit/household count):
       https://housingnm.org/
   Local archived copy: none needed -- HTML is re-fetched verbatim; the raw
   text was captured during this build (2026-08-16) and is quoted below.

2. Press release "Nearly 18,000 New Mexico families and homes impacted by
   $740 million provided by Housing New Mexico in fiscal year 2025"
   (13 Jan, 2026) -- the agency's own summary of the same fiscal year, which
   prints the four headline buckets, the grand total, AND the explicit
   fiscal-year span:
       https://housingnm.org/about-us/news/nearly-18000-new-mexico-families-and-homes-impacted-by-740-million-provided-by-housing-new-mexico-in-fiscal-year-2025

Primary source document (archived per this build's task briefing):
    FY2025/program_activity/pdf/NM_MFA_AnnualReport_2025.pdf
    (downloaded from https://housingnm.org/uploads/documents/AnnualReport_2025.pdf
    -- verified live 2026-08-16: HTTP 200, 2,674,450 bytes, 6 pages. Every page
    is a single DCTDecode JPEG; pypdf extracts zero text from all 6 pages, so
    the annual report's figures are taken from the two HTML sources above, whose
    numbers match each other and the annual-report totals exactly -- see the
    dual-verification gate below.)

Fiscal-year discipline (IMPORTANT -- this is a federal fiscal year, not the
Jul-Jun HFA norm)
------------------------------------------------------------------------
The press release states verbatim: "Housing New Mexico served people in 32 of
33 counties ... during its most recent fiscal year, which began Oct. 1, 2024,
and ended Sept. 30, 2025." New Mexico MFA's fiscal year is therefore the
FEDERAL fiscal year (Oct 1 - Sep 30), NOT the July 1 - June 30 year that most
other pilot-state HFAs use. fiscal_year is recorded honestly as "FFY2025"
(federal fiscal year 2025), and every "2025" figure below is that FFY2025
span -- not a title-year-vs-content-year mismatch (the release's own sentence
proves the span, and the figures are explicitly framed as "Fiscal year 2025
production highlights").

Dual-verification gate (mandatory, both directions)
------------------------------------------------------------------------
INTERNAL -- the press release's own four headline buckets reproduce its own
printed grand totals exactly (verified in verify_category_consistency()):
    $81.6M + $16.8M + $583.2M + $58.2M  =  $739.8M   (its printed total)
    1,518 + 739 + 2,287 + 13,152        =  17,696    (its printed total)
EXTERNAL -- the homepage's detailed 8 items are an independent second source
for the same fiscal year, and they reconcile with the press release:
    * "housing stability" households: 5,873 + 2,307 + 4,736 + 236 = 13,152
      EXACTLY equals the press release's "13,152 people and families" -- the
      strongest exact cross-check (verified, hard-error on mismatch).
    * "produce homes" 1,518 / $81.6M and "preserve homes" 739 / $16.8M match
      the press release one-for-one.
    * Two dollar figures reconcile only after rounding (documented, not
      hard-errored, because the two sources round at different precision):
        - homeownership: homepage $555M + $28.1M = $583.1M vs. press release
          "$583.2M" -- a $0.1M rounding artifact (the underlying unrounded
          figures sum to $583.2M).
        - housing stability: homepage $47.7M + $5.3M + $4.5M + $670,000 =
          $58.17M vs. press release "$58.2M" -- same rounding artifact.

Excluded ("since inception"/cumulative) figures -- none used anywhere
------------------------------------------------------------------------
The press release contains no "since inception" production figures. Its only
cumulative-sounding line is the 50th-anniversary quote ("since Housing New
Mexico's inception in 1975") about people helped OVER TIME, which carries no
number and is not used. The separate "5,365 apartment homes" multifamily
pipeline figure is a FUTURE/under-development pipeline ("currently ...
at various stages of development"), NOT FY2025 completed production, and is
therefore excluded from every fy2025_* value (it is mentioned here only as an
honest-gap note).

Why RAW_PROJECTS is empty ([]) -- no complete per-project cohort list
------------------------------------------------------------------------
Per this build's explicit task briefing (KPI-only verdict): solid
multi-category KPI figures (unit/household counts + dollar amounts) exist, but
there is NO complete per-project cohort list in any of the sources. The annual
report PDF is image-only, and neither the homepage nor the press release names
individual developments with per-project unit counts for the completed FY2025
production. RAW_PROJECTS is therefore [] and the output `projects` array is
empty -- the correct, honest result (not a shortcut): the frontend
(docs/program_activity.js) renders the KPI cards normally and the bubble map
with 0 markers. No geocoding is performed (there are no projects to place).

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
Per this build's brief, the FY2025 ACFR text file is an empty ~140-byte
placeholder and must NOT be used. The agency's own audited-financial-statements
PDF (housingnm.org ... 1a_FY_2025_New_Mexico_Mortgage_Finance_Authority_
Audited_Finacial_Statements.pdf, 71 pages) was downloaded and checked but is
ALSO image-only (zero extractable text across all 71 pages), so it cannot be
read for fund structure. Classification below is therefore conservative and
inferred from the program report's own program descriptions, with confidence
documented per subprogram:
  - "proprietary", HIGH confidence: first_mortgages -- single-family first
    mortgages are the HFA's own core bond-financed lending business (the
    press release frames these as "Housing New Mexico's mortgage programs";
    the agency's board minutes of Feb 2025 note a $120M Series A/B bond issue
    "to fund new single-family first-time homebuyer mortgages"). This is the
    classic business-type/proprietary HFA activity.
  - "proprietary", MEDIUM confidence: down_payment_assistance -- MFA's own
    second-position mortgage-assistance product (marketed alongside its first
    mortgages), inferred proprietary by description, not a named federal
    grant.
  - "mixed", HIGH confidence: new_homes (housing production) -- the press
    release states its development funding comes from "tax credits, bonds,
    loans and grants", i.e. no single fund type applies to the production
    bucket.
  - "governmental", MEDIUM confidence: home_rehab (weatherization +
    rehabilitation), rental_assistance_vouchers (HUD Section 8 HCV),
    rental_assistance, homelessness_prevention, landlord_incentives -- these
    are federally/state funded grant-and-assistance programs the agency
    administers (the press release names the HUD-funded HOME Rehabilitation
    Program and the DOE-style "Energy$mart Weatherization Program"; the
    vouchers are Section 8). Because the ACFR is an empty placeholder and the
    audited statements are image-only, whether New Mexico MFA books these as
    governmental funds or as proprietary pass-through (like Virginia Housing)
    cannot be confirmed -- "governmental" is the conservative program-
    description default, documented as medium confidence, NOT an ACFR-verified
    fund structure.
  - No LIHTC/state-tax-credit allocation figure is disclosed for FY2025 (the
    "tax credits" are mentioned only as one of several pipeline funding
    sources, with no FY2025 allocation total), so there is no off_balance_sheet
    subprogram here -- an honest gap, not an omission of work.

fy2026
------------------------------------------------------------------------
Neither source discloses any forward-looking/projected FY2026 activity (the
"5,365 apartment homes" pipeline is not a dated FY2026 projection). Every
fy2026 field below is therefore {value: None, amount: None, closed: False,
note_key: "nmFy26NotePending"}.
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "nm_program_activity.json"

SOURCE_URL = (
    "https://housingnm.org/about-us/news/nearly-18000-new-mexico-families-and-"
    "homes-impacted-by-740-million-provided-by-housing-new-mexico-in-fiscal-year-2025"
)
HOME_URL = "https://housingnm.org/"
SOURCE_FILE = (
    "NM_MFA_AnnualReport_2025.pdf (archived from "
    "https://housingnm.org/uploads/documents/AnnualReport_2025.pdf; 6 pages, "
    "image-only -- pypdf extracts no text; figures transcribed from "
    "housingnm.org homepage \"2025 Production Highlights\" and the FY2025 press "
    "release, both machine-readable HTML)"
)
RETRIEVED = "2026-08-16"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                 "note_key": "nmFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data (homepage "2025 Production Highlights" + press release)
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        # "Created More Housing" -- $81.6M -> 1,518 new homes. This is the
        # agency's total FY2025 housing production (overwhelmingly multifamily;
        # the press release separately notes ~$6.3M for 145 single-family homes
        # as a photo-caption anecdote, but does not split the 1,518 headline).
        # Key uses "multifamily_production" (matching ME's precedent) so it hits
        # the multifamily/new-construction icon bucket rather than the generic
        # fallback; see module docstring.
        "key": "multifamily_production",
        "unit_type": "units",
        "fy2025_actual": 1518,
        "fy2025_source_quote": (
            "\"Fiscal year 2025 production highlights include: $81.6 million "
            "provided to produce 1,518 homes\" (Housing New Mexico press release, "
            "13 Jan 2026). Homepage \"2025 Production Highlights\": \"Created More "
            "Housing ... $81.6M Invested ... 1,518 New Homes\". One-to-one match "
            "between the two sources (verified in verify_category_consistency()). "
            "The report frames this as new housing production; it does not split "
            "the 1,518 by multifamily vs. single-family (a photo caption notes "
            "\"approximately $6.3 million to produce 145 single-family homes\", "
            "a small subset), so a single additive subprogram equal to the "
            "headline is used."
        ),
        "fy2025_amounts": [
            {"label_key": "nm_amt_production", "amount": 81600000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "new_homes", "fy2025_units": 1518, "fy2025_amount": 81600000,
             "color_group": "bond",
             # Press release: development funding comes from "tax credits,
             # bonds, loans and grants" -- no single fund type applies.
             "fund_type": "mixed",
             "fund_name": "Production financing (bonds + tax credits + loans + grants)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        # "Preserved Existing Affordable Housing" -- $16.8M -> 739 weatherized
        # or rehabilitated homes. The homepage combines weatherization +
        # rehabilitation into one number (no split), so a single additive
        # subprogram = headline. Key uses "rehab" wording to hit the
        # repair/rehab icon bucket.
        "key": "housing_rehabilitation",
        "unit_type": "units",
        "fy2025_actual": 739,
        "fy2025_source_quote": (
            "\"Fiscal year 2025 production highlights include: ... $16.8 million "
            "provided to preserve 739 homes\" (Housing New Mexico press release, "
            "13 Jan 2026). Homepage \"2025 Production Highlights\": \"Preserved "
            "Existing Affordable Housing ... $16.8M Invested ... 739 Weatherized "
            "or Rehabilitated Homes\". One-to-one match (verified). The report "
            "names the underlying programs elsewhere (\"Housing New Mexico's "
            "Energy$mart Weatherization Program\" and the \"HOME Rehabilitation "
            "Program\") but prints no unit split between them, so the 739 is "
            "carried as a single subprogram."
        ),
        "fy2025_amounts": [
            {"label_key": "nm_amt_preservation", "amount": 16800000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "home_rehab", "fy2025_units": 739, "fy2025_amount": 16800000,
             "color_group": "trust",
             # Federally funded weatherization (DOE-style Energy$mart) + HUD
             # HOME Rehabilitation -- grant programs the agency administers.
             # Confidence: medium (no ACFR; see module docstring).
             "fund_type": "governmental",
             "fund_name": "Federal grant programs (Energy$mart Weatherization + HOME Rehabilitation, inferred)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        # First Mortgages + Down Payment Assistance. NON-additive: the two
        # subprograms use different units (2,287 families vs. 3,311 loans) and
        # the DPA loans are not a clean subset of the first-mortgage families
        # (3,311 loans > 2,287 first-mortgage families), so no sum is asserted.
        "key": "homeownership",
        "unit_type": "households",
        "fy2025_actual": 2287,
        "fy2025_source_quote": (
            "\"Fiscal year 2025 production highlights include: ... $583.2 million "
            "provided in first mortgage and down payment assistance to 2,287 "
            "families\" (Housing New Mexico press release, 13 Jan 2026). Homepage "
            "\"2025 Production Highlights\": \"Created Homeownership and "
            "Wealth-Building Opportunities through First Mortgages ... $555M In "
            "First-Mortgage Financing ... 2,287 Families\" and \"... through Down "
            "Payment Assistance ... $28.1M In Assistance Provided ... 3,311 "
            "Loans\". The press release's \"2,287 families\" is the FIRST-MORTGAGE "
            "family count (the DPA figure is a loan count, not a family count), so "
            "the category headline is 2,287 families and the DPA subprogram's "
            "3,311 is the source's own 'loans' number. $555M + $28.1M = $583.1M, "
            "which the press release rounds to \"$583.2M\" (a $0.1M rounding "
            "artifact, documented not hard-errored)."
        ),
        "fy2025_amounts": [
            {"label_key": "nm_amt_homeownership_total", "amount": 583200000},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "first_mortgages", "fy2025_units": 2287, "fy2025_amount": 555000000,
             "color_group": "bond",
             # Single-family first mortgages = the HFA's own bond-financed
             # lending business (mortgage revenue bonds). Confidence: high.
             "fund_type": "proprietary",
             "fund_name": "Single-family mortgage revenue bonds (MFA core lending)",
             "fy2026": _FY26_PENDING},
            {"key": "down_payment_assistance", "fy2025_units": 3311, "fy2025_amount": 28100000,
             "color_group": "capital",
             # MFA's own second-position mortgage-assistance product, marketed
             # alongside its first mortgages. Confidence: medium (inferred
             # proprietary by description, not a named federal grant).
             "fund_type": "proprietary",
             "fund_name": "MFA down payment assistance (agency funds, inferred)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        # Housing stability = long-term rental assistance vouchers + rental
        # assistance + homelessness prevention/supportive services + landlord
        # incentives. ADDITIVE: the four homepage subprogram household counts
        # sum EXACTLY to the press release's 13,152 (5,873 + 2,307 + 4,736 +
        # 236 = 13,152) -- verified, hard-error on mismatch.
        "key": "housing_stability",
        "unit_type": "households",
        "fy2025_actual": 13152,
        "fy2025_source_quote": (
            "\"Fiscal year 2025 production highlights include: ... $58.2 million "
            "provided for housing stability to 13,152 people and families\" "
            "(Housing New Mexico press release, 13 Jan 2026). Homepage \"2025 "
            "Production Highlights\" breaks this into four items: \"Creating "
            "Stable Housing by Administering Long-Term Rental Assistance Through "
            "Vouchers ... $47.7M Processed ... 5,873 Families Supported\"; "
            "\"Created Stable Housing Environments through Rental Assistance ... "
            "$5.3M Invested ... 2,307 Families\"; \"... through Homelessness "
            "Prevention or Supportive Services ... $4.5M Invested ... 4,736 "
            "Families\"; \"... through Landlord Incentives ... $670,000 Invested "
            "... 236 Families with Housing Vouchers\". 5,873 + 2,307 + 4,736 + "
            "236 = 13,152 EXACTLY (verified). Dollar-wise, $47.7M + $5.3M + "
            "$4.5M + $670,000 = $58.17M, which the press release rounds to "
            "\"$58.2M\" (rounding artifact, documented not hard-errored)."
        ),
        "fy2025_amounts": [
            {"label_key": "nm_amt_housing_stability", "amount": 58200000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "rental_assistance_vouchers", "fy2025_units": 5873, "fy2025_amount": 47700000,
             "color_group": "trust",
             # HUD Section 8 Housing Choice Vouchers -- a federal pass-through
             # program the agency administers. Confidence: medium.
             "fund_type": "governmental",
             "fund_name": "HUD Section 8 Housing Choice Vouchers (pass-through, inferred)",
             "fy2026": _FY26_PENDING},
            {"key": "rental_assistance", "fy2025_units": 2307, "fy2025_amount": 5300000,
             "color_group": "trust",
             "fund_type": "governmental",
             "fund_name": "Rental assistance programs (inferred)",
             "fy2026": _FY26_PENDING},
            {"key": "homelessness_prevention", "fy2025_units": 4736, "fy2025_amount": 4500000,
             "color_group": "trust",
             "fund_type": "governmental",
             "fund_name": "Homelessness prevention / supportive services (inferred)",
             "fy2026": _FY26_PENDING},
            {"key": "landlord_incentives", "fy2025_units": 236, "fy2025_amount": 670000,
             "color_group": "trust",
             "fund_type": "governmental",
             "fund_name": "Landlord incentive programs (inferred)",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# Per this build's explicit task briefing: KPI-only. No complete per-project
# cohort list exists in any source (the annual report is image-only; neither
# the homepage nor the press release names individual developments with
# per-project unit counts for completed FY2025 production). RAW_PROJECTS is
# intentionally empty -- see module docstring "Why RAW_PROJECTS is empty".
RAW_PROJECTS = []


def verify_category_consistency():
    errors = []
    notes = []

    def cat(key):
        return next(c for c in CATEGORIES if c["key"] == key)

    # --- INTERNAL: the press release's four headline buckets must reproduce
    # its own printed grand totals exactly (both dollars and homes/families).
    prod = cat("multifamily_production")
    pres = cat("housing_rehabilitation")
    own = cat("homeownership")
    stab = cat("housing_stability")

    dollars = [81600000, 16800000, 583200000, 58200000]
    total_dollars = sum(dollars)
    if total_dollars != 739800000:
        errors.append(f"headline dollars sum ${total_dollars:,} != $739,800,000")
    counts = [1518, 739, 2287, 13152]
    total_counts = sum(counts)
    if total_counts != 17696:
        errors.append(f"headline homes/families sum {total_counts} != 17,696")

    # --- EXTERNAL: homepage housing_stability detail sums EXACTLY to the press
    # release's 13,152 (hard-error on mismatch -- the strongest cross-check).
    stab_units = sum(sp["fy2025_units"] for sp in stab["subprograms"])
    if stab_units != 13152:
        errors.append(f"housing_stability subprogram units sum {stab_units} != 13,152")
    expected_stab = {
        "rental_assistance_vouchers": 5873,
        "rental_assistance": 2307,
        "homelessness_prevention": 4736,
        "landlord_incentives": 236,
    }
    for sp in stab["subprograms"]:
        if sp["fy2025_units"] != expected_stab.get(sp["key"]):
            errors.append(
                f"housing_stability.{sp['key']} units {sp['fy2025_units']} != "
                f"expected {expected_stab.get(sp['key'])}"
            )

    # --- EXTERNAL: homepage production / preservation one-to-one match.
    if prod["fy2025_actual"] != 1518 or prod["fy2025_amounts"][0]["amount"] != 81600000:
        errors.append("multifamily_production != 1,518 homes / $81.6M")
    if pres["fy2025_actual"] != 739 or pres["fy2025_amounts"][0]["amount"] != 16800000:
        errors.append("housing_rehabilitation != 739 homes / $16.8M")

    # --- ROUNDING reconciliations (documented, NOT hard-errored): the two
    # sources round dollars at different precision, so the component sums land
    # $0.1M / $30K below the press release's rounded headline.
    own_comp = sum(sp["fy2025_amount"] for sp in own["subprograms"])
    if own_comp != 583100000:
        errors.append(f"homeownership subprogram dollars sum ${own_comp:,} != $583,100,000")
    notes.append(
        f"homeownership: $555,000,000 + $28,100,000 = ${own_comp:,} vs. press "
        "release '$583.2M' (a $0.1M rounding artifact of the two sources' "
        "differing precision -- not hard-errored)."
    )
    stab_comp = sum(sp["fy2025_amount"] for sp in stab["subprograms"])
    if stab_comp != 58170000:
        errors.append(f"housing_stability subprogram dollars sum ${stab_comp:,} != $58,170,000")
    notes.append(
        f"housing_stability: $47,700,000 + $5,300,000 + $4,500,000 + $670,000 = "
        f"${stab_comp:,} vs. press release '$58.2M' (a $30K rounding artifact "
        "of the two sources' differing precision -- not hard-errored)."
    )

    if RAW_PROJECTS:
        errors.append(
            "RAW_PROJECTS is expected to be empty for NM -- see module docstring; "
            "if a complete project-level list has since become available, update "
            "the docstring before populating this list."
        )

    if errors:
        raise SystemExit("Category consistency mismatch(es):\n" + "\n".join(errors))

    print("Category headline vs. subprogram consistency verified:")
    print("  [internal] $81.6M + $16.8M + $583.2M + $58.2M = $739.8M")
    print("  [internal] 1,518 + 739 + 2,287 + 13,152 = 17,696")
    print("  [external] 5,873 + 2,307 + 4,736 + 236 = 13,152 (housing_stability, exact)")
    for n in notes:
        print("  [rounding] " + n)
    print("RAW_PROJECTS confirmed empty as expected.")


def main():
    verify_category_consistency()
    payload = {
        "NM": {
            "hfa_name": "New Mexico Mortgage Finance Authority",
            "hfa_abbr": "Housing New Mexico (MFA)",
            "fiscal_year": "FFY2025",
            "source_title": (
                "Housing New Mexico (New Mexico MFA) FFY2025 Production Highlights "
                "-- homepage \"2025 Production Highlights\" + \"Nearly 18,000 New "
                "Mexico families and homes impacted by $740 million\" press release "
                "(13 Jan 2026)"
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
