"""
Builds docs/ar_program_activity.json from the Arkansas Development Finance
Authority's (ADFA) own "2025 Affordable Housing Tax Credit Developments"
announcement -- a single-category (multifamily 9% LIHTC) award round with a
complete 10-development awardee list -- plus ADFA's FY2025 audited combined
financial statements (used ONLY for GASB fund-type classification).

Source
------------------------------------------------------------------------
1. "Arkansas Development Finance Authority Announces 2025 Affordable Housing
   Tax Credit Developments" (web page, published July 30, 2025 -- the
   "datePublished" metadata in the page's own JSON-LD):
     https://adfa.arkansas.gov/arkansas-development-finance-authority-announces-2025-affordable-housing-tax-credit-developments/
   Local copy: FY2025/program_activity/pdf/AR_ADFA_LIHTC_2025_announcement.html
2. ADFA's own separately-issued FY2025 audited combined financial statements
   (used ONLY for fund-type classification):
     FY2025/txt/AR_ADFA_FY2025_ACFR.txt

Data-provenance check on the checked-in ACFR text
------------------------------------------------------------------------
FY2025/txt/AR_ADFA_FY2025_ACFR.txt WAS verified to be ADFA's own financial
statements before use (unlike the PA build earlier in this pilot series,
which caught its checked-in .txt pointing at the wrong, Commonwealth-wide
document). The AR file's title page reads "ARKANSAS DEVELOPMENT FINANCE
AUTHORITY, A COMPONENT UNIT OF THE STATE OF ARKANSAS, June 30, 2025,
Combined Financial Statements", the auditor's report covers "the combined
financial statements of the business-type activities ... of the Arkansas
Development Finance Authority", and the transmittal date is December 8, 2025
-- i.e. this is the correctly-scoped ADFA document. No substitution was
needed; no wrong-report problem here.

Fiscal-year vs. award-round naming
------------------------------------------------------------------------
The source is a CALENDAR-YEAR award announcement: "2025" names ADFA's 2025
9% LIHTC competitive round, published July 30, 2025. ADFA's own fiscal year
ends June 30 (per the ACFR's "June 30, 2025" title), so a strict Jul-Jun
reading would place this July-30 announcement inside ADFA's FY2026. This
build follows the task brief's own labeling ("fiscal_year": "FY2025") for the
2025 award round, but that timing nuance is recorded here rather than
silently assumed -- same title-year-vs-content-year discipline this pilot
series has applied throughout.

Fund-type classification (fund_type/fund_name on each subprogram)
------------------------------------------------------------------------
ADFA's own ACFR reports ONLY business-type activities (proprietary,
enterprise-style) -- the auditor's opinion covers "the combined financial
statements of the business-type activities and the aggregate discretely
presented component unit of the Arkansas Development Finance Authority".
There are no GASB governmental funds anywhere; the MD&A names nine internal
programs presented as supplementary information: Single Family Housing
Programs, Federal Housing Programs, Multi-Family Programs, Economic
Development Bond Guaranty Program, State Facilities and Amendment 82
Programs, Other Economic Development Programs, Tobacco Settlement Revenue
Bonds Program, Student Loan Programs, and General Fund Program. Within
"Federal Housing Programs", Note-level program descriptions name the two
federal programs relevant here:
  - "HOME Investment Partnerships Program -- Accounts for federal financial
    assistance received from [HUD] for the purpose of developing and
    supporting affordable housing through tenant based rental assistance,
    rental rehabilitation, new construction, or assistance to homebuyers and
    homeowners." The SEFA (Schedule of Expenditures of Federal Awards)
    reports HOME (FAL 14.239) loans with an outstanding receivable of
    $138,155,098 at June 30, 2025 -- i.e. HOME funds sit directly on ADFA's
    own balance sheet.
  - "National Housing Trust Fund Program -- Accounts for federal financial
    assistance received from HUD for the purpose of expanding and preserving
    the supply of affordable housing, particularly rental housing, for
    extremely low-income to very low income households." The SEFA reports
    Housing Trust Fund (FAL 14.275) federal expenditures of $4,153,721.
  - "proprietary" (inside ADFA's own business-type activities):
      * home -- the HOME Investment Partnerships Program, named verbatim as
        an ADFA-accounted Federal Housing Program with a $138M loan
        receivable on its own books. Confidence: high.
      * nhtf -- the National Housing Trust Fund Program, likewise named as
        an ADFA-accounted Federal Housing Program. Note this differs from
        PA's build, where NHTF was off_balance_sheet because PHFA's own
        statements never mention it; ADFA's statements explicitly do, so
        NHTF is carried on ADFA's own books here. Confidence: high.
  - "off_balance_sheet":
      * lihtc -- the 9% federal Low-Income Housing Tax Credit is allocated
        directly to developers/investors and never booked as an ADFA asset.
        The ACFR's only "low-income housing tax credit" mention is inside
        the Tax Credit Assistance Program (TCAP) description, as an
        eligibility condition ("developments that were awarded low-income
        housing tax credits under Section 42(h)"), not as an ADFA-carried
        balance. Same off-balance-sheet logic as every other state's
        9%/4% HTC subprograms in this pilot series. Confidence: high.

Category-level methodology
------------------------------------------------------------------------
This is a SINGLE-category state (the task brief is explicit: one multifamily
LIHTC KPI card + bubble map; no second category is invented to pad the
module). The one category, multifamily_lihtc, is the 2025 9% LIHTC round.

TWO honest-labeling requirements drive the numbers below:

(1) LIHTC is a 10-YEAR credit, and the source mixes the two bases. The
announcement's own headline ("$104,962,000 in federal 9% Low-Income Housing
Tax Credits") is the 10-YEAR TOTAL, while its per-development list prints the
ANNUAL "LIHTC (Federal)" credit. The two reconcile exactly: the 10 per-
project annual credits sum to $10,496,200, and $10,496,200 x 10 =
$104,962,000. This script therefore keeps the per-project source_amounts in
the source's own annual terms (what the list literally prints) while the
category's LIHTC chip and the lihtc subprogram amount use the source's own
10-year headline -- flagged in the docstring, the fy2025_source_quote, AND
the i18n label text ("10-year total"), per the build brief's instruction that
"$104.96M is the 10-year total, not a single-year figure."

(2) The headline's unit count does NOT reconcile with the list. The headline
reads "support the development of 524 affordable rental units," but the
awardee list's own "Total Units" column sums to 527 (60+60+60+62+18+61+60
+46+60+40). Unlike PA's Map Doc -- which prints two explicit unit columns
(LI Units vs. Total Units) whose 46-unit gap is a real affordable-vs-total
split -- ADFA prints only one "Total Units" column and never explains the
3-unit gap against its own 524 headline. Both figures are reproduced
verbatim: fy2025_actual uses the headline 524 (the source's own KPI and the
figure the task brief specifies), while the lihtc subprogram's fy2025_units
uses the list's own 527 column sum (the physical total of the 10 awarded
developments), and the discrepancy is asserted, not silently resolved.

HOME and NHTF are additional subsidy sources layered onto a SUBSET of the 10
LIHTC projects (6 and 5 projects respectively, all of which also receive
LIHTC), so the category is non-additive (additive=False) -- a naive sum of
the three subprogram unit counts (527+285+245=1,057) would grossly overcount
physical units, the same reasoning as PA's and IHDA's multifamily categories.
Neither HOME nor NHTF is stated as a headline total in the source; each is
this script's own column sum ($10,652,209 and $3,428,631), asserted once in
verify_totals() against independently-transcribed constants. Summed per-
project Total Development Cost is $108,372,137, consistent with the
headline's "approximate total development cost $110 million" (used only as a
verification check -- Total Development Cost includes private equity/debt
and is not a funding-source amount, so it is not surfaced in the JSON).

fy2026
------------------------------------------------------------------------
The announcement is a single award-round notice with no forward-looking/
projected-activity figure anywhere (unlike IHDA's Report of Activities), so
every fy2026 field below is {value: None, amount: None, closed: False,
note_key: "arFy26NotePending"} -- nothing is invented.

Geocoding
------------------------------------------------------------------------
The awardee list gives City + County but no street address for any of the 10
developments, so -- like WSHFC's 9% Allocation List -- every project is
geocoded to city precision: primary query "{City}, {County} County, AR",
falling back to "{City}, AR", with geocode_status uniformly recorded as
"city_center" (this state's best available precision; "ok" is reserved for a
resolved street address). Self-throttled to <=1 request/second with an
identifying User-Agent per Nominatim's usage policy.

Rate-limit resilience: at build time (2026-08-16) Nominatim was returning
HTTP 429 for this environment's IP (a temporary block), so the script carries
a deterministic CITY_COORDS fallback keyed by city. These are the
city-center coordinates served by OpenStreetMap's place nodes (retrieved via
the Photon geocoder, which serves the same OSM data Nominatim does), so they
are the identical-provenance values Nominatim itself would return for these
8 well-known Arkansas municipalities -- not fabricated locations. geocode()
still attempts Nominatim first (per this project's spec); the fallback is
used only when that lookup fails, and the resulting geocode_status stays
"city_center" either way. Because the fallback is a fixed table, a re-run is
byte-identical regardless of Nominatim's availability.
"""

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "ar_program_activity.json"

