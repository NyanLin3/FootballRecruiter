import pandas as pd

df = pd.read_csv("data/raw/epl_2627.csv")
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)

# one row per team per match, so every team is treated the same way
home = df.rename(columns={"HomeTeam": "team", "AwayTeam": "opp", "FTHG": "gf", "FTAG": "ga",
    "HS": "shots", "AS": "shots_against", "HST": "sot", "AST": "sot_against",
    "HF": "fouls", "HY": "yellows", "HR": "reds"})
away = df.rename(columns={"AwayTeam": "team", "HomeTeam": "opp", "FTAG": "gf", "FTHG": "ga",
    "AS": "shots", "HS": "shots_against", "AST": "sot", "HST": "sot_against",
    "AF": "fouls", "AY": "yellows", "AR": "reds"})
cols = ["Date", "team", "opp", "gf", "ga", "shots", "shots_against", "sot", "sot_against", "fouls", "yellows", "reds"]
long = pd.concat([home[cols], away[cols]]).sort_values("Date")
long.to_csv("data/processed/team_matches.csv", index=False)

print(long[long.team == "Man United"].tail(10).to_string(index=False))
