import pandas as pd
from prep import to_long
from diagnose import build_metrics, zscores, METRICS

long = to_long("data/raw/epl_2526.csv")
long["n"] = long.groupby("team").cumcount()
early, late = long[long.n < 10], long[long.n >= 10]

z_early = zscores(build_metrics(early))
z_early_adj = zscores(build_metrics(early), adjust=True)
z_late = zscores(build_metrics(late, window=999))

rows = []
for col in METRICS:
    flagged = z_early[col] <= -1.0
    rows.append({
        "metric": col,
        "corr_raw": round(z_early[col].corr(z_late[col]), 2),
        "corr_adjusted": round(z_early_adj[col].corr(z_late[col]), 2),
        "n_flagged": int(flagged.sum()),
        "flagged_late_z": round(z_late.loc[flagged, col].mean(), 2) if flagged.any() else None,
    })
res = pd.DataFrame(rows)
print(res.to_string(index=False))
res.to_csv("data/processed/backtest.csv", index=False)