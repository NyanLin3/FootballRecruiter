import pandas as pd
from diagnose import zscores, METRICS
from needs import team_needs

CFG = {"threshold_sd": -1.0, "rules": [
    {"weakness": ["sot_pct", "goals_per_shot"], "position": "striker"},
    {"type": "defence", "volume": "shots_against_pg", "quality": ["sot_against_pg"],
     "volume_position": "defensive_midfielder", "quality_position": "centre_back", "both_position": "team_defence"},
    {"type": "keeper", "metric": "ga_per_sot", "unless_weak": "sot_against_pg",
     "position": "goalkeeper", "max_level": "watch"},
]}

def _z(**over):
    base = {c: 0.0 for c in METRICS}
    base.update(over)
    return pd.DataFrame([base], index=["T"])

def test_negative_z_is_weakness():
    m = pd.DataFrame({c: [1.0, 2.0, 3.0] for c in METRICS}, index=["a", "b", "c"])
    z = zscores(m)
    assert z.loc["a", "gf_pg"] < 0   # scores least = weak
    assert z.loc["a", "ga_pg"] > 0   # concedes least = strong

def test_striker_flag():
    n = team_needs("T", _z(goals_per_shot=-1.5), CFG)
    assert list(n.position) == ["striker"] and n.iloc[0].level == "FLAG"

def test_both_defence_problems_merge():
    n = team_needs("T", _z(shots_against_pg=-1.2, sot_against_pg=-1.3), CFG)
    assert list(n.position) == ["team_defence"]

def test_keeper_is_watch_only_and_needs_ok_shot_quality():
    n = team_needs("T", _z(ga_per_sot=-1.5), CFG)
    assert list(n.position) == ["goalkeeper"] and n.iloc[0].level == "watch"
    n = team_needs("T", _z(ga_per_sot=-1.5, sot_against_pg=-1.2), CFG)
    assert "goalkeeper" not in list(n.position)
