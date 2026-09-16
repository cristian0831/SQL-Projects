import sqlite3
from pathlib import Path

import pandas as pd

from src.config import DB_PATH


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def run_query(sql: str, params: tuple = ()) -> pd.DataFrame:
    """Run a SQL string, or a path to a .sql file, against superstore.db."""
    if sql.strip().lower().endswith(".sql"):
        sql = Path(sql).read_text()
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params)
