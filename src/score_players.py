import sys
import pandas as pd
import yaml

MIN_MINUTES = 450      # drop players below this
THIN_MINUTES = 1800    # flag players below this as a thin sample

def load_players(path):
    df = pd.read_csv(path)
    df = df[df.minutes >= MIN_MINUTES].copy()
    n90 = df.minutes / 90
    df["xg_per90"] = df.xg / n90
    df["shots_per90"] = df.shots / n90
    df["xa_per90"] = df.xa / n90
    df["sot_pct"] = df.shots_on_target / df.shots
    df["goals_minus_xg_per90"] = (df.goals - df.xg) / n90
    df["xg_per_shot"] = df.xg / df.shots        # shot quality, shown but not scored yet
    df["thin"] = df.minutes < THIN_MINUTES
    return df

def score(df, weights):
    out = df.copy()
    total = 0
    for stat, w in weights.items():
        total = total + w * out[stat].rank(pct=True)   # percentile within this pool
    out["score"] = (100 * total).round(1)
    return out.sort_values("score", ascending=False)

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/players/strikers.csv"
    with open("config/needs_map.yaml") as f:
        weights = yaml.safe_load(f)["player_weights"]["striker"]
    ranked = score(load_players(path), weights)
    cols = ["player", "team", "age", "minutes", "xg_per90", "shots_per90", "xg_per_shot",
            "xa_per90", "sot_pct", "goals_minus_xg_per90", "score", "thin"]
    print(ranked[cols].round(2).to_string(index=False))
    ranked.to_csv("data/processed/striker_scores.csv", index=False)
