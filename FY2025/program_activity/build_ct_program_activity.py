"""
Builds docs/ct_program_activity.json from Connecticut Housing Finance
Authority's (CHFA) 2025 Annual Report, plus CHFA's own FY2025 audited
financial statements (for GASB fund-type classification).

Sources
---------------------------------------------------------------------------
1. "CHFA 2025 Annual Report" (cover page prints "Reporting Period: January
   1, 2025 - December 31, 2025"):
     https://www.chfa.org/assets/1/6/2025_Annual_Report_.pdf
   Index page (historical annual reports, same format each year):
     https://www.chfa.org/about-us/pre-annual-reports/
   Local copy: FY2025/program_activity/pdf/CT_CHFA_AnnualReport_2025.pdf
   (39 pages; downloaded and verified 200 OK / valid PDF before use.)
2. CHFA's own separately-issued FY2025 (CY2025) audited financial
   statements, used ONLY for fund-type classification:
     FY2025/txt/CT_CHFA_FY2025_ACFR.txt
   (also available as FY2025/pdf/CT_CHFA_FY2025_ACFR.pdf, used here to
   pull exact printed page numbers -- the .txt has no page markers of its
   own for a couple of citations below.)

IMPORTANT reporting-period note: CY2025, not FY2025
---------------------------------------------------------------------------
Unlike most of this project's other pilot states, CHFA's Annual Report and
audited financial statements both run on a CALENDAR year, January-December
2025 (confirmed independently by (a) the Annual Report's own cover page,
quoted above, and (b) the ACFR's title page: "FINANCIAL STATEMENTS AND
SUPPLEMENTARY INFORMATION DECEMBER 31, 2025 AND 2024" and its Independent
Auditors' Report: "...as of and for the year ended December 31, 2025 and
2024..."). This script therefore uses "CY2025" (not "FY2025") everywhere
the reporting period is described in its output, even though the
file/module is still named "fy2025"-style to match this project's directory
convention -- same approach as the FL build script.

IMPORTANT entity-identity check: this is Connecticut's CHFA, not Colorado's
---------------------------------------------------------------------------
"CHFA" is also the acronym of the unrelated Colorado Housing and Finance
Authority. FY2025/txt/CT_CHFA_FY2025_ACFR.txt was verified before use: its
title page and every page header read "CONNECTICUT HOUSING FINANCE
AUTHORITY", its Independent Auditors' Report addresses "the Board of
Directors, Connecticut Housing Finance Authority", and Note 1 states the
Authority "is a public instrumentality and political subdivision of the
State of Connecticut" created in 1969 under "Chapter 134 of the Connecticut
General Statutes" -- unambiguously the Connecticut agency, no substitution
needed, no mix-up with Colorado's identically-abbreviated HFA.

Category-level methodology
---------------------------------------------------------------------------
Homeownership (Annual Report pp.9-12): the category headline (3,788 first
mortgages / $1.063B, p.9) is the report's own printed stat-panel figure,
used verbatim (CHFA discloses this only rounded to 3 significant figures --
"$1.063B" -- no further-decimalized total is published anywhere in the
report, so none is invented here). Its two down-payment-assistance
subprograms are each disclosed with an exact dollar total:
  - DAP (p.11): "In 2025, CHFA assisted 818 borrowers using Down Payment
    Assistance Program loans totaling $9,548,887."
  - Time To Own / TTO (p.12, loan-closing count; CHFA's own FY2025 ACFR
    Note 16, p.58-60, dollar amount): p.12 states "2,684 Time To Own Loan
    Closings"; the ACFR's Note 16 "Grant Programs" activity table (p.60)
    separately gives an exact CHFA-recognized dollar figure for the same
    program: "TIME TO OWN 65,058 65,058" (Program Funding = Program
    Expenses, in $000s) = $65,058,000. This is the more precise, ACFR-
    sourced figure used here rather than approximating 2,684 x the Annual
    Report's own "$23,437 Median TTO Amount" (which would yield only a
    rough $62.9M estimate, not a number either document actually states).
Per the Annual Report (p.11): "In early 2024, CHFA revised its policy to
disallow the use of DAP in combination with the Time To Own (TTO) Program.
Borrowers are now limited to selecting one form of CHFA subordinate
financing" -- i.e. DAP and TTO are mutually exclusive of EACH OTHER
(additive=True relative to each other is correct, matching PA's K-FIT/
Advantage/PENNVEST pattern), but their sum (818 + 2,684 = 3,502) is
intentionally smaller than the category headline of 3,788 first mortgages
-- most first mortgages close with no CHFA/DOH-sourced second-mortgage
assistance at all.

Multifamily Development (Annual Report pp.14, 17-19, Appendix C pp.37-38):
the category headline uses 1,804 units -- the sum of Appendix C's own
"Total Units" column across its 23 named developments -- NOT the report's
separately-published "3,150 Units Reaching Initial Closings" headline
(p.3/p.14 stat panel), for the same reason FL's build used 12,007 over
13,196: 1,804 is the only figure with fully-verifiable, named-development,
per-funding-source detail behind it (this same Appendix C table), so the
category headline, every subprogram's unit count, and the map's own
markers are all internally consistent and traceable to one table. The
report's own footnote on "3,150" (p.3) reads: "*Initial closings include
9% and 4% LIHTC projects, Build For CT, SSHP Priority Needs, and DOH SSHP
Grant funded developments" -- a DIFFERENT and even broader footnote than
the one on the same stat on p.14 ("*Initial closings include 9% and 4%
LIHTC projects, Build For CT, and DOH SSHP grant-funded developments",
omitting "SSHP Priority Needs"). Neither footnote is used to force a
reconciliation: 1,804 (this category, Appendix C only) + 1,192 (Build For
CT, Appendix D, a separate category below) = 2,996, still 154 units short
of 3,150 -- the gap is presumably the "SSHP Priority Needs" slice named in
the p.3 footnote, which has NO corresponding appendix table anywhere in
this 39-page report (checked: only Appendices A, B, C, D exist, and none
is titled or described as "SSHP Priority Needs"). This script does not
guess at those 154 units or which developments they belong to -- it is
recorded here, in fy2025_source_quote, as an unresolved and apparently
undocumented discrepancy in CHFA's own report, not silently absorbed.

A second, separate undocumented-appendix gap: p.18 states "Fourteen
developments were awarded 4% LIHTC's in the 2025 competitive round...
located in nine Connecticut municipalities and will create or preserve
1,285 units... A full list of the award recipients can be found in the
appendix" -- but unlike the 9% LIHTC awards (Appendix A) and the HTCC
awards (Appendix B), NO "4% LIHTC Awards" appendix actually exists in this
report (only Appendices A/B/C/D, confirmed by reading every appendix
page/title). The category's fy2025_amounts below still reports the
"$23,820,954 4% Tax Credits Awarded" stat-panel figure (p.14) because it is
CHFA's own published number, but it is flagged there as unverifiable
against any per-development list, unlike the 9% and HTCC figures (both of
which reconcile exactly to their own appendix's printed Total row -- see
verify_9pct_awards()/verify_htcc_awards() below).

IMPORTANT: "Tax Credits Awarded" (p.14 stat panel / Appendix A's own
column) is NOT the same figure as Appendix C's "9% LIHTC Equity" /
"4% LIHTC Equity" columns. The former is the annual federal/state tax-
credit ALLOCATION amount (claimed by investors over a 10-year period); the
latter is the actual investor-syndicated EQUITY dollars raised at a
development's closing (roughly an order of magnitude larger, and drawn
from a different vintage of awards -- CT's competitive 9% round typically
closes 1-2 years after the award year, so Appendix A's 2025 AWARDS and
Appendix C's 2025 CLOSINGS are mostly different developments). This script
keeps the two figures clearly separate: fy2025_amounts on the multifamily
category use the p.14 "Tax Credits/HTCC Awarded" figures (cross-checked
against Appendices A/B's own printed totals), while the lihtc_4pct/
lihtc_9pct subprograms' fy2025_amount fields use Appendix C's own "LIHTC
Equity" column sums (independently verified against a pdfplumber-computed
column total, see verify_multifamily_source_totals()) -- these are
deliberately different dollar universes and are never added together.

Build For CT (Annual Report pp.20-21, Appendix D p.39): a separate
category from Multifamily above (both are plausible presentations per this
build's brief; a separate category was chosen because Build For CT has its
own clean, fully-reconciled headline figures independent of the LIHTC
funding stack). fy2025_actual (1,192 units), the $41,125,000 total funding
figure, and the 362 middle-income-unit figure are all Appendix D's own
printed Total row (p.39), cross-checked here by independently re-summing
all 13 of Appendix D's own rows (see verify_build_for_ct_totals()) -- all
three totals (Total M.I. Units, Total Units, Funding Provided) matched
exactly. Per this build's task brief, Appendix D is used ONLY for this
category-level verification, not exploded into individual map markers (the
bubble map below is built from Appendix C alone, per Multifamily's own
methodology note above) -- so Build For CT has no `projects` entries and no
map presence, matching how PA's HEMAP/PHARE/Homeownership categories (which
also have no per-development table) have no map presence either.

Appendix B / HTCC narrative-vs-table note: p.19 states "CHFA awarded HTCC
funds to 22 developments... In addition, three statewide loan funds also
received awards" (implying 22 + 3 = 25 total funded entities), but Appendix
B itself (pp.35-36) prints exactly 22 rows total, of which only 2 (not 3)
carry a "*" placeholder instead of a unit count ("Live Where You Work
(Round 18) - Workforce Housing" and "Capital for Change Loan Pool", both
plausibly the "statewide loan funds" the narrative refers to). The
appendix's own printed Total row (548 units / $9,670,675) reconciles
exactly against summing all 22 rows (verify_htcc_awards() below), so this
script trusts the appendix's own row count (22) over the narrative's
implied 25, and records the one-off gap here rather than fabricating a
23rd row.

Fund-type classification (fund_type/fund_name on each subprogram)
---------------------------------------------------------------------------
CHFA's own FY2025 (CY2025) audited financial statements state, in Note 2
("Summary of Significant Accounting Policies", "Basis of Accounting", ACFR
p.18 / PDF p.20): "While detail sub-fund information is not presented,
separate accounts are maintained for each program and include certain
funds that are legally designated as to use. The funds of the Authority
and similar component units are proprietary fund types." I.e. like Florida
Housing (a single enterprise fund) and unlike IHDA (7 governmental + 4
proprietary major funds), CHFA has NO governmental funds at all -- every
dollar CHFA itself carries is inside its (undifferentiated, in the audited
statements) proprietary fund. Note 2's "Reporting Entity" section (ACFR
pp.18-19 / PDF pp.20-21) separately NAMES several of CHFA's own internally
designated funds: the Housing Mortgage General and Capital Reserve Funds,
the Investment Trust Fund, the Housing Mortgage Insurance Fund (the "CHFA
Insurance Fund"), the Special Needs Housing Program/Renewal-and-Replacement
Funds, the Multifamily Special Obligation Bond and Other Bond Funds
("MFSOB"), the Qualified Energy Conservation Bond Fund ("QECB"), and the
Housing Revenue Bond Fund ("HRB", est. 2023). The working distinction below
therefore parallels FL's: "proprietary" when a subprogram maps onto one of
these named CHFA funds/programs (or is otherwise explicitly recognized with
its own dollar figure inside CHFA's own Notes to Financial Statements) vs.
"off_balance_sheet" when a subprogram is confirmed absent from CHFA's own
89-page-equivalent financial statements by name (checked via full-text
search of FY2025/txt/CT_CHFA_FY2025_ACFR.txt).
  - "proprietary", high confidence:
      * chfa_taxable_bonds, chfa_tax_exempt_bonds -- CHFA's own bond-fund
        financing of a multifamily loan, matching the MFSOB/"Multifamily
        Other Bond Resolution" and Housing Revenue Bond Fund named in Note
        2 (ACFR p.19 / PDF p.21): "the Multifamily Special Obligation Bond
        and Other Bond Funds which the Authority is authorized to
        maintain..." and "the Housing Revenue Bond Fund which the
        Authority is authorized to maintain... to allow the Authority to
        structure the issuance of debt based on market demand."
      * dap -- Note 16 ("Grant Programs", ACFR pp.59-60 / PDF pp.61-62)
        states in its own prose (not the summary table, which only covers
        the smaller pass-through grant lines): "The Authority manages a
        Down Payment Assistance Program (DAP)... During 2024, the
        Authority received $9,000,000 from the State of Connecticut to
        further capitalize the program." I.e. DAP is explicitly CHFA's OWN
        managed loan program (a second-mortgage product, presumably booked
        within the Housing Mortgage General Fund's loan portfolio), even
        though partly capitalized by a one-time 2024 State contribution.
      * tto (Time To Own) -- Note 16's own "Activity under these programs"
        table (ACFR p.60 / PDF p.62) lists "TIME TO OWN $65,058 $65,058"
        (Program Funding = Program Expenses, in $000s) as one of eight
        named line items recognized directly inside CHFA's own Notes to
        Financial Statements -- the same "revenue/expense recognized
        within the entity's own financial statements" logic this project
        uses for PHFA's HEMAP. Funding equals expenses exactly (a full
        pass-through, DOH's money net of any CHFA retention), but it is
        still CHFA-administered and CHFA-recognized, not merely mentioned
        in passing.
  - "proprietary" (inferred, lower confidence -- CHFA's own fund by name
    prefix, but not itself found as a literal, separately-broken-out
    dollar figure anywhere in the ACFR):
      * chfa_opportunity_fund -- never appears by name in
        CT_CHFA_FY2025_ACFR.txt (checked "Opportunity Fund" -- zero
        matches), but Note 2 (ACFR p.19 / PDF p.21) states "In addition to
        the aforementioned funds, the Authority, as permitted by the Act,
        has established other funds" -- i.e. CHFA is on record as capable
        of standing up ad hoc named funds beyond the ones Note 2 happens to
        enumerate, and the fund's own name is prefixed "CHFA" (unlike the
        DOH-branded lines below), consistent with it being CHFA's own
        internal gap-financing vehicle rather than a pass-through of
        someone else's money. Confidence: medium-low, flagged as inferred.
  - "off_balance_sheet" (confirmed absent from CHFA's own ACFR by name, or
    structurally external to CHFA's own balance sheet):
      * lihtc_4pct, lihtc_9pct -- Note 3's narrative (MD&A) mentions "9%
        LIHTC" only once, describing external MARKET conditions ("the
        demand for 9% LIHTC taxable financings"), never as a CHFA-carried
        balance; federal/state Low-Income Housing Tax Credits are
        allocated by CHFA directly to developers/investors and never
        become a CHFA fund asset -- same off-balance-sheet logic used for
        IL's LIHTC/IAHTC, PA's LIHTC/PHTC, and FL's HC9/HC4.
      * htcc -- "HTCC"/"Housing Tax Credit Contribution" never appears
        anywhere in CT_CHFA_FY2025_ACFR.txt (zero matches) -- a Connecticut
        state tax credit purchased by businesses and passed to nonprofit
        developers, structurally the same as LIHTC/PHTC above.
      * doh_sshp_grant, doh_hud_cdbg -- "SSHP", "State Sponsored Housing
        [Portfolio]", and "CDBG" never appear anywhere in
        CT_CHFA_FY2025_ACFR.txt (zero matches for all three) -- Department
        of Housing/HUD grant money that CHFA administers on the State's
        behalf for its State Sponsored Housing Portfolio, but does not
        carry as its own balance-sheet asset.
      * build_for_ct_closings -- "Build For CT" never appears anywhere in
        CT_CHFA_FY2025_ACFR.txt (zero matches). The Annual Report itself
        (p.20) describes Build For CT as "a Connecticut Department of
        Housing (DOH) program administered by [CHFA] that leverages more
        than $300 million of State bonding" -- explicitly STATE (not CHFA)
        general obligation bonding, structurally the same as FL's
        `local_bonds` (municipal/county bonds layered onto a CHFA-financed
        deal but never a CHFA liability) and PA's PENNVEST (a separate
        state authority's money administered, not carried, by the HFA).

Geocoding
---------------------------------------------------------------------------
Appendix C gives only a Town for each development -- no street address (the
report's own per-development detail never goes finer than town/city
anywhere in this document). Every project is therefore geocoded to its
town centroid via Nominatim ("{Town}, CT"), one query per unique town,
self-throttled to <=1 request/second with an identifying User-Agent per
Nominatim's usage policy, and every project's geocode_status is uniformly
recorded as "city_center" -- the highest location precision this state's
source document actually discloses (matching PA/IL's own "city_center"
fallback tier, used here as the ONLY tier rather than a fallback, since no
project in this dataset has a street address to attempt first). One
transcription note: Appendix C's own table prints the town of "Meadow
Gardens" (a Norwalk, CT development) as "Nowalk" -- corrected to "Norwalk"
here for geocoding/display accuracy; this is a source-PDF typo fix, not a
fabrication (Norwalk is unambiguously the intended, well-known Fairfield
County city, and CHFA's own Multifamily Development narrative page
elsewhere in this report separately confirms Fairfield County activity).

fy2026
---------------------------------------------------------------------------
The 2025 Annual Report has no forward-looking/projected-activity section of
any kind (checked: the string "2026" does not appear anywhere in the
39-page PDF) -- every fy2026 field below is {value: None, amount: None,
closed: False, note_key: "ctFy26NotePending"}.
"""

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "ct_program_activity.json"

