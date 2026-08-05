# weather_map.py
# Visualization step: reads the star schema built by weather_etl.py
# (read-only) and renders a self-contained interactive Leaflet map of
# the cities into plots/weather_map.html.
# Note: the HTML file embeds its own data as JSON, but Leaflet's JS/CSS
# and the OpenStreetMap tiles load from a CDN, so a browser needs
# internet access to actually view the map.
# Usage: python3 weather_map.py

import argparse
import json
import logging
import sqlite3
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────
DB_PATH      = Path("weather.db")
PLOTS_DIR    = Path("plots")
MAP_FILENAME = "weather_map.html"
ZOOM         = 10
COLD_RGB     = (65, 105, 225)   # royalblue
HOT_RGB      = (220, 20, 60)    # crimson

# ── Logging ────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Database (read-only) ───────────────────────────────────────
def connect_db(db_path: Path) -> sqlite3.Connection:
    """Opens the DB in read-only mode — this script never writes to it."""
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    log.info(f"Connected (read-only): {db_path}")
    return conn

def load_city_summary(conn: sqlite3.Connection) -> list:
    """Returns (city_name, latitude, longitude, avg_temp_max, min_temp_max, max_temp_max, n_days, n_flagged)."""
    return conn.execute("""
        SELECT c.city_name, c.latitude, c.longitude,
               s.avg_temp_max, s.min_temp_max, s.max_temp_max, s.n_days, s.n_flagged
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

# ── Color scale ────────────────────────────────────────────────
def temp_to_color(value: float, vmin: float, vmax: float) -> str:
    """Interpolates royalblue (coldest) -> crimson (hottest) as a hex string."""
    t = 0.5 if vmax == vmin else (value - vmin) / (vmax - vmin)
    t = max(0.0, min(1.0, t))
    r = round(COLD_RGB[0] + t * (HOT_RGB[0] - COLD_RGB[0]))
    g = round(COLD_RGB[1] + t * (HOT_RGB[1] - COLD_RGB[1]))
    b = round(COLD_RGB[2] + t * (HOT_RGB[2] - COLD_RGB[2]))
    return f"#{r:02x}{g:02x}{b:02x}"

# ── Popup content ──────────────────────────────────────────────
def build_popup_html(city_name: str, avg_temp: float, min_temp: float, max_temp: float,
                      n_days: int, n_flagged: int, daily_rows: list) -> str:
    """Builds the click-popup HTML for one city: stats + a mini date/temp table."""
    table_rows = "".join(
        f"<tr><td>{dt}</td><td align='right'>{temp:.1f}</td></tr>"
        for dt, temp in daily_rows
    )
    return (
        f"<b>{city_name.title()}</b><br>"
        f"Avg max temp: {avg_temp:.1f} °C<br>"
        f"Range: {min_temp:.1f} – {max_temp:.1f} °C<br>"
        f"Days recorded: {n_days} ({n_flagged} flagged)"
        f"<hr style='margin:4px 0'>"
        f"<table style='font-size:0.85em'>"
        f"<tr><th align='left'>Date</th><th align='right'>Max °C</th></tr>"
        f"{table_rows}"
        f"</table>"
    )

# ── HTML template ──────────────────────────────────────────────
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Boyacá Weather Map</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    html, body, #map { height: 100%; margin: 0; }
    .legend {
      position: absolute; bottom: 20px; right: 10px; z-index: 1000;
      background: white; padding: 8px 12px; border-radius: 4px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.4); font-family: sans-serif; font-size: 13px;
    }
    .legend .gradient {
      width: 120px; height: 12px; margin: 4px 0;
      background: linear-gradient(to right, #4169e1, #dc143c);
    }
    .legend .labels { display: flex; justify-content: space-between; }
  </style>
</head>
<body>
  <div id="map"></div>
  <div class="legend">
    <b>Avg Max Temp (°C)</b>
    <div class="gradient"></div>
    <div class="labels"><span>__VMIN__°C</span><span>__VMAX__°C</span></div>
  </div>
  <script>
    const CITIES = __CITIES_JSON__;

    var map = L.map('map').setView([__CENTER_LAT__, __CENTER_LON__], __ZOOM__);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 19
    }).addTo(map);

    CITIES.forEach(function (c) {
      L.circleMarker([c.lat, c.lon], {
        radius: 12,
        color: '#333',
        weight: 1.5,
        fillColor: c.color,
        fillOpacity: 0.85
      }).addTo(map).bindPopup(c.popup_html);
    });
  </script>
</body>
</html>
"""

def render_html(cities: list, center_lat: float, center_lon: float, vmin: float, vmax: float) -> str:
    """Substitutes the template's sentinel placeholders with real data."""
    return (
        HTML_TEMPLATE
        .replace("__CITIES_JSON__", json.dumps(cities, ensure_ascii=False))
        .replace("__CENTER_LAT__", str(center_lat))
        .replace("__CENTER_LON__", str(center_lon))
        .replace("__ZOOM__", str(ZOOM))
        .replace("__VMIN__", f"{vmin:.1f}")
        .replace("__VMAX__", f"{vmax:.1f}")
    )

# ── Main pipeline ──────────────────────────────────────────────
def run(db_path: Path, out_dir: Path):
    out_dir.mkdir(exist_ok=True)
    conn = connect_db(db_path)

    summary_rows = load_city_summary(conn)
    daily_rows = load_daily_readings(conn)
    conn.close()

    daily_by_city = {}
    for city, dt, temp, _ in daily_rows:
        daily_by_city.setdefault(city, []).append((dt, temp))

    avg_temps = [row[3] for row in summary_rows]
    vmin, vmax = min(avg_temps), max(avg_temps)

    cities = []
    for city_name, lat, lon, avg_temp, min_temp, max_temp, n_days, n_flagged in summary_rows:
        cities.append({
            "name": city_name.title(),
            "lat": lat,
            "lon": lon,
            "avg_temp": avg_temp,
            "min_temp": min_temp,
            "max_temp": max_temp,
            "n_days": n_days,
            "n_flagged": n_flagged,
            "color": temp_to_color(avg_temp, vmin, vmax),
            "popup_html": build_popup_html(
                city_name, avg_temp, min_temp, max_temp, n_days, n_flagged,
                daily_by_city.get(city_name, [])
            ),
        })

    center_lat = sum(c["lat"] for c in cities) / len(cities)
    center_lon = sum(c["lon"] for c in cities) / len(cities)

    html = render_html(cities, center_lat, center_lon, vmin, vmax)
    path = out_dir / MAP_FILENAME
    path.write_text(html, encoding="utf-8")
    log.info(f"  Saved: {path}")

def main():
    parser = argparse.ArgumentParser(
        description="Weather Map — interactive Leaflet map from the star schema"
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
        help=f"Output directory for the map (default: {PLOTS_DIR})"
    )
    args = parser.parse_args()

    run(args.db, args.out)

if __name__ == "__main__":
    main()
