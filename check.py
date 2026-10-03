"""Step 5: the project's check. Recompute with different code: plain Python on the raw UN files (gzip and csv, no pandas). The audit (including what the UN's growth-rate column is: 100 x ln of the
1 January population next year over this year), the world's path and the peak of each scenario and interval curve, how many countries make up half of humanity, the continents' shares, the
count of shrinking countries by year, every country's peak year, change and density, the median and the population-weighted density, and the summary figures.

    ./venv/bin/python check.py          (run download.py first: the raw files are not committed)
"""
import csv
import gzip
import math
from pathlib import Path

HERE = Path(__file__).parent
R = HERE / "results"
CONTINENTS = ["Africa", "Asia", "Europe", "Latin America and the Caribbean", "Northern America", "Oceania"]
BOUNDS = {"Low": "low", "High": "high", "Median PI": "median_pi", "Lower 95 PI": "lo95", "Upper 95 PI": "hi95", "Lower 80 PI": "lo80", "Upper 80 PI": "hi80"}
FIRST, LAST = 1950, 2100
n_ok = 0


def same(label, got, want, abs_tol=1e-6):
    global n_ok
    n_ok += 1
    assert abs(float(got) - float(want)) <= abs_tol, f"{label}: recount {got} != results {want}"


def eq(label, got, want):
    global n_ok
    n_ok += 1
    assert got == want, f"{label}: recount {got!r} != results {want!r}"


def table(name):
    return list(csv.DictReader(open(R / f"{name}.csv")))


