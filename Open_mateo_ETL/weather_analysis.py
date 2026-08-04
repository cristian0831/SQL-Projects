# weather_analysis.py
# Analysis step: reads the star schema built by weather_etl.py (read-only)
# and produces exploratory plots into a local `plots/` directory.
# Usage: python3 weather_analysis.py

import argparse
import logging
import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless-safe: never tries to open a display
import matplotlib.pyplot as plt

# ── Configuration ──────────────────────────────────────────────
DB_PATH   = Path("weather.db")
PLOTS_DIR = Path("plots")

# ── Logging ────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)
logging.getLogger("matplotlib").setLevel(logging.WARNING)

# ── Database (read-only) ───────────────────────────────────────
def connect_db(db_path: Path) -> sqlite3.Connection:
    """Opens the DB in read-only mode — this script never writes to it."""
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    log.info(f"Connected (read-only): {db_path}")
    return conn

def load_city_summary(conn: sqlite3.Connection) -> list:
    """Returns (city_name, avg_temp_max, min_temp_max, max_temp_max, n_days, n_flagged)."""
    return conn.execute("""
        SELECT c.city_name, s.avg_temp_max, s.min_temp_max, s.max_temp_max, s.n_days, s.n_flagged
        FROM agg_city_summary s
        JOIN cities c ON c.city_id = s.city_id
        ORDER BY c.city_name
    """).fetchall()

def load_daily_readings(conn: sqlite3.Connection) -> list:
    """Returns (city_name, reading_date, max_temp_celsius, is_weekend)."""
    return conn.execute("""
        SELECT c.city_name, r.reading_date, r.max_temp_celsius, r.is_weekend
        FROM daily_temperature_readings r
        JOIN cities c ON c.city_id = r.city_id
        ORDER BY c.city_name, r.reading_date
    """).fetchall()

# ── Plots ──────────────────────────────────────────────────────
def plot_city_ranking(summary_rows: list, out_dir: Path):
    """Bar chart: avg max temp per city, sorted hottest to coldest."""
    rows = sorted(summary_rows, key=lambda r: r[1], reverse=True)
    cities = [r[0] for r in rows]
    avgs = [r[1] for r in rows]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(cities, avgs, color="tab:orange")
    ax.set_title("Average Max Temperature by City")
    ax.set_ylabel("°C")
    fig.tight_layout()
    path = out_dir / "city_ranking.png"
    fig.savefig(path)
    plt.close(fig)
    log.info(f"  Saved: {path}")

def plot_daily_trend(readings_rows: list, out_dir: Path):
    """Line chart: max temp per day, one line per city."""
    by_city = {}
    for city, dt, temp, _ in readings_rows:
        by_city.setdefault(city, {"dates": [], "temps": []})
        by_city[city]["dates"].append(dt)
        by_city[city]["temps"].append(temp)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for city, data in sorted(by_city.items()):
        ax.plot(data["dates"], data["temps"], marker="o", label=city)
    ax.set_title("Daily Max Temperature Trend")
    ax.set_ylabel("°C")
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    fig.tight_layout()
    path = out_dir / "daily_trend.png"
    fig.savefig(path)
    plt.close(fig)
    log.info(f"  Saved: {path}")

def plot_temperature_range(summary_rows: list, out_dir: Path):
    """Bar chart: max-min spread per city (volatility)."""
    cities = [r[0] for r in summary_rows]
    ranges = [r[3] - r[2] for r in summary_rows]  # max_temp_max - min_temp_max

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(cities, ranges, color="tab:purple")
    ax.set_title("Temperature Range (Volatility) by City")
    ax.set_ylabel("°C spread (max - min)")
    fig.tight_layout()
    path = out_dir / "temperature_range.png"
    fig.savefig(path)
    plt.close(fig)
    log.info(f"  Saved: {path}")

def plot_weekday_vs_weekend(readings_rows: list, out_dir: Path):
    """Grouped bar chart: weekday vs weekend average max temp, per city."""
    sums = {}  # city -> {0: [temps], 1: [temps]}
    for city, _, temp, is_weekend in readings_rows:
        sums.setdefault(city, {0: [], 1: []})[is_weekend].append(temp)

    cities = sorted(sums.keys())
    weekday_avgs = [sum(sums[c][0]) / len(sums[c][0]) if sums[c][0] else 0 for c in cities]
    weekend_avgs = [sum(sums[c][1]) / len(sums[c][1]) if sums[c][1] else 0 for c in cities]

    x = range(len(cities))
    width = 0.35
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar([i - width / 2 for i in x], weekday_avgs, width, label="Weekday", color="tab:blue")
    ax.bar([i + width / 2 for i in x], weekend_avgs, width, label="Weekend", color="tab:red")
    ax.set_title("Weekday vs Weekend Average Max Temperature")
    ax.set_ylabel("°C")
    ax.set_xticks(list(x))
    ax.set_xticklabels(cities)
    ax.legend()
    fig.tight_layout()
    path = out_dir / "weekday_vs_weekend.png"
    fig.savefig(path)
    plt.close(fig)
    log.info(f"  Saved: {path}")

def plot_data_quality(summary_rows: list, out_dir: Path):
    """Bar chart: % of flagged (non-OK) rows per city."""
    cities = [r[0] for r in summary_rows]
    pct_flagged = [100 * r[5] / r[4] if r[4] else 0 for r in summary_rows]  # n_flagged / n_days

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(cities, pct_flagged, color="tab:gray")
    ax.set_title("Flagged Readings by City")
    ax.set_ylabel("% flagged (NULL_VALUE / OUT_OF_RANGE)")
    ax.set_ylim(0, 100)
    fig.tight_layout()
    path = out_dir / "data_quality.png"
    fig.savefig(path)
    plt.close(fig)
    log.info(f"  Saved: {path}")

# ── Main pipeline ──────────────────────────────────────────────
def run(db_path: Path, out_dir: Path):
    out_dir.mkdir(exist_ok=True)
    conn = connect_db(db_path)

    summary_rows = load_city_summary(conn)
    readings_rows = load_daily_readings(conn)
    conn.close()

    plot_city_ranking(summary_rows, out_dir)
    plot_daily_trend(readings_rows, out_dir)
    plot_temperature_range(summary_rows, out_dir)
    plot_weekday_vs_weekend(readings_rows, out_dir)
    plot_data_quality(summary_rows, out_dir)

    log.info(f"Analysis complete. 5 plot(s) saved to {out_dir}/")

def main():
    parser = argparse.ArgumentParser(
        description="Weather Analysis — exploratory plots from the star schema"
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DB_PATH,
        help=f"Database path (default: {DB_PATH})"
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=PLOTS_DIR,
        help=f"Output directory for plots (default: {PLOTS_DIR})"
    )
    args = parser.parse_args()

    run(args.db, args.out)

if __name__ == "__main__":
    main()
