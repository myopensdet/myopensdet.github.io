# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Schema: every database has the same tables and columns, whatever its own types."""

import pytest

EXPECTED_COLUMNS = {
    "customers": ["id", "email", "full_name", "country"],
    "orders": ["id", "customer_id", "status", "total", "created_at"],
}


@pytest.mark.smoke
@pytest.mark.parametrize("table", EXPECTED_COLUMNS)
def test_table_has_the_expected_columns(db, table):
    assert db.columns(table) == EXPECTED_COLUMNS[table]
