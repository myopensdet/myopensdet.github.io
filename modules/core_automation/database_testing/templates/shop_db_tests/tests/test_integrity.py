# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Integrity tests: the database itself refuses bad rows, whatever the app sends."""

import pytest
from psycopg import errors

GOOD_CUSTOMER = "INSERT INTO customers (email, full_name) VALUES (%s, %s)"


def test_good_row_is_accepted(db):
    assert db.run(GOOD_CUSTOMER, ("new.customer@example.com", "New Customer")) == 1


def test_email_is_required(db):
    with pytest.raises(errors.NotNullViolation), db.savepoint():
        db.run(GOOD_CUSTOMER, (None, "No Email"))


def test_email_must_be_unique(db):
    with pytest.raises(errors.UniqueViolation), db.savepoint():
        db.run(GOOD_CUSTOMER, ("arshad@example.com", "Second Arshad"))


def test_order_needs_a_real_customer(db):
    with pytest.raises(errors.ForeignKeyViolation), db.savepoint():
        db.run("INSERT INTO orders (customer_id) VALUES (%s)", (99999,))


@pytest.mark.parametrize(
    ("sql", "params"),
    [
        ("INSERT INTO books (title, price) VALUES (%s, %s)", ("Free Book", 0)),
        ("INSERT INTO books (title, price, stock) VALUES (%s, %s, %s)", ("Minus", 5, -1)),
        ("INSERT INTO orders (customer_id, status) VALUES (%s, %s)", (1, "lost")),
    ],
    ids=["price must be above 0", "stock can't go below 0", "status must be a known one"],
)
def test_check_rules(db, sql, params):
    with pytest.raises(errors.CheckViolation), db.savepoint():
        db.run(sql, params)


def test_order_id_is_made_by_the_database(db):
    with pytest.raises(errors.GeneratedAlways), db.savepoint():
        db.run("INSERT INTO orders (id, customer_id) VALUES (%s, %s)", (1, 1))


def test_customer_with_orders_cant_be_deleted(db):
    with pytest.raises(errors.ForeignKeyViolation), db.savepoint():
        db.run("DELETE FROM customers WHERE email = %s", ("arshad@example.com",))


def test_deleting_an_order_deletes_its_items(db):
    db.run("DELETE FROM orders WHERE id = %s", (2,))
    assert db.value("SELECT COUNT(*) FROM order_items WHERE order_id = %s", (2,)) == 0
