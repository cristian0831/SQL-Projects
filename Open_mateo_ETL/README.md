# Open-Meteo Weather ETL

A small, dependency-light ETL pipeline that pulls 7-day weather forecasts for four cities in Boyacá, Colombia — Tunja, Duitama, Paipa, and Sogamoso — from the free [Open-Meteo API](https://open-meteo.com/), loads them into a SQLite star schema, and turns them into exploratory charts and an interactive map.

It's a four-stage pipeline: **Extract → Transform/Load → Analyze → Visualize**, each stage a standalone script.

## What it does

1. **Extract** ([weather_scraper.py](weather_scraper.py)) — fetches daily max temperature forecasts from Open-Meteo for each city and stores them in a raw SQLite table. Safe to re-run: already-stored (city, date) rows are skipped.
2. **Transform/Load** ([weather_etl.py](weather_etl.py)) — validates the raw data (flags null and out-of-range readings) and reshapes it into a clean star schema: a `cities` dimension table, a `daily_temperature_readings` fact table, and an `agg_city_summary` rollup.
3. **Analyze** ([weather_analysis.py](weather_analysis.py)) — reads the star schema (read-only) and saves 5 exploratory PNG charts to `plots/`: city ranking, daily trend, temperature range/volatility, weekday vs. weekend average, and % of flagged readings.
4. **Visualize** ([weather_map.py](weather_map.py)) — reads the star schema (read-only) and renders `plots/weather_map.html`: a self-contained, interactive Leaflet.js map with a marker per city, color-coded by average temperature, with click-to-explore popups showing stats and a 7-day breakdown.

## Requirements

- Python 3
- [`requests`](https://pypi.org/project/requests/) (Extract stage)
- [`matplotlib`](https://pypi.org/project/matplotlib/) (Analysis stage)

No package manager or dependency manifest is used — everything else is Python's standard library (`sqlite3`, `json`, `logging`, `argparse`, `pathlib`, `datetime`). Install the two dependencies with:

```bash
pip install requests matplotlib
```

## Usage

Run the stages in order — each one depends on data produced by the previous stage:

```bash
python3 weather_scraper.py     # Extract:      pulls forecasts into weather.db
python3 weather_etl.py         # Transform/Load: builds the star schema
python3 weather_analysis.py    # Analyze:       saves PNG charts to plots/
python3 weather_map.py         # Visualize:     saves an interactive map to plots/weather_map.html
```

All four scripts default to `weather.db` for the database path and accept `--db PATH` to point elsewhere. `weather_scraper.py` also accepts `--cities NAME...` to limit which cities are fetched; `weather_analysis.py` and `weather_map.py` accept `--out DIR` to change where output files are saved (default `plots/`).

Open `plots/weather_map.html` directly in a browser to explore the interactive map — it loads Leaflet.js and map tiles from a CDN, so an internet connection is needed to view it (not to generate it).

## Project structure

```
weather_scraper.py    Extract  — Open-Meteo API -> raw `temperature` table
weather_etl.py         Transform/Load — raw table -> star schema
weather_analysis.py    Analyze  — star schema -> PNG charts in plots/
weather_map.py          Visualize — star schema -> interactive map in plots/
weather_scraper.md     Reference notes on the Open-Meteo API parameters used
weather.db              SQLite database (generated, not source)
plots/                  Generated charts and the interactive map (generated, not source)
```

## Data source

Forecast data comes from [Open-Meteo](https://open-meteo.com/), a free weather API that requires no API key for non-commercial use. See [weather_scraper.md](weather_scraper.md) for the specific parameters and response format this project relies on.
