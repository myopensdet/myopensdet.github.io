# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Put data straight into the database, then check the API reads and changes it right."""

import pytest


@pytest.fixture
def order_in_db(db, cleanup, customer, book):
    """An order written straight into the database, with values the API must show as they are."""
    row = db.one(
        "INSERT INTO orders (customer_id, book_id, quantity, unit_price, total, status) "
        "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
        (customer["id"], book["id"], 1, 24.99, 24.99, "shipped"),
    )
    cleanup.add("orders", row["id"])
    return row["id"]


def test_api_shows_what_the_database_holds(api, order_in_db, book):
    response = api.get(f"/orders/{order_in_db}")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "shipped"  # a status the API can't make on its own
    assert body["book_id"] == book["id"]
    assert float(body["total"]) == 24.99


def test_delete_through_the_api_removes_the_row(api, db, order_in_db, book):
    response = api.delete(f"/orders/{order_in_db}")

    assert response.status_code == 204
    assert db.one("SELECT id FROM orders WHERE id = %s", (order_in_db,)) is None
    assert db.value("SELECT stock FROM books WHERE id = %s", (book["id"],)) == book["stock"] + 1


def test_unknown_order_is_404(api):
    assert api.get("/orders/999999999").status_code == 404
