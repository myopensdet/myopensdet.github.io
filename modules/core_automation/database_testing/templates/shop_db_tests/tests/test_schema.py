# Template from myOpenSDET: https://myopensdet.github.io/
"""Schema tests: the tables and columns are what the app expects."""

import pytest

# What the app's code expects. Copy it from the migration or the data model, not from the database.
EXPECTED = {
    "customers": {
        "id": ("integer", False),
        "email": ("text", False),
        "full_name": ("text", False),
        "created_at": ("timestamp with time zone", False),
    },
    "books": {
        "id": ("integer", False),
        "title": ("text", False),
        "price": ("numeric", False),
        "stock": ("integer", False),
    },
    "orders": {
        "id": ("integer", False),
        "customer_id": ("integer", False),
        "status": ("text", False),
        "total": ("numeric", False),
        "created_at": ("timestamp with time zone", False),
        "updated_at": ("timestamp with time zone", False),
    },
    "order_items": {
        "order_id": ("integer", False),
        "book_id": ("integer", False),
        "quantity": ("integer", False),
        "unit_price": ("numeric", False),
    },
}


@pytest.mark.smoke
@pytest.mark.parametrize("table", EXPECTED)
def test_table_has_the_expected_columns(db, table):
    actual = {name: (c["type"], c["nullable"]) for name, c in db.columns(table).items()}
    assert actual == EXPECTED[table]


def test_email_is_unique(db):
    unique_columns = db.all(
        """
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON kcu.constraint_name = tc.constraint_name AND kcu.table_schema = tc.table_schema
        WHERE tc.table_schema = current_schema()
          AND tc.table_name = 'customers' AND tc.constraint_type = 'UNIQUE'
        """
    )
    assert {"column_name": "email"} in unique_columns


def test_orders_point_at_customers(db):
    target = db.one(
        """
        SELECT ccu.table_name, ccu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON kcu.constraint_name = tc.constraint_name AND kcu.table_schema = tc.table_schema
        JOIN information_schema.constraint_column_usage ccu
          ON ccu.constraint_name = tc.constraint_name AND ccu.table_schema = tc.table_schema
        WHERE tc.table_schema = current_schema() AND tc.table_name = 'orders'
          AND tc.constraint_type = 'FOREIGN KEY' AND kcu.column_name = 'customer_id'
        """
    )
    assert target == {"table_name": "customers", "column_name": "id"}
