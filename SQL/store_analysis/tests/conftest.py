import sqlite3

import pytest

from src import db_utils

SEED_ROWS = [
    (1, "alpha", 1.5),
    (2, "beta", 2.5),
    (3, "gamma", 3.5),
]


@pytest.fixture
def tmp_db_path(tmp_path):
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE widgets (id INTEGER PRIMARY KEY, name TEXT, value REAL)"
    )
    conn.executemany("INSERT INTO widgets VALUES (?, ?, ?)", SEED_ROWS)
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def patch_db_path(monkeypatch, tmp_db_path):
    monkeypatch.setattr(db_utils, "DB_PATH", tmp_db_path)
    return tmp_db_path


@pytest.fixture
def sql_file(tmp_path):
    def _make(text, name="query.sql"):
        path = tmp_path / name
        path.write_text(text)
        return path

    return _make
