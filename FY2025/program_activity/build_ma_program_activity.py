"""
Builds docs/ma_program_activity.json from MassHousing's (Massachusetts Housing
Finance Agency) FY2025 Annual Disclosure Report.

Source
------------------------------------------------------------------------
"Massachusetts Housing Finance Agency Annual Disclosure Report, For the
Fiscal Year Ended June 30, 2025" (a continuing-disclosure document filed
under SEC Rule 15c2-12), specifically its Exhibit B, "Annual Report of
MassHousing for the Fiscal Year Ended June 30, 2025" -- Chair/CEO message
plus MassHousing's own audited FY2025 financial statements:
    https://www.masshousing.com/-/media/Files/Financials/Annual-Disclosure-Report.pdf
Local copy: FY2025/program_activity/pdf/MA_MassHousing_AnnualDisclosureReport_FY2025.pdf
(re-downloaded and re-verified live on 2026-08-13: HTTP 200, 582 pages,
first page still reads "ANNUAL DISCLOSURE REPORT For the Fiscal Year Ended
June 30, 2025" -- URL from the FY2025 task briefing is current, no dead
link). pypdf DOES extract this PDF's text successfully page-by-page when
read directly (contrary to an earlier note that generic web-scraping
tooling could not get text out of it -- likely that note reflects a
WebFetch/plain-HTML-fetch attempt against the PDF rather than a proper PDF
text-extraction library); a local library was used regardless, per the
task briefing's instruction, and the resulting text matches this
project's already-checked-in FY2025/txt/MA_MassHousing_FY2025_ACFR.txt
byte-for-byte on every spot-checked passage.

IMPORTANT data-provenance note on the checked-in "ACFR" text
------------------------------------------------------------------------
FY2025/txt/MA_MassHousing_FY2025_ACFR.txt is NOT a standalone ACFR-style
document -- its own title page reads "MASSACHUSETTS HOUSING FINANCE AGENCY
ANNUAL DISCLOSURE REPORT For the Fiscal Year Ended June 30, 2025", and it
is in fact the exact same 582-page continuing-disclosure filing named
above (confirmed matching by direct byte comparison against a fresh
download of the live PDF, see above). It bundles several exhibits into one
file, of which Exhibit B, "Annual Report of MassHousing for the Fiscal
Year Ended June 30, 2025" (this build's category headline quotes, at
lines 97-99 of the .txt) is immediately followed, still inside Exhibit B,
by MassHousing's own "FINANCIAL STATEMENTS, REQUIRED SUPPLEMENTARY
INFORMATION, SCHEDULES AND SUPPLEMENTAL SCHEDULES JUNE 30, 2025 AND 2024"
-- i.e. this one file legitimately serves both purposes the task briefing
worried might be conflated (the activity-narrative "Annual Report" AND the
audited financial statements), because MassHousing's own filing bundles
them together in a single continuing-disclosure PDF rather than issuing
them as two separate documents the way most other states' HFAs do. This
was verified, not assumed: "Report of Independent Auditors" (PwC opinion,
line 157), "MANAGEMENT'S DISCUSSION AND ANALYSIS", "Statements of Net
Position", and "NOTES TO FINANCIAL STATEMENTS" all appear later in the
same file, under the same MassHousing entity heading, with no discretely-
presented other-agency component-unit summary anywhere -- so, unlike PA's
FY2025/txt mismatch, no substitution was needed here.

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
The independent auditors' opinion (Report of Independent Auditors, .txt
line 160) covers "the business-type activities and fiduciary fund
information of Massachusetts Housing Finance Agency and its affiliates" --
i.e., like Florida Housing (a single enterprise fund) and unlike IHDA (7
major governmental + 4 major proprietary + 14 nonmajor governmental
funds), MassHousing has NO governmental funds at all; it reports only
business-type activities plus two unrelated fiduciary trusts (OPEB and
Employees' Retirement System, neither a housing program). Internally,
Note A/B describe MassHousing's business-type activities as composed of
several named bond programs and a Working Capital Fund (WCF), each with
its own detailed schedule in "Supplemental Schedule 5" (.txt line
1303-1305: "Detailed financial information for each individual bond
program is presented in accompanying Supplemental Schedule 5"). Both
categories below are "proprietary" (carried inside MassHousing's own
business-type bond programs), not "off_balance_sheet":
  - multifamily_total -- the Chair's letter's "$310.9 million in
    financing" for "close to 1,400 rental homes" describes MassHousing's
    "Multifamily business line", which its own Note A(c) "Housing Bond
    Program" describes as financing "various loans and loan
    participations for multifamily residential ... properties" (.txt
    lines 1269-1273), and Exhibit D is separately captioned "Most Recent
    Rental Development Program Official Statement" (.txt line 10) -- i.e.
    this is MassHousing's own Rental Development / Housing Bond business-
    type program, not a pass-through. Confidence: high.
  - homeownership_total -- the press release's "$659.4 million in
    mortgage financing loans" to "1,893 Massachusetts homebuyers" matches
    MassHousing's own Note A(3) "Single-Family Housing Bond Programs"
    (SFHRB and RMRB, .txt lines 1275-1293), which finance "the purchase of
    single-family loans ... from participating lenders" -- MassHousing's
    own bond-financed first-mortgage business, not a pass-through.
    Confidence: high.
No "off_balance_sheet" or "governmental" subprogram appears in this file
because MassHousing's FY2025 Annual Disclosure Report and its own
financial statements do not disclose enough sub-source detail (e.g. a
per-program dollar/unit breakdown of the 1,400 rental homes or 1,893
homebuyers) for this script to identify anything sitting outside
MassHousing's own balance sheet, as PA's PHARE/PHFA-external LIHTC
allocations or FL's SHIP local-government pass-through were shown to be.

Why RAW_PROJECTS is empty ([]) -- MA has no usable project-level list
------------------------------------------------------------------------
Unlike IL/PA/OH/FL/WA/TX, MassHousing does not publish a single unified,
per-fiscal-year activity report with a named-development table (no "Report
of Activities", no per-county award table, no per-development LIHTC/award
list). Three channels were checked and all three were ruled out, per the
task briefing's explicit instruction not to fabricate a project list to
fill this gap:
  1. The FY2025 Annual Disclosure Report itself (the source of this
     script's category headlines) contains only two kinds of tabular
     detail: (a) bond-CUSIP/pricing schedules (Exhibits A, F, G -- not
     housing projects at all) and (b) "SUPPLEMENTAL SCHEDULE 1: MORTGAGE /
     CONSTRUCTION LOAN OBLIGATIONS AND COMMITMENTS" and the "RENTAL
     DEVELOPMENT MORTGAGE LOANS" schedule (.txt lines 19350+), which is an
     alphabetically-sorted list of MassHousing's ENTIRE outstanding
     rental-loan portfolio as of 06/30/2025 (the same population behind
     the Chair letter's separate "we serviced over 1,800 loans ...
     outstanding balance of $7.6 billion" sentence) -- a STOCK, not this
     year's FLOW. Its "Initial Loan Close Date" column runs across
     decades (spot-checked rows show 1972, 1995, 2008, 2012, 2013, 2022,
     etc.), so it cannot be filtered down to "developments newly financed
     or preserved in FY2025" without an unreliable, undocumented
     assumption about which closings this year's ~1,400-unit/$310.9M
     figure actually refers to (new construction vs. refinance/
     preservation of an old loan vs. an old loan that happens to have a
     FY2025 transaction of some other kind) -- exactly the kind of
     invented linkage this project's methodology prohibits. No comparable
     "new activity this fiscal year only" schedule exists in the document.
  2. The "MassHousing Impact Framework" PDF
     (https://www.masshousing.com/-/media/Files/Financials/MassHousing-Impact-Framework.pdf,
     checked live 2026-08-13) is confirmed to be a blank reporting-format
     specification -- it defines the *columns* a future "Sustainability
     Bonds Annual Report" / "Social Bonds Annual Report" would use
     (Project Name, Address, Total Development Cost, Loan Amount, Unit
     Set-Aside) but contains no populated project rows itself.
  3. The actual populated versions of those Sustainability/Social Bonds
     Annual Reports are filed per-bond-series on EMMA (emma.msrb.org), not
     centrally on MassHousing's own site or search-indexed anywhere; per a
     web search of MassHousing's EMMA-filed sustainability/social bond
     disclosures, reaching a usable list would require navigating EMMA's
     issuer-by-issuer, filing-by-filing interface by hand and would still
     only cover the subset of developments financed by bonds specifically
     tagged ESG/Sustainability/Social that fiscal year -- not the
     Multifamily business line's full ~1,400-unit total -- so even a
     completed EMMA pull would not reconcile with this script's own
     category headline. Per the task briefing's explicit guidance to
     abandon the project-level layer rather than force a partial, non-
     reconciling result, this path was not pursued further.
RAW_PROJECTS is therefore [] and the `projects` array in the output JSON
is empty -- an honest reflection of what MassHousing discloses, not a
placeholder for missing work. The frontend (docs/program_activity.js)
already handles this: the KPI cards render normally and the bubble map
renders with 0 markers ("0 projects" in its own count legend).

fy2026
------------------------------------------------------------------------
The Annual Disclosure Report is a backward-looking continuing-disclosure
filing with no forward-looking/projected-activity section (unlike IHDA's
Report of Activities) -- every fy2026 field below is {value: None,
amount: None, closed: False, note_key: "maFy26NotePending"}.
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "ma_program_activity.json"

SOURCE_URL = "https://www.masshousing.com/-/media/Files/Financials/Annual-Disclosure-Report.pdf"
SOURCE_FILE = "MA_MassHousing_AnnualDisclosureReport_FY2025.pdf"
RETRIEVED = "2026-08-13"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                  "note_key": "maFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data. Only two categories are supported by MassHousing's
# FY2025 Annual Disclosure Report -- see module docstring for why no third
# category (e.g. a repair/counseling or COVID-emergency program) is added:
# none is disclosed with a comparable FY2025 headline figure anywhere in the
# source document.
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "multifamily_rental",
        "unit_type": "units",
        "fy2025_actual": 1400,
        "fy2025_source_quote": (
            "\"Our Multifamily business line supported the creation or preservation of "
            "close to 1,400 rental homes, with $310.9 million in financing. At the close "
            "of FY25, we serviced over 1,800 loans with an outstanding balance of $7.6 "
            "billion.\" (Message from the Chair and Chief Executive Officer, MassHousing "
            "FY2025 Annual Disclosure Report, Exhibit B). \"Close to 1,400\" is "
            "MassHousing's own approximate phrasing -- not an exact count -- and is used "
            "as-is, not rounded or adjusted further. The \"1,800 loans / $7.6 billion\" "
            "figure is MassHousing's entire serviced loan portfolio outstanding as of "
            "06/30/2025 (a stock), not this year's new/preserved activity (a flow); it is "
            "shown here only as context and is not used as this category's own KPI number."
        ),
        "fy2025_amounts": [
            {"label_key": "ma_amt_multifamily_financing", "amount": 310900000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "multifamily_total", "fy2025_units": 1400, "fy2025_amount": 310900000,
             "color_group": "capital",
             # MassHousing's own Note A(c) "Housing Bond Program" (financing
             # "various loans and loan participations for multifamily
             # residential ... properties") and Exhibit D's "Rental
             # Development Program Official Statement" -- MassHousing's own
             # business-type bond program, not a pass-through.
             "fund_type": "proprietary",
             "fund_name": "Rental Development / Housing Bond Program (business-type activities)",
             "fy2026": _FY26_PENDING},
        ],
    },
    {
        "key": "homeownership_loans",
        "unit_type": "households",
        "fy2025_actual": 1893,
        "fy2025_source_quote": (
            "\"In Fiscal 2025, MassHousing helped 1,893 Massachusetts homebuyers buy a "
            "home, of whom 73 percent earned less than 100 percent of their Area Median "
            "Income, 54 percent were buyers of color and 51 percent of the loans were "
            "made in Gateway Cities ... In FY 25, through all its partner lenders, "
            "MassHousing provided a total of $659.4 million in mortgage financing loans "
            "... in 299 of the 351 cities and towns ... 89 percent of loans had down "
            "payment assistance attached.\" (\"MassHousing Announces Fiscal Year 2025 Top "
            "Partner Lenders\", MassHousing press release, July 17, 2025). This figure "
            "differs from the Annual Disclosure Report's own Chair's-letter figure of "
            "\"$608.7 million in first mortgage financing to help over 2,500 people buy a "
            "home\" -- the two MassHousing publications do not reconcile with each other "
            "and neither document explains the gap (likely a different counting "
            "methodology or as-of date between the two releases). This script uses the "
            "press release's figures because only they include the AMI/buyers-of-color/"
            "Gateway-Cities/down-payment-assistance breakdown; the discrepancy is flagged "
            "here rather than silently picking one number."
        ),
        "fy2025_amounts": [
            {"label_key": "ma_amt_mortgage_financing", "amount": 659400000},
        ],
        "additive": True,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "homeownership_total", "fy2025_units": 1893, "fy2025_amount": 659400000,
             "color_group": "bond",
             # MassHousing's own Note A(3) "Single-Family Housing Bond
             # Programs" (SFHRB + RMRB) -- MassHousing's own bond-financed
             # first-mortgage business, not a pass-through.
             "fund_type": "proprietary",
             "fund_name": "Single-Family Housing Bond Programs (SFHRB/RMRB, business-type activities)",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# No per-development list is available -- see module docstring. This is the
# allowed, honest outcome (not a placeholder for missing work): the frontend
# renders the bubble map with 0 markers when this is empty.
RAW_PROJECTS = []


def verify_category_consistency():
    """Sanity gate: each category's single subprogram must exactly equal
    that category's own headline (since additive=True with one subprogram
    is only meaningful if the subprogram *is* the headline, not a subset of
    it)."""
    errors = []
    for cat in CATEGORIES:
        subs = cat["subprograms"]
        if len(subs) != 1:
            errors.append(f"{cat['key']}: expected exactly 1 subprogram, got {len(subs)}")
            continue
        sp = subs[0]
        if sp["fy2025_units"] != cat["fy2025_actual"]:
            errors.append(
                f"{cat['key']}: subprogram units {sp['fy2025_units']} != "
                f"category fy2025_actual {cat['fy2025_actual']}"
            )
        cat_amt = cat["fy2025_amounts"][0]["amount"] if cat["fy2025_amounts"] else None
        if cat_amt is not None and sp["fy2025_amount"] != cat_amt:
            errors.append(
                f"{cat['key']}: subprogram amount {sp['fy2025_amount']} != "
                f"category fy2025_amounts[0].amount {cat_amt}"
            )
    if RAW_PROJECTS:
        errors.append(
            "RAW_PROJECTS is expected to be empty for MA -- see module docstring; "
            "if project-level data has since become available, update the docstring "
            "before populating this list."
        )
    if errors:
        raise SystemExit("Category consistency mismatch(es):\n" + "\n".join(errors))
    print("Category headline vs. subprogram consistency verified for both categories "
          "(multifamily_rental: 1,400 units / $310,900,000; homeownership_loans: "
          "1,893 households / $659,400,000); RAW_PROJECTS confirmed empty as expected.")


def main():
    verify_category_consistency()
    payload = {
        "MA": {
            "hfa_name": "MassHousing",
            "hfa_abbr": "MassHousing",
            "fiscal_year": "FY2025",
            "source_title": "MassHousing Annual Disclosure Report for Fiscal Year 2025 (Exhibit B: Annual Report of MassHousing)",
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