def main():
    countries, world, cont, years = {}, {}, {c: {} for c in CONTINENTS}, range(FIRST, LAST + 1)
    with gzip.open(HERE / "data" / "WPP2024_Demographic_Indicators_Medium.csv.gz", "rt", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            t = int(r["Time"])
            if not FIRST <= t <= LAST:
                continue
            rec = {"jan": float(r["TPopulation1Jan"]), "jul": float(r["TPopulation1July"]), "dens": float(r["PopDensity"]), "gr": float(r["PopGrowthRate"]), "iso3": r["ISO3_code"]}
            if r["LocTypeName"] == "Country/Area":
                countries.setdefault(r["Location"], {})[t] = rec
            elif r["LocTypeName"] == "World":
                world[t] = rec
            elif r["LocTypeName"] == "Geographic region" and r["Location"] in cont:
                cont[r["Location"]][t] = rec
    ps = {}
    with gzip.open(HERE / "data" / "WPP2024_TotalPopulationBySex.csv.gz", "rt", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["Location"] == "World" and (r["Variant"] in BOUNDS or r["Variant"] == "Medium") and FIRST <= int(r["Time"]) <= LAST:
                ps[(r["Variant"], int(r["Time"]))] = float(r["PopTotal"])
    assert len(world) == 151 and all(len(v) == 151 for v in countries.values()) and all(len(v) == 151 for v in cont.values())

    # audit
    a = {r["check"]: float(r["value"]) for r in table("audit")}
    big = sorted(n for n, v in countries.items() if v[2023]["jul"] >= 1000)
    same("countries or areas", len(countries), a["countries or areas"]); same("first year", min(world), a["first year"]); same("last year", max(world), a["last year"])
    same("world minus countries", max(abs(world[t]["jul"] - sum(v[t]["jul"] for v in countries.values())) for t in years), a["world minus the sum of the countries, largest gap in any year (thousand people)"], 1e-6)
    same("world minus continents", max(abs(world[t]["jul"] - sum(v[t]["jul"] for v in cont.values())) for t in years), a["world minus the sum of the six continents, largest gap in any year (thousand people)"], 1e-6)
    same("countries with one million", len(big), a["countries or areas with at least one million people in 2023"])
    same("medium in two files", max(abs(ps[("Medium", t)] - world[t]["jul"]) for t in range(2024, LAST + 1)), a["medium path, world, in the two files, largest gap 2024 to 2100 (thousand people)"], 1e-6)
    gap = max(abs(100 * math.log(v[t + 1]["jan"] / v[t]["jan"]) - v[t]["gr"]) for v in countries.values() for t in range(FIRST, LAST))
    same("growth rate definition", gap, a["growth rate against 100 x ln(population on 1 January next year / this year), largest gap (percentage points)"], 1e-6); assert gap < 0.001

    # the world's path and its peaks
    wy = {int(r["year"]): r for r in table("world_years")}
    for t in years:
        same(f"medium {t}", world[t]["jul"], wy[t]["medium"]); same(f"growth {t}", world[t]["gr"], wy[t]["growth_rate_pct"])
        for v, name in BOUNDS.items():
            if t >= 2024:
                same(f"{name} {t}", ps[(v, t)], wy[t][name])
            else:
                eq(f"{name} {t} blank", wy[t][name], "")
    series = {"medium": {t: world[t]["jul"] for t in years}, **{name: {t: ps[(v, t)] for t in range(2024, LAST + 1)} for v, name in BOUNDS.items()}}
    for r in table("world_peaks"):
        s = series[r["series"]]; yr = max(s, key=lambda t: (s[t], -t))
        eq(f"peak year {r['series']}", yr, int(r["peak_year"])); same("peak", s[yr] / 1e6, r["peak_billion"]); same("2100", s[LAST] / 1e6, r["billion_in_2100"])

    # distribution
    def ranked(t):
        return sorted(((v[t]["jul"], n) for n, v in countries.items()), key=lambda x: (-x[0], x[1]))
    half = {}
    for r in table("concentration"):
        t = int(r["year"]); rk = ranked(t); tot = sum(p for p, _ in rk); cum = 0; n_half = None
        for i, (p, n) in enumerate(rk):
            cum += p
            if n_half is None and cum / tot >= 0.5:
                n_half = i + 1
        eq(f"n_half {t}", n_half, int(r["n_half"])); same(f"top10 {t}", 100 * sum(p for p, _ in rk[:10]) / tot, r["top10_share_pct"]); eq(f"largest {t}", rk[0][1], r["largest"]); same("largest share", 100 * rk[0][0] / tot, r["largest_share_pct"])
        half[t] = (n_half, rk, tot)
    for r in table("half_of_humanity"):
        t = int(r["year"]); n_half, rk, tot = half[t]; i = int(r["rank"]) - 1
        eq(f"half list {t} {i}", rk[i][1], r["country"]); same("population", rk[i][0], r["population"]); same("cumulative", 100 * sum(p for p, _ in rk[:i + 1]) / tot, r["cumulative_share_pct"])
    assert {int(r["year"]) for r in table("half_of_humanity")} == {1950, 2023, 2100} and all(sum(1 for r in table("half_of_humanity") if int(r["year"]) == t) == half[t][0] for t in (1950, 2023, 2100))
    for r in table("regions"):
        t = int(r["year"]); same(f"region {r['region']} {t}", cont[r["region"]][t]["jul"], r["population"]); same("share", 100 * cont[r["region"]][t]["jul"] / sum(v[t]["jul"] for v in cont.values()), r["share_pct"])

    # shrinking countries, peaks, density
    for r in table("shrinking"):
        t = int(r["year"]); same(f"shrinking {t}", sum(countries[n][t]["gr"] < 0 for n in big), r["shrinking"]); same("countries", len(big), r["countries"])
    rows = {r["Location"]: r for r in table("countries")}; eq("same 161 countries", sorted(rows), big)
    for n in big:
        v = countries[n]; yr = max(years, key=lambda t: (v[t]["jul"], -t)); r = rows[n]
        eq(f"iso3 {n}", v[2023]["iso3"], r["iso3"]); same(f"pop_2023 {n}", v[2023]["jul"], r["pop_2023"]); same("pop_2100", v[LAST]["jul"], r["pop_2100"]); eq(f"peak year {n}", yr, int(r["peak_year"])); same("peak population", v[yr]["jul"], r["peak_population"])
        same("growth_2023", v[2023]["gr"], r["growth_2023_pct"]); same("density_2023", v[2023]["dens"], r["density_2023"]); same("change", 100 * (v[LAST]["jul"] / v[2023]["jul"] - 1), r["change_2023_2100_pct"])
        eq(f"status {n}", "peaked by 2023" if yr <= 2023 else "still growing in 2100" if yr >= LAST else "peaks 2024 to 2099", r["status"])
    order = [r["Location"] for r in table("countries")]; assert order == sorted(big, key=lambda n: -countries[n][2023]["jul"]), "countries.csv is sorted by 2023 population"
    dens = sorted(((countries[n][2023]["dens"], n) for n in big), reverse=True)
    for r, (d, n) in zip(table("density_top"), dens[:10]):
        eq("density_top name", n, r["Location"]); same("density_top value", d, r["density_2023"]); same("density_top pop", countries[n][2023]["jul"], r["pop_2023"])
    vals = sorted(d for d, _ in dens); med = vals[len(vals) // 2] if len(vals) % 2 else (vals[len(vals) // 2 - 1] + vals[len(vals) // 2]) / 2
    wmean = sum(countries[n][2023]["dens"] * countries[n][2023]["jul"] for n in big) / sum(countries[n][2023]["jul"] for n in big)
    peak = {n: max(years, key=lambda t: (countries[n][t]["jul"], -t)) for n in big}
    sm = {r["key"]: float(r["value"]) for r in table("summary")}
    exp = {"countries_1m_2023": len(big), "world_2023": world[2023]["jul"], "world_1950": world[1950]["jul"], "world_2100": world[LAST]["jul"],
           **{f"shrinking_{t}": sum(countries[n][t]["gr"] < 0 for n in big) for t in (1990, 2023, 2050, 2100)},
           "peaked_by_2023": sum(peak[n] <= 2023 for n in big), "peaked_by_2050": sum(peak[n] <= 2050 for n in big), "still_growing_2100": sum(peak[n] >= LAST for n in big),
           "share_of_world_2023_in_peaked_countries_pct": 100 * sum(countries[n][2023]["jul"] for n in big if peak[n] <= 2023) / world[2023]["jul"],
           "median_density_2023": med, "weighted_density_2023": wmean,
           "world_growth_peak_year": max(years, key=lambda t: (world[t]["gr"], -t)), "world_growth_peak_pct": max(world[t]["gr"] for t in years), "world_growth_2023_pct": world[2023]["gr"],
           "world_growth_first_negative_year": min(t for t in years if world[t]["gr"] < 0), "world_growth_2100_pct": world[LAST]["gr"],
           "people_in_countries_over_1m_share_of_world_2023_pct": 100 * sum(countries[n][2023]["jul"] for n in big) / world[2023]["jul"]}
    eq("summary keys", sorted(sm), sorted(exp))
    for k, v in exp.items():
        same(f"summary {k}", v, sm[k])
    print(f"check.py: {n_ok} recomputed numbers agree with results/ (the UN's growth rate is 100 x ln(Jan 1 population next year / this year) to within {gap:.4f} points)")


if __name__ == "__main__":
    main()
