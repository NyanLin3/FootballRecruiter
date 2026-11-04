import sys
import pandas as pd
import yaml

def load_rules(path="config/needs_map.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)

def team_needs(team, z, cfg, watch_sd=-0.5):
    flag_sd = cfg["threshold_sd"]
    out = []

    def add(position, driver, value):
        out.append({
            "position": position,
            "driver": driver,
            "z": round(value, 2),
            "level": "FLAG" if value <= flag_sd else "watch",
        })

    for rule in cfg["rules"]:
        if rule.get("penalty_only"):
            continue

        if rule.get("type") == "defence":
            vol = z.loc[team, rule["volume"]]
            qual_vals = z.loc[team, rule["quality"]]
            qual, qual_driver = qual_vals.min(), qual_vals.idxmin()
            vol_weak, qual_weak = vol <= watch_sd, qual <= watch_sd
            if vol_weak and qual_weak:
                add(rule["both_position"], f"{rule['volume']} + {qual_driver}", min(vol, qual))
            elif vol_weak:
                add(rule["volume_position"], rule["volume"], vol)
            elif qual_weak:
                add(rule["quality_position"], qual_driver, qual)
            continue

        vals = z.loc[team, rule["weakness"]]
        worst = vals.min()
        if worst <= watch_sd:
            add(rule["position"], vals.idxmin(), worst)

    return pd.DataFrame(out).sort_values("z") if out else pd.DataFrame()

if __name__ == "__main__":
    team = sys.argv[1] if len(sys.argv) > 1 else "Man United"
    z = pd.read_csv("data/processed/team_z.csv", index_col=0)
    needs = team_needs(team, z, load_rules())
    print(team)
    print(needs.to_string(index=False) if len(needs) else "No needs flagged")