SOURCE_URL = ("https://adfa.arkansas.gov/arkansas-development-finance-authority-"
              "announces-2025-affordable-housing-tax-credit-developments/")
SOURCE_FILE = "AR_ADFA_LIHTC_2025_announcement.html"
RETRIEVED = "2026-08-16"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
GEOCODER_USER_AGENT = "us-hfa-data-map/1.0 (github.com/MD-ai-fin/us-hfa-data-map)"

_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                 "note_key": "arFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "multifamily_lihtc",
        "unit_type": "units",
        "fy2025_actual": 524,  # headline "524 affordable rental units" (list sums to 527 -- see docstring)
        "fy2025_source_quote": (
            "\"LITTLE ROCK, Ark. — The Arkansas Development Finance Authority "
            "announced today that it will award $104,962,000 in federal 9% Low-Income "
            "Housing Tax Credits (LIHTC) to 10 multifamily housing developments across "
            "Arkansas. The 2025 awards are expected to generate about $84.5 million in "
            "equity from private investors and support the development of 524 affordable "
            "rental units. Approximate total development cost is $110 million.\" (ADFA "
            "\"2025 Affordable Housing Tax Credit Developments\" announcement, July 30, "
            "2025). The $104,962,000 LIHTC figure is a 10-YEAR TOTAL: the announcement's "
            "own per-development list prints ANNUAL \"LIHTC (Federal)\" credits that sum "
            "to $10,496,200, which is exactly $104,962,000 ÷ 10. The list (\"2025 "
            "Arkansas Low-Income Housing Tax Credit Awardees\") has 10 rows; its own "
            "\"Total Units\" column sums to 527, which does NOT reconcile with the "
            "headline's \"524 affordable rental units\" (a 3-unit discrepancy the source "
            "never explains -- both figures reproduced verbatim, neither adjusted). "
            "Summed per-project HOME = $10,652,209 and NHTF = $3,428,631 (neither stated "
            "as a headline total, so each is this script's own column sum). Summed "
            "per-project Total Development Cost = $108,372,137, consistent with the "
            "headline's \"approximate total development cost $110 million.\""
        ),
        "fy2025_amounts": [
            {"label_key": "ar_amt_lihtc", "amount": 104962000},   # 10-year total (annual sum = 10,496,200)
            {"label_key": "ar_amt_home", "amount": 10652209},
            {"label_key": "ar_amt_nhtf", "amount": 3428631},
        ],
        "additive": False,
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "lihtc", "fy2025_units": 527, "fy2025_amount": 104962000,
             "color_group": "credit",
             # 9% federal tax credits are allocated directly to
             # developers/investors, never booked as an ADFA asset. The ACFR's
             # only "low-income housing tax credit" mention is inside the TCAP
             # description as an eligibility condition, not as an
             # ADFA-carried balance. The 104,962,000 amount is the source's
             # own 10-year headline; per-project annual credits sum to
             # 10,496,200 (see docstring).
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
            {"key": "home", "fy2025_units": 285, "fy2025_amount": 10652209,
             "color_group": "capital",
             # ACFR "Federal Housing Programs -- HOME Investment Partnerships
             # Program ... Accounts for federal financial assistance received
             # from HUD"; SEFA reports a $138,155,098 HOME loan receivable at
             # June 30, 2025 -- carried on ADFA's own business-type books.
             "fund_type": "proprietary",
             "fund_name": "Federal Housing Programs (HOME Investment Partnerships Program)",
             "fy2026": _FY26_PENDING},
            {"key": "nhtf", "fy2025_units": 245, "fy2025_amount": 3428631,
             "color_group": "trust",
             # ACFR "Federal Housing Programs -- National Housing Trust Fund
             # Program ... Accounts for federal financial assistance received
             # from HUD" -- named as an ADFA-accounted federal program (unlike
             # PA, where NHTF never appears in the HFA's own statements).
             "fund_type": "proprietary",
             "fund_name": "Federal Housing Programs (National Housing Trust Fund Program)",
             "fy2026": _FY26_PENDING},
        ],
    },
]

