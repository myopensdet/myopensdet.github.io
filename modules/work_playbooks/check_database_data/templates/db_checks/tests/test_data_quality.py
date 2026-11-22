# Template from myOpenSDET: https://myopensdet.github.io/
"""Is the data healthy? Each check looks for rows that break one rule. No rows = pass.
Run them after every release or data migration. The same queries are in sql/data_checks.sql.
"""

from conftest import problems, rows

KNOWN_STATUSES = ("new", "paid", "shipped", "delivered", "cancelled")


def test_no_duplicate_emails(db):
    found = rows(
        db,
        "SELECT lower(email), count(*) FROM customers GROUP BY lower(email) HAVING count(*) > 1",
    )
    assert not found, problems(found, "emails used more than once")


def test_every_order_item_belongs_to_an_order(db):
    found = rows(
        db,
        "SELECT oi.id, oi.order_id FROM order_items oi "
        "LEFT JOIN orders o ON o.id = oi.order_id WHERE o.id IS NULL",
    )
    assert not found, problems(found, "order items with no order (id, order_id)")


def test_every_order_belongs_to_a_customer(db):
    found = rows(
        db,
        "SELECT o.order_number FROM orders o "
        "LEFT JOIN customers c ON c.id = o.customer_id WHERE c.id IS NULL",
    )
    assert not found, problems(found, "orders with no customer")


def test_every_order_has_items(db):
    found = rows(
        db,
        "SELECT o.order_number FROM orders o "
        "LEFT JOIN order_items oi ON oi.order_id = o.id WHERE oi.id IS NULL",
    )
    assert not found, problems(found, "orders with no items")


def test_order_totals_match_their_items(db):
    found = rows(
        db,
        "SELECT o.order_number, o.total, sum(oi.quantity * oi.unit_price) FROM orders o "
        "JOIN order_items oi ON oi.order_id = o.id GROUP BY o.id, o.order_number, o.total "
        "HAVING o.total <> sum(oi.quantity * oi.unit_price)",
    )
    assert not found, problems(found, "orders whose total is wrong (order, total, items)")


def test_order_statuses_are_known(db):
    found = rows(
        db,
        "SELECT order_number, status FROM orders WHERE NOT status = ANY(%s)",
        (list(KNOWN_STATUSES),),
    )
    assert not found, problems(found, "orders with an unknown status")


def test_stock_is_never_negative(db):
    found = rows(db, "SELECT sku, stock FROM products WHERE stock < 0")
    assert not found, problems(found, "products with negative stock")


def test_prices_are_above_zero(db):
    found = rows(db, "SELECT sku, price FROM products WHERE price <= 0")
    assert not found, problems(found, "products with a zero or negative price")
