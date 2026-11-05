from prep import to_long

long = to_long("data/raw/epl_2627.csv")
long.to_csv("data/processed/team_matches.csv", index=False)
print(long[long.team == "Man United"].tail(10).to_string(index=False))
