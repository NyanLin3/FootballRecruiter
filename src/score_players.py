import sys
import pandas as pd
import yaml

MIN_MINUTES = 450      # drop players below this
THIN_MINUTES = 1800    # flag players below this as a thin sample

def derive_striker(df):
    n90 = df.minutes / 90
    df["xg_per90"] = df.xg / n90
    df["shots_per90"] = df.shots / n90
    df["xa_per90"] = df.xa / n90
    df["sot_pct"] = df.shots_on_target / df.shots
    df["goals_minus_xg_per90"] = (df.goals - df.xg) / n90
    df["xg_per_shot"] = df.xg / df.shots        # shot quality, shown but not scored
    return df

def derive_none(df):
    return df    # centre-back file already holds per-90 values and percentages

POSITIONS = {
    "striker": ("data/players/strikers.csv", derive_striker),
    "centre_back": ("data/players/centrebacks.csv", derive_none),
}

def load_players(path, derive):
    df = pd.read_csv(path)
    df = df[df.minutes >= MIN_MINUTES].copy()
    df = derive(df)
    df["thin"] = df.minutes < THIN_MINUTES
    return df

def score(df, weights):
    use = {k: v for k, v in weights.items() if k in df.columns}
    if not use:
        raise SystemExit("None of the weighted stats are columns in this file.")
    scale = sum(use.values())
    out = df.copy()
    total = 0
    for stat, w in use.items():
        total = total + (w / scale) * out[stat].rank(pct=True)   # percentile within this pool
    out["score"] = (100 * total).round(1)
    return out.sort_values("score", ascending=False), list(use)

if __name__ == "__main__":
    position = sys.argv[1] if len(sys.argv) > 1 else "striker"
    default_path, derive = POSITIONS[position]
    path = sys.argv[2] if len(sys.argv) > 2 else default_path
    with open("config/needs_map.yaml") as f:
        weights = yaml.safe_load(f)["player_weights"][position]
    ranked, used = score(load_players(path, derive), weights)
    extra = ["xg_per_shot"] if "xg_per_shot" in ranked.columns else []
    cols = ["player", "team", "age", "minutes"] + extra + used + ["score", "thin"]
    print("scored on:", used)
    print(ranked[cols].round(2).to_string(index=False))
    ranked.to_csv(f"data/processed/{position}_scores.csv", index=False)
