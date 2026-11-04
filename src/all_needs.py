import pandas as pd
from needs import load_rules, team_needs

z = pd.read_csv("data/processed/team_z.csv", index_col=0)
cfg = load_rules()

rows = []
for team in z.index:
    n = team_needs(team, z, cfg)
    for _, r in n.iterrows():
        rows.append({"team": team, **r})
out = pd.DataFrame(rows)
out.to_csv("data/processed/league_needs.csv", index=False)

print(out[out.level == "FLAG"].sort_values(["position", "z"]).to_string(index=False))
print("\nFLAGS per team:")
print(out[out.level == "FLAG"].groupby("team").size().reindex(z.index, fill_value=0).to_string())