# ---------------------------------------------------------------------------
# Multifamily project-level detail ("2025 Arkansas Low-Income Housing Tax
# Credit Awardees" list -- all 10 awarded developments). Manually transcribed
# from the announcement page's per-development blocks; "units" uses the
# list's own "Total Units" column. The source gives City + County but no
# street address, so every project is geocoded to city-center precision.
# (name, city, county, total_units, [funding source keys])
# ---------------------------------------------------------------------------

RAW_PROJECTS = [
    ("Avalon at Clarksville", "Clarksville", "Johnson", 60, ["lihtc"]),
    ("Avalon at Hope", "Hope", "Hempstead", 60, ["lihtc"]),
    ("Enclave Estates at Batesville", "Batesville", "Independence", 60, ["lihtc"]),
    ("Homes at Willow Bend", "Fayetteville", "Washington", 62, ["lihtc"]),
    ("Mount Ida Housing", "Mount Ida", "Montgomery", 18, ["lihtc", "home", "nhtf"]),
    ("Pine Ridge Place", "Little Rock", "Pulaski", 61, ["lihtc", "home", "nhtf"]),
    ("Timber Ridge", "Sheridan", "Grant", 60, ["lihtc", "home", "nhtf"]),
    ("Villas at Spring Valley (Senior)", "Cabot", "Lonoke", 46, ["lihtc", "home", "nhtf"]),
    ("Waystone Batesville Family", "Batesville", "Independence", 60, ["lihtc", "home", "nhtf"]),
    ("Waystone Batesville Senior", "Batesville", "Independence", 40, ["lihtc", "home"]),
]

