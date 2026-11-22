# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Call the API, then prove the change landed in the database, exactly."""

from decimal import Decimal

import pytest


def test_order_is_saved_as_the_api_said(db, place_order, customer, book):
    answer = place_order(customer_id=customer["id"], book_id=book["id"], quantity=2)

    saved = db.one(
        "SELECT customer_id, book_id, quantity, unit_price, total, status "
        "FROM orders WHERE id = %s",
        (answer["id"],),
    )
    assert saved is not None, "The API answered 201, but there is no order in the database"
    assert saved["customer_id"] == customer["id"]
    assert saved["book_id"] == book["id"]
    assert saved["quantity"] == 2
    assert saved["total"] == Decimal("49.98")
    assert saved["status"] == "new"
    assert Decimal(str(answer["total"])) == saved["total"]  # the answer matches what was saved


def test_order_takes_the_stock(db, place_order, customer, book):
    place_order(customer_id=customer["id"], book_id=book["id"], quantity=3)
    assert db.value("SELECT stock FROM books WHERE id = %s", (book["id"],)) == book["stock"] - 3


def test_refused_order_changes_nothing(api, db, customer, book):
    orders_before = db.value("SELECT COUNT(*) FROM orders")

    response = api.post(
        "/orders", json={"customer_id": customer["id"], "book_id": book["id"], "quantity": 11}
    )

    assert response.status_code == 422
    assert db.value("SELECT COUNT(*) FROM orders") == orders_before
    assert db.value("SELECT stock FROM books WHERE id = %s", (book["id"],)) == book["stock"]


@pytest.mark.xfail(
    reason="Practice API bug: a price sent by the client is saved",
    raises=AssertionError,
    strict=True,
)
def test_price_comes_from_the_database_not_the_client(db, place_order, customer, book):
    answer = place_order(
        customer_id=customer["id"], book_id=book["id"], quantity=1, unit_price=0.01
    )
    saved = db.value("SELECT unit_price FROM orders WHERE id = %s", (answer["id"],))
    assert saved == book["price"]
