import os, sys, json, time
from pathlib import Path
import requests
import pandas as pd

KEY = os.environ.get("APIFOOTBALL_KEY")
BASE = "https://v3.football.api-sports.io"
RAW = Path("data/raw")
LEAGUE, SEASON = 39, 2024        # Premier League; season = the year it started (free plan: 2022-2024)
CACHE = RAW / f"apifootball_players_{LEAGUE}_{SEASON}_byteam.json"

def get(path, params):
    r = requests.get(f"{BASE}/{path}", headers={"x-apisports-key": KEY}, params=params, timeout=30)
    r.raise_for_status()
    print("requests left today:", r.headers.get("x-ratelimit-requests-remaining"))
    data = r.json()
    if data.get("errors"):
        raise SystemExit(f"API said: {data['errors']}")
    return data

def pull():
    RAW.mkdir(parents=True, exist_ok=True)
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    if "_teams" not in cache:
        t = get("teams", {"league": LEAGUE, "season": SEASON})["response"]
        cache["_teams"] = [[x["team"]["id"], x["team"]["name"]] for x in t]
        CACHE.write_text(json.dumps(cache))
    rows = []
    for tid, name in cache["_teams"]:
        if str(tid) not in cache:
            players, page = [], 1
            while True:
                time.sleep(7)            # stay well under the per-minute cap
                data = get("players", {"league": LEAGUE, "season": SEASON, "team": tid, "page": page})
                players += data["response"]
                if page >= min(data["paging"]["total"], 3):   # free plan: max page 3
                    break
                page += 1
            cache[str(tid)] = players
            CACHE.write_text(json.dumps(cache))      # save progress after every team
            print(name, len(players), "players")
        rows += cache[str(tid)]
    return rows

def flatten(rows):
    recs = []
    for r in rows:
        p = r["player"]
        for s in r["statistics"]:
            g = s["games"]
            recs.append({
                "player": f"{p.get('firstname') or ''} {p.get('lastname') or ''}".strip() or p["name"],
                "short_name": p["name"], "team": s["team"]["name"], "age": p["age"],
                "position": g["position"], "minutes": g["minutes"] or 0,
                "goals": s["goals"]["total"] or 0,
                "shots": s["shots"]["total"] or 0, "shots_on_target": s["shots"]["on"] or 0,
                "duels_total": s["duels"]["total"] or 0, "duels_won": s["duels"]["won"] or 0,
                "tackles": s["tackles"]["total"] or 0, "interceptions": s["tackles"]["interceptions"] or 0,
                "key_passes": s["passes"]["key"] or 0,
            })
    return pd.DataFrame(recs)

if __name__ == "__main__":
    if not KEY:
        raise SystemExit("Set APIFOOTBALL_KEY first (export APIFOOTBALL_KEY=...)")
    df = flatten(pull())
    n90 = df.minutes / 90
    df["duels_won_pct"] = (100 * df.duels_won / df.duels_total).where(df.duels_total > 0)
    df["tackles_int_per90"] = (df.tackles + df.interceptions) / n90
    df["key_passes_per90"] = df.key_passes / n90
    df["source"] = f"api-football {LEAGUE}/{SEASON}"
    df.to_csv("data/processed/players_api.csv", index=False)
    print(df.shape, "rows saved to data/processed/players_api.csv")
    print(df.position.value_counts().to_string())
