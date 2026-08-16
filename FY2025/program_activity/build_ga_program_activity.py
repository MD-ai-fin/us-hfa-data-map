"""
Builds docs/ga_program_activity.json from the Georgia Department of
Community Affairs (DCA) "2025 Nine Percent Housing Credit Award"
announcement.

Source
------------------------------------------------------------------------
"Georgia DCA awards more than $37 million in tax credits to bolster
Georgia's affordable housing" (announcement dated September 25, 2025; body
datelined September 23, 2025), which includes the full per-development
"2025 Nine Percent Housing Credit Award" table:
    https://dca.georgia.gov/announcement/2025-09-25/dca-awards-37m-tax-credits
Local copy: FY2025/program_activity/pdf/GA_DCA_LIHTC_2025_announcement.html
(downloaded live via requests on 2026-08-16; HTTP 200). The announcement
links to a separate "detailed" award-list page (dca.georgia.gov/node/15961),
but that page returns HTTP 403 to this environment (bot-blocked) and adds no
figure this script needs -- the announcement page itself already carries the
complete 31-row table (Property Name / Annual Credit Allocation Reserved /
City / Total Units / Tenancy / Primary Construction Activity) plus the prose
headline figures, all of which this script transcribes verbatim.

IMPORTANT data-provenance note: DCA, not GHFA
------------------------------------------------------------------------
Georgia's designated Housing Finance Agency is the Georgia Housing and
Finance Authority (GHFA). However, GHFA does not itself administer the
state's 9% Low-Income Housing Tax Credit (LIHTC) awards -- that program is
run by the Georgia Department of Community Affairs (DCA), which shares a
governing board with GHFA. This script's hfa_name / hfa_abbr /
source_title therefore name DCA as the awarding agency; they do NOT claim
this is GHFA's own data.

The checked-in text FY2025/txt/GA_GHFA_FY2025_ACFR.txt is the WRONG
document for this build -- it is a text dump of the State of Georgia's
statewide CAFR, in which GHFA appears only as a discretely-presented
component-unit summary with no program-output detail (no project counts,
no unit counts). It was NOT used as a data source, only as context for the
fund-type classification below.

Fund-type classification (fund_type on the single subprogram)
------------------------------------------------------------------------
The single subprogram (9% LIHTC) is classified "off_balance_sheet". Federal
low-income housing tax credits are allocated directly to the developers and
their investors; they are never booked as an asset of DCA or GHFA -- same
off-balance-sheet logic as PA/IL/WA's LIHTC subprograms. (DCA itself is a
state executive-branch department, i.e. a governmental entity, but the
credit allocation it administers is not a DCA fund asset.) Because the
local .txt is the state's own CAFR rather than DCA's/GHFA's financial
statements, this classification is by program description (the standard
LIHTC pass-through model) rather than by direct cross-reference to a
DCA/GHFA statement of net position -- confidence: high for "off-balance-
sheet" (this is how every other state's LIHTC subprogram is classified),
but no fund_name is asserted.

Category-level methodology (single category, by design)
------------------------------------------------------------------------
Georgia's announcement discloses exactly one program-output KPI -- the
9% LIHTC award round -- so this build produces ONE category
("multifamily_lihtc") with ONE subprogram ("lihtc") and ONE amount label,
not a multi-category annual report. No second category is invented to pad
the module.

Dual verification gate:
  - INTERNAL (the announcement table prints no TOTAL/footer row of its own,
    so, per the PA Map-Doc pattern, the column sums are computed once
    directly from the table cells and asserted): the 31 rows' "Annual Credit
    Allocation Reserved" column sums to $37,235,164 and the "Total Units"
    column sums to 1,977.
  - EXTERNAL (the press-release prose, the agency's own top-line claim):
    "$37,235,164 in Housing Tax Credits to construct or preserve 31
    affordable housing developments" (matches the column sum exactly, and
    rounds to the headline "$37M" / $37.24M) and "will increase the number
    of affordable homes by 1,983 units" -- which does NOT match the table's
    1,977 unit sum.

The 6-unit gap (prose "1,983 units" vs table column sum "1,977") is a
genuine internal inconsistency in DCA's own document: the source prints no
table total and does not reconcile the two figures. This script does NOT
silently pick one or force-fit the other. It uses the press release's
"1,983 units" as the category headline (the agency's own top-line claim,
and the number cited in the task briefing) while the per-project "units"
below are transcribed verbatim from the table and therefore sum to 1,977.
The discrepancy is flagged in the category's fy2025_source_quote and in the
verify gate's printed output. (This mirrors the project's IA/WI precedent:
a small unreconciled gap between a headline and the project list is
disclosed, not hidden.) The dollar figure reconciles exactly and needs no
such caveat.

fy2026
------------------------------------------------------------------------
The announcement is a single back-dated press release with no forward-
looking/next-round projection, so every fy2026 field below is {value: None,
amount: None, closed: False, note_key: "gaFy26NotePending"} -- nothing is
invented.

Geocoding
------------------------------------------------------------------------
The source table gives city only (no street addresses), so every project is
geocoded as "{city}, GA" and honestly marked geocode_status="city_center"
(never "ok" -- a city-center guess is not street precision). Nominatim
(OpenStreetMap), self-throttled to <=1 request/second with an identifying
User-Agent per Nominatim's usage policy, with a persisted cache
(ga_geocode_cache.json) so a re-run is byte-identical without re-querying
Nominatim (which rate-limits and would otherwise make a bare re-run trip
HTTP 429 and drop coordinates). Three city names that collide with a
different Georgia county's name ("Douglas", "Calhoun", "Clayton") are
disambiguated to their county-qualified city via CITY_QUERY_OVERRIDE -- see
the comment there.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "ga_program_activity.json"

SOURCE_URL = "https://dca.georgia.gov/announcement/2025-09-25/dca-awards-37m-tax-credits"
SOURCE_FILE = "GA_DCA_LIHTC_2025_announcement.html"
RETRIEVED = "2026-08-16"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
GEOCODER_USER_AGENT = "us-hfa-data-map/1.0 (github.com/MD-ai-fin/us-hfa-data-map)"
# Persisted geocode cache: Nominatim is rate-limited (1 req/sec), so a bare
# re-run would re-query and can trip HTTP 429, breaking byte-identical
# reproducibility. The first run populates this file; every later run reads
# it and never touches the network, guaranteeing a deterministic output.
GEOCODE_CACHE_PATH = Path(__file__).resolve().parent / "ga_geocode_cache.json"

# fy2026 uniform shape: {value, amount, closed, note_key} -- see docstring.
_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                 "note_key": "gaFy26NotePending"}

# ---------------------------------------------------------------------------
# Category-level data. One category only -- see docstring for why a second
# category is NOT added (Georgia's announcement discloses a single 9%-LIHTC
# award-round KPI, not a multi-program annual report).
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "key": "multifamily_lihtc",
        "unit_type": "units",
        # The press release's own top-line claim ("1,983 units"). NOTE: the
        # accompanying 31-row table's "Total Units" column sums to 1,977 --
        # a 6-unit gap DCA's document does not reconcile. Documented here,
        # not silently adjusted. See docstring + verify gate.
        "fy2025_actual": 1983,
        "fy2025_source_quote": (
            "\"Atlanta, Ga. (September 23, 2025) -- The Georgia Department of "
            "Community Affairs (DCA) is awarding $37,235,164 in Housing Tax Credits "
            "to construct or preserve 31 affordable housing developments across the "
            "state.\" ... \"These awards, part of the 2024-2025 Qualified Allocation "
            "Plan, are earmarked for 25 new construction properties and six "
            "rehabilitation properties. Twenty of these properties are designated for "
            "families, 10 exclusively house senior citizens, and one will focus on "
            "housing for persons with disabilities.\" ... \"Housing Tax Credit awards "
            "support statewide economic growth and will increase the number of "
            "affordable homes by 1,983 units.\" (DCA announcement, September 25, 2025, "
            "dca.georgia.gov). Cross-check against the announcement's own 31-row '2025 "
            "Nine Percent Housing Credit Award' table: the 'Annual Credit Allocation "
            "Reserved' column sums exactly to $37,235,164 (matching the headline), but "
            "the 'Total Units' column sums to 1,977 -- 6 fewer than the press release's "
            "own '1,983 units' sentence. The source prints no table-total row and does "
            "not reconcile the two unit figures, so the discrepancy is disclosed here "
            "rather than silently adjusted; the category headline keeps the press "
            "release's 1,983 while the per-project 'units' below (transcribed verbatim "
            "from the table) sum to 1,977."
        ),
        "fy2025_amounts": [
            {"label_key": "ga_amt_lihtc", "amount": 37235164},
        ],
        "additive": True,  # a single subprogram that IS the whole category
        "fy2026": _FY26_PENDING,
        "subprograms": [
            {"key": "lihtc", "fy2025_units": 1983, "fy2025_amount": 37235164,
             "color_group": "credit",
             # Federal 9% LIHTC -- allocated directly to developers and their
             # investors, never booked as a DCA/GHFA fund asset. DCA is a
             # state executive-branch department (governmental entity), but
             # the credit allocation it administers sits off its own balance
             # sheet; same off-balance-sheet logic as PA/IL/WA's LIHTC
             # subprograms. Confidence: high (program-description basis --
             # the local GA txt is the state's own CAFR, not a DCA/GHFA
             # statement, so no fund_name is asserted).
             "fund_type": "off_balance_sheet", "fund_name": None,
             "fy2026": _FY26_PENDING},
        ],
    },
]

# ---------------------------------------------------------------------------
# 9% LIHTC project-level detail ("2025 Nine Percent Housing Credit Award"
# table). Manually transcribed from the announcement page's own HTML table
# (one row per development). "units" uses the table's "Total Units" column;
# "amount" uses "Annual Credit Allocation Reserved" (the per-project annual
# 9% LIHTC allocation). The source table gives city only -- no street
# addresses -- so every project carries address=None and is city-center
# geocoded. "tenancy" / "activity" are transcribed for the verify gate only
# (they back the prose's 20 family / 10 senior / 1 disability and
# 25 new-construction / 6 rehab breakdown) and are not surfaced in the
# output JSON (the project schema has no such field).
# ---------------------------------------------------------------------------

# (name, city, total_units, annual_credit_allocation, tenancy, construction_activity)
RAW_PROJECTS = [
    ("1700 Drayton St.", "Savannah", 41, 903229, "Family", "New Construction"),
    ("Aberdeen Cottages", "Thomasville", 72, 1215000, "Family", "New Construction"),
    ("Catoosa Senior", "Calhoun", 60, 1052913, "Senior", "Acquisition/Rehabilitation"),
    ("Chattooga Ridge", "Trion", 44, 1215000, "Family", "New Construction"),
    ("Classic City Heights Apartments", "Athens", 68, 1350000, "Senior", "New Construction"),
    ("Cosmopolitan Village", "Atlanta", 70, 1350000, "Family", "New Construction"),
    ("Edmund Doraville II", "Doraville", 54, 1310000, "Family", "New Construction"),
    ("Edmund Gainesville", "Gainesville", 64, 1350000, "Family", "New Construction"),
    ("Evergreen", "Marietta", 64, 1300000, "Senior", "New Construction"),
    ("Folio House", "Atlanta", 50, 1350000, "Family", "New Construction"),
    ("Harding Court Senior", "Albany", 60, 1258500, "Senior", "New Construction"),
    ("John Graham Homes", "Rome", 56, 1224848, "Family", "New Construction"),
    ("Lanier Gardens", "Athens", 150, 1270000, "Senior", "Acquisition/Rehabilitation"),
    ("Laurel Pointe", "Statesboro", 72, 1145000, "Senior", "Acquisition/Rehabilitation"),
    ("McDonald Crossing", "Douglas", 48, 1215000, "Family", "New Construction"),
    ("Moon Creek Phase I", "Columbus", 90, 1350000, "Senior", "New Construction"),
    ("Mountain View Terrace", "East Ellijay", 50, 1215000, "Family", "New Construction"),
    ("Peaks of Clayton", "Clayton", 48, 1215000, "Family", "New Construction"),
    ("Pine Forest", "Cairo", 64, 896008, "Family", "Acquisition/Rehabilitation"),
    ("Residences of Hope", "Atlanta", 42, 1080000, "Senior", "New Construction"),
    ("RHA Redevelopment Phase II", "Roswell", 102, 1350000, "Family", "New Construction"),
    ("Sand Hills Estates", "Augusta", 40, 1070805, "Family", "New Construction"),
    ("Unity Mill", "LaGrange", 104, 1350000, "Family", "New Construction"),
    ("Villages at Meadowbrook Phase 2", "Augusta", 75, 1350000, "Senior", "New Construction"),
    ("Vine Street Village", "Waycross", 53, 1215000, "Family", "New Construction"),
    ("Wagon Works Phase II", "East Point", 40, 1300000, "Family", "New Construction"),
    ("Walnut Village", "Montezuma", 44, 1147600, "Family", "New Construction"),
    ("West Pine Residences Phase III", "Sylvester", 48, 1115900, "Family", "New Construction"),
    ("Wildwood", "Tifton", 88, 1102547, "Family", "Acquisition/Rehabilitation"),
    ("Willow Song Village", "Cornelia", 60, 1215000, "Persons with Disabilities", "New Construction"),
    ("Windcliff Apartments", "Gainesville", 56, 752814, "Senior", "Acquisition/Rehabilitation"),
]

# City-name disambiguation for geocoding. The source gives city names only
# (no county), and three of those names collide with the name of a DIFFERENT
# Georgia county, so Nominatim's bare "{city}, GA" query returns the wrong
# place (~100-200 miles off):
#   * "Douglas"  -> the incorporated city "Douglas" (Coffee County seat,
#     south GA), but the bare query returns the Douglasville / Douglas County
#     (metro Atlanta) area. "McDonald Crossing" is read as Douglas city: the
#     source writes "Douglas" (not "Douglasville") and this award round
#     clusters in small south-Georgia cities (Thomasville, Cairo, Tifton,
#     Sylvester, Montezuma, Waycross, Statesboro, Albany).
#   * "Calhoun"  -> Calhoun city (Gordon County seat, north-west GA; the
#     adjacent county is literally "Catoosa", matching the project name
#     "Catoosa Senior"), but the bare query returns Calhoun COUNTY (south-
#     west GA, seat Morgan).
#   * "Clayton"  -> Clayton city (Rabun County seat, north-east GA mountains;
#     the project is named "Peaks of Clayton"), but the bare query risks
#     returning Clayton County (metro Atlanta).
# The source gives no county and the linked "detailed" list (node/15961) is
# HTTP 403, so each is a documented county-qualified disambiguation (these
# are well-known county seats), not a silently-fabricated county.
CITY_QUERY_OVERRIDE = {
    "Douglas": "Douglas, Coffee County, Georgia",
    "Calhoun": "Calhoun, Gordon County, Georgia",
    "Clayton": "Clayton, Rabun County, Georgia",
}

# Headline figures from the announcement prose, used as the external gate.
HEADLINE_PROJECT_COUNT = 31
HEADLINE_CREDIT_TOTAL = 37235164       # "$37,235,164 in Housing Tax Credits"
HEADLINE_UNITS = 1983                   # "increase ... by 1,983 units"
EXPECTED_TOTAL_UNITS_SUM = 1977        # table's own "Total Units" column sum


def verify_project_table():
    """Internal gate: re-sum the transcribed table and assert against the
    source's own figures. The credit column must reproduce the press
    release's headline exactly; the unit column reproduces the table's own
    column sum (1,977) and is separately flagged as differing from the prose
    headline (1,983) -- see docstring."""
    errors = []
    if len(RAW_PROJECTS) != HEADLINE_PROJECT_COUNT:
        errors.append(f"project count: expected {HEADLINE_PROJECT_COUNT}, got {len(RAW_PROJECTS)}")

    credit_sum = sum(amount for _n, _c, _u, amount, _t, _a in RAW_PROJECTS)
    if credit_sum != HEADLINE_CREDIT_TOTAL:
        errors.append(
            f"Annual Credit Allocation Reserved column sum: expected "
            f"{HEADLINE_CREDIT_TOTAL}, got {credit_sum}"
        )
    if round(credit_sum / 1e6, 2) != 37.24:
        errors.append(f"credit total ${credit_sum:,} does not round to $37.24M headline")

    units_sum = sum(units for _n, _c, units, _a, _t, _act in RAW_PROJECTS)
    if units_sum != EXPECTED_TOTAL_UNITS_SUM:
        errors.append(
            f"Total Units column sum: expected {EXPECTED_TOTAL_UNITS_SUM}, got {units_sum}"
        )

    family = sum(1 for _n, _c, _u, _amt, tenancy, _act in RAW_PROJECTS if tenancy == "Family")
    senior = sum(1 for _n, _c, _u, _amt, tenancy, _act in RAW_PROJECTS if tenancy == "Senior")
    disabled = sum(1 for _n, _c, _u, _amt, tenancy, _act in RAW_PROJECTS if tenancy == "Persons with Disabilities")
    if (family, senior, disabled) != (20, 10, 1):
        errors.append(
            f"tenancy breakdown: expected (20 family, 10 senior, 1 disability), "
            f"got ({family}, {senior}, {disabled})"
        )

    new_construction = sum(1 for _n, _c, _u, _amt, _t, act in RAW_PROJECTS if act == "New Construction")
    rehab = sum(1 for _n, _c, _u, _amt, _t, act in RAW_PROJECTS if act == "Acquisition/Rehabilitation")
    if (new_construction, rehab) != (25, 6):
        errors.append(
            f"construction breakdown: expected (25 new construction, 6 rehab), "
            f"got ({new_construction}, {rehab})"
        )

    if errors:
        raise SystemExit("Project-table verification mismatch(es):\n" + "\n".join(errors))

    print(
        f"Verified {len(RAW_PROJECTS)} projects: credit column sums to "
        f"${credit_sum:,} (== $37.24M headline, exact match to $37,235,164); "
        f"unit column sums to {units_sum}; tenancy {family}/{senior}/{disabled} "
        f"(family/senior/disability) and construction {new_construction}NC/{rehab}rehab "
        f"match the prose. NOTE: the prose headline '{HEADLINE_UNITS} units' differs "
        f"from the table's {units_sum}-unit column sum by "
        f"{HEADLINE_UNITS - units_sum} -- a source-document inconsistency that is "
        f"disclosed in the JSON quote, not force-fit."
    )


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
    time.sleep(1.1)  # Nominatim usage policy: max 1 request/second (+ margin)
    return result


def load_geocode_cache():
    if GEOCODE_CACHE_PATH.exists():
        return json.loads(GEOCODE_CACHE_PATH.read_text(encoding="utf-8"))
    return {}


def save_geocode_cache(cache):
    GEOCODE_CACHE_PATH.write_text(
        json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def build_projects():
    cache = load_geocode_cache()
    projects = []
    for name, city, units, amount, _tenancy, _activity in RAW_PROJECTS:
        query = CITY_QUERY_OVERRIDE.get(city, f"{city}, GA")
        coords = geocode(query, cache)
        # City-level source list -> honest "city_center" precision, never
        # "ok" (which would over-claim street-level accuracy the source does
        # not provide).
        status = "city_center" if coords else "unresolved"
        projects.append({
            "id": name.lower().replace(" ", "-").replace("'", "").replace(".", "").replace("&", "and").replace("+", "plus"),
            "name": name,
            "address": None,  # source table gives city only, no street address
            "city": city,
            "lat": round(coords[0], 5) if coords else None,
            "lon": round(coords[1], 5) if coords else None,
            "units": units,
            "funding_sources": ["lihtc"],
            "source_amounts": {"lihtc": amount},
            "total_amount": amount,
            "primary_color_group": "credit",
            "overlaps": False,  # single funding source (9% LIHTC)
            "geocode_status": status,
        })
    save_geocode_cache(cache)
    return projects


def main():
    verify_project_table()
    print("Geocoding project cities via Nominatim...")
    projects = build_projects()
    unresolved = [p["name"] for p in projects if p["geocode_status"] == "unresolved"]
    if unresolved:
        print(f"  {len(unresolved)} project(s) could not be geocoded: {unresolved}")
    city_center = [p["name"] for p in projects if p["geocode_status"] == "city_center"]
    if city_center:
        print(f"  {len(city_center)} project(s) geocoded to city-center precision.")

    payload = {
        "GA": {
            "hfa_name": "Georgia Department of Community Affairs (DCA)",
            "hfa_abbr": "Georgia DCA",
            "fiscal_year": "FY2025",
            "source_title": "Georgia DCA 2025 Nine Percent Housing Credit Award list (9% LIHTC administered by the Georgia Department of Community Affairs, not GHFA)",
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
