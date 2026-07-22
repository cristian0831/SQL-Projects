# weather_scraper.py
# Extracts daily max temperature for 4 cities via the Open-Meteo API
# Usage: python3 weather_scraper.py

import json
import logging
import sqlite3
import time
from pathlib import Path

import requests

# ── Configuration ──────────────────────────────────────────────
BASE_URL    = "https://api.open-meteo.com/v1/forecast"
DB_PATH     = Path("weather.db")
MAX_RETRIES = 3
BACKOFF_BASE = 2   # seconds: 2, 4, 8...
TIMEOUT      = 10

CITIES = {
    "TUNJA":    {"lat":  5.5353, "lon": -73.3578},
    "DUITAMA":  {"lat":  5.8278, "lon": -73.0358},
    "PAIPA":    {"lat":  5.7833, "lon": -73.1167},
    "SOGAMOSO": {"lat":  5.7167, "lon": -72.9333},
}

# ── Logging ────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── HTTP client with retry/backoff ─────────────────────────────
def fetch(url: str, params: dict) -> dict:
    """GET request with retries and exponential backoff."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            log.debug(f"  GET {url}  (attempt {attempt}/{MAX_RETRIES})")
            r = requests.get(url, params=params, timeout=TIMEOUT)
            r.raise_for_status()          # error if status != 2xx
            return r.json()
        except (requests.RequestException, ValueError) as e:
            if attempt == MAX_RETRIES:
                raise RuntimeError(f"Failed after {MAX_RETRIES} attempts: {e}")
            wait_time = BACKOFF_BASE ** attempt
            log.warning(f"  Error: {e}. Retrying in {wait_time}s…")
            time.sleep(wait_time)

# ── Database ───────────────────────────────────────────────────
def init_db(db_path: Path) -> sqlite3.Connection:
    """Creates the table if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS temperatura (
            ciudad   TEXT NOT NULL,
            fecha    TEXT NOT NULL,
            temp_max REAL,
            UNIQUE (ciudad, fecha)          -- idempotency
        )
    """)
    conn.commit()
    log.info(f"Database ready: {db_path}")
    return conn

# ── Parser + persistence ───────────────────────────────────────
def save(conn: sqlite3.Connection, city: str, data: dict):
    """Extracts dates and temperatures from the JSON and stores them."""
    dates      = data["daily"]["time"]                # list of strings
    temp_maxs  = data["daily"]["temperature_2m_max"]  # list of floats

    new_count = skipped_count = 0
    for date, temp in zip(dates, temp_maxs):
        # Using INSERT OR IGNORE — idempotent behavior
        cur = conn.execute("""
            INSERT OR IGNORE INTO temperatura (ciudad, fecha, temp_max)
            VALUES (?, ?, ?)
        """, (city, date, temp))
        if cur.rowcount:
            new_count += 1
        else:
            skipped_count += 1
    conn.commit()
    log.info(f"  {city:<10} → {new_count} new, {skipped_count} skipped")

# ── Main pipeline ──────────────────────────────────────────────
def run():
    # create the database
    conn = init_db(DB_PATH)
    # request and navigate through data
    for city, coords in CITIES.items():
        log.info(f"Downloading: {city}")
        params = {
            "latitude":     coords["lat"],
            "longitude":    coords["lon"],
            "daily":        "temperature_2m_max",
            "timezone":     "America/Bogota",
            "forecast_days": 7,
        }
        data = fetch(BASE_URL, params)   # ← HTTP request
        save(conn, city, data)           # ← parse + persist

    conn.close()
    log.info("Extraction complete.")

if __name__ == "__main__":
    run()
