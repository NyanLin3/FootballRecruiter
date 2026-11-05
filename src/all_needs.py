import sys
import pandas as pd
from needs import load_rules, team_needs

path = sys.argv[1] if len(sys.argv) > 1 else "data/processed/team_z.csv"
z = pd.read_csv(path, index_col=0)
cfg = load_rules()

rows = []
for team in z.index:
    n = team_needs(team, z, cfg)
    for _, r in n.iterrows():
        rows.append({"team": team, **r})
out = pd.DataFrame(rows)
out.to_csv("data/processed/league_needs.csv", index=False)

print("using:", path)
print(out[out.level == "FLAG"].sort_values(["position", "z"]).to_string(index=False))
print("\nFLAGS per team:")
print(out[out.level == "FLAG"].groupby("team").size().reindex(z.index, fill_value=0).to_string())