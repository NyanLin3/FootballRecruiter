from pathlib import Path
import requests

RAW = Path("data/raw")
URL = "https://www.football-data.co.uk/mmz4281/2627/E0.csv"  # 2026/27 Premier League

RAW.mkdir(parents=True, exist_ok=True)
r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
r.raise_for_status()
(RAW / "epl_2627.csv").write_bytes(r.content)
print("saved", len(r.content), "bytes")