SOURCE_URL = "https://www.chfa.org/assets/1/6/2025_Annual_Report_.pdf"
SOURCE_FILE = "CT_CHFA_AnnualReport_2025.pdf"
RETRIEVED = "2026-08-13"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
GEOCODER_USER_AGENT = "us-hfa-data-map/1.0 (github.com/MD-ai-fin/us-hfa-data-map)"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "ctFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "multifamily",
        "unit_type": "units",
        "fy2025_actual": 1804,
        "fy2025_source_quote": (
            "\"Appendix C: 2025 Multifamily Initial Closings\" (pp.37-38), 23 named "
            "developments, Total Units column sums to 1,804 (independently computed by "
            "this script -- the appendix prints no Total row of its own). The Annual "
            "Report's separate p.3/p.14 stat-panel figure of \"3,150 Units Reaching "
            "Initial Closings\" is a broader, differently-footnoted aggregate that also "
            "folds in Build For CT (a separate category below, 1,192 units) and an "
            "undocumented \"SSHP Priority Needs\" slice (~154 units) with no appendix "
            "table anywhere in this report -- this script uses 1,804, the only fully "
            "project-verifiable figure, and records the gap rather than forcing a "
            "reconciliation. Stat-panel dollar figures (p.14): \"$14,841,228 9% Tax "
            "Credits Awarded\" (= Appendix A's own printed Total, 10 developments/550 "
            "units, a 2025 AWARDS list -- a different vintage of developments than this "
            "category's 2025 CLOSINGS list), \"$23,820,954 4% Tax Credits Awarded\" "
            "(p.18 narrative promises \"a full list... in the appendix\" but no such "
            "appendix exists in this 39-page report -- unverifiable against any "
            "per-development detail, unlike the other two figures here), and "
            "\"$9,670,675 HTCC Credits Awarded\" (= Appendix B's own printed Total, 22 "
            "developments/548 units)."
        ),
        "fy2025_amounts": [
            {"label_key": "ct_amt_9pct_awarded", "amount": 14841228},
            {"label_key": "ct_amt_4pct_awarded", "amount": 23820954},
            {"label_key": "ct_amt_htcc_awarded", "amount": 9670675},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "lihtc_4pct", "fy2025_units": 1181, "fy2025_amount": 197057571,
             "color_group": "credit",
             # Never appears as a CHFA-carried balance in CT_CHFA_FY2025_ACFR.txt --
             # tax credit equity is investor money passed to developers, same
             # off-balance-sheet logic as IL/PA/FL's LIHTC treatment.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "lihtc_9pct", "fy2025_units": 465, "fy2025_amount": 90558306,
             "color_group": "credit",
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "chfa_taxable_bonds", "fy2025_units": 304, "fy2025_amount": 17709644,
             "color_group": "bond",
             # Note 2 (ACFR p.19/PDF p.21) names the Multifamily Special Obligation
             # Bond and Other Bond Funds ("MFSOB") CHFA is authorized to maintain --
             # this is that CHFA-carried bond financing.
             "fund_type": "proprietary", "fund_name": "Multifamily Special Obligation Bond and Other Bond Funds (MFSOB)",
             "fy2026": _FY26_PENDING},
            {"key": "chfa_tax_exempt_bonds", "fy2025_units": 610, "fy2025_amount": 54678000,
             "color_group": "bond",
             # Note 2 (ACFR p.19/PDF p.21) names the Housing Revenue Bond Fund ("HRB",
             # est. 2023) CHFA is authorized to maintain for exactly this kind of debt.
             "fund_type": "proprietary", "fund_name": "Housing Revenue Bond Fund (HRB) / MFSOB",
             "fy2026": _FY26_PENDING},
            {"key": "chfa_opportunity_fund", "fy2025_units": 522, "fy2025_amount": 7158000,
             "color_group": "trust",
             # Never appears by literal name in CT_CHFA_FY2025_ACFR.txt, but Note 2
             # (ACFR p.19/PDF p.21) states the Authority "has established other funds"
             # beyond those it enumerates, and the fund's own name is CHFA-prefixed
             # (unlike the DOH-branded sources below) -- inferred proprietary,
             # confidence: medium-low.
             "fund_type": "proprietary", "fund_name": "CHFA Opportunity Fund (inferred, not separately named in the ACFR)",
             "fy2026": _FY26_PENDING},
            {"key": "doh_sshp_grant", "fy2025_units": 158, "fy2025_amount": 11678685,
             "color_group": "capital",
             # "SSHP"/"State Sponsored Housing" never appears in CT_CHFA_FY2025_ACFR.txt
             # -- DOH grant money for the State Sponsored Housing Portfolio, CHFA
             # administers but does not carry as its own balance.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "doh_hud_cdbg", "fy2025_units": 158, "fy2025_amount": 4833298,
             "color_group": "capital",
             # "CDBG" never appears in CT_CHFA_FY2025_ACFR.txt -- federal HUD grant
             # money passed through DOH, not a CHFA balance.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "build_for_ct",
        "unit_type": "units",
        "fy2025_actual": 1192,
        "fy2025_source_quote": (
            "\"Appendix D: Build For CT Closings\" (p.39), printed Total row: Total M.I. "
            "Units 362, Total Units 1,192, Funding Provided $41,125,000, across 13 "
            "closings -- independently re-summed from all 13 of the appendix's own rows "
            "and matched exactly on all three totals (see verify_build_for_ct_totals()). "
            "Program description (p.20): \"Build For CT is a Connecticut Department of "
            "Housing (DOH) program administered by [CHFA] that leverages more than $300 "
            "million of State bonding to increase the supply of market rate and "
            "middle-income rental housing.\" Per this build's task brief, Appendix D is "
            "used only for this category-level verification, not exploded into "
            "individual map markers -- this category has no `projects`/map presence."
        ),
        "fy2025_amounts": [
            {"label_key": "ct_amt_build_for_ct_total", "amount": 41125000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "build_for_ct_closings", "fy2025_units": 1192, "fy2025_amount": 41125000,
             "color_group": "bond",
             # Explicitly "State bonding" (Connecticut State Bond Commission), not one
             # of CHFA's own named bond funds (MFSOB/HRB/QECB/Bond Resolution) -- never
             # appears in CT_CHFA_FY2025_ACFR.txt by name (checked "Build For CT" --
             # zero matches), same off-balance-sheet logic as FL's local_bonds.
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "homeownership",
        "unit_type": "households",
        "fy2025_actual": 3788,
        "fy2025_source_quote": (
            "\"Homeownership\" (p.9): \"3,788 Number of Homebuyer First Mortgages\" / "
            "\"$1.063B Total First Mortgages Financed\" -- \"In 2025, CHFA assisted "
            "nearly 3,800 first-time homebuyers... 153 [Connecticut towns]... over 2,700 "
            "homebuyers received forgivable down payment assistance through the "
            "Department of Housing's Time to Own Program... 818 borrowers took advantage "
            "of CHFA's Down Payment Assistance Program (DAP).\" Per p.11: \"In early "
            "2024, CHFA revised its policy to disallow the use of DAP in combination "
            "with the Time To Own (TTO) Program. Borrowers are now limited to selecting "
            "one form of CHFA subordinate financing\" -- DAP and TTO are mutually "
            "exclusive of each other, but their sum (3,502) is intentionally smaller "
            "than the 3,788 first-mortgage headline -- most first mortgages close with "
            "no CHFA/DOH-sourced second-mortgage assistance at all."
        ),
        "fy2025_amounts": [
            {"label_key": "ct_amt_first_mortgages", "amount": 1063000000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "dap", "fy2025_units": 818, "fy2025_amount": 9548887,
             "color_group": "capital",
             # ACFR Note 16 (p.59/PDF p.61) prose: "The Authority manages a Down
             # Payment Assistance Program (DAP)... During 2024, the Authority received
             # $9,000,000 from the State of Connecticut to further capitalize the
             # program" -- CHFA's own managed loan product.
             "fund_type": "proprietary", "fund_name": "Down Payment Assistance Program (DAP), Housing Mortgage General Fund",
             "fy2026": _FY26_PENDING},
            {"key": "tto", "fy2025_units": 2684, "fy2025_amount": 65058000,
             "color_group": "trust",
             # ACFR Note 16 "Grant Programs" activity table (p.60/PDF p.62): "TIME TO
             # OWN $65,058 $65,058" (Program Funding = Program Expenses, $000s) --
             # recognized directly inside CHFA's own Notes to Financial Statements, a
             # DOH-funded pass-through CHFA administers and reports.
             "fund_type": "proprietary", "fund_name": "Time To Own (TTO), Grant Programs (Note 16), DOH-funded pass-through",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# ---------------------------------------------------------------------------
# Multifamily project-level detail ("Appendix C: 2025 Multifamily Initial
# Closings", pp.37-38, incl. its "State Sponsored Housing Portfolio"
# sub-table). Extracted via pdfplumber's column-position-aware
# find_tables()/extract() (not the raw text stream, whose column alignment
# is unreliable for this wide, multi-source table) -- one row per
# development; (name, town, total_units, [funding source keys]).
# ---------------------------------------------------------------------------

RAW_PROJECTS = [
    ("Hartford Trinity Street", "Hartford", 21, ["lihtc_4pct"]),
    ("Northeast Hartford Affordable Housing", "Hartford", 78,
     ["lihtc_4pct", "chfa_tax_exempt_bonds"]),
    ("Enfield Manor & Extension", "Enfield", 99,
     ["lihtc_4pct", "chfa_tax_exempt_bonds"]),
    ("West Hartford Fellowship Housing Redv. Phase II", "West Hartford", 77,
     ["lihtc_9pct", "chfa_taxable_bonds"]),
    ("240 Deming", "South Windsor", 55,
     ["lihtc_9pct", "chfa_taxable_bonds", "chfa_opportunity_fund"]),
    ("The Windward Apartments, Phase II", "Bridgeport", 51,
     ["lihtc_4pct", "chfa_tax_exempt_bonds", "chfa_opportunity_fund"]),
    ("Waltersville Commons", "Bridgeport", 70,
     ["lihtc_4pct", "chfa_tax_exempt_bonds", "chfa_opportunity_fund"]),
    ("Laurel Estates Apartments", "Waterbury", 276, ["lihtc_4pct"]),
    ("Oak Woods Apartments", "Terryville", 47,
     ["lihtc_9pct", "chfa_taxable_bonds", "chfa_opportunity_fund"]),
    ("Parcel B Phase I", "Naugatuck", 60,
     ["lihtc_9pct", "chfa_taxable_bonds", "chfa_opportunity_fund"]),
    ("West Ridge", "New Haven", 65,
     ["lihtc_9pct", "chfa_taxable_bonds", "chfa_opportunity_fund"]),
    ("Brewery Square Apartments", "New Haven", 104, ["lihtc_9pct"]),
    ("10 Liberty", "New Haven", 150,
     ["lihtc_4pct", "chfa_tax_exempt_bonds"]),
    ("2980 State Street", "Hamden", 64,
     ["lihtc_4pct", "chfa_tax_exempt_bonds", "chfa_opportunity_fund"]),
    ("Horizon View", "Montville", 57,
     ["lihtc_9pct", "chfa_opportunity_fund"]),
    ("Rotary Commons", "Stamford", 39,
     ["lihtc_4pct", "chfa_tax_exempt_bonds"]),
    # PDF prints town as "Nowalk" -- corrected to "Norwalk" for
    # geocoding/display accuracy (Fairfield County's well-known city; not a
    # fabrication, a typo fix -- see module docstring).
    ("Meadow Gardens", "Norwalk", 59,
     ["lihtc_4pct", "chfa_tax_exempt_bonds"]),
    ("Augustus Manor", "Stamford", 105, ["lihtc_4pct"]),
    ("Kimberly Place Apartments", "Danbury", 116, ["lihtc_4pct"]),
    ("Leonard Street Apartments", "Norwalk", 53,
     ["lihtc_4pct", "chfa_opportunity_fund"]),
    ("The Rocky Hill Seniors", "Rocky Hill", 40,
     ["doh_hud_cdbg", "doh_sshp_grant"]),
    ("Terry Court", "Windham", 68,
     ["doh_hud_cdbg", "doh_sshp_grant"]),
    ("Father Honan Terrace", "Windham", 50,
     ["doh_hud_cdbg", "doh_sshp_grant"]),
]

# Per-project, per-funding-source dollar amount, transcribed from Appendix
# C's own 4% LIHTC Equity / 9% LIHTC Equity / CHFA Taxable Bonds / CHFA Tax
# Exempt Bonds / CHFA Opportunity Fund columns (top two tables, pp.37-38)
# and the State Sponsored Housing Portfolio sub-table's DOH/HUD CDBG /
# DOH-SSHP Grant columns (bottom of p.38).
PROJECT_SOURCE_AMOUNTS = {
    "Hartford Trinity Street": {"lihtc_4pct": 3614294},
    "Northeast Hartford Affordable Housing": {"lihtc_4pct": 6814573, "chfa_tax_exempt_bonds": 3325000},
    "Enfield Manor & Extension": {"lihtc_4pct": 19757617, "chfa_tax_exempt_bonds": 5210000},
    "West Hartford Fellowship Housing Redv. Phase II": {"lihtc_9pct": 18925107, "chfa_taxable_bonds": 1971150},
    "240 Deming": {"lihtc_9pct": 11768553, "chfa_taxable_bonds": 4730000, "chfa_opportunity_fund": 1000000},
    "The Windward Apartments, Phase II": {"lihtc_4pct": 14122932, "chfa_tax_exempt_bonds": 4362000, "chfa_opportunity_fund": 500000},
    "Waltersville Commons": {"lihtc_4pct": 13953448, "chfa_tax_exempt_bonds": 4725000, "chfa_opportunity_fund": 250000},
    "Laurel Estates Apartments": {"lihtc_4pct": 32712002},
    "Oak Woods Apartments": {"lihtc_9pct": 12571641, "chfa_taxable_bonds": 2400000, "chfa_opportunity_fund": 1000000},
    "Parcel B Phase I": {"lihtc_9pct": 12238776, "chfa_taxable_bonds": 875000, "chfa_opportunity_fund": 1000000},
    "West Ridge": {"lihtc_9pct": 13258666, "chfa_taxable_bonds": 7733494, "chfa_opportunity_fund": 1000000},
    "Brewery Square Apartments": {"lihtc_9pct": 10175448},
    "10 Liberty": {"lihtc_4pct": 29637342, "chfa_tax_exempt_bonds": 16085000},
    "2980 State Street": {"lihtc_4pct": 9523552, "chfa_tax_exempt_bonds": 1127000, "chfa_opportunity_fund": 1000000},
    "Horizon View": {"lihtc_9pct": 11620115, "chfa_opportunity_fund": 1000000},
    "Rotary Commons": {"lihtc_4pct": 8364281, "chfa_tax_exempt_bonds": 4750000},
    "Meadow Gardens": {"lihtc_4pct": 15549297, "chfa_tax_exempt_bonds": 15094000},
    "Augustus Manor": {"lihtc_4pct": 18677360},
    "Kimberly Place Apartments": {"lihtc_4pct": 15805065},
    "Leonard Street Apartments": {"lihtc_4pct": 8525808, "chfa_opportunity_fund": 408000},
    "The Rocky Hill Seniors": {"doh_hud_cdbg": 2000000, "doh_sshp_grant": 3170374},
    "Terry Court": {"doh_hud_cdbg": 1244684, "doh_sshp_grant": 3000000},
    "Father Honan Terrace": {"doh_hud_cdbg": 1588614, "doh_sshp_grant": 5508311},
}

# Independently computed once (via pdfplumber's find_tables()/extract(),
# directly off Appendix C's own table cells, before any manual RAW_PROJECTS
# transcription) sum of each funding-source column -- Appendix C prints no
# Total row of its own, so this stands in as the "PDF-printed total" for
# the double-verification gate (same approach PA's Map Doc build used).
EXPECTED_SOURCE_TOTALS = {
    "lihtc_4pct": 197057571,
    "lihtc_9pct": 90558306,
    "chfa_taxable_bonds": 17709644,
    "chfa_tax_exempt_bonds": 54678000,
    "chfa_opportunity_fund": 7158000,
    "doh_hud_cdbg": 4833298,
    "doh_sshp_grant": 11678685,
}
EXPECTED_TOTAL_UNITS = 1804
EXPECTED_PROJECT_COUNT = 23

# Appendix A: 9% Low-Income Housing Tax Credit Awards (p.34) -- verification
# only, per this build's task brief (not exploded into map markers).
# (development, town, total_units, credits_awarded)
APPENDIX_A_9PCT_AWARDS = [
    ("Oak Park Phase 2", "Stamford", 43, 1290000),
    ("West Hartford Fellowship Housing Redevelopment", "West Hartford", 77, 2170000),
    ("240 Deming", "South Windsor", 55, 1307617),
    ("55 Nye Road", "Glastonbury", 64, 1529500),
    ("The Homes at Avon Park - 9% Component", "Avon", 73, 2100840),
    ("Horizon View", "Montville", 57, 1263056),
    ("66 Union", "New London", 46, 1080000),
    ("Oak Tree Village II", "Griswold", 60, 1440000),
    ("Windsor Locks TOD - Phase 1B/9%", "Windsor Locks", 35, 1460215),
    ("The Judd Homestead at Russo Estates", "Fairfield", 40, 1200000),
]
EXPECTED_9PCT_TOTAL_UNITS = 550
EXPECTED_9PCT_TOTAL_CREDITS = 14841228

# Appendix B: Housing Tax Credit Contribution (HTCC) Awards (pp.35-36) --
# verification only. units=None marks the 2 rows Appendix B itself prints
# with "*" instead of a unit count (statewide loan funds, per the module
# docstring's HTCC note).
APPENDIX_B_HTCC_AWARDS = [
    ("Live Where You Work (Round 18) - Workforce Housing", "Stamford", None, 500000),
    ("24 Berkeley Street", "Norwalk", 5, 500000),
    ("Jefferson Commons", "New London", 12, 470000),
    ("Green Court", "Middletown", 14, 500000),
    ("St. Vincent's Common's", "Middletown", 16, 500000),
    ("20-22 Center St and 57 Belden", "New London", 3, 500000),
    ("Capital for Change Loan Pool", "Various", None, 500000),
    ("Habitat Affordable Homeownership 2025", "Bridgeport", 3, 500000),
    ("New Haven Habitat Homes", "New Haven", 3, 500000),
    ("95 Chestnut Street", "Hartford", 6, 500000),
    ("Scattered Sites - Norwich Apartment Improvement", "Taftville and Norwich", 58, 500000),
    ("Ferry Crossing", "Old Saybrook", 16, 500000),
    ("Martin Luther King Jr. Apartments", "Stamford", 95, 483000),
    ("#2 and #21 Myfield Lane New Preston", "New Preston", 2, 500000),
    ("Scattered Site Affordable Homeownership Development Project", "New Haven & Hamden", 14, 500000),
    ("Residential Rehabilitation and Energy Conservation Project - Phase 3", "New London", 14, 380250),
    ("Lake of Isles", "North Stonington", 3, 403513),
    ("Robin Ridge Apartments", "Waterbury", 144, 433912),
    ("810 Boston Avenue", "Bridgeport", 23, 0),
    ("Cathedral Green", "Hartford", 28, 0),
    ("Village at Park River VI-B", "Hartford", 44, 500000),
    ("Angela Gardens", "Enfield", 45, 500000),
]
EXPECTED_HTCC_TOTAL_UNITS = 548
EXPECTED_HTCC_TOTAL_CREDITS = 9670675

# Appendix D: Build For CT Closings (p.39) -- verification only (see
# Build For CT category's fy2025_source_quote above for why it has no map
# presence). (development, town, mi_units, total_units, funding)
APPENDIX_D_BUILD_FOR_CT = [
    ("Clock Tower Apartments", "Shelton", 20, 100, 2500000),
    ("Luminary at Simsbury Center Apartments", "Simsbury", 36, 175, 4500000),
    ("Village at Saugatuck", "Westport", 78, 157, 6750000),
    ("Stonington Village", "Stonington", 40, 160, 5000000),
    ("Steele Center", "Berlin", 16, 52, 2000000),
    ("Colony Street", "Meriden", 19, 69, 2375000),
    ("203 Amston Road", "Colchester", 12, 30, 1250000),
    ("72 & 78 East Main Street", "Meriden", 15, 46, 1875000),
    ("24 Belden Ave", "Norwalk", 32, 102, 4000000),
    ("106 Simsbury Road", "West Hartford", 22, 108, 2750000),
    ("208 State Street", "New London", 20, 40, 2500000),
    ("The Jayden", "West Hartford", 35, 70, 3500000),
    ("Taunton Woods", "Newtown", 17, 83, 2125000),
]
EXPECTED_BFCT_MI_UNITS = 362
EXPECTED_BFCT_TOTAL_UNITS = 1192
EXPECTED_BFCT_FUNDING = 41125000

FUNDING_COLOR_GROUP = {
    "lihtc_4pct": "credit", "lihtc_9pct": "credit",
    "chfa_taxable_bonds": "bond", "chfa_tax_exempt_bonds": "bond",
    "chfa_opportunity_fund": "trust",
    "doh_sshp_grant": "capital", "doh_hud_cdbg": "capital",
}
# priority order for picking a project's single "primary" color when it has
# multiple funding sources (first match wins) -- LIHTC first since it is
# CHFA's own core allocating-agency program, present on 20 of 23 rows.
FUNDING_PRIORITY = ["lihtc_4pct", "lihtc_9pct", "chfa_tax_exempt_bonds",
                     "chfa_taxable_bonds", "chfa_opportunity_fund",
                     "doh_sshp_grant", "doh_hud_cdbg"]


def verify_multifamily_project_count_and_units():
    errors = []
    if len(RAW_PROJECTS) != EXPECTED_PROJECT_COUNT:
        errors.append(f"project count: expected {EXPECTED_PROJECT_COUNT}, got {len(RAW_PROJECTS)}")
    total_units = sum(units for _n, _t, units, _s in RAW_PROJECTS)
    if total_units != EXPECTED_TOTAL_UNITS:
        errors.append(f"Total Units sum: expected {EXPECTED_TOTAL_UNITS}, got {total_units}")
    if set(PROJECT_SOURCE_AMOUNTS) != {n for n, *_ in RAW_PROJECTS}:
        errors.append("RAW_PROJECTS and PROJECT_SOURCE_AMOUNTS project-name sets differ")
    for name, _town, _units, sources in RAW_PROJECTS:
        amounts = PROJECT_SOURCE_AMOUNTS.get(name, {})
        missing = [s for s in sources if s not in amounts]
        extra = [s for s in amounts if s not in sources]
        if missing:
            errors.append(f"{name!r} is missing amounts for source(s) {missing}")
        if extra:
            errors.append(f"{name!r} has amounts for undeclared source(s) {extra}")
    if errors:
        raise SystemExit("Multifamily project count/unit mismatch(es):\n" + "\n".join(errors))
    print(f"Appendix C: project count ({EXPECTED_PROJECT_COUNT}) and Total Units sum "
          f"({EXPECTED_TOTAL_UNITS}) verified (independently computed column sum -- "
          "Appendix C prints no Total row of its own).")


def verify_multifamily_source_totals():
    sums = {k: 0 for k in EXPECTED_SOURCE_TOTALS}
    for name, _town, _units, sources in RAW_PROJECTS:
        amounts = PROJECT_SOURCE_AMOUNTS.get(name, {})
        for src in sources:
            sums[src] = sums.get(src, 0) + amounts[src]
    errors = []
    for key, expected in EXPECTED_SOURCE_TOTALS.items():
        got = sums.get(key, 0)
        if got != expected:
            errors.append(f"{key} (amount): expected {expected:,}, got {got:,}")
    if errors:
        raise SystemExit("Funding-source amount mismatch(es):\n" + "\n".join(errors))
    print(f"All {len(EXPECTED_SOURCE_TOTALS)} Appendix C funding-source dollar totals "
          "verified against the independently pdfplumber-computed column sums.")


def verify_category_subprogram_totals():
    """Cross-checks the multifamily category's own subprogram fy2025_units/
    fy2025_amount fields (CATEGORIES, hand-entered) against RAW_PROJECTS'
    independently-computed per-source sums -- closing the loop between the
    two data structures, not just RAW_PROJECTS' internal self-consistency.
    """
    units_by_source = {}
    amounts_by_source = {}
    for name, _town, units, sources in RAW_PROJECTS:
        for src in sources:
            units_by_source[src] = units_by_source.get(src, 0) + units
            amounts_by_source[src] = amounts_by_source.get(src, 0) + PROJECT_SOURCE_AMOUNTS[name][src]
    mf_cat = next(c for c in CATEGORIES if c["key"] == "multifamily")
    errors = []
    for sp in mf_cat["subprograms"]:
        key = sp["key"]
        if sp["fy2025_units"] != units_by_source.get(key, 0):
            errors.append(f"{key} fy2025_units: category says {sp['fy2025_units']}, "
                           f"RAW_PROJECTS sums to {units_by_source.get(key, 0)}")
        if sp["fy2025_amount"] != amounts_by_source.get(key, 0):
            errors.append(f"{key} fy2025_amount: category says {sp['fy2025_amount']:,}, "
                           f"RAW_PROJECTS sums to {amounts_by_source.get(key, 0):,}")
    if errors:
        raise SystemExit("Category/RAW_PROJECTS subprogram mismatch(es):\n" + "\n".join(errors))
    print("Multifamily category's 7 subprogram fy2025_units/fy2025_amount fields "
          "verified against RAW_PROJECTS' own independently-computed per-source sums.")


def verify_9pct_awards():
    errors = []
    if len(APPENDIX_A_9PCT_AWARDS) != 10:
        errors.append(f"Appendix A row count: expected 10, got {len(APPENDIX_A_9PCT_AWARDS)}")
    units = sum(u for _n, _t, u, _c in APPENDIX_A_9PCT_AWARDS)
    credits = sum(c for _n, _t, _u, c in APPENDIX_A_9PCT_AWARDS)
    if units != EXPECTED_9PCT_TOTAL_UNITS:
        errors.append(f"Appendix A Total Units: expected {EXPECTED_9PCT_TOTAL_UNITS}, got {units}")
    if credits != EXPECTED_9PCT_TOTAL_CREDITS:
        errors.append(f"Appendix A Credits Awarded: expected {EXPECTED_9PCT_TOTAL_CREDITS:,}, got {credits:,}")
    if errors:
        raise SystemExit("Appendix A (9% LIHTC Awards) mismatch(es):\n" + "\n".join(errors))
    print("Appendix A (9% LIHTC Awards): 10 developments, 550 units, $14,841,228 "
          "verified against the appendix's own printed Total row.")


def verify_htcc_awards():
    errors = []
    if len(APPENDIX_B_HTCC_AWARDS) != 22:
        errors.append(f"Appendix B row count: expected 22, got {len(APPENDIX_B_HTCC_AWARDS)}")
    units = sum(u for _n, _t, u, _c in APPENDIX_B_HTCC_AWARDS if u is not None)
    credits = sum(c for _n, _t, _u, c in APPENDIX_B_HTCC_AWARDS)
    if units != EXPECTED_HTCC_TOTAL_UNITS:
        errors.append(f"Appendix B Total Units: expected {EXPECTED_HTCC_TOTAL_UNITS}, got {units}")
    if credits != EXPECTED_HTCC_TOTAL_CREDITS:
        errors.append(f"Appendix B Credits Awarded: expected {EXPECTED_HTCC_TOTAL_CREDITS:,}, got {credits:,}")
    if errors:
        raise SystemExit("Appendix B (HTCC Awards) mismatch(es):\n" + "\n".join(errors))
    print("Appendix B (HTCC Awards): 22 developments, 548 units, $9,670,675 verified "
          "against the appendix's own printed Total row (2 rows carry the appendix's "
          "own '*' no-unit-count placeholder -- see module docstring's HTCC note on the "
          "narrative's '22 developments + three statewide loan funds' vs. this 22-row "
          "table discrepancy).")


def verify_build_for_ct_totals():
    errors = []
    if len(APPENDIX_D_BUILD_FOR_CT) != 13:
        errors.append(f"Appendix D row count: expected 13, got {len(APPENDIX_D_BUILD_FOR_CT)}")
    mi_units = sum(m for _n, _t, m, _u, _f in APPENDIX_D_BUILD_FOR_CT)
    total_units = sum(u for _n, _t, _m, u, _f in APPENDIX_D_BUILD_FOR_CT)
    funding = sum(f for _n, _t, _m, _u, f in APPENDIX_D_BUILD_FOR_CT)
    if mi_units != EXPECTED_BFCT_MI_UNITS:
        errors.append(f"Appendix D Total M.I. Units: expected {EXPECTED_BFCT_MI_UNITS}, got {mi_units}")
    if total_units != EXPECTED_BFCT_TOTAL_UNITS:
        errors.append(f"Appendix D Total Units: expected {EXPECTED_BFCT_TOTAL_UNITS}, got {total_units}")
    if funding != EXPECTED_BFCT_FUNDING:
        errors.append(f"Appendix D Funding Provided: expected {EXPECTED_BFCT_FUNDING:,}, got {funding:,}")
    if errors:
        raise SystemExit("Appendix D (Build For CT Closings) mismatch(es):\n" + "\n".join(errors))
    print("Appendix D (Build For CT Closings): 13 closings, 362 M.I. units, 1,192 "
          "total units, $41,125,000 verified against the appendix's own printed Total row.")


def slugify(name):
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug


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
    for name, town, units, sources in RAW_PROJECTS:
        query = f"{town}, CT"
        coords = geocode(query, cache)
        status = "city_center" if coords else "unresolved"
        primary = next((s for s in FUNDING_PRIORITY if s in sources), sources[0])
        source_amounts = PROJECT_SOURCE_AMOUNTS.get(name, {})
        projects.append({
            "id": slugify(name),
            "name": name,
            "address": None,
            "city": town,
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
    verify_multifamily_project_count_and_units()
    verify_multifamily_source_totals()
    verify_category_subprogram_totals()
    verify_9pct_awards()
    verify_htcc_awards()
    verify_build_for_ct_totals()
    print("Geocoding project towns via Nominatim (town-center precision)...")
    projects = build_projects()
    unresolved = [p["name"] for p in projects if p["geocode_status"] == "unresolved"]
    if unresolved:
        print(f"  {len(unresolved)} project(s) could not be geocoded: {unresolved}")
    unique_towns = len({p["city"] for p in projects})
    print(f"  {len(projects)} projects across {unique_towns} unique towns.")

    payload = {
        "CT": {
            "hfa_name": "Connecticut Housing Finance Authority",
            "hfa_abbr": "CHFA",
            "fiscal_year": "CY2025",
            "source_title": "CHFA 2025 Annual Report (calendar-year reporting period)",
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
