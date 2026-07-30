# weather_etl.py
# Transform + Load step: reads the raw `temperature` table populated by
# weather_scraper.py, validates it, and builds a star schema plus
# aggregation tables. Never writes to `temperature`.
# Usage: python3 weather_etl.py

import argparse
import logging
import sqlite3
from datetime import date

from weather_scraper import CITIES
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────
DB_PATH = Path("weather.db")
TEMP_MIN_PLAUSIBLE = -10.0   # °C, loose bound to catch sentinels/absurd values only
TEMP_MAX_PLAUSIBLE = 40.0    # °C

# ── Logging ────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Database ───────────────────────────────────────────────────
def init_db(db_path: Path) -> sqlite3.Connection:
    """Opens the DB, enables FK enforcement, creates all ETL tables if missing."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS cities (
            city_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            city_name TEXT NOT NULL UNIQUE,
            latitude  REAL NOT NULL,
            longitude REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS daily_temperature_readings (
            reading_id          INTEGER PRIMARY KEY AUTOINCREMENT,
            city_id             INTEGER NOT NULL REFERENCES cities(city_id),
            reading_date        TEXT    NOT NULL,
            max_temp_celsius    REAL,
            max_temp_fahrenheit REAL,
            month               INTEGER NOT NULL,
            day_of_week         TEXT    NOT NULL,
            is_weekend          INTEGER NOT NULL DEFAULT 0 CHECK (is_weekend IN (0, 1)),
            quality_flag        TEXT    NOT NULL DEFAULT 'OK'
                                CHECK (quality_flag IN ('OK', 'NULL_VALUE', 'OUT_OF_RANGE')),
            UNIQUE (city_id, reading_date)
        );

        CREATE TABLE IF NOT EXISTS agg_city_summary (
            city_id      INTEGER PRIMARY KEY REFERENCES cities(city_id),
            avg_temp_max REAL,
            min_temp_max REAL,
            max_temp_max REAL,
            n_days       INTEGER NOT NULL,
            n_flagged    INTEGER NOT NULL DEFAULT 0
        );
    """)
    conn.commit()
    log.info(f"Database ready: {db_path}")
    return conn

def load_cities(conn: sqlite3.Connection) -> dict:
    """INSERT OR IGNORE each entry of CITIES into cities; returns {name: city_id}."""
    conn.executemany(
        "INSERT OR IGNORE INTO cities (city_name, latitude, longitude) VALUES (?, ?, ?)",
        [(name, coords["lat"], coords["lon"]) for name, coords in CITIES.items()],
    )
    conn.commit()
    rows = conn.execute("SELECT city_id, city_name FROM cities").fetchall()
    return {name: city_id for city_id, name in rows}

def fetch_raw(conn: sqlite3.Connection) -> list:
    """Reads the raw temperature table. Read-only — never writes here."""
    return conn.execute(
        "SELECT city, date, temp_max FROM temperature ORDER BY city, date"
    ).fetchall()

# ── Data quality ───────────────────────────────────────────────
def classify_row(temp_max) -> str:
    """Returns 'NULL_VALUE' | 'OUT_OF_RANGE' | 'OK' for a single temp_max reading."""
    if temp_max is None:
        return "NULL_VALUE"
    if not (TEMP_MIN_PLAUSIBLE <= temp_max <= TEMP_MAX_PLAUSIBLE):
        return "OUT_OF_RANGE"
    return "OK"

# ── Transform ──────────────────────────────────────────────────
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def build_daily_temperature_readings(conn: sqlite3.Connection, raw_rows: list, city_ids: dict):
    """Rebuilds daily_temperature_readings from raw_rows with derived columns."""
    reading_rows = []
    for city, dt, temp_max_c in raw_rows:
        parsed = date.fromisoformat(dt)
        temp_max_f = temp_max_c * 9 / 5 + 32 if temp_max_c is not None else None
        weekday = parsed.weekday()  # 0=Monday..6=Sunday
        reading_rows.append((
            city_ids[city],
            dt,
            temp_max_c,
            temp_max_f,
            parsed.month,
            DAY_NAMES[weekday],
            1 if weekday >= 5 else 0,
            classify_row(temp_max_c),
        ))

    conn.execute("DELETE FROM daily_temperature_readings")
    conn.executemany("""
        INSERT INTO daily_temperature_readings
            (city_id, reading_date, max_temp_celsius, max_temp_fahrenheit, month, day_of_week, is_weekend, quality_flag)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, reading_rows)
    conn.commit()
    log.info(f"  daily_temperature_readings: {len(reading_rows)} row(s)")

# ── Aggregation ────────────────────────────────────────────────
def build_city_summary(conn: sqlite3.Connection):
    """Rebuilds agg_city_summary: overall stats per city."""
    conn.execute("DELETE FROM agg_city_summary")
    conn.execute("""
        INSERT INTO agg_city_summary (city_id, avg_temp_max, min_temp_max, max_temp_max, n_days, n_flagged)
        SELECT
            city_id,
            AVG(max_temp_celsius),
            MIN(max_temp_celsius),
            MAX(max_temp_celsius),
            COUNT(*),
            SUM(CASE WHEN quality_flag != 'OK' THEN 1 ELSE 0 END)
        FROM daily_temperature_readings
        GROUP BY city_id
    """)
    conn.commit()
    n = conn.execute("SELECT COUNT(*) FROM agg_city_summary").fetchone()[0]
    log.info(f"  agg_city_summary: {n} row(s)")

# ── Main pipeline ──────────────────────────────────────────────
def run(db_path: Path):
    conn = init_db(db_path)
    city_ids = load_cities(conn)
    raw_rows = fetch_raw(conn)
    build_daily_temperature_readings(conn, raw_rows, city_ids)
    build_city_summary(conn)
    conn.close()
    log.info("Transform/Load complete.")

def main():
    parser = argparse.ArgumentParser(
        description="Weather ETL — Transform & Load into star schema"
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DB_PATH,
        help=f"Database path (default: {DB_PATH})"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable DEBUG-level logging"
    )
    args = parser.parse_args()
    if args.verbose:
        log.setLevel(logging.DEBUG)

    run(args.db)

if __name__ == "__main__":
    main()
