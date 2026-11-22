# Template from myOpenSDET: https://myopensdet.github.io/
"""Is the structure what the app expects? Catches a missing table or column, a changed type,
or a missing rule, right after a release, before the app trips over it."""

from conftest import rows

EXPECTED_TABLES = {"customers", "products", "orders", "order_items"}
EXPECTED_ORDER_COLUMNS = [
    ("id", "integer", "NO"),
    ("order_number", "text", "NO"),
    ("customer_id", "integer", "NO"),
    ("status", "text", "NO"),
    ("total", "numeric", "NO"),
    ("created_at", "timestamp with time zone", "NO"),
]


def test_all_tables_exist(db):
    found = {
        name
        for (name,) in rows(
            db, "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )
    }
    assert not EXPECTED_TABLES - found, f"missing tables: {EXPECTED_TABLES - found}"


def test_orders_columns_and_types(db):
    found = rows(
        db,
        "SELECT column_name, data_type, is_nullable FROM information_schema.columns "
        "WHERE table_name = 'orders' ORDER BY ordinal_position",
    )
    assert found == EXPECTED_ORDER_COLUMNS


def test_orders_are_linked_to_customers_by_a_foreign_key(db):
    found = rows(
        db,
        "SELECT pg_get_constraintdef(oid) FROM pg_constraint "
        "WHERE conrelid = 'orders'::regclass AND contype = 'f'",
    )
    assert any("REFERENCES customers" in rule for (rule,) in found), (
        "orders.customer_id has no foreign key: nothing stops orders with no customer"
    )
