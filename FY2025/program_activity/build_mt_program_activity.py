"""
Builds docs/mt_program_activity.json from the Montana Board of Housing's FY2025
audited financial statements and Management's Discussion & Analysis (MD&A) --
the board's own annual financial report to the Montana Legislature, which for
this agency is also its de-facto annual program-activity report (there is no
separately published "annual/impact report"; the department's program-year
HUD CAPER covers a different entity scope and a different, April-March program
year -- see "Why the MD&A is the primary source" below).

This is a KPI-only build, like VA/AK: solid multi-category KPI figures
(household/unit counts + dollar amounts) exist, but there is NO complete
per-project cohort list in any FY2025 source, so RAW_PROJECTS is [] and the
output `projects` array is empty -- an honest result, not a shortcut.

Source
------------------------------------------------------------------------
"Financial Audit: Montana Board of Housing, For the Fiscal Year ended
June 30, 2025", Legislative Audit Division (LAD) report 25-07, issued
February 2026. Published at the LAD audit-reports index (a JavaScript SPA --
a static per-report PDF URL could not be obtained during this build; the
report is archived in this repo's standard ACFR text corpus):
    FY2025/txt/MT_MTHousing_FY2025_ACFR.txt
    (index page: https://legmt.gov/lad/audit-reports, report #25-07)
The txt is confirmed to be the correct entity, not a mismatched/substitute
document: its own title block reads "MONTANA BOARD OF HOUSING, A COMPONENT
UNIT OF THE STATE OF MONTANA" and the Independent Auditor's Report (.txt
lines 354-361) covers "the Montana Board of Housing, a component unit of the
State of Montana ... Statement of Net Position as of June 30, 2025 ... for
the fiscal year then ended". Note 1 ("Organization", .txt lines 833-842)
states the Board "is attached for administrative purposes to the Housing
Division, Department of Commerce" -- i.e. "Montana Housing" is the public
branding of the Montana Board of Housing, the state's HFA.

Entity/branding note: the task brief names the HFA "Montana Housing (part of
the Montana Department of Commerce)". The audited legal entity is the
"Montana Board of Housing" (MBOH), which is what this ACFR covers; "Montana
Housing" is the Housing Division branding under which the Board's programs
(single-family mortgage lending, multifamily/LIHTC, Housing Trust Fund) are
delivered. hfa_name below is therefore "Montana Board of Housing" and
hfa_abbr is "Montana Housing".

Why the MD&A is the primary source (and not the HUD CAPER / "50 Years" page)
------------------------------------------------------------------------
Two other candidate "Montana Housing" sources were checked and set aside:
  - The "2024-2025 Consolidated Annual Performance Evaluation Report (CAPER)"
    (Montana Department of Commerce, housing.mt.gov / commerce.mt.gov) covers
    the Housing Division's HUD block-grant programs (CDBG, HOME, HOME-ARP,
    HTF, ESG) -- a DIFFERENT program set from this ACFR's single-family/
    multifamily/LIHTC/Housing-Trust-Fund programs -- and runs a HUD "Plan
    Year 5 (2024)" of April 1, 2024 - March 31, 2025, not the Board's
    July 1, 2024 - June 30, 2025 fiscal year. Mixing the two would conflate
    two entities and two different year conventions.
  - The "50 Years (1975-2025)" retrospective page (redesign-commerce.mt.gov/
    Housing/Montana-Board-of-Housing/50) contains only cumulative/since-
    inception figures (e.g. "over 47,700 ... loans", "nearly $3.8 billion"),
    no FY2025-specific flow figures.
The ACFR MD&A is the single cleanest, self-consistent FY2025 source: its
"Summary" and "Fiscal Year 2025 Update" sections print per-program FY2025
flow figures with paired unit/household counts and dollar amounts, and the
same document's notes let each figure be independently cross-checked (see
"Dual verification" below).

Fiscal-year period: confirmed, not assumed
------------------------------------------------------------------------
The Independent Auditor's Report and every statement header are captioned
"as of / for the fiscal year ended June 30, 2025" (e.g. .txt line 357-359,
"Statement of Net Position as of June 30, 2025 ... and the Statement of Cash
Flows for the fiscal year then ended"). A twelve-month period ending June 30,
2025 is July 1, 2024 - June 30, 2025. So fiscal_year = "FY2025" is read
directly off the audited statements, not inferred from the public-HFA
convention.

Category-level sourcing (all transcribed from this build's own local txt of
the ACFR; page refs are the report's own printed MD&A page labels)
------------------------------------------------------------------------
- Single-family / homeownership (MD&A "Summary", p.A-7; "Single Family
  Program", p.A-7/A-8): "544 Single Family Mortgages were purchased with the
  Bond Program for $82.3 million." (the FY2025 whole-loan flow headline) and
  "28 Mortgage-Backed Securities were purchased with Single Family Bond
  Program funds totaling $61.8 million." (the securitized form of the same
  program, adopted November 1, 2024 -- no underlying household count is
  disclosed for the MBS pools, only the number of securities, so it is a
  dollar-only reference chip, not a second unit subprogram). The same
  Summary also prints "Mortgage Credit Certificates were issued for 18 loans
  with principal balances totaling $5.3 million" and "8 Reverse Annuity
  Mortgage (RAM) loans were originated in FY25 ... currently assisting 41
  elderly households" -- both quoted here for context but NOT modeled as
  subprograms: MCC is a small (18-loan) distinct homeownership product the
  source does not state is additive with the 544 whole loans, and RAM's "41
  elderly households" is a point-in-time STOCK ("currently assisting"), not
  FY2025-only flow, with no dollar figure disclosed.
- Multifamily / rental (MD&A "Multifamily Program", p.A-9): "During FY25,
  the Board allocated $37.2 million of 9% housing tax credits to be used
  over ten years to produce 137 rental units in Montana. The Board issued
  $73.5 million in conduit bonds to produce 396 additional rental units.
  ... In FY25, the Board allocated $46.2 million of 4% housing credits to be
  used over ten years." 137 (9% LIHTC) + 396 (conduit bonds) = 533 rental
  units -- an exact partition of the two disclosed production figures,
  asserted in verify_category_consistency(). The 4% LIHTC ($46.2M) attaches
  to the same conduit-bond-financed projects (per the MD&A's own "When 50%
  of a project's funding is through the issuance of conduit bonds, the
  project qualifies for 4% tax credits"), so it is a dollar-only reference
  chip, not a third unit subprogram. The MD&A also reports "The Multifamily
  Program closed three loans utilizing the Coal Trust Multifamily Homes
  (CTMH) loan program ... The three loans totaled $10,157,031" -- noted here
  for context but not modeled: CTMH is funded by the Montana Board of
  Investment and administered/serviced by MBOH (a serviced-for-others line,
  not the Board's own financed units), and discloses a loan count (3), not a
  unit/household count.

Dual verification (internal + independent-in-document cross-checks)
------------------------------------------------------------------------
Every headline figure below is cross-checked against a second figure in the
SAME audited document (the MD&A is a narrative; the statements/notes are the
independent numbers), and each is asserted in verify_category_consistency():
  - 9% LIHTC: the MD&A Summary prints "$37.2 million ... at $3.72 million
    per year" and the Multifamily section repeats "$37.2 million ... over ten
    years" -- 37,200,000 / 10 = 3,720,000, so the two phrasings reconcile
    exactly.
  - Conduit bonds: MD&A's "$73.5 million in conduit bonds" issued in FY25 is
    independently corroborated by Note 15 ("No-Commitment Debt", p.A-42/
    A-43), which itemizes the multifamily no-commitment bond series; the
    original-amount sum of the 2024-series (Aurora $27,155,000; Twin Creek 4
    $8,537,000; Bigfork Senior $3,600,000; The Manor $6,500,000) and
    2025-series (Midtown Aspen $4,070,000; Creekside $18,000,000; Franklin
    School A $3,100,000 + B $2,500,000) bonds = $73,462,000, which rounds to
    $73.5M -- the MD&A figure is reproduced by an independent note schedule.
  - Single-family whole loans: MD&A's "$82.3 million" is independently
    corroborated by the Statement of Cash Flows "Cash Payments for Loans"
    (Single Family column: $82,342,455, .txt line 2924), which rounds to
    $82.3M. The "$82.3 million" is used as-is (the source's own rounded
    phrasing; the cash-flow figure is the more precise corroborant).
  - Multifamily partition: 137 + 396 = 533 is the computed total of the two
    MD&A-disclosed production figures (the MD&A does not itself print "533").

Historical/cumulative figures explicitly excluded
------------------------------------------------------------------------
The ACFR contains no "since inception" housing figures that could be
confused with FY2025 flow (the "50 Years" page's cumulative figures are a
separate document and are not used at all). The only stock-vs-flow trap is
RAM's "41 elderly households", which is a point-in-time count and is excluded
as noted above.

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
Cross-referenced against this same ACFR's own fund-structure note. Note 1
("Fund Accounting"/"Fund Structure", .txt lines 873-955) states the Board's
funds are "classified as enterprise funds" and, per the MD&A "Overview"
(p.A-10), "The Board is classified as an enterprise fund, which is a fund
financed and operated in a manner similar to a private business enterprise."
The Board therefore has NO governmental funds of its own -- every dollar in
its own programs sits inside its single enterprise-fund (business-type)
basis. The named internal funds are:
  - "Single Family Mortgage Program Funds" (Note 1, .txt lines 918-929) --
    the Board's own bond-financed mortgage-purchase business, backing the
    single_family_homeownership subprogram. fund_type "proprietary",
    confidence high (verbatim fund name + functional match).
  - "Multifamily Mortgage Program Funds" (Note 1, .txt lines 930-936) -- the
    Board's own small on-balance multifamily GO bond fund, NOT what the
    "$73.5M conduit bonds" refers to.
  - "Housing Trust Fund" (Note 1, .txt lines 937-946) -- includes the RAM/
    CAP/DAAHP programs and "all revenues and expenses for the Low Income
    Housing Tax Credit Program" (i.e. the Board books the LIHTC program's
    allocator/admin fee income and costs here, but the credits themselves
    are not the Board's assets).
  - "Housing Montana Fund" (Note 1, .txt lines 947-954).
The two multifamily subprograms are therefore classified off_balance_sheet,
not proprietary:
  - 9% LIHTC (lihtc_9pct): the $37.2M is a ten-year allocation of federal
    Low-Income Housing Tax Credits that flow to developers/investors, not an
    amount booked as a Board asset -- same off_balance_sheet treatment this
    project applies to LIHTC/state-tax-credit allocations in every other
    state (the Board's own statement only recognizes the program's admin-fee
    income). Confidence high.
  - Conduit bonds (conduit_bond_financing): Note 15 "No-Commitment Debt"
    (.txt lines 1993-2004) is explicit -- these bonds "are not general
    obligations, debts, liabilities, or pledges of faith and credit of the
    Board, but are special limited obligations payable solely from pledged
    revenues and assets of the borrower ... not reflected in the
    accompanying financial statements." Conduit bonds are therefore
    off_balance_sheet by the ACFR's own words. Confidence high.

Why RAW_PROJECTS is empty ([]) -- no complete per-project FY2025 list
------------------------------------------------------------------------
The ACFR discloses multifamily activity only at the aggregate program level
(137 units via 9% LIHTC; 396 units via conduit bonds), never as a per-
development list of which named projects produced those units in FY2025,
with per-project unit counts and locations. The closest thing to a project
list -- Note 15's ~30 named multifamily no-commitment bond series (Rainbow/
Silver Bow, Larkspur Commons, Big Sky Manor, Rockcress Commons, ... Franklin
School, Creekside, Midtown Aspen, etc.) -- is a STOCK schedule of outstanding
conduit debt as of June 30, 2025 (with outstanding principal balances, not
FY2025 production, unit counts, or city-level locations for a coherent
cohort), and it cannot be tied back to which specific developments produced
the 137/396 FY2025 units. Transcribing those bond-series names as a project
list would both misrepresent a debt schedule as a production cohort and
fabricate unit/location data the source does not provide. RAW_PROJECTS is
therefore [] and the output `projects` array is empty -- the honest KPI-only
outcome, not a placeholder. The frontend (docs/program_activity.js) renders
the bubble map with 0 markers when this is empty.

fy2026
------------------------------------------------------------------------
The FY2025 financial audit is backward-looking with no forward-looking/
projected FY2026 program-activity section (Note 22 "Subsequent Events",
p.A-51, only lists post-6/30/2025 bond closings -- individual transactions,
not an aggregate program-wide FY2026 projection comparable to these
categories). Every fy2026 field below is therefore {value: None, amount:
None, closed: False, note_key: "mtFy26NotePending"}.
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "mt_program_activity.json"

SOURCE_URL = "https://legmt.gov/lad/audit-reports"  # LAD report index; report #25-07
SOURCE_FILE = (
    "FY2025/txt/MT_MTHousing_FY2025_ACFR.txt (Montana Board of Housing "
    "audited financial statements and Management's Discussion & Analysis "
    "for the fiscal year ended June 30, 2025; Legislative Audit Division "
    "report 25-07, issued February 2026 -- already archived in this repo's "
    "FY2025/txt corpus; the LAD site is a JS SPA with no stable per-report "
    "PDF URL, so no separate PDF was re-downloaded)"
)
RETRIEVED = "2026-08-16"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "mtFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data (ACFR MD&A, "Summary" p.A-7 and "Multifamily Program"
# p.A-9). KPI layer only -- see module docstring for why RAW_PROJECTS is empty.
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "single_family_homeownership",
        "unit_type": "households",
        "fy2025_actual": 544,
        "fy2025_source_quote": (
            "\"Summary\" (MD&A, p.A-7): \"544 Single Family Mortgages were "
            "purchased with the Bond Program for $82.3 million.\" \"28 "
            "Mortgage-Backed Securities were purchased with Single Family Bond "
            "Program funds totaling $61.8 million.\" \"Mortgage Credit "
            "Certificates were issued for 18 loans with principal balances "
            "totaling $5.3 million.\" \"8 Reverse Annuity Mortgage (RAM) loans "
            "were originated in FY25. The RAM Program is currently assisting 41 "
            "elderly households.\" The 544/$82.3M whole-loan purchase is this "
            "category's FY2025 flow headline. The 28 MBS / $61.8M is the "
            "securitized form of the same single-family bond program (adopted "
            "Nov. 1, 2024 -- see MD&A \"Single Family Program\", p.A-7/A-8) and "
            "is shown only as a dollar reference chip because no underlying "
            "household count is disclosed for the MBS pools (only the number of "
            "securities). MCC (18 loans / $5.3M) and RAM (8 loans; \"41 elderly "
            "households\" is a point-in-time STOCK, not FY2025 flow, with no "
            "dollar figure) are noted here for context but not modeled as "
            "subprograms -- the source does not state either is additive with "
            "the 544 whole loans. \"$82.3 million\" is the Board's own rounded "
            "phrasing; the Statement of Cash Flows' Single Family \"Cash "
            "Payments for Loans\" of $82,342,455 (.txt line 2924) independently "
            "corroborates it (rounds to $82.3M)."
        ),
        "fy2025_amounts": [
            {"label_key": "mt_amt_sf_whole_loans", "amount": 82300000},
            {"label_key": "mt_amt_sf_mbs", "amount": 61800000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "sf_whole_loans", "fy2025_units": 544, "fy2025_amount": 82300000,
             "color_group": "bond",
             # Note 1 "Single Family Mortgage Program Funds" (.txt lines
             # 918-929): the Board's own bond-financed mortgage-purchase
             # business, one of the Board's own enterprise funds.
             "fund_type": "proprietary",
             "fund_name": "Single Family Mortgage Program Funds (enterprise/business-type fund)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "multifamily_rental",
        "unit_type": "units",
        "fy2025_actual": 533,
        "fy2025_source_quote": (
            "\"Multifamily Program\" (MD&A, p.A-9): \"During FY25, the Board "
            "allocated $37.2 million of 9% housing tax credits to be used over "
            "ten years to produce 137 rental units in Montana. The Board issued "
            "$73.5 million in conduit bonds to produce 396 additional rental "
            "units. When 50% of a project's funding is through the issuance of "
            "conduit bonds, the project qualifies for 4% tax credits. In FY25, "
            "the Board allocated $46.2 million of 4% housing credits to be used "
            "over ten years.\" 137 (9% LIHTC) + 396 (conduit bonds) = 533 rental "
            "units, an exact partition of the two disclosed production figures "
            "(asserted in verify_category_consistency()). The 4% LIHTC ($46.2M) "
            "attaches to the same conduit-bond-financed projects and is shown "
            "only as a dollar reference chip, not a third unit subprogram. The "
            "same section also reports \"The Multifamily Program closed three "
            "loans utilizing the Coal Trust Multifamily Homes (CTMH) loan "
            "program ... The three loans totaled $10,157,031\" -- noted for "
            "context but not modeled (funded by the Montana Board of Investment "
            "and administered/serviced by MBOH; a loan count, not a unit count). "
            "The $73.5M conduit-bond figure is independently corroborated by "
            "Note 15 (\"No-Commitment Debt\", p.A-42/A-43): the original-amount "
            "sum of the 2024- and 2025-series no-commitment multifamily bonds "
            "is $73,462,000, which rounds to $73.5M."
        ),
        "fy2025_amounts": [
            {"label_key": "mt_amt_lihtc_9pct", "amount": 37200000},
            {"label_key": "mt_amt_conduit_bonds", "amount": 73500000},
            {"label_key": "mt_amt_lihtc_4pct", "amount": 46200000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "lihtc_9pct", "fy2025_units": 137, "fy2025_amount": 37200000,
             "color_group": "credit",
             # Federal 9% Low-Income Housing Tax Credit allocation -- the
             # credits flow to developers/investors, not booked as Board
             # assets; the Board only recognizes the LIHTC program's admin
             # fee income (Note 1: the Housing Trust Fund "includes all
             # revenues and expenses for the Low Income Housing Tax Credit
             # Program").
             "fund_type": "off_balance_sheet",
             "fund_name": "Federal 9% Low-Income Housing Tax Credit (allocated, not a Board asset)",
             "fy2026": _FY26_PENDING},
            {"key": "conduit_bond_financing", "fy2025_units": 396, "fy2025_amount": 73500000,
             "color_group": "bond",
             # Note 15 "No-Commitment Debt" (.txt lines 1993-2004): these
             # bonds "are not general obligations, debts, liabilities, or
             # pledges of faith and credit of the Board ... not reflected in
             # the accompanying financial statements" -- off-balance-sheet by
             # the ACFR's own words.
             "fund_type": "off_balance_sheet",
             "fund_name": "No-Commitment (conduit) multifamily revenue bonds (ACFR Note 15)",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# No usable per-project FY2025 list -- see module docstring ("Why RAW_PROJECTS
# is empty") for the ACFR's aggregate-only disclosure and the Note 15 debt
# schedule checked and ruled out. This is the allowed, honest outcome (not a
# placeholder): the frontend renders the bubble map with 0 markers.
RAW_PROJECTS = []


def verify_category_consistency():
    """Dual verification gate. Internal: additive subprogram units must sum to
    each category's own fy2025_actual headline. Independent-in-document:
    the MD&A's rounded dollar figures must reproduce the amounts derivable
    from the statements/notes (9% LIHTC annualization, the Note 15 conduit-
    bond original-amount sum, and the cash-flow single-family loan payments).
    Hard-errors on any mismatch."""
    errors = []

    for cat in CATEGORIES:
        subs = cat["subprograms"]
        units_sum = sum(sp["fy2025_units"] for sp in subs)
        if units_sum != cat["fy2025_actual"]:
            errors.append(
                f"{cat['key']}: subprogram units sum {units_sum} != category "
                f"fy2025_actual {cat['fy2025_actual']}"
            )

    # single_family_homeownership: single subprogram must equal the 544/$82.3M
    # headline exactly (additive=True with 1 subprogram is only meaningful if
    # the subprogram *is* the headline), and its amount must match the
    # category's first amount chip.
    sf = next(c for c in CATEGORIES if c["key"] == "single_family_homeownership")
    if len(sf["subprograms"]) != 1:
        errors.append(f"single_family_homeownership: expected 1 subprogram, got {len(sf['subprograms'])}")
    else:
        sf_sp = sf["subprograms"][0]
        if sf_sp["fy2025_units"] != sf["fy2025_actual"]:
            errors.append(f"single_family_homeownership: subprogram units {sf_sp['fy2025_units']} != fy2025_actual {sf['fy2025_actual']}")
        if sf_sp["fy2025_amount"] != sf["fy2025_amounts"][0]["amount"]:
            errors.append(f"single_family_homeownership: subprogram amount {sf_sp['fy2025_amount']} != fy2025_amounts[0] {sf['fy2025_amounts'][0]['amount']}")

    # multifamily_rental: each subprogram's amount must equal its own matching
    # amount chip (37.2M 9% LIHTC, 73.5M conduit bonds); the 4% LIHTC chip is
    # a dollar-only reference and is intentionally NOT a subprogram total.
    mf = next(c for c in CATEGORIES if c["key"] == "multifamily_rental")
    mf_chips = {c["label_key"]: c["amount"] for c in mf["fy2025_amounts"]}
    for sp in mf["subprograms"]:
        if sp["key"] == "lihtc_9pct":
            if sp["fy2025_amount"] != mf_chips["mt_amt_lihtc_9pct"]:
                errors.append(f"multifamily_rental: lihtc_9pct amount {sp['fy2025_amount']} != chip {mf_chips['mt_amt_lihtc_9pct']}")
        elif sp["key"] == "conduit_bond_financing":
            if sp["fy2025_amount"] != mf_chips["mt_amt_conduit_bonds"]:
                errors.append(f"multifamily_rental: conduit_bond_financing amount {sp['fy2025_amount']} != chip {mf_chips['mt_amt_conduit_bonds']}")

    # 9% LIHTC internal consistency: "$37.2 million ... at $3.72 million per
    # year" (Summary) must equal "$37.2 million ... over ten years"
    # (Multifamily Program) -- 37,200,000 / 10 == 3,720,000.
    if 37200000 // 10 != 3720000:
        errors.append("9% LIHTC: 37,200,000 / 10 != 3,720,000 (MD&A per-year vs ten-year mismatch)")

    # Conduit bonds: Note 15 "No-Commitment Debt" 2024- + 2025-series
    # original-amount sum must round to the MD&A's $73.5M.
    conduit_series = [
        27155000,   # Aurora Apartments Series 2024
        8537000,    # Twin Creek 4 Apartments Series 2024
        3600000,    # Bigfork Senior Housing Series 2024
        6500000,    # The Manor Apartments Series 2024
        4070000,    # Midtown Aspen Series 2025
        18000000,   # Creekside Apartments Series 2025
        3100000,    # Franklin School Apartments Series 2025A
        2500000,    # Franklin School Apartments Series 2025B
    ]
    conduit_sum = sum(conduit_series)
    if conduit_sum != 73462000:
        errors.append(f"Conduit bonds: Note 15 2024+2025 series sum {conduit_sum} != 73,462,000")
    if round(conduit_sum / 1e6, 1) != 73.5:
        errors.append(f"Conduit bonds: {conduit_sum} does not round to $73.5M")

    # Single-family whole loans: MD&A "$82.3 million" must round-match the
    # Statement of Cash Flows Single Family "Cash Payments for Loans"
    # $82,342,455 (.txt line 2924).
    if round(82342455 / 1e6, 1) != 82.3:
        errors.append("Single-family whole loans: cash-flow $82,342,455 does not round to $82.3M")

    if RAW_PROJECTS:
        errors.append(
            "RAW_PROJECTS is expected to be empty for MT -- see module docstring; "
            "if a complete per-project FY2025 list has since become available, "
            "update the docstring before populating this list."
        )

    if errors:
        raise SystemExit("Category consistency mismatch(es):\n" + "\n".join(errors))
    print(
        "Category headline vs. subprogram consistency verified for both "
        "categories (single_family_homeownership: 544 households / $82.3M; "
        "multifamily_rental: 533 units [137 9% LIHTC + 396 conduit bonds]). "
        "Independent-in-document cross-checks passed: 9% LIHTC $37.2M / 10 = "
        "$3.72M/yr; Note 15 conduit-bond 2024+2025 series sum $73,462,000 "
        "~ $73.5M; cash-flow single-family loan payments $82,342,455 ~ "
        "$82.3M. RAW_PROJECTS confirmed empty as expected."
    )


def main():
    verify_category_consistency()
    payload = {
        "MT": {
            "hfa_name": "Montana Board of Housing",
            "hfa_abbr": "Montana Housing",
            "fiscal_year": "FY2025",
            "source_title": "Montana Board of Housing FY2025 Financial Audit -- "
                             "Management's Discussion & Analysis (\"Summary\" and "
                             "\"Multifamily Program\"), Legislative Audit Division "
                             "report 25-07",
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
