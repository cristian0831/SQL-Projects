import pytest

from src.db_utils import run_query

EXPECTED_TABLES = {
    "customers",
    "order_items",
    "products",
    "orders_raw",
    "orders_clean",
    "geography",
}


@pytest.mark.integration
def test_real_db_expected_tables_exist():
    df = run_query("SELECT name FROM sqlite_master WHERE type='table'")
    assert EXPECTED_TABLES <= set(df["name"])


@pytest.mark.integration
def test_real_db_customers_has_rows():
    df = run_query("SELECT COUNT(*) AS n FROM customers")
    assert df.loc[0, "n"] > 0