# Per-project, per-funding-source dollar amount, transcribed from the
# announcement's own "LIHTC (Federal)"/"HOME Funds"/"NHTF Funds" lines. NOTE:
# the lihtc values are the ANNUAL credit amount as printed in the per-
# development list (their 10-year value is each x10; the category's lihtc
# subprogram/chip uses the source's own 10-year headline, see docstring).
PROJECT_SOURCE_AMOUNTS = {
    "Avalon at Clarksville": {"lihtc": 1221000},
    "Avalon at Hope": {"lihtc": 1221000},
    "Enclave Estates at Batesville": {"lihtc": 1221000},
    "Homes at Willow Bend": {"lihtc": 1193500},
    "Mount Ida Housing": {"lihtc": 360800, "home": 1125000, "nhtf": 940000},
    "Pine Ridge Place": {"lihtc": 1235300, "home": 2000000, "nhtf": 466486},
    "Timber Ridge": {"lihtc": 1201200, "home": 1720000, "nhtf": 1000000},
    "Villas at Spring Valley (Senior)": {"lihtc": 884400, "home": 2000000, "nhtf": 642645},
    "Waystone Batesville Family": {"lihtc": 1188000, "home": 2114431, "nhtf": 379500},
    "Waystone Batesville Senior": {"lihtc": 770000, "home": 1692778},
}

