import sys
import pandas as pd
import yaml

def load_rules(path="config/needs_map.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)

def team_needs(team, z, cfg, watch_sd=-0.5):
    flag_sd = cfg["threshold_sd"]
    out = []
    for rule in cfg["rules"]:
        if rule.get("penalty_only"):
            continue
        vals = z.loc[team, rule["weakness"]]
        worst = vals.min()
        if worst <= watch_sd:
            out.append({
                "position": rule["position"],
                "driver": vals.idxmin(),
                "z": round(worst, 2),
                "level": "FLAG" if worst <= flag_sd else "watch",
            })
    return pd.DataFrame(out).sort_values("z") if out else pd.DataFrame()

if __name__ == "__main__":
    team = sys.argv[1] if len(sys.argv) > 1 else "Man United"
    z = pd.read_csv("data/processed/team_z.csv", index_col=0)
    needs = team_needs(team, z, load_rules())
    print(team)
    print(needs.to_string(index=False) if len(needs) else "No needs flagged")