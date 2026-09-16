from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "superstore.csv"
DB_PATH = PROJECT_ROOT / "db" / "superstore.db"
