"""Step 6: charts.   ./venv/bin/python charts.py -> charts/00_cover.png, 01_world.png, 02_growth.png, 03_distribution.png, 04_density.png, 05_peaks.png"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
R = HERE / "results"
INK, DIM, GRID, BG, BLUE, ORANGE, GRAY, GREEN = "#f2f2f0", "#8a8a87", "#1d1d1d", "#0b0b0b", "#3987e5", "#d95926", "#9a9a96", "#3aa876"
plt.rcParams.update({"figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG, "text.color": INK,
                     "axes.edgecolor": "#3a3a3a", "axes.labelcolor": DIM, "xtick.color": DIM, "ytick.color": DIM,
                     "axes.grid": True, "axes.axisbelow": True, "grid.color": GRID, "grid.linewidth": 1,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "font.family": ["Helvetica Neue", "Arial", "DejaVu Sans"], "font.size": 11, "axes.titlesize": 13,
                     "axes.titlelocation": "left", "axes.titlepad": 12})
CONTINENTS = ["Asia", "Africa", "Europe", "Latin America and the Caribbean", "Northern America", "Oceania"]
CCOL = [BLUE, ORANGE, GRAY, GREEN, "#7fb2f0", "#c9a227"]
wy = pd.read_csv(R / "world_years.csv").set_index("year"); S = pd.read_csv(R / "summary.csv").set_index("key")["value"]


def save(fig, name):
    fig.tight_layout(); fig.savefig(HERE / "charts" / name, dpi=150); plt.close(fig)


def world(ax):
    y = wy.index.to_numpy(); f = wy.loc[2024:]
    ax.fill_between(f.index, f["lo95"] / 1e6, f["hi95"] / 1e6, color=BLUE, alpha=0.18, linewidth=0, label="95% interval")
    ax.fill_between(f.index, f["lo80"] / 1e6, f["hi80"] / 1e6, color=BLUE, alpha=0.32, linewidth=0, label="80% interval")
    ax.plot(f.index, f["low"] / 1e6, color=GRAY, linestyle="--", linewidth=1.2, label="low and high scenarios"); ax.plot(f.index, f["high"] / 1e6, color=GRAY, linestyle="--", linewidth=1.2)
    ax.plot(y, wy["medium"] / 1e6, color=INK, linewidth=2.2, label="UN median path")
    pk = pd.read_csv(R / "world_peaks.csv").set_index("series").loc["medium"]
    ax.scatter([pk["peak_year"]], [pk["peak_billion"]], s=60, color=ORANGE, zorder=5)
    ax.vlines(pk["peak_year"], 0, pk["peak_billion"], color=ORANGE, linestyle=":", linewidth=1); ax.text(pk["peak_year"] - 2, 2.2, f"peak: {int(pk['peak_year'])}\n{pk['peak_billion']:.2f} billion", ha="right", color=ORANGE, fontsize=10)
    ax.axvline(2023.5, color=DIM, linestyle=":", linewidth=1); ax.text(2022, 14.6, "estimates", ha="right", color=DIM, fontsize=9); ax.text(2025, 14.6, "projections", color=DIM, fontsize=9)
    ax.set_xlim(1950, 2100); ax.set_ylim(0, 15.5); ax.set_ylabel("billion people"); ax.legend(frameon=False, labelcolor=INK, fontsize=9, loc="upper left", bbox_to_anchor=(0.0, 0.9))
    ax.set_title("World population: UN estimates to 2023, projections to 2100")


def growth(ax):
    ax.plot(wy.index, wy["growth_rate_pct"], color=BLUE, linewidth=2.2); ax.axhline(0, color=DIM, linewidth=1)
    for yr, xy in ((int(S["world_growth_peak_year"]), (1972, 2.42)), (2023, (2036, 1.5))):
        v = wy.loc[yr, "growth_rate_pct"]; ax.scatter([yr], [v], s=45, color=ORANGE, zorder=5); ax.annotate(f"{v:.2f}% in {yr}", (yr, v), xytext=xy, color=ORANGE, fontsize=10, arrowprops={"arrowstyle": "-", "color": ORANGE, "linewidth": 0.8})
    ax.set_xlim(1950, 2100); ax.set_ylim(-0.5, 2.6); ax.set_ylabel("% per year"); ax.set_title("World growth rate")


def shrinking(ax):
    s = pd.read_csv(R / "shrinking.csv"); ax.fill_between(s["year"], s["shrinking"], step="mid", color=ORANGE, alpha=0.85, linewidth=0)
    for yr in (1990, 2023, 2050, 2100):
        v = int(s.loc[s["year"] == yr, "shrinking"].iloc[0]); ax.text(yr if yr < 2100 else 2096, v + 3, str(v), ha="center", color=INK, fontsize=10)
    ax.set_xlim(1950, 2100); ax.set_ylim(0, 115); ax.set_ylabel("countries"); ax.grid(axis="x", visible=False); ax.set_title(f"Countries with a shrinking population (of {int(S['countries_1m_2023'])})")


def half(ax):
    c = pd.read_csv(R / "concentration.csv"); ax.step(c["year"], c["n_half"], where="mid", color=BLUE, linewidth=2.2)
    for yr in (1950, 2023, 2100):
        v = int(c.loc[c["year"] == yr, "n_half"].iloc[0]); ax.scatter([yr], [v], s=45, color=ORANGE, zorder=5); ax.text(yr + (3 if yr < 2100 else -3), v + 0.35, str(v), ha="left" if yr < 2100 else "right", color=ORANGE, fontsize=10)
    ax.set_xlim(1950, 2100); ax.set_xticks([1950, 2000, 2050, 2100]); ax.set_ylim(0, 12); ax.set_ylabel("countries"); ax.set_title("Largest countries that make up half of humanity")


def continents(ax):
    r = pd.read_csv(R / "regions.csv").pivot(index="year", columns="region", values="share_pct")[CONTINENTS]
    ax.stackplot(r.index, [r[c] for c in CONTINENTS], colors=CCOL, labels=[c.replace(" and the Caribbean", "") for c in CONTINENTS], linewidth=0, alpha=0.92)
    ax.set_xlim(1950, 2100); ax.set_xticks([1950, 2000, 2050, 2100]); ax.set_ylim(0, 100); ax.set_ylabel("% of world population"); ax.legend(frameon=False, labelcolor=INK, fontsize=8, loc="center left", bbox_to_anchor=(1.0, 0.5)); ax.set_title("Share of world population by continent")


def density(ax):
    t = pd.read_csv(R / "density_top.csv").iloc[::-1]; y = np.arange(len(t))
    ax.hlines(y, 10, t["density_2023"], color=BLUE, linewidth=1.5); ax.scatter(t["density_2023"], y, s=55, color=BLUE, zorder=4)
    for yi, (_, r) in zip(y, t.iterrows()):
        ax.text(r["density_2023"] * 1.12, yi, f"{r['density_2023']:,.0f}", va="center", color=INK, fontsize=9)
    for v, lab, yy in ((S["median_density_2023"], "median country", 10.9), (S["weighted_density_2023"], "average person's country", 10.1)):
        ax.axvline(v, color=ORANGE, linestyle="--", linewidth=1); ax.text(v * (0.94 if lab.startswith("median") else 1.06), yy, f"{lab}: {v:,.0f}", color=ORANGE, fontsize=9, ha="right" if lab.startswith("median") else "left")
    ax.set_xscale("log"); ax.set_xlim(10, 30000); ax.set_ylim(-0.6, 11.5); ax.set_yticks(y); ax.set_yticklabels([n.replace("China, ", "").replace("Taiwan Province of China", "Taiwan") for n in t["Location"]]); ax.grid(axis="y", visible=False)
    ax.set_xlabel("people per km², 2023 (log scale)"); ax.set_title("The ten densest of the countries and areas with a million people or more")


def peaks(ax):
    c = pd.read_csv(R / "countries.csv"); edges = list(range(1950, 2030, 10)) + [2024] + list(range(2030, 2110, 10))
    edges = sorted(set(edges)); edges[edges.index(2030)] = 2030; edges = [1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020, 2024, 2030, 2040, 2050, 2060, 2070, 2080, 2090, 2100]
    labels = ["1950s", "60s", "70s", "80s", "90s", "2000s", "10s", "2020\n-23", "2024\n-29", "30s", "40s", "50s", "60s", "70s", "80s", "90s"]
    n = [int(((c["peak_year"] >= a) & (c["peak_year"] < b)).sum()) for a, b in zip(edges[:-1], edges[1:])]; still = int((c["peak_year"] >= 2100).sum())
    x = np.arange(len(n) + 1); vals = n + [still]; cols = [ORANGE] * 8 + [BLUE] * 8 + [GRAY]
    ax.bar(x, vals, color=cols, width=0.72)
    for xi, v in zip(x, vals):
        ax.text(xi, v + 0.8, str(v), ha="center", color=INK, fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels(labels + ["still\ngrowing\nin 2100"], fontsize=8); ax.set_ylabel("countries"); ax.grid(axis="x", visible=False); ax.set_ylim(0, max(vals) + 8)
    ax.set_title(f"Year each of the {len(c)} countries reaches its peak population (UN median path)")


def main():
    (HERE / "charts").mkdir(exist_ok=True)
    fig, (a, b) = plt.subplots(1, 2, figsize=(14, 8), gridspec_kw={"width_ratios": [1.35, 1]})
    world(a); peaks(b); a.set_title("World population: UN estimates and projections"); b.set_title("Year each country's population peaks")
    for ax in (a, b):
        ax.title.set_fontsize(15)
    fig.suptitle("When will the world's population peak? The UN's median path says 2084, at 10.3 billion", x=0.01, ha="left", fontsize=20, color=INK, y=0.98)
    fig.tight_layout(rect=(0, 0, 1, 0.94)); fig.savefig(HERE / "charts" / "00_cover.png", dpi=100); plt.close(fig)
    fig, ax = plt.subplots(figsize=(10, 4.4)); world(ax); save(fig, "01_world.png")
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 3.8)); growth(a); shrinking(b); save(fig, "02_growth.png")
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 3.8), gridspec_kw={"width_ratios": [1, 1.2]}); half(a); continents(b); save(fig, "03_distribution.png")
    fig, ax = plt.subplots(figsize=(10, 4.0)); density(ax); save(fig, "04_density.png")
    fig, ax = plt.subplots(figsize=(10, 3.8)); peaks(ax); save(fig, "05_peaks.png")


if __name__ == "__main__":
    main()
