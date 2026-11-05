import pandas as pd
from prep import to_long
from diagnose import build_metrics, zscores, METRICS

SEASONS = ["2324", "2425", "2526"]
early_z, late_z = {}, {}
for s in SEASONS:
    long = to_long(f"data/raw/epl_{s}.csv")
    long["n"] = long.groupby("team").cumcount()
    early_z[s] = zscores(build_metrics(long[long.n < 10]))
    late_z[s] = zscores(build_metrics(long[long.n >= 10], window=999))

pe = pd.concat(early_z.values()).reset_index(drop=True)
pl = pd.concat(late_z.values()).reset_index(drop=True)

rows = []
for col in METRICS:
    flagged = pe[col] <= -1.0
    row = {"metric": col, "corr_pooled": round(pe[col].corr(pl[col]), 2)}
    for s in SEASONS:
        row[s] = round(early_z[s][col].corr(late_z[s][col]), 2)
    row["n_flagged"] = int(flagged.sum())
    row["flagged_late_z"] = round(pl.loc[flagged, col].mean(), 2) if flagged.any() else None
    rows.append(row)

res = pd.DataFrame(rows)
print(res.to_string(index=False))
res.to_csv("data/processed/backtest.csv", index=False)