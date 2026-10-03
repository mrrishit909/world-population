"""Step 1: the United Nations World Population Prospects 2024 (Population Division, UN DESA): two CSV files.

    ./venv/bin/python download.py   -> data/WPP2024_Demographic_Indicators_Medium.csv.gz, data/WPP2024_TotalPopulationBySex.csv.gz, results/pull.json

Licence CC BY 3.0 IGO. Citation: United Nations, Department of Economic and Social Affairs, Population Division (2024). World Population Prospects 2024, Online Edition.
Demographic_Indicators_Medium: 237 countries or areas, regions and groups, 1950 to 2100, medium variant (population, density, growth rate, fertility, ...).
TotalPopulationBySex: the same places with the other variants (low, high, ...) and the 80% and 95% prediction intervals, from 2024.
The files are 33 MB together, so they are not committed; this script fetches them.
"""
import gzip
import hashlib
import json
import ssl
import urllib.request
from datetime import date
from pathlib import Path

import certifi

HERE = Path(__file__).parent
BASE = "https://population.un.org/wpp/assets/Excel%20Files/1_Indicator%20(Standard)/CSV_FILES/"
FILES = ("WPP2024_Demographic_Indicators_Medium.csv.gz", "WPP2024_TotalPopulationBySex.csv.gz")
CTX = ssl.create_default_context(cafile=certifi.where())


def main():
    (HERE / "data").mkdir(exist_ok=True)
    (HERE / "results").mkdir(exist_ok=True)
    info = {"pulled": date.today().isoformat(), "files": {}}
    for name in FILES:
        blob = urllib.request.urlopen(urllib.request.Request(BASE + name, headers={"User-Agent": "research-portfolio (Rishit Raj Mathur)"}), context=CTX, timeout=300).read()
        (HERE / "data" / name).write_bytes(blob)
        with gzip.open(HERE / "data" / name, "rt", encoding="utf-8") as f:
            rows = sum(1 for _ in f) - 1
        info["files"][name] = {"url": BASE + name, "bytes": len(blob), "rows": rows, "sha256": hashlib.sha256(blob).hexdigest()}
    (HERE / "results" / "pull.json").write_text(json.dumps(info, indent=2) + "\n")
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
