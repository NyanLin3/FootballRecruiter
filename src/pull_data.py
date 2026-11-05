import sys
from pathlib import Path
import requests

season = sys.argv[1] if len(sys.argv) > 1 else "2627"
RAW = Path("data/raw")
RAW.mkdir(parents=True, exist_ok=True)
r = requests.get(f"https://www.football-data.co.uk/mmz4281/{season}/E0.csv",
                 headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
r.raise_for_status()
(RAW / f"epl_{season}.csv").write_bytes(r.content)
print("saved", season, len(r.content), "bytes")
