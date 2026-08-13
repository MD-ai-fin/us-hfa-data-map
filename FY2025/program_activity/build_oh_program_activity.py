"""
Builds docs/oh_program_activity.json from OHFA's FY2025 Annual Report (housing
production section, pages 18-19) plus its own Appendix C (per-development
initial funding reservations) and its separately-issued FY2025 audited
financial statements (for GASB fund-type classification).

Sources (OHFA's fiscal year = July 1, 2024 - June 30, 2025)
------------------------------------------------------------------------
1. "Ohio Housing Finance Agency Fiscal Year 2025 Annual Report"
     https://ohiohome.org/news/documents/annualreport_25.pdf
   Local copy: FY2025/program_activity/pdf/OH_OHFA_AnnualReport_FY2025.pdf
   - Category-level "Breakdown of Affordable Housing Units" / "Breakdown of
     Overall Funding" (pages 18-19).
   - Appendix A, "Homebuyer Program Lenders by Total Loan Volume, Fiscal Year
     2025" (pages 23-26) -- used only for its own printed Grand Total row
     (6,664 loans / $1,320,664,985); the per-lender rows are a different
     dimension (by lender, not by program) and are not transcribed.
   - Appendix C, "Multifamily Housing Developments Receiving Initial Funding
     Reservations, Fiscal Year 2025" (pages 32-35) -- the per-development
     detail behind this script's bubble map. Manually transcribed via a
     pdfplumber word-position pass (see "Transcription method" below), not
     by eye off the raw pdftotext dump, which garbles this table badly
     (multi-line cells with no ruled grid lines between rows).
   - Appendix D, "IRS Form 8609 Issuances, Fiscal Year 2025" (pages 36-37)
     was reviewed but NOT used for the bubble map -- see "Appendix C vs D"
     below.
2. OHFA's own separately-issued FY2025 audited financial statements (used
   ONLY for GASB fund-type classification):
     FY2025/txt/OH_OHFA_FY2025_ACFR.txt
   Confirmed to be the correct, OHFA-scoped document (unlike a prior PA
   build in this same pilot series, where the checked-in ACFR .txt turned
   out to be the wrong, state-wide report) -- this file's own title page
   reads "Ohio Housing Finance Agency ... Notes to the Financial
   Statements, June 30, 2025" and its auditor's opinion is scoped to
   exactly "the Single-Family Mortgage Revenue Program Fund, General Fund,
   and Federal Program Fund of the Ohio Housing Finance Agency" (p.4) --
   i.e. OHFA's complete basic financial statements, not a component-unit
   summary buried in a larger state report. No data-provenance problem
   here.

Category-level methodology
------------------------------------------------------------------------
Multifamily (fy2025_actual = 8,183 units): OHFA's own published aggregate
from the "Breakdown of Affordable Housing Units" box (p.18) -- used
verbatim, NOT derived by summing Appendix C, because Appendix C's own
funding-source columns overlap heavily (the same development routinely
draws 9% or 4% LIHTC *and* HDL *and* MF Bonds *and/or* HDAP simultaneously
-- OHFA's own narrative says so explicitly: "OHFA may provide a single
project funding from more than one program", p.19). Category subprograms
are therefore additive=False, matching IHDA's and PHFA's identical
treatment of their own overlapping multifamily categories.

Homebuyer Loans (fy2025_actual = 6,664 households): Appendix A's own
printed Grand Total row. The "Your Choice! Down Payment Assistance" count
(5,000, split 710 at 2.5% / 4,290 at 5%, p.9) is a SUBSET of the 6,664 (a
borrower either does or doesn't take DPA on top of their first mortgage),
not a partition of it, so additive=False here too. Grants for Grads (465)
and Ohio Heroes (1,300) are named discounted-rate products (p.8) that can
in principle stack with DPA and with each other (nothing in the report
states otherwise), so they are shown as informational reference chips only
-- no dollar figure is disclosed for any of DPA/Grants for Grads/Ohio
Heroes individually, so none is invented (fy2025_amount=None on all three).

Appendix C vs Appendix D
------------------------------------------------------------------------
Appendix C ("... Receiving Initial Funding Reservations") is used for the
bubble map, matching this pilot series' existing convention (IHDA's
closing-report exhibits, PHFA's LIHTC award list) of mapping the award/
reservation moment, not the later placed-in-service moment. Appendix D
("IRS Form 8609 Issuances") lists ~60 additional rows of buildings that
were formally placed in service and issued their federal 8609 tax-credit
certification during FY25 -- a mix of prior-year AND FY25 reservations
reaching completion, with materially incomplete Municipality/County/Units
fields in a large fraction of its own rows (see the raw table on pages
36-37: many rows have County but no Municipality, Units, or Credits
value at all). Adding Appendix D's projects to Appendix C's would NOT be
a clean union -- a development can appear in both (reservation in FY25,
then also placed in service in FY25) or in only one, and Appendix D gives
no funding-source breakdown (only a single "Credits" dollar column), so it
cannot be merged into Appendix C's richer per-source structure without
guessing at overlap. Appendix D is therefore left out of this build
entirely rather than risk double-counting or fabricating a merge; a future
pilot iteration could treat it as a separate, non-additive category if
useful.

Transcription method for Appendix C (pages 32-35)
------------------------------------------------------------------------
Appendix C's PDF table has no ruled grid lines between data rows (only
colored header cells), and its cells are printed as separate PDF text runs
whose vertical position does not reliably line up with the row's nominal
"anchor" line (a project's own County/Units/Month values sometimes sit 1-2
lines above or below that project's other cells, and a project with many
funding sources can have its last funding line sit closer, in raw y-
distance, to the *next* project's anchor row than to its own). Both the
raw pdftotext dump (FY2025/program_activity/pdf/appendix_c_d.txt) and a
naive "nearest anchor by y-distance" pdfplumber pass therefore silently
misattribute a handful of funding lines to the wrong neighboring project.
This script's transcription was produced by: (1) a pdfplumber
extract_words() pass with x-position column binning (Project
Name/Municipality/County/Units/Month/OHFA Funds Allocated/Rehab/Senior/
PSH/AAL/Syndicator, using each page's own header row's x0 as the column
boundaries) to recover per-project Units/County/Month/funding-line/flag
data page by page; (2) a full visual read of the rendered page images
(FY2025/program_activity/pdf/page_32.png .. page_35.png) to fix project
names/municipalities (the noisy field in the word-position pass, because
multi-line names interleave with neighboring rows) and to catch the
handful of funding-line misattributions the y-distance heuristic got
wrong (identified because they left one project's funding stack short a
line while a neighbor had an extra, out-of-place one): Foster Senior
Lofts' own $8m MF Bonds line and PC St. Clairsville Courtyard's own $210k
4% LIHTC line had both been pulled onto Olympia Building's row; At Main's
own $1.2m 4% LIHTC line had been pulled onto Asbury Apartments' row
(printing there as a spurious duplicate of Asbury's real, separate $1.2m
4% LIHTC line). All three were corrected by cross-reading the page image.
No unit total, dollar total, or project count was ever adjusted to make a
verification gate pass -- see verify_* below, which fail loudly instead.

Double verification (Appendix C prints no footer/grand-total row)
------------------------------------------------------------------------
Two independent gates, both computed from RAW_PROJECTS/PROJECT_SOURCE_AMOUNTS
(never fabricated to force a match):
  1. External: summed RAW_PROJECTS units across all 85 developments must
     equal 8,183 -- OHFA's own printed "8,183 Total Units Funded" headline
     (p.18). This is the strongest available check, since it is an
     independently *published* number this script never derives from
     Appendix C itself.
  2. Internal: EXPECTED_SOURCE_TOTALS below (each funding source's total
     dollar amount, funding-line count, and covered-unit sum) was computed
     ONCE, programmatically, straight off Appendix C's own table cells via
     the pdfplumber word-position pass described above -- before the
     project-name cross-read that produced the final RAW_PROJECTS/
     PROJECT_SOURCE_AMOUNTS transcription below. verify_source_totals()
     re-sums the finished RAW_PROJECTS/PROJECT_SOURCE_AMOUNTS and checks it
     reproduces those same three numbers per source, exactly matching this
     pilot series' PHFA build script's "EXPECTED_SOURCE_TOTALS independently
     computed once, then checked" methodology (used there for the same
     reason: PHFA's own Map Doc table also prints no footer total row).
Note: these per-source Appendix C tallies (e.g. 21 developments carrying a
9% LIHTC line, $30,552,000 total) do NOT exactly match OHFA's own p.19
"Breakdown of Overall Funding" press-release-style counts (31 projects --
9% LIHTC / 59 projects -- 4% LIHTC / 35 projects -- Multifamily Bond
Program, etc.). This is expected and is flagged here rather than silently
forced to reconcile: Appendix C only lists developments receiving their
*initial* funding reservation during FY25, while OHFA's own aggregate
figures on p.19 plausibly also include supplemental/subsequent-round
allocation actions to developments initially reserved in an earlier fiscal
year (not re-listed as a new Appendix C row) and/or Appendix D's
placed-in-service issuances -- see "Appendix C vs Appendix D" above. The
8,183-unit total (gate 1) is the number this script treats as
authoritative for the category headline; the per-source Appendix C sums
(gate 2) are presented as Appendix C's own internally-consistent detail,
not as a restatement of OHFA's press-release aggregate.

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
OHFA's own MD&A states plainly: "OHFA is a self-supporting, public purpose
financial entity and follows enterprise fund reporting" (ACFR p.6), and its
basic financial statements are a Statement of Net Position / Statement of
Revenues, Expenses and Changes in Net Position / Statement of Cash Flows
for exactly three funds: the Single-Family Mortgage Revenue Program Fund,
the General Fund, and the Federal Program Fund (auditor's opinion, p.4).
All three are proprietary (business-type) funds -- OHFA, like PHFA in this
same pilot series, carries no governmental funds of its own at all.
  - "proprietary":
      * Homebuyer first mortgages + down payment assistance -> the Single-
        Family Mortgage Revenue Program Fund (Note 1, "Single Family
        Mortgage Revenue Program Fund", p.33 -- explicitly "provides
        qualified mortgagors with down payment and closing cost assistance
        under the Agency's residential homeownership programs"; Note 6
        "Loans Receivable", p.46, separately lines out "Market Rate
        Program" and "Down Payment Assistance" loans within this same
        fund). Grants for Grads and Ohio Heroes are rate-discount products
        on the same mortgage-origination pipeline; Grants for Grads is the
        one of the two the ACFR actually names (Note 6, p.46, listing a
        "Grants for Grads" loan balance under BOTH the Single Family
        Program's Bond Series Program Funds AND the General Fund --
        confidence: high, but genuinely split across two funds, hence
        fund_type="mixed" for it specifically). Ohio Heroes never appears
        by name anywhere in the ACFR; it is inferred to sit in the same
        Single Family Program pipeline as Grants for Grads, since no other
        OHFA fund books mortgage-loan products at all -- confidence: low,
        marked "(inferred)".
      * HDL (Housing Development Loan) -> the General Fund's "Housing
        Development Fund (HDF)" (Note 1, "General Fund", p.33: "includes
        amounts borrowed from [Ohio Department of] Commerce's Division of
        Unclaimed Funds to fund loans to qualified housing sponsors to
        develop affordable housing" -- matches the Annual Report's own
        HDL description on p.19 almost verbatim, including the Division of
        Unclaimed Funds detail. Confidence: high.).
      * Multifamily Lending Program -> the General Fund's own named
        "Multifamily Loan Program" loan-receivable line (Note 6, p.46, and
        Note 13 "Commitments", p.68, "Multifamily Lending Program
        $59,631,285"). Confidence: high.
      * HDAP-HOME/-NHTF -> the Federal Program Fund (Note 1, "Federal
        Program Fund", p.34, names HOME/HOME-ARPA/NHTF as the fund's HUD
        pass-through revenue sources that OHFA "utilizes ... to fund the
        HDAP"). Confidence: high.
      * HDAP-OHTF -> the General Fund (Note 1, "General Fund", p.33: "The
        Housing Development Assistance Program (HDAP) includes money
        provided by the Ohio Housing Trust Fund (OHTF) ... Loans are
        repaid to the OHTF" -- appears in the General Fund paragraph, not
        the Federal Program Fund one, since OHTF is a state, not a HUD
        federal, revenue source). Confidence: high.
  - "off_balance_sheet":
      * 9% LIHTC / 4% LIHTC / Ohio LIHTC (OLIHTC) -- the credit VALUE
        itself is allocated directly to developers/investors and is
        confirmed never booked as an OHFA fund asset; the ACFR's only
        LIHTC-adjacent balance is unearned *administrative fee* revenue
        for running the reservation/compliance-monitoring process ("Total
        unearned revenue in the General Fund ... is primarily Housing Tax
        Credit reservation and compliance monitoring [fees]", Note 2,
        p.35) -- the fee income sits in the General Fund, but the credits
        themselves do not, matching this pilot series' identical
        IHDA/PHFA LIHTC treatment.
      * Multifamily Bond Program (MF Bonds) -- confirmed CONDUIT DEBT, not
        an OHFA fund liability at all (Note 4, "Conduit Debt Obligations",
        p.44: "The bonds issued are limited obligations of OHFA, payable
        only out of the trust estate specifically pledged to each bond
        issue ... No recourse may be taken against any properties, funds
        or assets of OHFA for the payment of any amounts owed with respect
        to these bonds"). This is a different underlying reason than the
        LIHTC entries above (conduit issuance vs. tax-credit allocation),
        but the same GASB-fund-type conclusion: not an OHFA balance-sheet
        item.

Geocoding
------------------------------------------------------------------------
Appendix C gives only Municipality + County for each development (no
street address column at all -- unlike IHDA's and PHFA's project-level
sources), so every project geocodes to a municipality center, never a
street address. Query: "{Municipality}, {County} County, OH" via Nominatim
(OpenStreetMap), falling back to "{Municipality}, OH" if the county-
qualified query returns nothing (several Appendix C "Municipality" values
are unincorporated townships that Nominatim only resolves without the
county qualifier). geocode_status is set to "city_center" for every
successfully-resolved project (never "ok", since no project here is ever
resolved at street precision) and "unresolved" for any that fail both
attempts. Self-throttled to <=1 request/second with an identifying
User-Agent, per Nominatim's usage policy, matching this pilot series'
IHDA/PHFA build scripts.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "oh_program_activity.json"

SOURCE_URL = "https://ohiohome.org/news/documents/annualreport_25.pdf"
SOURCE_FILE = "OH_OHFA_AnnualReport_FY2025.pdf"
RETRIEVED = "2026-08-13"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
GEOCODER_USER_AGENT = "us-hfa-data-map/1.0 (github.com/MD-ai-fin/us-hfa-data-map)"

# fy2026 uniform shape: {value, amount, closed, note_key} -- see IHDA/PHFA
# build scripts' identical convention. The FY2025 Annual Report contains no
# FY2026 projections anywhere (checked via full-text search for
# "2026"/"projected" -- zero forward-looking figures of any kind), so every
# fy2026 field below is the same all-pending placeholder; nothing is
# invented.
_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "ohFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "multifamily_developments",
        "unit_type": "units",
        "fy2025_actual": 8183,
        "fy2025_source_quote": (
            "\"In fiscal year 2025, OHFA allocated $1.2 billion for the creation or "
            "preservation of 8,183 affordable housing units through the federal 9% and "
            "4% Low-Income Housing Tax Credit (LIHTC) programs. These funds will be "
            "claimed over the next 10 years.\" Breakdown of Affordable Housing Units: "
            "5,286 New construction or adaptive reuse units + 2,897 Preserved through "
            "rehab of existing units = 8,183 Total Units Funded (6,114 General "
            "occupancy / 1,353 Senior / 164 Permanent supportive housing / 552 "
            "Assisted living). \"In order to make affordable housing developments "
            "financially feasible, OHFA may provide a single project funding from more "
            "than one program ... The total number of developments OHFA funded in FY25 "
            "is 116.\" (Annual Report, pp.18-19)"
        ),
        "fy2025_amounts": [
            {"label_key": "oh_amt_federal_lihtc", "amount": 1200000000},
            {"label_key": "oh_amt_ohio_lihtc", "amount": 109000000},
            {"label_key": "oh_amt_hdap", "amount": 52000000},
            {"label_key": "oh_amt_mf_bonds", "amount": 596000000},
            {"label_key": "oh_amt_hdl", "amount": 101000000},
            {"label_key": "oh_amt_mf_lending", "amount": 5400000},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "lihtc_9", "fy2025_units": 1271, "fy2025_amount": 30552000,
             "color_group": "credit",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "lihtc_4", "fy2025_units": 6141, "fy2025_amount": 75307000,
             "color_group": "credit",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "olihtc", "fy2025_units": 989, "fy2025_amount": 10895000,
             "color_group": "credit",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "mf_bonds", "fy2025_units": 2014, "fy2025_amount": 382500000,
             "color_group": "bond",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "hdl", "fy2025_units": 3291, "fy2025_amount": 100300000,
             "color_group": "capital",
             "fund_type": "proprietary", "fund_name": "General Fund (Housing Development Fund)",
             "fy2026": _FY26_PENDING},
            {"key": "mf_lending", "fy2025_units": None, "fy2025_amount": 5400000,
             "color_group": "capital",
             "fund_type": "proprietary", "fund_name": "General Fund (Multifamily Loan Program)",
             "fy2026": _FY26_PENDING},
            {"key": "hdap_home", "fy2025_units": 437, "fy2025_amount": 20700000,
             "color_group": "trust",
             "fund_type": "proprietary", "fund_name": "Federal Program Fund (HOME/HOME-ARPA)",
             "fy2026": _FY26_PENDING},
            {"key": "hdap_nhtf", "fy2025_units": 314, "fy2025_amount": 12312000,
             "color_group": "trust",
             "fund_type": "proprietary", "fund_name": "Federal Program Fund (National Housing Trust Fund)",
             "fy2026": _FY26_PENDING},
            {"key": "hdap_ohtf", "fy2025_units": 249, "fy2025_amount": 17325000,
             "color_group": "trust",
             "fund_type": "proprietary", "fund_name": "General Fund (Housing Development Assistance Program – Ohio Housing Trust Fund)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "homebuyer_loans",
        "unit_type": "households",
        "fy2025_actual": 6664,
        "fy2025_source_quote": (
            "\"With more than $1.3 billion in loans financed -- up from $813 million in "
            "fiscal year 2024 -- ... 6,664 borrowers used OHFA's homebuyer programs and "
            "of those, 5,000 used the Agency's down payment assistance program.\" "
            "Appendix A (\"Homebuyer Program Lenders by Total Loan Volume, Fiscal Year "
            "2025\") Grand Total row: 6,664 loans, $1,320,664,985 total loan volume, "
            "$198,179 average loan amount. \"465 Grants for Grads loans financed in "
            "FY25\"; \"1,300 Ohio Heroes loans financed in FY25\" (pp.8-9, 23-26)."
        ),
        "fy2025_amounts": [
            {"label_key": "oh_amt_total_financed", "amount": 1320664985},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "first_mortgages", "fy2025_units": 6664, "fy2025_amount": 1320664985,
             "color_group": "capital",
             "fund_type": "proprietary", "fund_name": "Single-Family Mortgage Revenue Program Fund",
             "fy2026": _FY26_PENDING},
            {"key": "downpayment_assistance", "fy2025_units": 5000, "fy2025_amount": None,
             "color_group": "trust",
             "fund_type": "proprietary", "fund_name": "Single-Family Mortgage Revenue Program Fund (Down Payment Assistance)",
             "fy2026": _FY26_PENDING},
            {"key": "grants_for_grads", "fy2025_units": 465, "fy2025_amount": None,
             "color_group": "trust",
             # Note 6 "Loans Receivable" (p.46) lists a "Grants for Grads" loan
             # balance under BOTH the Single Family Program's Bond Series
             # Program Funds AND the General Fund -- genuinely split across
             # two funds, unlike every other subprogram here.
             "fund_type": "mixed", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "ohio_heroes", "fy2025_units": 1300, "fy2025_amount": None,
             "color_group": "trust",
             # Never named anywhere in the ACFR; inferred to ride the same
             # Single Family Program mortgage-origination pipeline as Grants
             # for Grads, since no other OHFA fund books loan products at
             # all -- confidence: low.
             "fund_type": "proprietary", "fund_name": "Single-Family Mortgage Revenue Program Fund (inferred)",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# ---------------------------------------------------------------------------
# Multifamily project-level detail (Appendix C, pages 32-35). One row per
# development; address is always None (Appendix C gives only Municipality +
# County, no street address -- see docstring "Geocoding").
# (name, municipality, county, units, [funding source keys])
# ---------------------------------------------------------------------------

RAW_PROJECTS = [
    ("Arlington Senior Housing", "Toledo", "Lucas", 57, ["lihtc_9"]),
    ("Channing Street Redevelopment", "Delaware Township", "Delaware", 44, ["lihtc_9"]),
    ("Carol Crossing", "Washington Township", "Muskingum", 42, ["lihtc_9", "hdl"]),
    ("Sunrise Homes", "Lorain", "Lorain", 35, ["lihtc_4"]),
    ("Cedar Redevelopment Phase IV", "Cleveland", "Cuyahoga", 50, ["lihtc_4", "mf_bonds"]),
    ("Kinship Family Housing", "Dayton", "Montgomery", 26, ["lihtc_4", "hdl", "mf_bonds"]),
    ("Nelson Court Rehabilitation Phase II", "Lakewood", "Cuyahoga", 5, ["hdap_nhtf"]),
    ("PC Plumly Townhomes", "Warren Township", "Belmont", 31, ["lihtc_4", "hdap_nhtf", "hdl", "mf_bonds"]),
    ("Gates Mills Villa", "Mayfield Heights", "Cuyahoga", 191, ["lihtc_4"]),
    ("Foster Senior Lofts", "Elyria Township", "Lorain", 46, ["lihtc_4", "hdap_home", "hdap_nhtf", "hdl", "mf_bonds"]),
    ("Olympia Building", "Cleveland", "Cuyahoga", 20, ["hdap_nhtf", "hdap_ohtf"]),
    ("PC St. Clairsville Courtyard", "Richland Township", "Belmont", 24, ["lihtc_4", "hdap_home", "hdap_ohtf", "hdl", "mf_bonds"]),
    ("The Caravel", "Franklin Township", "Franklin", 234, ["lihtc_4"]),
    ("Westerville Crossing", "Mifflin Township", "Franklin", 264, ["lihtc_4"]),
    ("Nobility Court", "Cleveland Heights", "Cuyahoga", 52, ["hdl", "lihtc_9"]),
    ("The Reserve at Chatford", "Truro Township", "Franklin", 192, ["lihtc_4"]),
    ("Fairview I & II", "Marion Township", "Marion", 124, ["lihtc_4", "mf_bonds"]),
    ("Havens Edge Apartments", "Truro Township", "Franklin", 246, ["lihtc_4", "mf_bonds"]),
    ("Norwalk North Apartments", "Norwalk Township", "Huron", 72, ["lihtc_4", "mf_bonds"]),
    ("Wyandot Square Apartments", "Polk Township", "Crawford", 62, ["lihtc_4", "mf_bonds"]),
    ("Beechwood Apartments", "Cincinnati", "Hamilton", 149, ["lihtc_9", "hdap_nhtf", "mf_bonds"]),
    ("Marquette Manor", "Cincinnati", "Hamilton", 140, ["lihtc_4", "hdl", "mf_bonds"]),
    ("Allerton Apartments", "Cleveland", "Cuyahoga", 199, ["lihtc_4", "hdl"]),
    ("Asbury Apartments", "Dayton", "Montgomery", 119, ["lihtc_4"]),
    ("At Main", "Trotwood", "Montgomery", 63, ["lihtc_4", "hdap_home", "hdap_nhtf", "hdl", "mf_bonds"]),
    ("Berkshire Commons", "Berkshire Township", "Delaware", 58, ["hdl"]),
    ("Northcrest Gardens Apartments", "Harrison Township", "Montgomery", 182, ["lihtc_4"]),
    ("Mad River Manor", "Riverside", "Montgomery", 74, ["lihtc_4"]),
    ("Albright Apartments", "Trotwood", "Montgomery", 112, ["lihtc_4"]),
    ("Silver Birch of Mansfield", "Mansfield", "Richland", 120, ["lihtc_4", "mf_bonds"]),
    ("Pinewood Gardens Apartments", "Trotwood", "Montgomery", 80, ["lihtc_4"]),
    ("Arrowhead Lofts", "Maumee", "Lucas", 58, ["hdl", "lihtc_9"]),
    ("Artem on Gay", "Columbus", "Franklin", 71, ["hdl", "lihtc_9"]),
    ("Senior Village at Valle Greene", "Bath Township", "Greene", 70, ["hdap_home", "hdl", "lihtc_9"]),
    ("Aspire COLUMBUS", "Columbus", "Franklin", 82, ["hdl", "lihtc_9"]),
    ("Beaumont Greene", "Canaan Township", "Athens", 40, ["hdl", "lihtc_9"]),
    ("Blackburn Landing", "Athens Township", "Athens", 50, ["hdl", "lihtc_9"]),
    ("Bowling Green Senior Housing", "Plain Township", "Wood", 66, ["hdl", "lihtc_9"]),
    ("Brookside Place Apartments", "Harrison Township", "Licking", 32, ["hdl", "lihtc_9"]),
    ("Churchill Gateway Phase II", "Cleveland", "Cuyahoga", 70, ["hdl", "lihtc_9"]),
    ("Cleveland West Veterans Housing", "Cleveland", "Cuyahoga", 62, ["hdap_home", "hdl", "lihtc_9"]),
    ("Divinity Landing", "Twinsburg Township", "Summit", 54, ["hdl", "lihtc_9"]),
    ("Emerald Senior", "Cleveland", "Cuyahoga", 62, ["lihtc_9", "hdap_home", "hdl"]),
    ("Knoll View Place", "Columbus", "Franklin", 50, ["hdap_home", "hdl", "lihtc_9"]),
    ("Roberts Run Landing", "Richland Township", "Belmont", 76, ["lihtc_9"]),
    ("Scioto Rise Place", "Columbus", "Franklin", 60, ["lihtc_9", "hdap_home", "hdl"]),
    ("Edgemont Colony", "St. Joseph Township", "Williams", 24, ["lihtc_9"]),
    ("Stow Kent Gardens", "Stow", "Summit", 47, ["hdl"]),
    ("Thornville Manor", "Thorn Township", "Perry", 24, ["hdl"]),
    ("Commons at Grant", "Columbus", "Franklin", 100, ["hdl"]),
    ("Georgetown Village", "Harrison Township", "Montgomery", 101, ["mf_bonds"]),
    ("Cedarwood Commons", "Madison Township", "Franklin", 223, ["lihtc_4"]),
    ("Meadow Creek", "Madison Township", "Franklin", 252, ["lihtc_4"]),
    ("Kinsey Greene", "Xenia Township", "Greene", 110, ["lihtc_4"]),
    ("Community and Pendleton Apartments", "Cincinnati", "Hamilton", 61, ["lihtc_4", "hdl", "mf_bonds"]),
    ("Pebble Brooke", "Miami Township", "Clermont", 260, ["lihtc_4", "mf_bonds"]),
    ("Seton Portsmouth", "Washington Township", "Scioto", 57, ["lihtc_4", "hdl", "mf_bonds"]),
    ("Belmar Trail of Lebanon", "Lebanon", "Warren", 44, ["mf_bonds"]),
    ("Brentnell Pointe", "Columbus", "Franklin", 50, ["lihtc_4", "hdl", "mf_bonds"]),
    ("The Blair", "Cincinnati", "Hamilton", 49, ["lihtc_4", "hdl"]),
    ("Emerald Glen Apartments", "Prairie Township", "Franklin", 130, ["hdl"]),
    ("HoM Flats at Forest Avenue", "Harrison Township", "Montgomery", 260, ["lihtc_4"]),
    ("Wirthman Yard", "Truro Township", "Franklin", 315, ["lihtc_4"]),
    ("Belmar Hill of Mt. Washington", "Anderson Township", "Hamilton", 54, ["lihtc_4", "olihtc", "hdl"]),
    # Appendix C prints the municipality as "Stubenville Township" -- corrected
    # to "Steubenville Township" for geocoding accuracy (Jefferson County's
    # well-known seat; not a fabrication, a typo fix, matching this pilot
    # series' identical PHFA "Belthlehem"->"Bethlehem" correction).
    ("Booth Pointe", "Steubenville Township", "Jefferson", 46, ["lihtc_4", "olihtc", "hdap_ohtf", "hdl"]),
    ("Cornerstone at Eclipse Run", "Athens Township", "Athens", 58, ["lihtc_4", "olihtc", "hdap_ohtf", "hdl"]),
    ("Easton Place Homes III", "Mifflin Township", "Franklin", 50, ["hdl", "olihtc"]),
    ("Gateway66", "Cleveland", "Cuyahoga", 80, ["hdl"]),
    ("Hamilton Place", "Plain Township", "Franklin", 60, ["hdl"]),
    ("Harding Heights Apartments", "Marion Township", "Marion", 50, ["lihtc_4", "olihtc", "hdap_ohtf", "hdl"]),
    ("Kinsey Lofts", "Cincinnati", "Hamilton", 52, ["lihtc_4", "olihtc", "hdl"]),
    ("Reserve at Maryland Avenue", "Columbus", "Franklin", 84, ["lihtc_4", "hdl", "mf_bonds"]),
    ("Silver Birch of Bedford Heights", "Bedford Heights", "Cuyahoga", 120, ["lihtc_4", "mf_bonds"]),
    ("The Heights", "Springfield Township", "Summit", 160, ["lihtc_4", "olihtc", "hdl"]),
    ("The Lofts on First", "Athens Township", "Athens", 51, ["lihtc_4", "olihtc", "hdap_ohtf", "hdl"]),
    ("Springfield AAL", "Springfield Township", "Clark", 124, ["lihtc_4"]),
    ("Vivera Northbrook", "Colerain Township", "Hamilton", 118, ["lihtc_4"]),
    ("Gateway Plaza", "Cincinnati", "Hamilton", 349, ["lihtc_4"]),
    ("HUB 27", "Cleveland", "Cuyahoga", 53, ["lihtc_4", "olihtc", "hdl"]),
    ("Lofts at 40 Long", "Columbus", "Franklin", 121, ["lihtc_4", "olihtc", "hdl"]),
    ("Residences at Ascend", "Akron", "Summit", 71, ["lihtc_4", "olihtc", "hdl"]),
    ("The Heights on Main", "Truro Township", "Franklin", 103, ["lihtc_4", "olihtc", "hdl"]),
    ("The Scarborough", "Columbus", "Franklin", 84, ["lihtc_4", "mf_bonds"]),
    ("Walton Senior Apartments", "Cleveland", "Cuyahoga", 52, ["hdl"]),
    ("Midtown Lofts", "Cleveland", "Cuyahoga", 120, ["lihtc_4", "olihtc", "hdl"]),
]

# Per-project, per-funding-source dollar amount, transcribed from Appendix
# C's own "OHFA Funds Allocated" column (see docstring "Transcription
# method" for how misattributed lines were caught and corrected).
PROJECT_SOURCE_AMOUNTS = {
    "Arlington Senior Housing": {"lihtc_9": 1200000},
    "Channing Street Redevelopment": {"lihtc_9": 1800000},
    "Carol Crossing": {"lihtc_9": 1000000, "hdl": 1800000},
    "Sunrise Homes": {"lihtc_4": 142000},
    "Cedar Redevelopment Phase IV": {"lihtc_4": 950000, "mf_bonds": 12000000},
    "Kinship Family Housing": {"lihtc_4": 693000, "hdl": 2000000, "mf_bonds": 8000000},
    "Nelson Court Rehabilitation Phase II": {"hdap_nhtf": 487000},
    "PC Plumly Townhomes": {"lihtc_4": 264000, "hdap_nhtf": 3000000, "hdl": 2000000, "mf_bonds": 4100000},
    "Gates Mills Villa": {"lihtc_4": 1700000},
    "Foster Senior Lofts": {"lihtc_4": 635000, "hdap_home": 2000000, "hdap_nhtf": 2500000, "hdl": 2000000, "mf_bonds": 8000000},
    "Olympia Building": {"hdap_nhtf": 525000, "hdap_ohtf": 925000},
    "PC St. Clairsville Courtyard": {"lihtc_4": 210000, "hdap_home": 1400000, "hdap_ohtf": 1700000, "hdl": 1000000, "mf_bonds": 3800000},
    "The Caravel": {"lihtc_4": 2500000},
    "Westerville Crossing": {"lihtc_4": 4200000},
    "Nobility Court": {"hdl": 1600000, "lihtc_9": 1200000},
    "The Reserve at Chatford": {"lihtc_4": 2700000},
    "Fairview I & II": {"lihtc_4": 1200000, "mf_bonds": 16000000},
    "Havens Edge Apartments": {"lihtc_4": 4400000, "mf_bonds": 56500000},
    "Norwalk North Apartments": {"lihtc_4": 457000, "mf_bonds": 8800000},
    "Wyandot Square Apartments": {"lihtc_4": 444000, "mf_bonds": 6000000},
    "Beechwood Apartments": {"lihtc_9": 2100000, "hdap_nhtf": 3000000, "mf_bonds": 25000000},
    "Marquette Manor": {"lihtc_4": 2200000, "hdl": 2000000, "mf_bonds": 25500000},
    "Allerton Apartments": {"lihtc_4": 1500000, "hdl": 2000000},
    "Asbury Apartments": {"lihtc_4": 1200000},
    "At Main": {"lihtc_4": 1200000, "hdap_home": 2000000, "hdap_nhtf": 2800000, "hdl": 1500000, "mf_bonds": 15000000},
    "Berkshire Commons": {"hdl": 1800000},
    "Northcrest Gardens Apartments": {"lihtc_4": 1900000},
    "Mad River Manor": {"lihtc_4": 773000},
    "Albright Apartments": {"lihtc_4": 1000000},
    "Silver Birch of Mansfield": {"lihtc_4": 1600000, "mf_bonds": 26000000},
    "Pinewood Gardens Apartments": {"lihtc_4": 630000},
    "Arrowhead Lofts": {"hdl": 1800000, "lihtc_9": 1700000},
    "Artem on Gay": {"hdl": 1800000, "lihtc_9": 1800000},
    "Senior Village at Valle Greene": {"hdap_home": 1400000, "hdl": 1800000, "lihtc_9": 1800000},
    "Aspire COLUMBUS": {"hdl": 1800000, "lihtc_9": 1800000},
    "Beaumont Greene": {"hdl": 1800000, "lihtc_9": 773000},
    "Blackburn Landing": {"hdl": 1800000, "lihtc_9": 1300000},
    "Bowling Green Senior Housing": {"hdl": 1800000, "lihtc_9": 1700000},
    "Brookside Place Apartments": {"hdl": 1800000, "lihtc_9": 543000},
    "Churchill Gateway Phase II": {"hdl": 1800000, "lihtc_9": 1800000},
    "Cleveland West Veterans Housing": {"hdap_home": 1000000, "hdl": 2500000, "lihtc_9": 1800000},
    "Divinity Landing": {"hdl": 1800000, "lihtc_9": 1600000},
    "Emerald Senior": {"lihtc_9": 1100000, "hdap_home": 1900000, "hdl": 1800000},
    "Knoll View Place": {"hdap_home": 5500000, "hdl": 2500000, "lihtc_9": 1500000},
    "Roberts Run Landing": {"lihtc_9": 1800000},
    "Scioto Rise Place": {"lihtc_9": 1800000, "hdap_home": 5500000, "hdl": 2500000},
    "Edgemont Colony": {"lihtc_9": 436000},
    "Stow Kent Gardens": {"hdl": 1800000},
    "Thornville Manor": {"hdl": 1800000},
    "Commons at Grant": {"hdl": 1800000},
    "Georgetown Village": {"mf_bonds": 13000000},
    "Cedarwood Commons": {"lihtc_4": 1800000},
    "Meadow Creek": {"lihtc_4": 2500000},
    "Kinsey Greene": {"lihtc_4": 973000},
    "Community and Pendleton Apartments": {"lihtc_4": 960000, "hdl": 2000000, "mf_bonds": 15000000},
    "Pebble Brooke": {"lihtc_4": 2700000, "mf_bonds": 49000000},
    "Seton Portsmouth": {"lihtc_4": 922000, "hdl": 2000000, "mf_bonds": 11000000},
    "Belmar Trail of Lebanon": {"mf_bonds": 8000000},
    "Brentnell Pointe": {"lihtc_4": 844000, "hdl": 2000000, "mf_bonds": 11300000},
    "The Blair": {"lihtc_4": 727000, "hdl": 2000000},
    "Emerald Glen Apartments": {"hdl": 1800000},
    "HoM Flats at Forest Avenue": {"lihtc_4": 3300000},
    "Wirthman Yard": {"lihtc_4": 4700000},
    "Belmar Hill of Mt. Washington": {"lihtc_4": 540000, "olihtc": 523000, "hdl": 2500000},
    "Booth Pointe": {"lihtc_4": 876000, "olihtc": 876000, "hdap_ohtf": 4000000, "hdl": 2500000},
    "Cornerstone at Eclipse Run": {"lihtc_4": 956000, "olihtc": 955000, "hdap_ohtf": 2800000, "hdl": 2500000},
    "Easton Place Homes III": {"hdl": 2500000, "olihtc": 609000},
    "Gateway66": {"hdl": 2000000},
    "Hamilton Place": {"hdl": 1800000},
    "Harding Heights Apartments": {"lihtc_4": 562000, "olihtc": 541000, "hdap_ohtf": 3900000, "hdl": 2500000},
    "Kinsey Lofts": {"lihtc_4": 845000, "olihtc": 556000, "hdl": 2500000},
    "Reserve at Maryland Avenue": {"lihtc_4": 1400000, "hdl": 2000000, "mf_bonds": 16000000},
    "Silver Birch of Bedford Heights": {"lihtc_4": 1600000, "mf_bonds": 30000000},
    "The Heights": {"lihtc_4": 2200000, "olihtc": 997000, "hdl": 2500000},
    "The Lofts on First": {"lihtc_4": 949000, "olihtc": 949000, "hdap_ohtf": 4000000, "hdl": 2500000},
    "Springfield AAL": {"lihtc_4": 1900000},
    "Vivera Northbrook": {"lihtc_4": 1900000},
    "Gateway Plaza": {"lihtc_4": 1600000},
    "HUB 27": {"lihtc_4": 955000, "olihtc": 955000, "hdl": 2500000},
    "Lofts at 40 Long": {"lihtc_4": 1800000, "olihtc": 1000000, "hdl": 2500000},
    "Residences at Ascend": {"lihtc_4": 1000000, "olihtc": 934000, "hdl": 2500000},
    "The Heights on Main": {"lihtc_4": 1300000, "olihtc": 1000000, "hdl": 2500000},
    "The Scarborough": {"lihtc_4": 1300000, "mf_bonds": 14500000},
    "Walton Senior Apartments": {"hdl": 1800000},
    "Midtown Lofts": {"lihtc_4": 1700000, "olihtc": 1000000, "hdl": 2500000},
}

# Independently computed once, via a pdfplumber word-position pass straight
# off Appendix C's own table cells, BEFORE the project-name cross-read that
# produced RAW_PROJECTS/PROJECT_SOURCE_AMOUNTS above -- the "PDF-printed
# total" stand-in for this table, which (like PHFA's Map Doc) prints no
# footer/grand-total row of its own. See docstring "Double verification".
EXPECTED_SOURCE_TOTALS = {
    # key: (dollar_amount_sum, funding_line_count, covered_unit_sum)
    "lihtc_9":   (30552000, 21, 1271),
    "lihtc_4":   (75307000, 51, 6141),
    "olihtc":    (10895000, 13, 989),
    "mf_bonds":  (382500000, 22, 2014),
    "hdl":       (100300000, 49, 3291),
    "hdap_home": (20700000, 8, 437),
    "hdap_nhtf": (12312000, 6, 314),
    "hdap_ohtf": (17325000, 6, 249),
}

FUNDING_COLOR_GROUP = {
    "lihtc_9": "credit", "lihtc_4": "credit", "olihtc": "credit",
    "mf_bonds": "bond",
    "hdl": "capital", "mf_lending": "capital",
    "hdap_home": "trust", "hdap_nhtf": "trust", "hdap_ohtf": "trust",
}
# priority order for picking a project's single "primary" color when it has
# multiple funding sources (first match wins) -- bonds and LIHTC are the
# largest-dollar pieces on the projects that carry them, so they lead.
FUNDING_PRIORITY = ["mf_bonds", "lihtc_9", "lihtc_4", "olihtc", "hdl",
                     "hdap_home", "hdap_nhtf", "hdap_ohtf"]


def verify_unit_total():
    total = sum(units for _n, _m, _c, units, _s in RAW_PROJECTS)
    if total != 8183:
        raise SystemExit(
            f"RAW_PROJECTS units sum: expected 8,183 (OHFA's own \"Total Units "
            f"Funded\" headline, p.18), got {total:,}"
        )
    if len(RAW_PROJECTS) != 85:
        raise SystemExit(f"RAW_PROJECTS count: expected 85, got {len(RAW_PROJECTS)}")
    if set(PROJECT_SOURCE_AMOUNTS) != {n for n, *_ in RAW_PROJECTS}:
        raise SystemExit("RAW_PROJECTS and PROJECT_SOURCE_AMOUNTS project-name sets differ")
    for name, _muni, _county, _units, sources in RAW_PROJECTS:
        amounts = PROJECT_SOURCE_AMOUNTS.get(name, {})
        missing = [s for s in sources if s not in amounts]
        extra = [s for s in amounts if s not in sources]
        if missing:
            raise SystemExit(f"{name!r} is missing amounts for source(s) {missing}")
        if extra:
            raise SystemExit(f"{name!r} has amounts for undeclared source(s) {extra}")
    print(f"RAW_PROJECTS: {len(RAW_PROJECTS)} developments, units sum = 8,183 "
          f"(matches OHFA's own \"8,183 Total Units Funded\" headline).")


def verify_source_totals():
    sums = {}
    counts = {}
    unit_sums = {}
    for name, _muni, _county, units, sources in RAW_PROJECTS:
        amounts = PROJECT_SOURCE_AMOUNTS[name]
        for src in sources:
            sums[src] = sums.get(src, 0) + amounts[src]
            counts[src] = counts.get(src, 0) + 1
            unit_sums[src] = unit_sums.get(src, 0) + units
    errors = []
    for key, (exp_amount, exp_count, exp_units) in EXPECTED_SOURCE_TOTALS.items():
        got_amount = sums.get(key, 0)
        got_count = counts.get(key, 0)
        got_units = unit_sums.get(key, 0)
        if got_amount != exp_amount:
            errors.append(f"{key} amount: expected {exp_amount:,}, got {got_amount:,}")
        if got_count != exp_count:
            errors.append(f"{key} count: expected {exp_count}, got {got_count}")
        if got_units != exp_units:
            errors.append(f"{key} unit_sum: expected {exp_units:,}, got {got_units:,}")
    if errors:
        raise SystemExit("Funding-source total mismatch(es):\n" + "\n".join(errors))
    print("All 8 funding-source dollar/count/unit-sum totals verified against the "
          "independently pdfplumber-computed EXPECTED_SOURCE_TOTALS.")


def geocode(query, cache):
    if query in cache:
        return cache[query]
    params = urllib.parse.urlencode({"q": query, "format": "json", "limit": 1})
    url = f"{NOMINATIM_URL}?{params}"
    result = None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": GEOCODER_USER_AGENT})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.load(resp)
        if data:
            result = (float(data[0]["lat"]), float(data[0]["lon"]))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, KeyError, ValueError, IndexError) as exc:
        print(f"  geocode failed for {query!r}: {exc}")
    cache[query] = result
    time.sleep(1.0)  # Nominatim usage policy: max 1 request/second
    return result


def build_projects():
    cache = {}
    projects = []
    for name, muni, county, units, sources in RAW_PROJECTS:
        query = f"{muni}, {county} County, OH"
        coords = geocode(query, cache)
        status = "city_center"
        if coords is None:
            coords = geocode(f"{muni}, OH", cache)
            status = "city_center" if coords else "unresolved"
        primary = next((s for s in FUNDING_PRIORITY if s in sources), sources[0])
        source_amounts = PROJECT_SOURCE_AMOUNTS.get(name, {})
        projects.append({
            "id": name.lower().replace(" ", "-").replace("'", "").replace(".", "")
                        .replace("&", "and").replace(",", ""),
            "name": name,
            "address": None,
            "city": muni,
            "lat": round(coords[0], 5) if coords else None,
            "lon": round(coords[1], 5) if coords else None,
            "units": units,
            "funding_sources": sources,
            "source_amounts": source_amounts,
            "total_amount": sum(source_amounts.values()) if source_amounts else None,
            "primary_color_group": FUNDING_COLOR_GROUP[primary],
            "overlaps": len(sources) > 1,
            "geocode_status": status,
        })
    return projects


def main():
    verify_unit_total()
    verify_source_totals()
    print("Geocoding project municipalities via Nominatim...")
    projects = build_projects()
    unresolved = [p["name"] for p in projects if p["geocode_status"] == "unresolved"]
    if unresolved:
        print(f"  {len(unresolved)} project(s) could not be geocoded: {unresolved}")
    print(f"  {sum(1 for p in projects if p['geocode_status'] == 'city_center')} "
          f"project(s) resolved to municipality/city-center coordinates.")

    payload = {
        "OH": {
            "hfa_name": "Ohio Housing Finance Agency",
            "hfa_abbr": "OHFA",
            "fiscal_year": "FY2025",
            "source_title": "OHFA Fiscal Year 2025 Annual Report -- Housing production summary, Appendix A, and Appendix C",
            "source_url": SOURCE_URL,
            "source_file": SOURCE_FILE,
            "retrieved": RETRIEVED,
            "categories": CATEGORIES,
            "projects": projects,
        }
    }
    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT_PATH} ({len(projects)} projects, {len(CATEGORIES)} categories)")


if __name__ == "__main__":
    main()
