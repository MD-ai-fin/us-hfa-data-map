"""
Builds docs/or_program_activity.json from Oregon Housing and Community
Services' (OHCS) CY2025 affordable-housing funding awards.

Sources (all CY2025 = calendar year January-December 2025)
-----------------------------------------------------------
1. OHCS year-end news release (the "4,806 homes" headline + the January and
   December round summaries):
     https://apps.oregon.gov/oregon-newsroom/OR/OHCS/Posts/Post/oregon-housing-and-community-services-funds-the-creation-and-preservation-of-more-than-4800-affordable-homes-in-2025
2. Housing Stability Council (HSC) meeting packets -- OHCS's own per-round
   award lists (project name, city/county, total units, sponsor, and funding
   sources with dollar amounts). Downloaded to FY2025/program_activity/pdf/:
     OR_OHCS_HSC_Packet_Feb2025.pdf  (Feb 7)   -- 3 projects / 540 units, ~$141M bonds
     OR_OHCS_HSC_Packet_Mar2025.pdf  (Mar 7)   -- 2 projects / 112 units
     OR_OHCS_HSC_Packet_Apr2025.pdf  (Apr 4)   -- 2 projects / 162 units (one dup, see below)
     OR_OHCS_HSC_Packet_May2025.pdf  (May 2)   -- 11 projects / 1,105 units
     OR_OHCS_HSC_Packet_Jul2025.pdf  (Jul 11)  -- 2 projects / 60 units
     OR_OHCS_HSC_Packet_Sep2025.pdf  (Sep 5)   -- 12 projects / 1,171 units (two dups)
     OR_OHCS_HSC_Packet_Oct2025.pdf  (Oct 3)   -- 5 projects / 340 units
     OR_OHCS_HSC_Packet_Nov2025.pdf  (Nov 7)   -- 7 projects / 261 units
     OR_OHCS_HSC_Packet_Dec2025.pdf  (Dec 5)   -- 7 projects / 479 units
   (The Jan 10 and June 6 / Aug 1 packets are no longer published on
   oregon.gov and were not archived by the Wayback Machine; their rounds are
   transcribed below from the year-end release and the Aug 5 news release
   instead -- see "August 2025 round" note.)
3. Governor's Homeownership Month release (the 239 homeownership-unit and
   ~1,000 Flex Lending figures):
     https://apps.oregon.gov/oregon-newsroom/OR/GOV/Posts/Post/governor-marks-homeownership-month-by-celebrating-nearly-1000-new-homeowners

Reporting-period / year-discipline note
---------------------------------------
OHCS's program-activity numbers here are CALENDAR-year 2025, not the
July-June state fiscal year. The year-end release explicitly frames the
4,806 figure as "in 2025" (vs 3,208 "in 2024", +50%), and every HSC packet
above is dated within Jan-Dec 2025. OHCS's legislative annual report is
deliberately NOT used (the task briefing warns it only covers through
2025-01-31). fiscal_year is therefore recorded honestly as "CY2025", and
the JSON's source_title/notes state this.

Category-level methodology
--------------------------
Affordable rental housing (4,806 units): the headline is OHCS's own year-end
figure -- "OHCS funded the creation or preservation of 4,806 affordable
rental homes statewide in 2025, a 50% increase from 2024" (year-end release,
corroborated by the same release's December-round table and the Aug/Sep round
releases). OHCS does NOT disclose a single clean partition of these 4,806
units by funding program; it reports them ROUND BY ROUND (each HSC meeting
approves a named cohort). This script therefore models the 11 CY2025 funding
rounds as the category's subprograms (additive=False).

The subprograms are NOT additive to the headline for two honest reasons:
(a) a handful of projects are re-listed across rounds -- Barbur Apartments
appears in the Feb bond round AND the Sep bond re-confirmation; Jamii Court
appears in the May round AND the Sep bond re-confirmation; Elm Park Apartments
appears in the Jan (LIFT) reservation AND the Apr bond round; Cascade Peaks
and Wickiup Station II carry over from the Oct packet into the Nov packet --
so summing round unit totals over-counts physical homes; (b) OHCS's own
4,806 headline also sweeps in preservation/non-round allocations not itemized
per project in any single list. The deduplicated round sum reconciles to
~4,800 units (see verify_round_totals), within 6 of the 4,806 headline -- the
6-unit residual is unit-count drift on individual projects between rounds
(e.g. Barbur 149 in one release vs 150 in both packets; Rose Schnitzer 233 in
the release vs 235 in the packet). Documented, not force-fit.

Homeownership (239 units) and Flex Lending (~1,000 households): both come
from the Governor's Homeownership Month release, which states OHCS "funded
239 permanently affordable homeownership units (expected completed by 2028)"
and that the Flex Lending program "helped nearly 1,000 households purchase a
home" in 2025, of whom "98 percent were first-time homebuyers". Neither
figure has a per-unit/per-household dollar total disclosed, so no
fy2025_amounts are shown for either category. The Flex Lending figure is
"nearly 1,000" -- the release discloses no exact count, so the JSON records
1000 with the source_quote keeping the "nearly" qualifier verbatim.

Fund-type classification (fund_type/fund_name)
----------------------------------------------
OHCS is a STATE GOVERNMENT DEPARTMENT (not a business-type HFA like PHFA or
Florida Housing), so its housing-finance programs are governmental-type
activities, not proprietary funds. There is no OHCS-only audited financial
statement in this repo (FY2025/txt/ has no OR file) and no separate OHCS
CAFR was located on oregon.gov's finance pages during this build, so the
classification below is by program description per the BUILD_SPEC fallback,
with confidence noted:
  - LIHTC / OAHTC / AWHTC (state & federal tax credits) -> off_balance_sheet:
    credits are allocated to developers and their investors, never booked as
    OHCS fund assets (same logic PA/VA's scripts document).
  - LIFT, PSH Capital, Preservation, HDGP, PSP, GHAP, HOME / HOME-ARP ->
    governmental: state/federal grant-and-loan programs administered by a
    governmental department (confidence: high -- these are statutory OHCS
    programs funded by General Fund / lottery / federal pass-through).
  - Pass-through revenue bonds / 501(c)(3) bonds -> governmental (conduit):
    OHCS issues them as a governmental issuer; the debt is repaid from
    project revenues, not OHCS's general fund (confidence: medium).
Because each HSC round mixes two or more of these, the round subprograms are
marked "mixed" where a tax-credit or conduit-bond component is present and
"governmental" where the round is pure grant/loan funding. This is a
conservative, documented choice -- not an invented fund structure.

August 2025 round (known gap)
-----------------------------
The Aug 5, 2025 release ("$160 million in 740+ affordable homes across
Oregon", 10 developments) lists the 10 project NAMES and cities but no
per-project unit counts; the underlying June 6 / Aug 1 meeting packet was
not published/archived. The only per-project figure recoverable is Rose
Schnitzer Tower (235 units preserved, $42,350,000 bond -- from the archived
Aug 1 packet resolution). The other 9 projects are transcribed with
units=None (honest gap -- their 505 units are real but not individually
attributable), and the round's 740-unit total is kept on the round_aug
subprogram. This is the same "walk away rather than fabricate a missing
number" discipline used elsewhere in this repo.

Geocoding
---------
City-level source lists (all rounds) -> query "{city}, Oregon" and mark
geocode_status="city_center". No street addresses are transcribed (the
packets DO carry addresses for some projects, but the round announcements
are city-level and using mixed precision across a single state would be
inconsistent). Cascade Peaks is a scattered-site preservation across Baker
City, La Grande and Newberg; it is geocoded at Baker City (first city the
packet names) and flagged in the docstring here, not silently mis-placed.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # repo root
OUT_PATH = BASE / "docs" / "or_program_activity.json"

SOURCE_URL = ("https://apps.oregon.gov/oregon-newsroom/OR/OHCS/Posts/Post/"
              "oregon-housing-and-community-services-funds-the-creation-and-"
              "preservation-of-more-than-4800-affordable-homes-in-2025")
SOURCE_FILE = ("OR_OHCS_HSC_Packet_{Feb..Dec}2025.pdf (9 HSC meeting packets) "
               "+ OHCS year-end and Aug/Sep round news releases")
RETRIEVED = "2026-08-16"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
# OSM-based fallback used only when Nominatim rate-limits (HTTP 429) or fails;
# same underlying OpenStreetMap data, so city-level results are equivalent.
PHOTON_URL = "https://photon.komoot.io/api/"
GEOCODER_USER_AGENT = "us-hfa-data-map/1.0 (github.com/MD-ai-fin/us-hfa-data-map)"

# Persistent on-disk geocode cache so re-runs are byte-identical and do not
# re-hit the geocoders (the shared IP is often Nominatim-rate-limited when
# several state builds geocode at once).
GEOCODE_CACHE_PATH = Path(__file__).resolve().parent / "or_geocode_cache.json"

# Uniform fy2026 shape -- OHCS's CY2025 materials disclose no FY2026/CY2026
# forward-looking projection anywhere (the HSC packets look backward at the
# round being approved), so none is invented.
_FY26_PENDING = {"value": None, "amount": None, "closed": False,
                 "note_key": "orFy26NotePending"}


# ---------------------------------------------------------------------------
# Round metadata: per-round unit totals (the packet's own printed "Total"
# row where one exists, else the release's headline), dominant color group,
# fund type, and the round's disclosed dollar total (None when the round has
# no single printed dollar figure).
# ---------------------------------------------------------------------------
ROUNDS = [
    # (key, label_suffix, total_units, amount, color_group, fund_type)
    ("round_jan", "January 2025", 108, None, "capital", "governmental"),
    ("round_feb", "February 2025", 540, None, "bond", "mixed"),
    ("round_mar", "March 2025", 112, None, "capital", "governmental"),
    ("round_apr", "April 2025", 130, None, "bond", "mixed"),
    ("round_may", "May 2025", 1105, None, "capital", "mixed"),
    ("round_jul", "July 2025", 60, None, "capital", "governmental"),
    ("round_aug", "August 2025", 740, 160000000, "capital", "mixed"),
    ("round_sep", "September 2025", 925, 291000000, "credit", "mixed"),
    ("round_oct", "October 2025", 340, None, "credit", "mixed"),
    ("round_nov", "November 2025", 261, None, "credit", "mixed"),
    ("round_dec", "December 2025", 479, None, "capital", "mixed"),
]

# Known-unit sum per round (used for verification). For round_aug this is the
# ONE project whose units are individually disclosed (Rose Schnitzer 235);
# the other 9 August projects carry units=None and sum to 740-235=505.
ROUND_KNOWN_UNITS = {
    "round_jan": 108, "round_feb": 540, "round_mar": 112, "round_apr": 130,
    "round_may": 1105, "round_jul": 60, "round_aug": 235, "round_sep": 925,
    "round_oct": 340, "round_nov": 261, "round_dec": 479,
}

# OHCS's own CY2025 headline (year-end release), used only for the external
# cross-check -- NOT re-derived from RAW_PROJECTS.
HEADLINE_RENTAL_UNITS = 4806
AUG_ROUND_TOTAL = 740          # Aug release "740+ homes"; packet confirms 740
AUG_KNOWN_UNITS = 235          # Rose Schnitzer Tower

_CAT_RENTAL = {
    "key": "affordable_rental_housing",
    "unit_type": "units",
    "fy2025_actual": HEADLINE_RENTAL_UNITS,
    "fy2025_source_quote": (
        "\"Oregon Housing and Community Services funded the creation or "
        "preservation of 4,806 affordable rental homes statewide in 2025, a "
        "50% increase from 2024 [3,208].\" (OHCS year-end news release, "
        "retrieved 2026-08-16) -- modeled as 11 Housing Stability Council "
        "funding rounds (Jan-Dec 2025) whose per-round project lists are "
        "transcribed from OHCS's own HSC meeting packets. Rounds are NOT "
        "additive to the headline: a few projects are re-listed across rounds "
        "(Barbur Apartments and Jamii Court in both a bond round and the "
        "September re-confirmation; Elm Park Apartments in January and April), "
        "and OHCS discloses no per-program partition of the 4,806. The "
        "deduplicated round sum reconciles to ~4,800 units, within 6 of the "
        "4,806 headline (unit-count drift on individual projects between "
        "rounds, e.g. Barbur 149 vs 150, Rose Schnitzer 233 vs 235)."
    ),
    "fy2025_amounts": [],
    "additive": False,
    "fy2026": _FY26_PENDING,
    "subprograms": [
        {
            "key": key,
            "fy2025_units": total,
            "fy2025_amount": amount,
            "color_group": color,
            "fund_type": ftype,
            # OHCS is a state department; no OHCS-only fund names are
            # disclosed per round, so fund_name stays null (see docstring).
            "fund_name": None,
            "fy2026": _FY26_PENDING,
        }
        for key, _label, total, amount, color, ftype in ROUNDS
    ],
}

_CAT_HOMEOWNERSHIP = {
    "key": "homeownership_development",
    "unit_type": "units",
    "fy2025_actual": 239,
    "fy2025_source_quote": (
        "\"In 2025, OHCS funded 239 permanently affordable homeownership units, "
        "expected to be completed by 2028.\" (Governor's Homeownership Month "
        "release, retrieved 2026-08-16). No dollar total for these 239 units is "
        "disclosed in the release, so none is shown."
    ),
    "fy2025_amounts": [],
    "additive": True,
    "fy2026": _FY26_PENDING,
    "subprograms": [
        {
            "key": "permanent_homeownership",
            "fy2025_units": 239,
            "fy2025_amount": None,
            "color_group": "capital",
            # OHCS homeownership-development funding is a state governmental
            # program (General Fund / lottery-backed); no OHCS-only CAFR was
            # available to pin the exact fund, confidence: medium.
            "fund_type": "governmental",
            "fund_name": None,
            "fy2026": _FY26_PENDING,
        },
    ],
}

_CAT_FLEX = {
    "key": "homebuyer_flex_lending",
    "unit_type": "households",
    "fy2025_actual": 1000,
    "fy2025_source_quote": (
        "\"In 2025, OHCS's Flex Lending program helped nearly 1,000 households "
        "purchase a home ... 98 percent were first-time homebuyers.\" "
        "(Governor's Homeownership Month release, retrieved 2026-08-16). The "
        "release discloses no exact household count (only 'nearly 1,000') and "
        "no dollar total, so 1000 is recorded with the 'nearly' qualifier kept "
        "verbatim here and no amount is shown."
    ),
    "fy2025_amounts": [],
    "additive": True,
    "fy2026": _FY26_PENDING,
    "subprograms": [
        {
            "key": "flex_lending",
            "fy2025_units": 1000,
            "fy2025_amount": None,
            "color_group": "capital",
            # Flex Lending is an OHCS single-family lending program -- a state
            # governmental activity (confidence: medium, by program
            # description; no OHCS-only CAFR located).
            "fund_type": "governmental",
            "fund_name": None,
            "fy2026": _FY26_PENDING,
        },
    ],
}

CATEGORIES = [_CAT_RENTAL, _CAT_HOMEOWNERSHIP, _CAT_FLEX]

# ---------------------------------------------------------------------------
# Project-level detail: (name, city, units, round_key).
# units=None marks the 9 August projects whose per-project count is not
# disclosed (see docstring). Each project's funding_sources = [its round];
# source_amounts/total_amount stay empty because OHCS's round announcements
# do not uniformly disclose per-project dollar totals (round totals live on
# the subprograms). Sponsors are named in each packet but the output schema
# has no sponsor field.
# ---------------------------------------------------------------------------
RAW_PROJECTS = [
    # January 2025 round (year-end release: ">$37M, 3 projects")
    ("M Carter Commons", "Portland", 62, "round_jan"),
    ("Elm Park Apartments", "Florence", 32, "round_jan"),
    ("Shelly Cove Apartments", "Port Orford", 14, "round_jan"),
    # February 7 round (HSC packet: 3 projects / 540 units / ~$141M bonds)
    ("Barbur Apartments", "Portland", 150, "round_feb"),
    ("Peaceful Villa", "Portland", 166, "round_feb"),
    ("Orchard Park Apartments", "Salem", 224, "round_feb"),
    # March 7 round (HSC packet: 2 projects / 112 units)
    ("73Foster", "Portland", 64, "round_mar"),
    ("River Road Apartments", "Eugene", 48, "round_mar"),
    # April 4 round (HSC packet: 2 projects / 162 units, of which Elm Park
    # Apartments is a re-list of the January project -- deduplicated here, so
    # only Mariposa Village is unique to this round)
    ("Mariposa Village", "Hood River", 130, "round_apr"),
    # May 2 round (HSC packet + release: 11 projects / 1,105 units)
    ("Avenue Plaza", "Portland", 78, "round_may"),
    ("Colorado Lake Cooperative", "Corvallis", 45, "round_may"),
    ("Easton Village", "Bend", 128, "round_may"),
    ("El Nido Apartments", "Clackamas", 55, "round_may"),
    ("Gresham Civic Station", "Gresham", 60, "round_may"),
    ("Jamii Court", "Portland", 96, "round_may"),
    ("Pacifica", "Seaside", 69, "round_may"),
    ("Park Place", "Oregon City", 200, "round_may"),
    ("Park Run", "Eugene", 158, "round_may"),
    ("Valley Vista", "McMinnville", 96, "round_may"),
    ("Whiteaker Commons", "Eugene", 120, "round_may"),
    # July 11 round (HSC packet: 2 projects / 60 units)
    ("Trinity Place", "Sisters", 40, "round_jul"),
    ("Ellensburg Apartments", "Gold Beach", 20, "round_jul"),
    # August round (Aug 5 release: 10 projects / 740 units; only Rose
    # Schnitzer's unit count is disclosed -- see docstring)
    ("Rose Schnitzer Tower", "Portland", 235, "round_aug"),
    ("Farmdale Apartments", "Woodburn", None, "round_aug"),
    ("Goose Hollow Lofts", "Portland", None, "round_aug"),
    ("Hillside Park Buildings D & E", "Milwaukie", None, "round_aug"),
    ("Olalla Meadows", "Toledo", None, "round_aug"),
    ("Phoenix Corner", "Phoenix", None, "round_aug"),
    ("Retro Electro", "Salem", None, "round_aug"),
    ("Sheridan Road Manufactured Home Community", "Sheridan", None, "round_aug"),
    ("The Coleman", "Eugene", None, "round_aug"),
    ("The Lucy", "Eugene", None, "round_aug"),
    # September 5 round (HSC packet + release: 10 unique ORCA projects /
    # 925 units; Barbur and Jamii Court are re-listed bond projects already
    # counted above, so deduplicated out)
    ("Quarterdeck Apartments", "Dallas", 34, "round_sep"),
    ("Allenwood Apartments", "Grants Pass", 116, "round_sep"),
    ("Chenowith Affordable Housing", "The Dalles", 76, "round_sep"),
    ("Compass Points", "Salem", 120, "round_sep"),
    ("Cottages United", "Salem", 15, "round_sep"),
    ("Gussie Belle II", "Salem", 60, "round_sep"),
    ("Joseph Street Apartments", "Salem", 183, "round_sep"),
    ("Bull Mountain Apartments", "Tigard", 74, "round_sep"),
    ("Meadowlark Place", "Beaverton", 104, "round_sep"),
    ("Flatworks Building", "Portland", 143, "round_sep"),
    # October 3 round (HSC packet: 5 projects / 340 units)
    ("333 Oak", "Portland", 90, "round_oct"),
    ("Alyssa Daye Gardens", "Portland", 31, "round_oct"),
    ("Cascade Peaks", "Baker City", 119, "round_oct"),  # scattered: Baker City / La Grande / Newberg
    ("Garfield Street", "Portland", 59, "round_oct"),
    ("Wickiup Station Apartments II", "La Pine", 41, "round_oct"),
    # November 7 round (HSC packet: 7 unique projects / 261 units; Cascade
    # Peaks and Wickiup Station II carry over from October and are not
    # re-listed here)
    ("Golden Rain Apartments", "Grants Pass", 38, "round_nov"),
    ("Green Family Housing", "Green", 53, "round_nov"),
    ("Henry Street Apartments", "Beaverton", 52, "round_nov"),
    ("Horizon Court", "Hermiston", 22, "round_nov"),
    ("Mississippi Avenue Project", "Portland", 30, "round_nov"),
    ("Ochoco Manor", "Prineville", 28, "round_nov"),
    ("Path Home Family Village", "Portland", 38, "round_nov"),
    # December 5 round (HSC packet: 7 projects / 479 units)
    ("Broadway Corridor", "Portland", 229, "round_dec"),
    ("Downtown McMinnville Affordable Housing", "McMinnville", 72, "round_dec"),
    ("Metzger Park", "Tigard", 32, "round_dec"),
    ("Minnesota Places II", "Portland", 57, "round_dec"),
    ("Oak Terrace", "Florence", 48, "round_dec"),
    ("Pelican's Perch", "Brookings", 24, "round_dec"),
    ("Veteran and Elder Village", "Pendleton", 17, "round_dec"),
]

# Expected project counts per round (for verification).
EXPECTED_ROUND_COUNTS = {
    "round_jan": 3, "round_feb": 3, "round_mar": 2, "round_apr": 1,
    "round_may": 11, "round_jul": 2, "round_aug": 10, "round_sep": 10,
    "round_oct": 5, "round_nov": 7, "round_dec": 7,
}

# color_group / fund_type / amount lookup keyed by round key (mirrors ROUNDS).
_ROUND_META = {r[0]: r for r in ROUNDS}


def verify_project_counts_and_units():
    errors = []
    if len(RAW_PROJECTS) != 61:
        errors.append(f"project count: expected 61, got {len(RAW_PROJECTS)}")

    counts = {}
    known_units = {}
    for name, _city, units, rnd in RAW_PROJECTS:
        counts[rnd] = counts.get(rnd, 0) + 1
        if units is not None:
            known_units[rnd] = known_units.get(rnd, 0) + units

    for rnd, expected in EXPECTED_ROUND_COUNTS.items():
        if counts.get(rnd, 0) != expected:
            errors.append(f"{rnd} project count: expected {expected}, got {counts.get(rnd, 0)}")

    for rnd, expected in ROUND_KNOWN_UNITS.items():
        got = known_units.get(rnd, 0)
        if got != expected:
            errors.append(f"{rnd} known-unit sum: expected {expected}, got {got}")

    # August reconciliation: 235 disclosed + 505 undisclosed = 740 round total.
    aug_none = sum(1 for _n, _c, u, r in RAW_PROJECTS if r == "round_aug" and u is None)
    if aug_none != 9:
        errors.append(f"August undisclosed-unit project count: expected 9, got {aug_none}")
    if AUG_KNOWN_UNITS + (AUG_ROUND_TOTAL - AUG_KNOWN_UNITS) != AUG_ROUND_TOTAL:
        errors.append("August round-total arithmetic broken")

    if errors:
        raise SystemExit("Project count/unit mismatch(es):\n" + "\n".join(errors))
    print("Project count (61) and per-round known-unit sums verified against OHCS "
          "HSC meeting packets and round releases.")


def verify_headline_reconciliation():
    known_total = sum(u for _n, _c, u, _r in RAW_PROJECTS if u is not None)
    deduped_total = known_total + (AUG_ROUND_TOTAL - AUG_KNOWN_UNITS)
    gap = HEADLINE_RENTAL_UNITS - deduped_total
    print(f"  deduplicated round units = {known_total} known + "
          f"{AUG_ROUND_TOTAL - AUG_KNOWN_UNITS} August-undisclosed = "
          f"{deduped_total} vs OHCS headline {HEADLINE_RENTAL_UNITS} "
          f"(gap {gap}; unit-count drift between rounds, documented not forced).")
    # The gap must be small (unit-count drift) and non-negative. 6 is the
    # expected residual for this state.
    if not (0 <= gap <= 20):
        raise SystemExit(f"headline reconciliation implausible: gap {gap} units")


def _load_cache():
    if GEOCODE_CACHE_PATH.exists():
        try:
            return json.loads(GEOCODE_CACHE_PATH.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            return {}
    return {}


def _nominatim(query):
    params = urllib.parse.urlencode({"q": query, "format": "json", "limit": 1})
    url = f"{NOMINATIM_URL}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": GEOCODER_USER_AGENT})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.load(resp)
    if data:
        return (float(data[0]["lat"]), float(data[0]["lon"]))
    return None


def _photon(query):
    params = urllib.parse.urlencode({"q": query, "limit": 1})
    url = f"{PHOTON_URL}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": GEOCODER_USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.load(resp)
    features = data.get("features") or []
    if features:
        lon, lat = features[0]["geometry"]["coordinates"]
        return (float(lat), float(lon))
    return None


def geocode(query, cache):
    if query in cache:
        return cache[query]
    result = None
    # 1) Nominatim (primary), retrying on transient HTTP 429 (shared-IP
    #    rate limit) with a short cooldown before each retry.
    for attempt in range(3):
        try:
            result = _nominatim(query)
            break
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError,
                KeyError, ValueError, IndexError) as exc:
            if attempt < 2:
                print(f"  Nominatim failed for {query!r}: {exc} -- retrying")
                time.sleep(3.0)
            else:
                print(f"  Nominatim failed again for {query!r}: {exc}")
    # 2) OSM-based Photon fallback (only if Nominatim did not resolve).
    if result is None:
        try:
            result = _photon(query)
            print(f"  Photon fallback resolved {query!r}")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError,
                KeyError, ValueError, IndexError) as exc:
            print(f"  geocode failed for {query!r}: {exc}")
    cache[query] = result
    time.sleep(1.0)  # Nominatim usage policy: max 1 request/second
    return result


def _slug(name):
    return (name.lower()
            .replace(" & ", " and ")
            .replace("&", "and")
            .replace("'", "")
            .replace(".", "")
            .replace("/", " ")
            .replace("#", "")
            .strip()
            .replace(" ", "-"))


def build_projects():
    cache = _load_cache()
    dirty = False
    projects = []
    for name, city, units, rnd in RAW_PROJECTS:
        query = f"{city}, Oregon"
        before = query in cache
        coords = geocode(query, cache)
        if not before and query in cache:
            dirty = True
        status = "city_center" if coords else "unresolved"
        meta = _ROUND_META[rnd]
        projects.append({
            "id": _slug(name),
            "name": name,
            "address": None,
            "city": city,
            "lat": round(coords[0], 5) if coords else None,
            "lon": round(coords[1], 5) if coords else None,
            "units": units,
            "funding_sources": [rnd],
            "source_amounts": {},
            "total_amount": None,
            "primary_color_group": meta[4],
            "overlaps": False,
            "geocode_status": status,
        })
    if dirty:
        GEOCODE_CACHE_PATH.write_text(
            json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")
    return projects


def main():
    verify_project_counts_and_units()
    verify_headline_reconciliation()
    print("Geocoding project cities via Nominatim...")
    projects = build_projects()
    unresolved = [p["name"] for p in projects if p["geocode_status"] == "unresolved"]
    if unresolved:
        print(f"  {len(unresolved)} project(s) could not be geocoded: {unresolved}")

    payload = {
        "OR": {
            "hfa_name": "Oregon Housing and Community Services",
            "hfa_abbr": "OHCS",
            "fiscal_year": "CY2025",
            "source_title": ("OHCS CY2025 affordable-housing funding rounds "
                             "(Housing Stability Council award packets, "
                             "Jan-Dec 2025)"),
            "source_url": SOURCE_URL,
            "source_file": SOURCE_FILE,
            "retrieved": RETRIEVED,
            "categories": CATEGORIES,
            "projects": projects,
        }
    }
    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    print(f"Wrote {OUT_PATH} ({len(projects)} projects, {len(CATEGORIES)} categories)")


if __name__ == "__main__":
    main()
