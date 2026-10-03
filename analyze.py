"""Steps 2-4: audit the files, follow the world's population with its uncertainty, then growth, distribution, density and the year each country peaks.

    ./venv/bin/python analyze.py
        -> results/audit.csv  world_years.csv  world_peaks.csv  concentration.csv  half_of_humanity.csv  regions.csv  shrinking.csv  countries.csv  density_top.csv  summary.csv

Population is in thousand people (the UN's unit). The estimates run to 2023 and the projections start in 2024. "Countries" are the UN's "countries or areas"; the analysis of growth,
peaks and density keeps the 161 with at least one million people in 2023 and leaves out the 76 smaller ones, so that a few thousand people on an island do not count as a country's trend.
"""
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
R = HERE / "results"
FIRST, LAST = 1950, 2100
CONTINENTS = ["Africa", "Asia", "Europe", "Latin America and the Caribbean", "Northern America", "Oceania"]
BOUNDS = {"Low": "low", "High": "high", "Median PI": "median_pi", "Lower 95 PI": "lo95", "Upper 95 PI": "hi95", "Lower 80 PI": "lo80", "Upper 80 PI": "hi80"}


def main():
    R.mkdir(exist_ok=True)
    di = pd.read_csv(HERE / "data" / "WPP2024_Demographic_Indicators_Medium.csv.gz", low_memory=False,
                     usecols=["Location", "LocTypeName", "ISO3_code", "Time", "TPopulation1Jan", "TPopulation1July", "PopDensity", "PopGrowthRate"])
    ps = pd.read_csv(HERE / "data" / "WPP2024_TotalPopulationBySex.csv.gz", low_memory=False, usecols=["Location", "Variant", "Time", "PopTotal"])
    di = di[(di["Time"] >= FIRST) & (di["Time"] <= LAST)]
    c = di[di["LocTypeName"] == "Country/Area"]; world = di[di["Location"] == "World"].set_index("Time")
    P = "TPopulation1July"

    # Step 2: audit
    big = c[(c["Time"] == 2023) & (c[P] >= 1000)]["Location"]; cb = c[c["Location"].isin(big)].copy()
    cs = c.sort_values(["Location", "Time"]); nxt = cs.groupby("Location")["TPopulation1Jan"].shift(-1); ok = nxt.notna()
    growth_gap = float((100 * np.log(nxt[ok] / cs.loc[ok, "TPopulation1Jan"]) - cs.loc[ok, "PopGrowthRate"]).abs().max())
    reg = di[(di["LocTypeName"] == "Geographic region") & di["Location"].isin(CONTINENTS)]; ps_world = ps[ps["Location"] == "World"]
    medium_ps = ps_world[ps_world["Variant"] == "Medium"].set_index("Time")["PopTotal"]
    audit = [("countries or areas", c["Location"].nunique()), ("first year", FIRST), ("last year", LAST),
             ("world minus the sum of the countries, largest gap in any year (thousand people)", (world[P] - c.groupby("Time")[P].sum()).abs().max()),
             ("world minus the sum of the six continents, largest gap in any year (thousand people)", (world[P] - reg.groupby("Time")[P].sum()).abs().max()),
             ("countries or areas with at least one million people in 2023", len(big)),
             ("medium path, world, in the two files, largest gap 2024 to 2100 (thousand people)", (medium_ps.loc[2024:LAST] - world.loc[2024:LAST, P]).abs().max()),
             ("growth rate against 100 x ln(population on 1 January next year / this year), largest gap (percentage points)", growth_gap)]
    pd.DataFrame(audit, columns=["check", "value"]).to_csv(R / "audit.csv", index=False)

    # Step 3: the world's path, its uncertainty, and when it peaks
    wy = pd.DataFrame({"year": range(FIRST, LAST + 1)}).set_index("year"); wy["medium"] = world[P]; wy["growth_rate_pct"] = world["PopGrowthRate"]
    pw = ps_world.pivot(index="Time", columns="Variant", values="PopTotal")
    for v, name in BOUNDS.items():
        wy[name] = pw[v]
    wy.round(6).reset_index().to_csv(R / "world_years.csv", index=False)
    peaks = []
    for name in ["medium"] + list(BOUNDS.values()):
        s = wy[name].dropna(); yr = int(s.idxmax()); peaks.append({"series": name, "peak_year": yr, "peak_billion": s.loc[yr] / 1e6, "billion_in_2100": s.loc[LAST] / 1e6})
    pd.DataFrame(peaks).round(6).to_csv(R / "world_peaks.csv", index=False)

    # distribution: how many countries make up half of humanity, and the continents' shares
    conc, half = [], []
    for yr, t in c.groupby("Time"):
        t = t.sort_values(P, ascending=False); share = 100 * t[P].cumsum() / t[P].sum(); n = int((share < 50).sum() + 1)
        conc.append({"year": yr, "n_half": n, "top10_share_pct": share.iloc[9], "largest": t["Location"].iloc[0], "largest_share_pct": share.iloc[0]})
        if yr in (1950, 2023, 2100):
            half += [{"year": yr, "rank": i + 1, "country": t["Location"].iloc[i], "population": t[P].iloc[i], "cumulative_share_pct": share.iloc[i]} for i in range(n)]
    pd.DataFrame(conc).round(6).to_csv(R / "concentration.csv", index=False); pd.DataFrame(half).round(6).to_csv(R / "half_of_humanity.csv", index=False)
    rg = reg[["Location", "Time", P]].rename(columns={"Location": "region", "Time": "year", P: "population"})
    rg["share_pct"] = 100 * rg["population"] / rg.groupby("year")["population"].transform("sum"); rg.sort_values(["region", "year"]).round(6).to_csv(R / "regions.csv", index=False)

    # Step 4: shrinking countries, peaks and density among the countries with at least one million people in 2023
    shr = cb.groupby("Time")["PopGrowthRate"].agg(shrinking=lambda v: int((v < 0).sum()), countries="size").reset_index().rename(columns={"Time": "year"}); shr.to_csv(R / "shrinking.csv", index=False)
    pk = cb.loc[cb.groupby("Location")[P].idxmax()].set_index("Location")
    at = lambda yr, col: cb[cb["Time"] == yr].set_index("Location")[col]
    ct = pd.DataFrame({"iso3": pk["ISO3_code"], "pop_2023": at(2023, P), "pop_2100": at(2100, P), "peak_year": pk["Time"], "peak_population": pk[P], "growth_2023_pct": at(2023, "PopGrowthRate"), "density_2023": at(2023, "PopDensity")})
    ct["change_2023_2100_pct"] = 100 * (ct["pop_2100"] / ct["pop_2023"] - 1)
    ct["status"] = np.where(ct["peak_year"] <= 2023, "peaked by 2023", np.where(ct["peak_year"] >= LAST, "still growing in 2100", "peaks 2024 to 2099"))
    ct = ct.sort_values("pop_2023", ascending=False).reset_index(); ct.round(6).to_csv(R / "countries.csv", index=False)
    top = ct.sort_values("density_2023", ascending=False).head(10)[["Location", "density_2023", "pop_2023"]]; top.round(6).to_csv(R / "density_top.csv", index=False)
    s23 = ct["pop_2023"].sum(); dens = ct["density_2023"]
    summ = {"countries_1m_2023": len(ct), "world_2023": world.loc[2023, P], "world_1950": world.loc[1950, P], "world_2100": world.loc[LAST, P],
            "shrinking_1990": int(shr.loc[shr["year"] == 1990, "shrinking"].iloc[0]), "shrinking_2023": int(shr.loc[shr["year"] == 2023, "shrinking"].iloc[0]),
            "shrinking_2050": int(shr.loc[shr["year"] == 2050, "shrinking"].iloc[0]), "shrinking_2100": int(shr.loc[shr["year"] == LAST, "shrinking"].iloc[0]),
            "peaked_by_2023": int((ct["peak_year"] <= 2023).sum()), "peaked_by_2050": int((ct["peak_year"] <= 2050).sum()), "still_growing_2100": int((ct["peak_year"] >= LAST).sum()),
            "share_of_world_2023_in_peaked_countries_pct": 100 * ct.loc[ct["peak_year"] <= 2023, "pop_2023"].sum() / world.loc[2023, P],
            "median_density_2023": dens.median(), "weighted_density_2023": float(np.average(dens, weights=ct["pop_2023"])),
            "world_growth_peak_year": int(wy["growth_rate_pct"].idxmax()), "world_growth_peak_pct": wy["growth_rate_pct"].max(), "world_growth_2023_pct": wy.loc[2023, "growth_rate_pct"],
            "world_growth_first_negative_year": int(wy.index[wy["growth_rate_pct"] < 0][0]), "world_growth_2100_pct": wy.loc[LAST, "growth_rate_pct"], "people_in_countries_over_1m_share_of_world_2023_pct": 100 * s23 / world.loc[2023, P]}
    pd.DataFrame(list(summ.items()), columns=["key", "value"]).round(6).to_csv(R / "summary.csv", index=False)

    for f in ("audit", "world_peaks", "summary", "density_top"):
        print("==", f); print(pd.read_csv(R / f"{f}.csv").to_string(index=False))
    print(pd.read_csv(R / "concentration.csv").query("year in [1950, 2023, 2100]").to_string(index=False))
    print(ct["status"].value_counts().to_string()); print(pd.read_csv(R / "regions.csv").query("year in [1950, 2023, 2100]").pivot(index="region", columns="year", values="share_pct").round(1).to_string())


if __name__ == "__main__":
    main()
