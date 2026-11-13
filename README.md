# FootballRecruiter

A need-based recruitment tool for football clubs. Instead of asking "who are the best players?", it asks "what is this team bad at, how much should I trust that, and which players could fix it?"

Test case: Manchester United, 2026/27 Premier League. Goal: every team across the big leagues.

## How it works
1. **Diagnose:** for each team, take the last 10 league matches and compute shots, shots on target, goals, shots and goals conceded, fouls and cards. Convert each to a z-score against the other teams, with the sign flipped so a negative number is a weakness on every metric. A 10-game window is blended with the full-season baseline (they are identical until a team passes 10 games).
2. **Map weaknesses to needs:** `config/needs_map.yaml` holds the rules. A FLAG is -1 SD or worse, a watch is -0.5 SD or worse.
3. **Label reliability:** `src/report.py` attaches a reliability label to each need from the backtest (high at 0.6+, medium at 0.4+, otherwise low).
4. **Score players:** `src/score_players.py` ranks hand-entered candidates for a position using weights from the YAML.

## Rules (after the backtest)
- **Attack creation:** average of goals, shots and shots on target per game. Persistent in the backtest, so it can FLAG.
- **Striker (conversion):** shots on target % and goals per shot. Did not persist, so it can only trigger a watch.
- **Defence:** high shots against alone points to defensive midfield, high shots on target against alone points to centre back, and both together give one `team_defence` flag.
- **Fouls and cards:** used as a penalty in player scoring, not as a need.
- **Goalkeeper proxy:** removed. It had no predictive value.

## Run it
```bash
python src/pull_data.py            # current season CSV (also: 2324, 2425, 2526)
python src/check_data.py           # builds data/processed/team_matches.csv
python src/diagnose.py             # builds data/processed/team_z.csv
python src/all_needs.py            # needs for all 20 teams
python src/report.py               # adds reliability labels
python src/backtest.py             # pooled backtest over three seasons
python src/score_players.py        # ranks data/players/strikers.csv
python -m pytest tests/ -v
```
Run everything from the repo root.

## Data
- Team data: football-data.co.uk match CSVs (shots, shots on target, fouls, cards, corners). No xG.
- Player data: hand-entered from public stats sites into `data/players/`, with a `source` column per row. Understat was the plan but the site has been down.

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

## Results so far (10 games)
| Team | Need | Driver |
|---|---|---|
| Crystal Palace | team defence | shots against + shots on target against, -2.09 SD |
| Coventry | defensive midfield | shots against, -1.17 SD |
| Chelsea | centre back | shots on target against, -1.01 SD |
| Man United | no flags | watch: striker (conversion, low reliability), centre back (medium) |

United's attacking volume is the strongest in the league (shots per game +2.42 SD) but they concede on goals and shots on target (-1.11 and -0.90 SD) while allowing fewer shots than average. Run `python src/all_needs.py` for the full current list.

## Player scoring (strikers, first pass)
- 15 forwards entered by hand. Score = weighted percentile within the pool: xG per 90 (0.40), shots per 90 (0.25), xA per 90 (0.15), shots on target % (0.10), goals minus xG per 90 (0.10). Finishing gets a low weight because conversion did not persist in the team backtest.
- Players under 1,800 minutes are marked `thin`.
- **Finding:** Cunha takes about 3.2 shots per 90 but only 0.08 xG per shot, against 0.14 to 0.25 for everyone else in the pool. His goals minus xG is positive, so it looks like shot quality, not finishing.

## Known limitations
- 10 games per team. One flag is a lead, not proof.
- Goals per shot cannot separate bad finishing from bad chances. Team-level xG is needed for that.
- Team stats alone cannot establish a striker need.
- Player scores are percentiles within a hand-picked list, not the whole league. Percentiles hide the size of gaps, and the thin-sample cutoff is arbitrary.
- The player data covers a different period than the team diagnosis, so the two should not be linked directly.
- League games only, no cups.

## Dev log
- **Setup:** repo, venv, folder structure. Fixed GitHub login with the GitHub CLI after password auth failed.
- **Data:** the `understat` package failed, then the site went down. Switched to football-data.co.uk CSVs.
- **Diagnosis and needs:** per-team z-scores over a 10-game window, YAML rules, all 20 teams. Bugs hit: empty YAML returning `None`, a duplicate rule that kept firing, and scripts run from the wrong folder.
- **Rule merges:** fouls became penalty-only, and the CB and DM rules merged into one defence rule so one problem no longer gets two flags.
- **Backtest:** one season showed noise, three pooled seasons gave a clearer picture. Rebuilt the rules around what persisted.
- **United striker flag:** a 4-4 draw with Aston Villa (4 goals from 26 shots) moved United's goals per shot from -1.18 to -0.98 SD and the flag disappeared, consistent with the backtest on conversion.
- **Style adjustment:** tested and rejected, see Backtest.
- **Tests:** 4 pytest tests covering the z-score sign convention and the needs rules.
- **Players:** hand-filled striker table, scoring script, xG per shot and thin-sample flag.

## Next
- Centre-back table (duels, recoveries, progressive passes, aerial %), since that is United's best-supported need
- Squad-fit check and overlaps between clubs
- Player data from a real source when one is available
- Other leagues, and an automated refresh
