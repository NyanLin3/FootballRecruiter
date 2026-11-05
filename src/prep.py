import pandas as pd

def to_long(path):
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    home = df.rename(columns={"HomeTeam": "team", "AwayTeam": "opp", "FTHG": "gf", "FTAG": "ga",
        "HS": "shots", "AS": "shots_against", "HST": "sot", "AST": "sot_against",
        "HF": "fouls", "HY": "yellows", "HR": "reds", "HC": "corners", "AC": "corners_against"})
    away = df.rename(columns={"AwayTeam": "team", "HomeTeam": "opp", "FTAG": "gf", "FTHG": "ga",
        "AS": "shots", "HS": "shots_against", "AST": "sot", "HST": "sot_against",
        "AF": "fouls", "AY": "yellows", "AR": "reds", "AC": "corners", "HC": "corners_against"})
    cols = ["Date", "team", "opp", "gf", "ga", "shots", "shots_against", "sot", "sot_against",
            "fouls", "yellows", "reds", "corners", "corners_against"]
    return pd.concat([home[cols], away[cols]]).sort_values("Date")