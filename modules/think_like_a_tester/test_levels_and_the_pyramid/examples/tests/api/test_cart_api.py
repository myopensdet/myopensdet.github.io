# Template from myOpenSDET: https://myopensdet.github.io/
"""API tests: send real HTTP requests and check the answers, the way another program would."""

from fastapi.testclient import TestClient
from shop.api import app

client = TestClient(app)


def test_totals_for_a_normal_order():
    response = client.post(
        "/api/cart/totals",
        json={"lines": [{"name": "Python book", "price_cents": 2500, "quantity": 2}]},
    )
    assert response.status_code == 200
    assert response.json()["total"] == 5000


def test_quantity_above_10_is_refused():
    response = client.post(
        "/api/cart/totals",
        json={"lines": [{"name": "Python book", "price_cents": 2500, "quantity": 11}]},
    )
    assert response.status_code == 422


def test_an_unknown_coupon_gives_400():
    order = {"lines": [{"name": "Python book", "price_cents": 2500}], "coupon": "FREE100"}
    response = client.post("/api/cart/totals", json=order)
    assert response.status_code == 400
    assert response.json() == {"detail": "Unknown coupon: FREE100"}
