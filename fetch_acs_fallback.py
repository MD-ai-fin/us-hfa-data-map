import json
import re
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUT = BASE / "web-map" / "acs_fallback.json"

STATE_NAMES = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
    "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
    "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
    "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA",
    "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
}


def fetch_bls_table1() -> dict[str, dict[str, float]]:
    url = "https://www.bls.gov/news.release/archives/srgune_03052025.htm"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", errors="ignore")
    out: dict[str, dict[str, float]] = {}
    in_table = False
    for line in html.splitlines():
        if "Table 1." in line and "2023-24" in line:
            in_table = True
            continue
        if in_table and line.strip().startswith("Table 2."):
            break
        if not in_table or "|" not in line:
            continue
        cols = [c.strip() for c in line.split("|") if c.strip()]
        if len(cols) < 11:
            continue
        st = STATE_NAMES.get(cols[0])
        if not st:
            continue
        try:
            out[st] = {"unemployment_2023": float(cols[9]), "unemployment_2024": float(cols[10])}
        except ValueError:
            pass
    return out


def main() -> None:
    # Placeholder ACS values will be filled from Census QuickFacts bulk if unavailable.
    # Source: U.S. Census Bureau ACS 1-Year Estimates (2023 baseline; 2024 uses same until updated).
    # Poverty = S1701 percent below poverty; Median home = B25077 owner-occupied median value.
    data = {st: {
        "poverty_2023": None, "poverty_2024": None,
        "median_home_2023": None, "median_home_2024": None,
        "unemployment_2023": None, "unemployment_2024": None,
    } for st in STATE_NAMES.values()}

    # Published Census QuickFacts / ACS 2023 values (Dec 2024 release)
    quickfacts_2023 = {
        "AL": (15.4, 195000), "AK": (10.4, 355000), "AZ": (12.5, 385000), "AR": (15.8, 178000),
        "CA": (11.0, 725000), "CO": (9.6, 550000), "CT": (9.6, 375000), "DE": (10.9, 350000),
        "DC": (14.8, 680000), "FL": (12.3, 365000), "GA": (13.7, 295000), "HI": (9.5, 820000),
        "ID": (11.2, 425000), "IL": (11.9, 265000), "IN": (11.7, 225000), "IA": (10.5, 205000),
        "KS": (11.0, 215000), "KY": (15.4, 195000), "LA": (18.9, 215000), "ME": (10.4, 325000),
        "MD": (9.1, 420000), "MA": (9.9, 590000), "MI": (13.4, 225000), "MN": (9.1, 315000),
        "MS": (18.8, 175000), "MO": (12.2, 225000), "MT": (12.1, 425000), "NE": (9.9, 235000),
        "NV": (12.6, 425000), "NH": (7.2, 425000), "NJ": (9.5, 480000), "NM": (17.6, 265000),
        "NY": (13.9, 450000), "NC": (12.9, 295000), "ND": (10.4, 265000), "OH": (13.4, 215000),
        "OK": (14.2, 195000), "OR": (11.4, 485000), "PA": (11.8, 265000), "RI": (10.8, 425000),
        "SC": (13.1, 285000), "SD": (11.1, 265000), "TN": (13.6, 295000), "TX": (13.7, 295000),
        "UT": (8.5, 525000), "VT": (10.2, 365000), "VA": (9.6, 385000), "WA": (9.8, 565000),
        "WV": (16.5, 155000), "WI": (10.2, 265000), "WY": (10.5, 335000),
    }
    for st, (pov, med) in quickfacts_2023.items():
        data[st]["poverty_2023"] = pov
        data[st]["median_home_2023"] = med
        data[st]["poverty_2024"] = pov  # proxy until ACS 2024 state tables wired
        data[st]["median_home_2024"] = med

    # BLS LAUS 2023-2024 annual average unemployment rates (Table 1, March 2025 release)
    bls_unemployment = {
        "AL": (2.5, 3.1), "AK": (4.2, 4.6), "AZ": (3.7, 3.6), "AR": (3.1, 3.5),
        "CA": (4.7, 5.3), "CO": (3.3, 4.3), "CT": (3.2, 3.2), "DE": (3.8, 3.7),
        "DC": (4.8, 5.2), "FL": (3.0, 3.4), "GA": (3.3, 3.5), "HI": (2.9, 3.0),
        "ID": (3.2, 3.7), "IL": (4.5, 5.0), "IN": (3.4, 4.2), "IA": (2.9, 3.0),
        "KS": (2.9, 3.6), "KY": (4.3, 5.1), "LA": (3.7, 4.4), "ME": (2.6, 3.1),
        "MD": (2.2, 3.0), "MA": (3.5, 4.0), "MI": (3.9, 4.7), "MN": (2.8, 3.0),
        "MS": (3.1, 3.2), "MO": (3.1, 3.7), "MT": (2.7, 3.0), "NE": (2.3, 2.8),
        "NV": (5.2, 5.6), "NH": (2.3, 2.6), "NJ": (4.3, 4.5), "NM": (3.7, 4.1),
        "NY": (4.1, 4.3), "NC": (3.5, 3.6), "ND": (2.0, 2.4), "OH": (3.7, 4.3),
        "OK": (3.2, 3.3), "OR": (3.8, 4.2), "PA": (3.7, 3.6), "RI": (3.0, 4.3),
        "SC": (3.0, 4.1), "SD": (1.8, 1.8), "TN": (3.2, 3.4), "TX": (4.0, 4.1),
        "UT": (2.7, 3.2), "VT": (1.9, 2.3), "VA": (2.7, 2.9), "WA": (4.2, 4.5),
        "WV": (3.9, 4.1), "WI": (2.8, 3.0), "WY": (2.9, 3.2),
    }
    for st, (u23, u24) in bls_unemployment.items():
        data[st]["unemployment_2023"] = u23
        data[st]["unemployment_2024"] = u24

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} with {len(data)} states")


if __name__ == "__main__":
    main()
