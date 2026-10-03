# When will the world's population peak?

The United Nations estimates every country's population back to 1950 and projects it to 2100. Five questions:
- when does the UN's median path peak, and how sure is that;
- how fast has the world been growing, and how many countries are already shrinking;
- how concentrated is humanity: how many countries make up half of it, and which continents hold how much;
- when does each country reach its own peak;
- how crowded is the world, for the typical country and for the typical person.

The questions follow DataCamp's "World Population Analysis" (density, growth rates and global distributions). The data is the UN's World Population Prospects 2024, the official estimates and projections, not a course file.
The projections are scenarios, not observations, and this project says so wherever it uses them.

Build log: https://mrrishit909.github.io/projects/world-population/

## Data

United Nations, Department of Economic and Social Affairs, Population Division (2024), *World Population Prospects 2024*, Online Edition; licence CC BY 3.0 IGO. The 2024 revision is the latest I could find on 2026-10-03.
Two CSV files: `Demographic_Indicators_Medium` (237 countries or areas plus regions and groups, 1950 to 2100, the medium variant: population on 1 July in thousand people, density, growth rate, ...) and `TotalPopulationBySex`
(the same places under the other scenarios, and the 80% and 95% prediction intervals, from 2024). The estimates run to 2023 and the projections start in 2024. The files are 33 MB together, so they are not committed; `download.py` fetches them.

```
./venv/bin/pip install pandas numpy matplotlib certifi      # in a venv
./venv/bin/python download.py    # data/*.csv.gz
./venv/bin/python analyze.py     # results/*
./venv/bin/python check.py
./venv/bin/python charts.py
```

## Steps

1. **Download** the two files.
2. **Audit:** the number of countries or areas, whether the world equals the sum of its countries and of its six continents, whether the two files agree on the median path, and what the growth-rate column is (it matches
   100 x ln of the 1 January population of next year over this year).
3. **The world's path:** the median path with the low and high scenarios and the 80% and 95% prediction intervals, and the peak year and height of each curve.
4. **Growth and shrinking countries:** the world's growth rate, and for the 161 countries with at least a million people in 2023 the number whose population is falling in each year.
5. **Distribution:** how many of the largest countries it takes to reach half of humanity in each year, and the six continents' shares.
6. **Peaks and density:** each of the 161 countries' peak year on the median path (the year of its highest population), the share of the world's 2023 people in countries already past it, and density (the median
   country, and the mean weighted by population).
7. **Check.** `check.py` recomputes 5,679 numbers from the raw files with plain Python (gzip and csv, no pandas): the audit, every year of the world's path and every scenario curve, each curve's peak, the half-of-humanity
   counts and lists for every year, the continents' shares, the shrinking counts, each country's peak year, change and density, the median and weighted density, and the summary figures.
8. **Charts.**

## Results

- **The world's path.** 2.49 billion people in 1950, 8.09 billion in 2023. The median path peaks in 2084 at 10.29 billion and is at 10.18 billion in 2100: 2.2 billion more than today, after 5.6 billion added since 1950.
- **The date is not fixed.** In 2100 the UN's 95% prediction interval runs from 9.05 to 11.44 billion (80%: 9.41 to 11.03), and its low and high scenarios from 6.99 to 14.40. The lower 95% bound peaks in 2068 at 9.66 billion;
  the upper 95% bound, the upper 80% bound and the high scenario are still rising in 2100, so none of them has a peak before the data ends. The low scenario peaks in 2052 at 8.95 billion.
- **Growth.** The world's growth rate peaked at 2.28% a year in 1963, was 0.87% in 2023, and turns negative in 2084 on the median path (-0.13% in 2100).
- **Shrinking countries.** Of the 161 countries with at least a million people in 2023, 12 had a falling population in 1990, 30 in 2023; the median path has 55 in 2050 and 98 in 2100.
- **Half of humanity.** 6 countries in 1950 (China, India, the United States, Russia, Japan, Germany), 7 in 2023 (India, China, the United States, Indonesia, Pakistan, Nigeria, Brazil) and 10 in 2100 (India, China, Pakistan, Nigeria,
  DR Congo, the United States, Ethiopia, Indonesia, Tanzania, Bangladesh). The ten largest hold 61.1% of people in 1950, 57.1% in 2023 and 50.2% in 2100; the largest country holds 21.8% (China), 17.8% (India) and 14.8% (India).
- **Continents.** Asia 54.9% of the world in 1950, 59.0% in 2023, 45.3% in 2100; Africa 9.1%, 18.3% and 37.5%; Europe 22.0%, 9.2% and 5.8%; Latin America and the Caribbean 6.7%, 8.1% and 6.0%; Northern America 6.7%, 4.7% and 4.7%;
  Oceania 0.5%, 0.6% and 0.7%.
- **Peaks.** 37 of the 161 countries have already peaked by 2023, with 26.9% of the world's 2023 people: China in 2021, Russia in 1991, Japan in 2009, Thailand in 2022, Italy in 2014, South Korea in 2020, Spain and Poland in 2023,
  Ukraine in 1993 and Taiwan in 2019 are the ten largest. 20 more peak by 2050 (57 in all), 62 peak between 2024 and 2099 (45.0% of 2023 people), and 62 are still growing in 2100 (27.9%), among them Pakistan, Nigeria, Ethiopia,
  DR Congo and Tanzania. On the median path China falls from 1,423 million to 633 million by 2100 (-55.5%), India peaks in 2061 and is at 1,505 million in 2100, and Nigeria goes from 228 to 477 million.
- **Density.** In 2023 the median of the 161 countries has 84 people per km^2, and the average person lives in a country with 240 (the mean weighted by population). The densest are Singapore (8,476), Hong Kong (6,772), Bahrain (2,005)
  and Bangladesh (1,317, the densest country with 10 million people or more).

## Not done, and caveats

- 2024 to 2100 are projections: the median path is a scenario, and the 80% and 95% intervals are the UN's own probabilistic projections. Each bound is a curve of year-by-year bounds, not an interval for the peak year, and a curve that
  is still rising in 2100 has no peak in the data.
- The growth, peak and density figures use the 161 of 237 "countries or areas" with at least a million people in 2023 (99.8% of the world's people); the 76 smaller ones are left out so a few thousand people on an island do not
  count as a national trend. The UN's "areas" include places such as Hong Kong and Taiwan; names are the UN's.
- A peak year is the year of the highest population on the median path from 1950 to 2100. For 62 countries it is 2100, the last year in the files; for a country whose peak is 2023, that year is the last estimate and the next ones are projections.
- Density is the UN's population per km^2 of land area. The weighted figure is a mean of national densities weighted by population: it is not the density where a person lives, which in cities is far higher.
- Nothing here looks at age, sex, fertility or migration, which is where the projections come from; no scenario assumptions are examined, and nothing is said about why a country is growing or shrinking.
