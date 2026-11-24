import unicodedata
import pandas as pd

def norm(s):
    return unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()

d = pd.read_csv("data/processed/players_api.csv")
d = d[(d.position == "Defender") & (d.minutes >= 900)]
names = [norm(n.strip()) for n in open("data/players/cb_names.txt") if n.strip()]
d = d[d.player.apply(lambda x: any(n in norm(x) for n in names))]
cols = ["player", "team", "age", "minutes", "duels_won_pct", "tackles_int_per90", "key_passes_per90", "source"]
out = d[cols].round(2)
out.to_csv("data/players/centrebacks_api.csv", index=False)
print(out.to_string(index=False))
print(len(out), "players")
