# Template from myOpenSDET: https://myopensdet.github.io/
"""The orders service alone. Stock and payments are fakes, so each test decides
exactly what they answer, and checks exactly what orders sent them."""

import time

import requests

ITEM = (200, {"sku": "SNS-0042", "available": 40, "price_cents": 2499})


def test_a_paid_order_charges_price_times_quantity(orders_alone):
    stock, payments = orders_alone["stock"], orders_alone["payments"]
    stock.answers[("GET", "/stock/SNS-0042")] = ITEM
    stock.answers[("POST", "/reservations")] = (201, {"reservation_id": "r7"})
    payments.answers[("POST", "/charges")] = (201, {"charge_id": "c1"})

    response = requests.post(
        f"{orders_alone['url']}/orders", json={"sku": "SNS-0042", "qty": 2}, timeout=5
    )

    assert response.status_code == 201
    assert response.json()["status"] == "paid"
    assert payments.calls == [("POST", "/charges", {"order_id": "o1", "amount_cents": 4998})]


def test_a_declined_payment_gives_the_items_back(orders_alone):
    stock, payments = orders_alone["stock"], orders_alone["payments"]
    stock.answers[("GET", "/stock/SNS-0042")] = ITEM
    stock.answers[("POST", "/reservations")] = (201, {"reservation_id": "r7"})
    stock.answers[("DELETE", "/reservations/r7")] = (204, None)
    payments.answers[("POST", "/charges")] = (402, {"error": "declined"})

    response = requests.post(
        f"{orders_alone['url']}/orders", json={"sku": "SNS-0042", "qty": 2}, timeout=5
    )

    assert response.status_code == 402
    assert ("DELETE", "/reservations/r7", None) in stock.calls


def test_a_slow_stock_service_gets_a_quick_503(orders_alone):
    def slow():
        time.sleep(2)
        return ITEM[1]

    orders_alone["stock"].answers[("GET", "/stock/SNS-0042")] = (200, slow)

    started = time.monotonic()
    response = requests.post(
        f"{orders_alone['url']}/orders", json={"sku": "SNS-0042", "qty": 1}, timeout=5
    )

    assert response.status_code == 503
    assert time.monotonic() - started < 1.5  # orders waits 0.5 s, not the full 2 s
    assert orders_alone["payments"].calls == []  # and never charges the card
