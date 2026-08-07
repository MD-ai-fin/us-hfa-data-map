import json
from pathlib import Path

data = json.loads(Path("fy2025_metrics.json").read_text(encoding="utf-8"))
down = [d for d in data if d["status"] == "downloaded"]
miss = [d for d in data if d["status"] != "downloaded"]
print("Downloaded", len(down))
print("Missing", len(miss), ":", ", ".join(d["state"] for d in miss))
print()
for d in sorted(down, key=lambda x: x.get("net_position_2025") or 0, reverse=True)[:15]:
    print(
        d["state"],
        "np=",
        d.get("net_position_2025"),
        "assets=",
        d.get("total_assets_2025"),
        "chg%=",
        d.get("net_position_change_pct"),
    )
print("--- no metrics ---")
for d in down:
    if not d.get("net_position_2025") and not d.get("total_assets_2025"):
        print(d["state"], d.get("notes"))
