# FootballRecruiter

A need-based recruitment tool for football clubs. Instead of asking "who are the best players?", it asks "what is this team bad at, how much should I trust that, and which players could fix it?"

Test case: Manchester United, 2026/27 Premier League. Goal: every team across the big leagues.

## How it works
1. **Diagnose:** for each team, take the last 10 league matches and compute shots, shots on target, goals, shots and goals conceded, fouls and cards. Convert each to a z-score against the other teams, with the sign flipped so a negative number is a weakness on every metric. The 10-game window is blended 50/50 with the full-season baseline (identical until a team passes 10 games).
2. **Map weaknesses to needs:** `config/needs_map.yaml` holds the rules. A FLAG is -1 SD or worse, a watch is -0.5 SD or worse.
3. **Backtest:** `src/backtest.py` checks which metrics from the first 10 games still hold for the rest of the season, over three past seasons. The rules were rebuilt around what persisted.
4. **Score players:** `src/score_players.py` ranks candidates for a position using weights from the YAML (percentile within the pool).
5. **Recommend:** `src/recommend.py` takes a team's flagged needs, attaches the evidence reliability from the backtest, and lists the top candidates at the matching position from outside that club.

## Rules (after the backtest)
- **Attack creation:** average of goals, shots and shots on target per game. Persistent in the backtest, so it can FLAG.
- **Striker (conversion):** shots on target % and goals per shot. Did not persist, so it can only trigger a watch.
- **Defence:** high shots against alone points to defensive midfield, high shots on target against alone points to centre back, and both together give one `team_defence` flag.
- **Fouls and cards:** a penalty in player scoring, not a need.
- **Goalkeeper proxy:** removed. It had no predictive value.

## Run it
```bash
python src/pull_data.py 2627       # season CSVs (also 2324, 2425, 2526)
python src/check_data.py           # builds data/processed/team_matches.csv
python src/diagnose.py             # builds data/processed/team_z.csv
python src/all_needs.py            # needs for all 20 teams
python src/report.py               # adds reliability labels
python src/backtest.py             # pooled backtest over three seasons
python src/score_players.py striker
python src/build_cb_file.py        # builds the centre-back file from data/players/cb_names.txt
python src/score_players.py centre_back data/players/centrebacks_api.csv
python src/recommend.py "Man United"   # shortlist for one team
python -m pytest tests/ -v
```
Run everything from the repo root.

## Getting the data
Nothing under `data/raw/` is committed, so rebuild it after cloning:
```bash
python src/pull_data.py 2324 && python src/pull_data.py 2425 && python src/pull_data.py 2526 && python src/pull_data.py 2627
python src/check_data.py                    # builds data/processed/team_matches.csv
export APIFOOTBALL_KEY="your-key"           # free key from API-Football; never commit it
python src/pull_players.py                  # builds data/processed/players_api.csv
```

## Data
- **Team data:** football-data.co.uk match CSVs (shots, shots on target, fouls, cards, corners). No xG.
- **Strikers:** hand-entered from public stats sites into `data/players/strikers.csv`, with a `source` column per row. Understat was the plan but was down throughout.
- **Centre-backs:** API-Football free tier, 2024/25 season, pulled team by team. Free plan limits: seasons 2022 to 2024 only, 3 pages per query.

## Backtest (2023/24 to 2025/26)
For each season I compared a team's z-score over its first 10 games with the same metric over the rest of the season (about 60 team-seasons).

| Metric | Pooled corr | Range across seasons |
|---|---|---|
| Shots against per game | 0.72 | 0.61 to 0.87 |
| Shots per game | 0.66 | 0.53 to 0.81 |
| Shots on target per game | 0.60 | 0.53 to 0.67 |
| Fouls per game | 0.56 | 0.34 to 0.70 |
| Shots on target against per game | 0.54 | 0.33 to 0.76 |
| Goals per game | 0.50 | 0.45 to 0.56 |
| Goals against per game | 0.48 | 0.37 to 0.68 |
| Discipline | 0.36 | 0.24 to 0.55 |
| Goals per shot | 0.15 | -0.10 to 0.33 |
| Shots on target % | 0.05 | -0.12 to 0.34 |
| Goalkeeper proxy (goals per shot on target faced) | -0.05 | -0.37 to 0.14 |

- **Persisted:** shot volume for and against, shots on target against, goals scored.
- **Did not persist:** conversion and the goalkeeper proxy. Teams flagged early on the proxy came back above average later.
- **Style adjustment dropped:** I tried adjusting for corner share. It correlated -0.78 with shots against and -0.63 with shots on target against, so it removed the signal for weak teams.