# Per-project "Total Development Cost" (the full development budget, including
# private equity/debt) -- transcribed from the list but used ONLY for the
# internal "reproduce the ~$110M headline" verification; it is not a funding
# source and is not surfaced in the output JSON.
TOTAL_DEV_COST = {
    "Avalon at Clarksville": 11976435,
    "Avalon at Hope": 11953761,
    "Enclave Estates at Batesville": 11956054,
    "Homes at Willow Bend": 12399999,
    "Mount Ida Housing": 5237691,
    "Pine Ridge Place": 12594933,
    "Timber Ridge": 12506556,
    "Villas at Spring Valley (Senior)": 9894000,
    "Waystone Batesville Family": 11999930,
    "Waystone Batesville Senior": 7852778,
}

EXPECTED_PROJECT_COUNT = 10
EXPECTED_HEADLINE_UNITS = 524       # headline "524 affordable rental units"
EXPECTED_TOTAL_UNITS = 527          # list "Total Units" column sum (does NOT reconcile with 524)
EXPECTED_LIHTC_ANNUAL = 10496200    # sum of per-project ANNUAL LIHTC credits
EXPECTED_LIHTC_10YR = 104962000     # source's own 10-year headline = annual x 10
EXPECTED_HOME_TOTAL = 10652209
EXPECTED_NHTF_TOTAL = 3428631
EXPECTED_TOTAL_DEV_COST = 108372137

FUNDING_COLOR_GROUP = {
    "lihtc": "credit", "home": "capital", "nhtf": "trust",
}
# LIHTC first: it is the universal anchor credit present on all 10 awards.
FUNDING_PRIORITY = ["lihtc", "home", "nhtf"]

# Deterministic city-center fallback coordinates (lat, lon), sourced from
# OpenStreetMap place nodes via the Photon geocoder -- the same OSM data
# Nominatim serves. Used only when the live Nominatim lookup fails (e.g. the
# HTTP 429 block seen at build time); see the docstring's "Rate-limit
# resilience" note. geocode_status stays "city_center" either way.
CITY_COORDS = {
    "Clarksville": (35.47131, -93.46648),
    "Hope": (33.66706, -93.59157),
    "Batesville": (35.77081, -91.65311),
    "Fayetteville": (36.06258, -94.15743),
    "Mount Ida": (34.55762, -93.63264),
    "Little Rock": (34.74651, -92.28963),
    "Sheridan": (34.31010, -92.40135),
    "Cabot": (34.97453, -92.01653),
}


