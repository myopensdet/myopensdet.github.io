# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""CRUD tests: create, read, update and delete one customer, and check what was saved."""

import pytest


@pytest.fixture
def customer_id(db):
    """A new customer for one test. The db fixture undoes it afterwards."""
    return db.value(
        "INSERT INTO customers (email, full_name) VALUES (%s, %s) RETURNING id",
        ("crud.test@example.com", "Crud Test"),
    )


def test_create_saves_every_field(db, customer_id):
    row = db.one("SELECT email, full_name, created_at FROM customers WHERE id = %s", (customer_id,))
    assert row["email"] == "crud.test@example.com"
    assert row["full_name"] == "Crud Test"
    assert row["created_at"] is not None  # the database filled in the default


def test_read_finds_exactly_one(db, customer_id):
    rows = db.all("SELECT id FROM customers WHERE email = %s", ("crud.test@example.com",))
    assert rows == [{"id": customer_id}]


def test_update_changes_only_that_row(db, customer_id):
    others = "SELECT * FROM customers WHERE id <> %s ORDER BY id"
    others_before = db.all(others, (customer_id,))

    changed = db.run(
        "UPDATE customers SET full_name = %s WHERE id = %s", ("Crud Renamed", customer_id)
    )

    assert changed == 1
    name = db.value("SELECT full_name FROM customers WHERE id = %s", (customer_id,))
    assert name == "Crud Renamed"
    assert db.all(others, (customer_id,)) == others_before


def test_delete_removes_the_row(db, customer_id):
    assert db.run("DELETE FROM customers WHERE id = %s", (customer_id,)) == 1
    assert db.one("SELECT id FROM customers WHERE id = %s", (customer_id,)) is None


def test_update_of_unknown_id_changes_nothing(db):
    assert db.run("UPDATE customers SET full_name = %s WHERE id = %s", ("Nobody", 99999)) == 0
