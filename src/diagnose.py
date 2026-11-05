import numpy as np
import pandas as pd

WINDOW = 10
# metric: True if higher is better
METRICS = {
    "gf_pg": True, "sot_pct": True, "goals_per_shot": True,
    "ga_pg": False, "shots_against_pg": False, "sot_against_pg": False,
    "ga_per_sot": False,          # goalkeeper proxy: goals conceded per shot on target faced
    "fouls_pg": False, "discipline_pg": False,
    "shots_pg": True, "sot_pg": True,
}

def build_metrics(long, window=WINDOW):
    w = long.sort_values("Date").groupby("team").tail(window)
    g = w.groupby("team")
    return pd.DataFrame({
        "games": g.size(),
        "gf_pg": g.gf.mean(),
        "ga_pg": g.ga.mean(),
        "shots_pg": g.shots.mean(),
        "sot_pg": g.sot.mean(),
        "sot_pct": g.sot.sum() / g.shots.sum(),
        "goals_per_shot": g.gf.sum() / g.shots.sum(),
        "shots_against_pg": g.shots_against.mean(),
        "sot_against_pg": g.sot_against.mean(),
        "ga_per_sot": g.ga.sum() / g.sot_against.sum(),
        "fouls_pg": g.fouls.mean(),
        "discipline_pg": (g.yellows.sum() + 2 * g.reds.sum()) / g.size(),
        "corner_share": g.corners.sum() / (g.corners.sum() + g.corners_against.sum()),  # style proxy
    })

def zscores(m, adjust=False):
    """Negative z = weakness on every metric. adjust=True removes the part explained by corner share."""
    z = pd.DataFrame(index=m.index)
    for col, higher_better in METRICS.items():
        x = m[col]
        if adjust:
            slope, icpt = np.polyfit(m["corner_share"], x, 1)
            x = x - (slope * m["corner_share"] + icpt)
        s = (x - x.mean()) / x.std()
        z[col] = s if higher_better else -s
    return z

def blended_z(long, w_recent=0.5, window=WINDOW):
    recent = zscores(build_metrics(long, window))
    season = zscores(build_metrics(long, 999))
    return w_recent * recent + (1 - w_recent) * season, recent, season

def diagnose(team, long, threshold=-1.0):
    z, _, _ = blended_z(long)
    row = z.loc[team].sort_values()
    return row, row[row <= threshold]

if __name__ == "__main__":
    long = pd.read_csv("data/processed/team_matches.csv", parse_dates=["Date"])
    blend, recent, season = blended_z(long)
    blend.to_csv("data/processed/team_z.csv")
    zscores(build_metrics(long), adjust=True).to_csv("data/processed/team_z_adj.csv")

    t = "Man United"
    out = pd.DataFrame({"recent": recent.loc[t], "season": season.loc[t], "blend": blend.loc[t]})
    out["moved"] = out["recent"] - out["season"]
    print(out.sort_values("blend").round(2).to_string())