## Results so far (United at 11 games)
| Team | Need | Driver |
|---|---|---|
| Crystal Palace | team defence | shots against + shots on target against, -2.08 SD |
| Man United | centre back | shots on target against, -1.38 SD |
| Sunderland | attack creation | goals + shots + shots on target per game, -1.29 SD |
| Hull | team defence, attack creation | -1.24 and -1.16 SD |
| Ipswich | team defence | -1.20 SD |
| Coventry | defensive midfield | shots against, -1.12 SD |
| Chelsea | centre back | shots on target against, -1.09 SD |

This is a snapshot. Run `python src/all_needs.py` for the current list.

United concede goals and shots on target at a rate among the worst in the league (-1.47 and -1.38 SD blended) while allowing about an average number of shots (+0.08 SD), so the problem looks like the quality of chances conceded. Their attacking volume is the best in the league (shots per game +2.06 SD). Conversion (-1.09 SD) is only a watch because it did not persist in the backtest.

## Player scoring
**Strikers (hand-entered, 2025/26):** score is a weighted percentile within the pool: xG per 90 (0.40), shots per 90 (0.25), xA per 90 (0.15), shots on target % (0.10), goals minus xG per 90 (0.10). Finishing gets a low weight because conversion did not persist in the team backtest. Players under 1,800 minutes are marked `thin`. xG per shot is shown but not scored, since xG per 90 already includes it.
- **Finding:** Cunha takes about 3.2 shots per 90 but only 0.08 xG per shot, against 0.14 to 0.25 for everyone else in the pool. His goals minus xG is positive, so it looks like shot quality, not finishing.
- **Source check:** per the `source` column, xG comes from xgEdge and counts from StatMuse (10 rows) or FBref (5 rows). Haaland, Cunha and the other spot-checked counts matched FBref.

**Centre-backs (API-Football, 2024/25):** scored on duels won %, tackles plus interceptions per 90 and key passes per 90. The script keeps only the stats present in the file and re-weights the rest. Centre-backs are picked by name, because the API labels players only Defender, Midfielder, Attacker or Goalkeeper.
- **Source check:** Haaland's goals (22) and shots on target (60) matched FBref, but his shots did not (92 vs 109), so the API's shot stats are not used. Saliba's minutes, duels and tackles matched Sofascore.

## Recommendations
For a team, `recommend.py` lists each flagged need with its evidence reliability (high, medium or low, from the backtest correlation of the driving stat) and the top-scoring candidates at that position from other clubs. Needs without a player table yet (defensive midfield, attack creation, team defence) say so. It is a shortlist from the tables above, not a signing recommendation: the data is hand-picked and the centre-back table is two seasons old.

## Known limitations
- 10 games per team. One flag is a lead, not proof.
- Goals per shot cannot separate bad finishing from bad chances. Team-level xG is needed for that.
- Team stats alone cannot establish a striker need.
- A team-level centre-back need cannot separate the centre-backs from the goalkeeper, full-backs or midfield in front of them.
- Player scores are percentiles within a hand-picked pool, not the whole league. Percentiles hide the size of gaps, and the thin-sample cutoff is arbitrary.
- The centre-back table is two seasons old (the free API plan stops at 2024/25) and ages are from that season. It scores defensive volume, which partly reflects how much a defender is exposed, and it has no aerial, recovery or progressive passing data.
- The striker table is 2025/26 and the team diagnosis is 2026/27, so the two should not be linked directly.
- League games only, no cups.

## Dev log
- **Setup:** repo, venv, folder structure. Fixed GitHub login with the GitHub CLI after password auth failed.
- **Data:** the `understat` package failed, then the site went down. Switched to football-data.co.uk CSVs.
- **Diagnosis and needs:** per-team z-scores over a 10-game window, YAML rules, all 20 teams. Bugs hit: empty YAML returning `None`, a duplicate rule that kept firing, and scripts run from the wrong folder.
- **Rule merges:** fouls became penalty-only, and the CB and DM rules merged into one defence rule so one problem no longer gets two flags.
- **Backtest:** one season showed noise, three pooled seasons gave a clearer picture. Rebuilt the rules around what persisted: dropped the goalkeeper proxy, made conversion watch-only, averaged the attack metrics.
- **United striker flag:** a 4-4 draw with Aston Villa (4 goals from 26 shots) moved United's goals per shot from -1.18 to -0.98 SD and the flag disappeared, consistent with the backtest on conversion. Later United's centre-back need became a hard flag.
- **Style adjustment:** tested and rejected, see Backtest.
- **Tests:** 4 pytest tests covering the z-score sign convention and the needs rules.
- **Players:** hand-filled striker table, scoring script, xG per shot and thin-sample flag. Generalised the script to other positions.
- **Player API:** hit two free-plan limits (seasons, then pages), so the pull runs team by team on 2024/25. Spot-checked against FBref and Sofascore. Fixed accent matching for names like Martínez. Stopped tracking third-party data files in git.

## Next
- Age filter, and a current-season centre-back table (hand-filled or a paid data plan)
- Player tables for defensive midfield and attack creation
- Squad-fit check and overlaps between clubs
- Other leagues, and an automated refresh
