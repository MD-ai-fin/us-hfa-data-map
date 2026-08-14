"""
Builds docs/ak_program_activity.json from AHFC's (Alaska Housing Finance
Corporation) FY2025 Annual Report, "People Building Communities: Investing
in Alaska", cross-checked against AHFC's own FY2025 audited financial
statements for GASB fund-type classification.

KPI-only pilot -- no project-level bubble map
------------------------------------------------------------------------
Unlike IL/PA/OH/FL/WA/TX/NY/CA (which ship a per-development RAW_PROJECTS
list), this build follows MA's "KPI-layer-only" pattern per the explicit
task briefing: AK's only candidate project-level source, the "2025 LIHTC
Reservation List - Alaska" (5 projects, confirmed by direct PDF extraction
of the 2-page list, see local copy scratchpad/ahfc/lihtc2025.pdf), totals
just 124 units across 5 developments (Saxman Townhomes 20, Breezy Meadows
III 32, Baxter Family Housing 24, Valdez Affordable Housing 20, Ketchikan
PSH 28 -- unit counts verified by summing the list's own "Unit Count / Type"
field), and gives only city-level location ("Saxman", "Wasilla",
"Anchorage", "Valdez", "Ketchikan" -- no street address for any of the 5).
The only other candidate, ACAH's (Alaska Corporation for Affordable
Housing) own property list (2025 Annual Report p.33, "Building Community
Throughout Alaska"), names 5 more properties (Ridgeline Terrace 70,
Susitna Square net +2 after demolishing 16 to build 18, The Meadows 18,
Borealis Park 40, Blueberry Terrace 20), but most of these did NOT
complete in FY2025 specifically -- Borealis Park's own ribbon-cutting
photo caption dates it September 2024 (inside FY2025, since AHFC's fiscal
year runs July-June, see below), while Blueberry Terrace is explicitly
"under construction ... will open their doors to tenants in 2026" (i.e.
FY2026, not FY2025), and Ridgeline Terrace / Susitna Square / The Meadows
carry no FY2025-specific completion date in the report at all (unlike
Borealis Park, which is the one property both explicitly finished AND
dated). The two lists also overlap: LIHTC Reservation List project #4,
"Valdez Affordable Housing", is the same development the ACFR's Note 20
independently describes as receiving an $8,000,000 MTW-reserve transfer to
ACAH (FY2025/txt/AK_AHFC_FY2025_ACFR.txt, line ~1755) -- so the two
sources are not even fully additive. Combined, the two lists give at most
~10 point-in-time locations, most without a street address, several
outside the FY2025 completion window, and with at least one duplicate --
too sparse and too inconsistent in what year/precision they actually
represent to support a meaningful bubble map without fabricating
addresses, unit counts, or completion dates that the sources do not
themselves provide. Per this project's explicit "never invent a number to
fill a gap" rule, RAW_PROJECTS is therefore [] and this script only builds
the KPI/category layer -- exactly like MA's build_ma_program_activity.py.
The frontend (docs/program_activity.js) already handles this cleanly: KPI
cards render normally and the bubble map renders with 0 markers ("0
projects" in its own count legend).

Sources
------------------------------------------------------------------------
1. "2025 Annual Report -- People Building Communities: Investing in
   Alaska", Alaska Housing Finance Corporation. Landing page:
     https://www.ahfc.us/about-us/reports/2025-annual-report
   The report itself is NOT published as a downloadable PDF -- it is an
   Issuu flip-book embed:
     https://issuu.com/geretactical/docs/2025-ahfc-annual-report
   No PDF version could be located after checking both the landing page
   and the Issuu embed's own download affordances. Individual pages were
   instead captured from Issuu's page-image CDN
   (image.isu.pub/{doc_id}/jpg/page_N.jpg) as JPGs and read directly (not
   OCR'd -- each page's on-image text was read visually), local copies at
   scratchpad/ahfc/page_*.jpg (not checked into the repo; Issuu page
   numbers cited below are the report's own printed page numbers, e.g.
   "p.15", which are 2 less than the page_N.jpg filename since the cover
   and table-of-contents each occupy one filename before printed page 1).
   Every category's own fy2025_source_quote below cites the exact printed
   page it was read from, and every headline figure quoted below was
   independently re-confirmed by re-reading the corresponding page image
   during this build (not carried over from an unverified prior note).
   Report cover page states "All statistics in this report are for AHFC
   Fiscal Year 2025 unless otherwise noted."
2. AHFC's own FY2025 audited financial statements (used ONLY for
   fund-type classification and fiscal-year-period confirmation, see
   below): FY2025/txt/AK_AHFC_FY2025_ACFR.txt. Confirmed to be AHFC's own
   report, not a substitute/mismatched document (unlike PA's PHFA case) --
   its own title block reads "ALASKA HOUSING FINANCE CORPORATION, A
   Component Unit of the State of Alaska ... Basic Financial Statements
   and Independent Auditor's Report ... June 30, 2025", and the
   Independent Auditor's Report (line 62) is addressed to "Alaska Housing
   Finance Corporation" itself, not a statewide/Commonwealth report that
   merely mentions AHFC as a component unit.
3. "2025 LIHTC Reservation List - Alaska" (scratchpad/ahfc/lihtc2025.pdf,
   2 pages, 5 projects) -- checked only to confirm RAW_PROJECTS should stay
   empty (see above), not used for any category-level figure.

Fiscal-year period: confirmed, not merely assumed by convention
------------------------------------------------------------------------
The task briefing asked this to be verified against AHFC's own ACFR rather
than assumed from the "public HFAs typically run July-June" convention.
FY2025/txt/AK_AHFC_FY2025_ACFR.txt directly states the reporting period in
unambiguous terms: the Statement of Revenues, Expenses and Changes in Net
Position is captioned "FOR THE TWELVE MONTHS ENDED JUNE 30, 2025" (line
681), and the MD&A repeatedly describes "the fiscal year ended June 30,
2025" (e.g. lines 208, 279-282, 300-301) in comparison to "fiscal year
2024". A twelve-month period ending June 30, 2025 is, arithmetically,
July 1, 2024 - June 30, 2025 -- so AHFC's FY2025 = July 1, 2024 through
June 30, 2025 is confirmed directly from AHFC's own audited financial
statements, not inferred purely from the general public-HFA convention
(which happens to agree).

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
AHFC's own MD&A states plainly: "The Corporation is a component unit of
the State and is discretely presented in the State's financial
statements. It conducts business-type activities and follows enterprise
fund accounting rules" (.txt line 202-203) -- i.e., like MA/FL/PHFA, AHFC
has NO governmental funds of its own; every dollar it reports, including
its housing-grant programs, sits inside its own single enterprise-fund
basis of accounting. The MD&A's "Major Funds" section (.txt lines 233-253)
names AHFC's own internal major funds:
  - "The Mortgage and Bond Funds include resources to assist in financing
    loan programs ... This fund includes the Corporation's Home Mortgage
    Revenue Bonds, General Mortgage Revenue Bonds II, Collateralized Bonds
    (Veterans Mortgage Program), Governmental Purpose Bonds, and State
    Capital Project Bonds II indentures." (line 244-247) -- AHFC's own
    mortgage-purchase business, matching the Mortgage Operations category
    below. Confidence: high (near-verbatim functional match).
  - "The Grant Programs Fund includes resources provided to other agencies
    and individuals to develop and improve affordable housing units for
    lower income families and to assist in improving the energy efficiency
    of Alaskan homes, as well as tenant-based rental assistance programs
    for families in the private market that are administered by the
    Corporation under contract with ... HUD. These programs include the
    Energy Programs, the Section 8 Voucher Programs, and Other Grants."
    (line 239-243) -- covers the Housing Choice Voucher subprogram (Section
    8 Voucher Programs), the Weatherization category (Energy Programs), and
    the Supplemental Housing Development Grant category (Other Grants).
    Confidence: high (near-verbatim functional + program-name match).
  - "Other Funds and Programs include AHFC-owned housing for low-income
    families managed under contract with HUD as well as other programs
    that are not specifically grants or bond funds, such as the Low Rent
    Program..." (line 248-250) -- covers AHFC's own owned-and-operated
    public housing units. Confidence: high.
This is an important contrast with several other states' build scripts
(e.g. PA's PHARE/LIHTC, IL's LIHTC/IAHTC): those programs are classified
"off_balance_sheet" specifically because they NEVER appear anywhere in the
issuing HFA's own audited financial statements (the HFA merely
administers a pass-through of someone else's money). AHFC's Grant Programs
Fund is the opposite case -- it is one of AHFC's own four named major
funds, and Note 20, "HOUSING GRANTS AND SUBSIDIES EXPENSES" (.txt lines
1700-1760), shows the underlying grant payments (including line items
literally named "Energy Efficient Weatherization $2,265[K]" and
"Supplemental Housing Grant $4,362[K]" among ~40 named programs totaling
$127,681K) booked as an audited expense line inside AHFC's own Statement
of Revenues, Expenses and Changes in Net Position. So every subprogram
below is classified "proprietary", not "off_balance_sheet" -- the money
sits inside AHFC's own enterprise-fund financial statements, just
organized under a different one of AHFC's four internal major funds than
the Mortgage and Bond Funds.

Note 20 vs. the Annual Report's own weatherization/SHDG figures
------------------------------------------------------------------------
Note 20's "Energy Efficient Weatherization" grant-expense line is $2,265K
and its "Supplemental Housing Grant" line is $4,362K -- both close to, but
not identical to, the Annual Report's own headline figures used below
($3,772,828 weatherization allocated; $4,000,000 SHDG grant funding). The
two AHFC publications do not fully reconcile (most likely a difference in
scope/timing -- Note 20 reports grants actually PAID during FY2025 on a
cash/disbursement basis, while the Annual Report's figures read as
"allocated"/"grant funding" amounts, which need not match paid-out
amounts in the same twelve months). This mirrors MA's own build script,
which flags an unreconciled press-release-vs-filing gap rather than
silently picking one number: this script uses the Annual Report's own
p.27/p.28 headline figures (the source this build's category KPIs are
drawn from) and flags the Note 20 gap here rather than hiding it.

Category-level sourcing (all read directly off the cited Annual Report
page image, not carried over from any earlier unverified note)
------------------------------------------------------------------------
- Mortgage Operations (p.15, "Mortgage Operations" KPI page): "1,703
  Residential loans purchased" / "$648,329,443 Value of residential loans
  purchased" is this category's FY2025 flow headline. The same page also
  shows portfolio-STOCK figures as of FY25 end (15,670 residential loans /
  $3,876,582,729; 7,963 first-time-homebuyer loans = 50.82% of the
  portfolio) and a separate renovation-loan flow (37 loans /
  $11,715,297) -- all quoted in this category's fy2025_source_quote for
  context, but none of them is additive with the 1,703/$648,329,443 flow
  headline (the portfolio figures are a STOCK as of 6/30/2025, not
  FY2025-only activity; renovation loans are a distinct loan product on
  the same page, not a subset of the 1,703 residential purchases) so none
  of them is modeled as a second subprogram that would need to sum to the
  headline -- doing so would misrepresent a stock as a flow or double-count
  a separate loan product, both of which this project's methodology
  prohibits.
- Public Housing / Rental Assistance (p.21, "Rental Assistance" KPI
  block): "1,607 Statewide rental units owned by AHFC" and "4,707 Private
  rental units assisted through vouchers" are two disjoint populations
  (AHFC-owned units vs. privately-owned units where a tenant's rent is
  voucher-subsidized) reported on the same source page as of FY2025, so
  additive=True (their sum, 6,314, is the category headline). The same
  page also reports "447 Units for Sponsor Based Rental Assistance" and
  "12,000 Average number of individuals housed each night in all
  programs" -- both noted in the source quote for context but not modeled
  as their own subprogram (447 is not clearly disjoint from the 4,707
  voucher figure -- AHFC's own p.11 "Statewide Housing Development"
  narrative describes Sponsor-Based Rental Assistance as itself a form of
  voucher support attached to specific ACAH developments -- so adding it
  as a third additive subprogram risks double-counting some of the 4,707;
  no dollar figure is disclosed for either subprogram on this page, so
  fy2025_amount is None for both).
- Weatherization (p.27, "Weatherization" KPI block): "$3,772,828 Allocated
  for Weatherization (federal & state funds)" / "234 Homes improved
  through AHFC Weatherization funds" -- both figures read directly off the
  page image, exact match.
- Supplemental Housing Development Grant (p.28, "Supplemental Housing
  Development Grant" KPI block): "10 Regional Housing Authorities received
  funding" / "$4,000,000 Grant funding" / "78 New units" / "120
  Rehabilitated units" -- all four figures read directly off the page
  image. additive=True (78 + 120 = 198 = category headline); the "10
  Regional Housing Authorities" figure is noted in the source quote for
  context but is a count of grantee organizations, not a housing-unit
  count, so it is not itself modeled as a subprogram.

fy2026
------------------------------------------------------------------------
The 2025 Annual Report is a backward-looking annual report with no
forward-looking/projected FY2026 program-activity section anywhere in it
(the only FY2026-dated item found anywhere in the report is ACAH's
Blueberry Terrace property "coming soon" in 2026 -- a single project's
expected completion date, not an aggregate program-wide FY2026 projection
comparable to any of this script's own categories). Every fy2026 field
below is therefore {value: None, amount: None, closed: False,
note_key: "akFy26NotePending"}.
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "ak_program_activity.json"

SOURCE_URL = "https://www.ahfc.us/about-us/reports/2025-annual-report"
SOURCE_FILE = (
    "2025 Annual Report -- \"People Building Communities: Investing in "
    "Alaska\" (Issuu flip-book, no downloadable PDF; "
    "https://issuu.com/geretactical/docs/2025-ahfc-annual-report; pages "
    "captured individually from Issuu's page-image CDN) + "
    "FY2025/txt/AK_AHFC_FY2025_ACFR.txt (fund-type cross-check)"
)
RETRIEVED = "2026-08-14"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "akFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data. KPI layer only -- see module docstring for why
# RAW_PROJECTS is empty.
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "mortgage_operations",
        "unit_type": "households",
        "fy2025_actual": 1703,
        "fy2025_source_quote": (
            "\"Mortgage Operations\" KPI page (2025 Annual Report, p.15): "
            "\"1,703 Residential loans purchased\" / \"$648,329,443 Value of "
            "residential loans purchased.\" The same page separately shows "
            "AHFC's FY25-end portfolio STOCK (not this year's flow): "
            "\"15,670 Residential loans in AHFC's portfolio at the end of "
            "FY25\" / \"$3,876,582,729 Value of total residential loans\", "
            "and \"7,963 Total number of first-time homebuyer loans in "
            "AHFC's portfolio at the end of FY25\" (\"50.82% Percentage of "
            "AHFC's portfolio comprised of first-time homebuyer loans\"), "
            "plus a distinct FY2025 renovation-loan flow: \"37 Renovation "
            "loans purchased\" / \"$11,715,297 Value of renovation loans "
            "purchased.\" None of the portfolio-stock or renovation-loan "
            "figures is added into this category's own 1,703/$648,329,443 "
            "flow headline -- the portfolio figures are a snapshot as of "
            "6/30/2025, not FY2025-only activity, and renovation loans are "
            "a separate loan product on the same page, not a subset of the "
            "1,703 residential purchases."
        ),
        "fy2025_amounts": [
            {"label_key": "ak_amt_residential_loans_purchased", "amount": 648329443},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "residential_loans_purchased", "fy2025_units": 1703, "fy2025_amount": 648329443,
             "color_group": "bond",
             # AHFC's own MD&A "Major Funds" section: "The Mortgage and Bond
             # Funds include resources to assist in financing loan
             # programs ... Home Mortgage Revenue Bonds, General Mortgage
             # Revenue Bonds II, Collateralized Bonds (Veterans Mortgage
             # Program), Governmental Purpose Bonds, and State Capital
             # Project Bonds II indentures" (.txt line 244-247) -- AHFC's
             # own business-type mortgage-purchase business.
             "fund_type": "proprietary",
             "fund_name": "Mortgage and Bond Funds (business-type/enterprise fund activities)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "public_housing_rental_assistance",
        "unit_type": "units",
        "fy2025_actual": 6314,
        "fy2025_source_quote": (
            "\"Rental Assistance\" KPI block (2025 Annual Report, p.21): "
            "\"1,607 Statewide rental units owned by AHFC\" and \"4,707 "
            "Private rental units assisted through vouchers.\" The same "
            "block also reports \"447 Units for Sponsor Based Rental "
            "Assistance\" and \"12,000 Average number of individuals housed "
            "each night in all programs\" -- both noted here for context "
            "but not modeled as their own subprogram: p.11's own "
            "\"Statewide Housing Development\" narrative describes "
            "Sponsor-Based Rental Assistance as itself a form of voucher "
            "support tied to specific ACAH developments (e.g. \"Every unit "
            "is supported by public housing's Sponsor-Based Rental "
            "Assistance\" for The Meadows and Borealis Park), so it is not "
            "clearly disjoint from the 4,707 voucher figure and adding it "
            "as a third additive subprogram risks double-counting; no "
            "individuals-housed dollar/unit breakdown is disclosed either. "
            "No dollar figure is disclosed for either of the two "
            "subprograms modeled below."
        ),
        "fy2025_amounts": [],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "ahfc_owned_units", "fy2025_units": 1607, "fy2025_amount": None,
             "color_group": "capital",
             # AHFC's own MD&A "Major Funds" section: "Other Funds and
             # Programs include AHFC-owned housing for low-income families
             # managed under contract with HUD as well as other programs
             # that are not specifically grants or bond funds, such as the
             # Low Rent Program..." (.txt line 248-250).
             "fund_type": "proprietary",
             "fund_name": "Other Funds and Programs (Low Rent Program / AHFC-owned housing)",
             "fy2026": _FY26_PENDING},
            {"key": "voucher_assisted_units", "fy2025_units": 4707, "fy2025_amount": None,
             "color_group": "trust",
             # AHFC's own MD&A "Major Funds" section: "The Grant Programs
             # Fund includes resources ... tenant-based rental assistance
             # programs for families in the private market that are
             # administered by the Corporation under contract with ...
             # HUD. These programs include the Energy Programs, the
             # Section 8 Voucher Programs, and Other Grants" (.txt line
             # 239-243); Note 20's own grant-expense schedule separately
             # lists "Housing Choice Vouchers $37,265[K]" as a booked
             # AHFC expense (.txt line 1722).
             "fund_type": "proprietary",
             "fund_name": "Grant Programs Fund (Section 8 Voucher Programs)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "weatherization",
        "unit_type": "units",
        "fy2025_actual": 234,
        "fy2025_source_quote": (
            "\"Weatherization\" KPI block (2025 Annual Report, p.27): "
            "\"$3,772,828 Allocated for Weatherization (federal & state "
            "funds)\" / \"234 Homes improved through AHFC Weatherization "
            "funds.\" AHFC's own FY2025 ACFR Note 20 (\"Housing Grants and "
            "Subsidies Expenses\", .txt line 1716) separately lists "
            "\"Energy Efficient Weatherization $2,265[thousand]\" as a "
            "booked FY2025 grant-expense line -- a different figure from "
            "this page's $3,772,828 (likely a paid-during-the-year-vs."
            "-allocated-for-the-year scope difference between AHFC's two "
            "publications, not explained by either document); this script "
            "uses the Annual Report's own $3,772,828/234 headline figures "
            "(the source this category's KPI is drawn from) and flags the "
            "Note 20 gap here rather than silently picking one number."
        ),
        "fy2025_amounts": [
            {"label_key": "ak_amt_weatherization", "amount": 3772828},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "weatherization_homes", "fy2025_units": 234, "fy2025_amount": 3772828,
             "color_group": "capital",
             # AHFC's own MD&A "Major Funds" section names "the Energy
             # Programs" as one of the three named programs inside the
             # Grant Programs Fund (.txt line 239-243).
             "fund_type": "proprietary",
             "fund_name": "Grant Programs Fund (Energy Programs)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "supplemental_housing_grant",
        "unit_type": "units",
        "fy2025_actual": 198,
        "fy2025_source_quote": (
            "\"Supplemental Housing Development Grant\" KPI block (2025 "
            "Annual Report, p.28): \"10 Regional Housing Authorities "
            "received funding\" / \"$4,000,000 Grant funding\" / \"78 New "
            "units\" / \"120 Rehabilitated units.\" The \"10 Regional "
            "Housing Authorities\" figure counts grantee organizations, not "
            "housing units, so it is noted here for context but not "
            "modeled as a subprogram. AHFC's own FY2025 ACFR Note 20 "
            "separately lists \"Supplemental Housing Grant $4,362"
            "[thousand]\" as a booked FY2025 grant-expense line (.txt line "
            "1745) -- close to, but not identical to, this page's "
            "$4,000,000 grant-funding figure (likely the same "
            "paid-vs.-allocated scope gap noted for Weatherization above); "
            "this script uses the Annual Report's own $4,000,000/78/120 "
            "headline figures and flags the Note 20 gap here rather than "
            "silently picking one number."
        ),
        "fy2025_amounts": [
            {"label_key": "ak_amt_shdg", "amount": 4000000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "shdg_new_units", "fy2025_units": 78, "fy2025_amount": None,
             "color_group": "capital",
             # Same Grant Programs Fund "Other Grants" program as the
             # rehabilitated-units subprogram below -- AHFC's Note 20 books
             # the whole "Supplemental Housing Grant" line as one program
             # (.txt line 1745), with no new-vs-rehab dollar split
             # disclosed anywhere, so fy2025_amount is None for both
             # halves and the category's own $4,000,000 total is shown
             # only at the category level (fy2025_amounts above).
             "fund_type": "proprietary",
             "fund_name": "Grant Programs Fund (Other Grants -- Supplemental Housing Grant)",
             "fy2026": _FY26_PENDING},
            {"key": "shdg_rehab_units", "fy2025_units": 120, "fy2025_amount": None,
             "color_group": "trust",
             "fund_type": "proprietary",
             "fund_name": "Grant Programs Fund (Other Grants -- Supplemental Housing Grant)",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# No usable project-level list -- see module docstring ("KPI-only pilot"
# section) for the two sources checked and ruled out (2025 LIHTC
# Reservation List, ACAH property list). This is the allowed, honest
# outcome (not a placeholder for missing work): the frontend renders the
# bubble map with 0 markers when this is empty.
RAW_PROJECTS = []


def verify_category_consistency():
    """Sanity gate: each additive category's subprograms must sum exactly
    to that category's own fy2025_actual headline, and (when a category
    declares a single fy2025_amounts total) the subprograms' own amounts
    must sum to it too, wherever an amount is disclosed for every
    subprogram."""
    errors = []
    for cat in CATEGORIES:
        subs = cat["subprograms"]
        units_sum = sum(sp["fy2025_units"] for sp in subs)
        if units_sum != cat["fy2025_actual"]:
            errors.append(
                f"{cat['key']}: subprogram units sum {units_sum} != "
                f"category fy2025_actual {cat['fy2025_actual']}"
            )
        amounts = [sp["fy2025_amount"] for sp in subs]
        if all(a is not None for a in amounts):
            amt_sum = sum(amounts)
            cat_amt = cat["fy2025_amounts"][0]["amount"] if cat["fy2025_amounts"] else None
            if cat_amt is not None and amt_sum != cat_amt:
                errors.append(
                    f"{cat['key']}: subprogram amount sum {amt_sum} != "
                    f"category fy2025_amounts[0].amount {cat_amt}"
                )
    if RAW_PROJECTS:
        errors.append(
            "RAW_PROJECTS is expected to be empty for AK -- see module "
            "docstring; if project-level data has since become available "
            "with street-level precision and a clean FY2025 boundary, "
            "update the docstring before populating this list."
        )
    if errors:
        raise SystemExit("Category consistency mismatch(es):\n" + "\n".join(errors))
    print(
        "Category headline vs. subprogram consistency verified for all four "
        "categories (mortgage_operations: 1,703 households / $648,329,443; "
        "public_housing_rental_assistance: 6,314 units [1,607 + 4,707]; "
        "weatherization: 234 units / $3,772,828; "
        "supplemental_housing_grant: 198 units [78 + 120] / $4,000,000); "
        "RAW_PROJECTS confirmed empty as expected."
    )


def main():
    verify_category_consistency()
    payload = {
        "AK": {
            "hfa_name": "Alaska Housing Finance Corporation",
            "hfa_abbr": "AHFC",
            "fiscal_year": "FY2025",
            "source_title": "AHFC 2025 Annual Report -- \"People Building Communities: Investing in Alaska\"",
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
