import pandas as pd

needs = pd.read_csv("data/processed/league_needs.csv")
bt = pd.read_csv("data/processed/backtest.csv").set_index("metric")["corr_pooled"]

def reliability(driver):
    r = min(bt[m.strip()] for m in driver.split("+"))   # weakest link if a rule uses two stats
    label = "high" if r >= 0.6 else "medium" if r >= 0.4 else "low"
    return pd.Series({"reliability": label, "corr": r})

needs[["reliability", "corr"]] = needs.driver.apply(reliability)
print(needs.sort_values(["level", "z"]).to_string(index=False))
needs.to_csv("data/processed/league_needs_labeled.csv", index=False)