# FootballRecruiter

A need-based recruitment tool for football clubs. Instead of asking "who are the best players?", it asks "what is this team bad at, and which players would fix it?"

Test case: Manchester United, 2026/27 Premier League. Goal: run it for every team across the big leagues.

## How it works
1. **Diagnose:** take each team's last 10 league matches and compute shots on target %, goals per shot, goals and shots conceded, fouls and cards. Convert each to a z-score vs the other teams, with the sign flipped so a negative number is a weakness on every metric.
2. **Map weaknesses to positions:** `config/needs_map.yaml` holds the rules (e.g. low goals per shot → striker). A rule can be flagged as `penalty_only` if it should affect player scoring but not count as a need.
3. **Flag needs:** a team gets a FLAG at -1 SD or worse and a "watch" at -0.5 SD.
4. **Score players** (not built yet): rank candidates for each flagged position.

## Run it
```bash
python src/pull_data.py     # downloads the season CSV to data/raw/
python src/check_data.py    # builds data/processed/team_matches.csv
python src/diagnose.py      # builds data/processed/team_z.csv
python src/needs.py "Man United"
python src/all_needs.py     # needs for all 20 teams
```
Run everything from the repo root.

## Data
- Match data: football-data.co.uk (shots, shots on target, fouls, cards). No xG.
- Player data: not pulled yet. Understat was the plan but the site is down.

## Results so far (9 games)
| Team | Flag | Driver |
|---|---|---|
| Man United | striker | goals per shot, -1.18 SD |
| Nott'm Forest | striker | shots on target %, -2.14 SD |
| Crystal Palace | centre back | goals against, -2.17 SD |

United's shots against are better than average (+0.78 SD) but their shots on target against and goals against are worse, so the issue looks like shot quality conceded, not volume.

## Known limitations
- Only 9 games per team, so one flag is a lead and not proof.
- Goals per shot can't separate bad finishing from bad chances. xG is needed for that.
- The CB rule can't tell a bad centre back from a bad goalkeeper.
- Defensive rules overlap (shots against and goals against), so a team can get double flags for one problem.
- League games only, no cups.

## Dev log
- **Setup:** created the repo, Python venv, folder structure. Fixed GitHub login by using the GitHub CLI after password auth failed.
- **Data source:** `understat` package failed (JSONDecodeError) because the data isn't in the page anymore, then the site went down. Switched to football-data.co.uk CSVs.
- **Diagnosis:** built per-team metrics over a rolling 10-game window and z-scores across the league.
- **Needs engine:** YAML rules turn z-scores into flagged positions. Hit a bug where an empty YAML file returned `None`.
- **League check:** ran it for all 20 teams. The fouls rule flagged 6 clubs but isn't a real position need, so I made it `penalty_only`. I added a second copy of the rule instead of editing the first, which kept it firing until I deleted the duplicate.
- **Lesson:** run scripts from the repo root, because the paths are relative.

## Next
- Player data (xG, shots per 90, minutes) when a source is available
- `score_players.py`, starting with strikers
- Fix the overlapping defensive rules
- Goalkeeper rule
- Extend to the other leagues