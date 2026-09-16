import sqlite3

import pandas as pd
import pytest

from src import db_utils
from src.db_utils import get_connection, run_query
from tests.conftest import SEED_ROWS


def test_get_connection_returns_sqlite_connection(patch_db_path):
    conn = get_connection()
    assert isinstance(conn, sqlite3.Connection)
    conn.close()


def test_get_connection_points_at_patched_db(patch_db_path):
    conn = get_connection()
    tables = [
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    ]
    conn.close()
    assert "widgets" in tables


def test_run_query_raw_sql_string(patch_db_path):
    df = run_query("SELECT id, name, value FROM widgets ORDER BY id")
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["id", "name", "value"]
    assert [tuple(row) for row in df.values.tolist()] == SEED_ROWS


def test_run_query_sql_file_as_str_path(patch_db_path, sql_file):
    path = sql_file("SELECT id, name FROM widgets WHERE id = 2;")
    df = run_query(str(path))
    assert len(df) == 1
    assert tuple(df.iloc[0]) == (2, "beta")


def test_run_query_sql_file_as_pathlib_path(patch_db_path, sql_file):
    path = sql_file("SELECT id, name FROM widgets WHERE id = 2;")
    df = run_query(path)
    assert len(df) == 1
    assert tuple(df.iloc[0]) == (2, "beta")


def test_run_query_with_params(patch_db_path):
    df = run_query("SELECT * FROM widgets WHERE id = ?", params=(2,))
    assert len(df) == 1
    assert df.iloc[0]["name"] == "beta"


def test_run_query_bad_sql_raises_database_error(patch_db_path):
    with pytest.raises(pd.errors.DatabaseError):
        run_query("SELECT * FROM nonexistent_table")


def test_run_query_missing_sql_file_raises(patch_db_path, tmp_path):
    missing = tmp_path / "does_not_exist.sql"
    with pytest.raises(FileNotFoundError):
        run_query(missing)


def test_run_query_missing_db_directory_raises(monkeypatch, tmp_path):
    ghost_path = tmp_path / "no_such_subdir" / "ghost.db"
    monkeypatch.setattr(db_utils, "DB_PATH", ghost_path)
    with pytest.raises(sqlite3.OperationalError):
        run_query("SELECT 1")
