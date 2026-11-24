import os, sys
import pandas as pd

TEAM_NAMES = {"Man United": "Manchester United", "Man City": "Manchester City", "Nott'm Forest": "Nottingham Forest"}
TABLES = {
    "centre_back": ("data/processed/centre_back_scores.csv", "2024/25 API-Football data"),
    "striker": ("data/processed/striker_scores.csv", "hand-entered, see the source column"),
}
TOP = 5

bt = pd.read_csv("data/processed/backtest.csv").set_index("metric")["corr_pooled"]

def reliability(driver):
    r = min(bt[m.strip()] for m in driver.split("+"))
    return ("high" if r >= 0.6 else "medium" if r >= 0.4 else "low"), r

team = sys.argv[1] if len(sys.argv) > 1 else "Man United"
needs = pd.read_csv("data/processed/league_needs.csv")
needs = needs[needs.team == team].sort_values("z")
if needs.empty:
    sys.exit(f"No needs flagged for {team}")
own = TEAM_NAMES.get(team, team).lower()

print(f"=== {team} ===")
for _, n in needs.iterrows():
    label, r = reliability(n["driver"])
    print(f"\n{n['position'].upper()}: {n['level']} (z {n['z']}), evidence reliability {label} ({r:.2f}), driver: {n['driver']}")
    if n["position"] not in TABLES:
        print("  no player table for this need yet")
        continue
    path, period = TABLES[n["position"]]
    if not os.path.exists(path):
        print("  missing", path)
        continue
    t = pd.read_csv(path)
    t = t[~t.team.str.lower().str.startswith(own)]
    cols = [c for c in ["player", "team", "age", "minutes", "score", "thin"] if c in t.columns]
    print(f"  top candidates outside {team} ({period}); ages and scores are for that period")
    print(t.sort_values("score", ascending=False).head(TOP)[cols].to_string(index=False))
