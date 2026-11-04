import pandas as pd

WINDOW = 10
# metric: True if higher is better
METRICS = {
    "gf_pg": True, "sot_pct": True, "goals_per_shot": True,
    "ga_pg": False, "shots_against_pg": False, "sot_against_pg": False,
    "fouls_pg": False, "discipline_pg": False,
}

def build_metrics(long, window=WINDOW):
    w = long.sort_values("Date").groupby("team").tail(window)
    g = w.groupby("team")
    return pd.DataFrame({
        "games": g.size(),
        "gf_pg": g.gf.mean(),
        "ga_pg": g.ga.mean(),
        "sot_pct": g.sot.sum() / g.shots.sum(),
        "goals_per_shot": g.gf.sum() / g.shots.sum(),
        "shots_against_pg": g.shots_against.mean(),
        "sot_against_pg": g.sot_against.mean(),
        "fouls_pg": g.fouls.mean(),
        "discipline_pg": (g.yellows.sum() + 2 * g.reds.sum()) / g.size(),
    })

def zscores(m):
    z = pd.DataFrame(index=m.index)
    for col, higher_better in METRICS.items():
        s = (m[col] - m[col].mean()) / m[col].std()
        z[col] = s if higher_better else -s   # negative z = weakness for every metric
    return z

def diagnose(team, long, threshold=-1.0):
    z = zscores(build_metrics(long))
    row = z.loc[team].sort_values()
    return row, row[row <= threshold]

if __name__ == "__main__":
    long = pd.read_csv("data/processed/team_matches.csv", parse_dates=["Date"])
    z = zscores(build_metrics(long))
    z.to_csv("data/processed/team_z.csv")
    row, flags = diagnose("Man United", long)
    print(row.round(2).to_string())
    print("\nFLAGGED (<= -1 SD):", list(flags.index))