def verify_totals():
    errors = []
    if len(RAW_PROJECTS) != EXPECTED_PROJECT_COUNT:
        errors.append(f"project count: expected {EXPECTED_PROJECT_COUNT}, got {len(RAW_PROJECTS)}")
    names = [r[0] for r in RAW_PROJECTS]
    if len(set(names)) != len(names):
        errors.append("duplicate project name(s) in RAW_PROJECTS")
    if set(names) != set(PROJECT_SOURCE_AMOUNTS):
        errors.append("RAW_PROJECTS and PROJECT_SOURCE_AMOUNTS project-name sets differ")
    if set(names) != set(TOTAL_DEV_COST):
        errors.append("RAW_PROJECTS and TOTAL_DEV_COST project-name sets differ")
    for name, _city, _county, _units, sources in RAW_PROJECTS:
        amounts = PROJECT_SOURCE_AMOUNTS.get(name, {})
        missing = [s for s in sources if s not in amounts]
        extra = [s for s in amounts if s not in sources]
        if missing:
            errors.append(f"{name!r} is missing amounts for source(s) {missing}")
        if extra:
            errors.append(f"{name!r} has amounts for undeclared source(s) {extra}")

    total_units = sum(r[3] for r in RAW_PROJECTS)
    if total_units != EXPECTED_TOTAL_UNITS:
        errors.append(f"Total Units column sum: expected {EXPECTED_TOTAL_UNITS}, got {total_units}")

    lihtc_annual = sum(a["lihtc"] for a in PROJECT_SOURCE_AMOUNTS.values())
    if lihtc_annual != EXPECTED_LIHTC_ANNUAL:
        errors.append(f"annual LIHTC sum: expected {EXPECTED_LIHTC_ANNUAL}, got {lihtc_annual}")
    if lihtc_annual * 10 != EXPECTED_LIHTC_10YR:
        errors.append(
            f"annual LIHTC x10 = {lihtc_annual * 10}, expected to equal the source's "
            f"10-year headline {EXPECTED_LIHTC_10YR}"
        )

    home_total = sum(a.get("home", 0) for a in PROJECT_SOURCE_AMOUNTS.values())
    if home_total != EXPECTED_HOME_TOTAL:
        errors.append(f"HOME total: expected {EXPECTED_HOME_TOTAL}, got {home_total}")
    nhtf_total = sum(a.get("nhtf", 0) for a in PROJECT_SOURCE_AMOUNTS.values())
    if nhtf_total != EXPECTED_NHTF_TOTAL:
        errors.append(f"NHTF total: expected {EXPECTED_NHTF_TOTAL}, got {nhtf_total}")

    dev_cost = sum(TOTAL_DEV_COST.values())
    if dev_cost != EXPECTED_TOTAL_DEV_COST:
        errors.append(f"Total Development Cost sum: expected {EXPECTED_TOTAL_DEV_COST}, got {dev_cost}")

    if errors:
        raise SystemExit("Transcription mismatch(es):\n" + "\n".join(errors))

    print(f"Project count ({EXPECTED_PROJECT_COUNT}) verified against the announcement's "
          f"\"10 multifamily housing developments\".")
    print(f"LIHTC annual credits sum to ${lihtc_annual:,}; x10 = ${EXPECTED_LIHTC_10YR:,}, "
          "matching the source's own 10-year headline exactly.")
    print(f"HOME (${home_total:,}) and NHTF (${nhtf_total:,}) column sums verified "
          "(self-consistent with the per-project list).")
    print(f"Total Development Cost sums to ${dev_cost:,} (~ the headline's "
          "\"approximate $110 million\").")
    print(f"NOTE: the list's \"Total Units\" column sums to {total_units}, which does "
          f"NOT reconcile with the headline's \"{EXPECTED_HEADLINE_UNITS} affordable "
          "rental units\" -- a 3-unit source-internal discrepancy, documented not "
          "resolved (see module docstring).")


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def geocode(query, cache, city=None):
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
        # 429 is the expected block state here; other errors are worth logging.
        if not (isinstance(exc, urllib.error.HTTPError) and exc.code == 429):
            print(f"  geocode failed for {query!r}: {exc}")
    if result is None and city and city in CITY_COORDS:
        result = CITY_COORDS[city]  # deterministic OSM city-center fallback
    cache[query] = result
    time.sleep(1.0)  # Nominatim usage policy: max 1 request/second
    return result


def build_projects():
    cache = {}
    projects = []
    for name, city, county, units, sources in RAW_PROJECTS:
        coords = geocode(f"{city}, {county} County, AR", cache, city=city)
        if coords is None:
            coords = geocode(f"{city}, AR", cache, city=city)
        status = "city_center" if coords else "unresolved"
        primary = next((s for s in FUNDING_PRIORITY if s in sources), sources[0])
        source_amounts = PROJECT_SOURCE_AMOUNTS.get(name, {})
        projects.append({
            "id": slugify(name),
            "name": name,
            "address": None,
            "city": f"{city} ({county} County)",
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
    verify_totals()
    print("Geocoding project cities via Nominatim (city-center precision)...")
    projects = build_projects()
    unresolved = [p["name"] for p in projects if p["geocode_status"] == "unresolved"]
    if unresolved:
        print(f"  {len(unresolved)} project(s) could not be geocoded: {unresolved}")

    payload = {
        "AR": {
            "hfa_name": "Arkansas Development Finance Authority",
            "hfa_abbr": "ADFA",
            "fiscal_year": "FY2025",
            "source_title": "ADFA 2025 Affordable Housing Tax Credit Developments announcement (9% LIHTC award round)",
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
