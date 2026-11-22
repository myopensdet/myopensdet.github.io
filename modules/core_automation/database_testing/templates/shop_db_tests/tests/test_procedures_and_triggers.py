# Template from myOpenSDET: https://myopensdet.github.io/
"""Stored functions and triggers: code that runs inside the database, tested from outside."""

import pytest
from psycopg import errors


def stock(db, book_id):
    return db.value("SELECT stock FROM books WHERE id = %s", (book_id,))


def test_place_order_takes_stock_and_saves_the_order(db):
    before = stock(db, 1)

    order_id = db.value("SELECT place_order(%s, %s, %s)", (2, 1, 3))

    assert stock(db, 1) == before - 3
    order = db.one("SELECT customer_id, status, total FROM orders WHERE id = %s", (order_id,))
    assert order["customer_id"] == 2
    assert order["status"] == "new"
    assert str(order["total"]) == "74.97"  # 3 x 24.99
    items = db.all("SELECT book_id, quantity FROM order_items WHERE order_id = %s", (order_id,))
    assert items == [{"book_id": 1, "quantity": 3}]


def test_place_order_refuses_when_out_of_stock(db):
    orders_before = db.value("SELECT COUNT(*) FROM orders")

    with pytest.raises(errors.RaiseException, match="Not enough stock for book 3"), db.savepoint():
        db.value("SELECT place_order(%s, %s, %s)", (1, 3, 1))

    assert db.value("SELECT COUNT(*) FROM orders") == orders_before
    assert stock(db, 3) == 0


def test_place_order_refuses_a_negative_quantity(db):
    with pytest.raises(errors.CheckViolation), db.savepoint():
        db.value("SELECT place_order(%s, %s, %s)", (1, 1, -2))
    assert stock(db, 1) == 10  # the stock change was undone with the rest


def test_status_change_is_logged(db):
    db.run("UPDATE orders SET status = %s WHERE id = %s", ("shipped", 1))

    history = db.all(
        "SELECT old_status, new_status FROM order_status_history WHERE order_id = %s", (1,)
    )
    assert history == [{"old_status": "paid", "new_status": "shipped"}]


def test_status_change_moves_updated_at(db):
    # A brand-new order, made in this test's transaction: the hardest case for the trigger.
    order_id = db.value("SELECT place_order(%s, %s, %s)", (5, 4, 1))
    db.run("UPDATE orders SET status = %s WHERE id = %s", ("paid", order_id))
    times = db.one("SELECT created_at, updated_at FROM orders WHERE id = %s", (order_id,))
    assert times["updated_at"] > times["created_at"]


def test_same_status_is_not_logged(db):
    db.run("UPDATE orders SET status = status WHERE id = %s", (1,))
    assert db.value("SELECT COUNT(*) FROM order_status_history WHERE order_id = %s", (1,)) == 0
