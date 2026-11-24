# Template from myOpenSDET: https://myopensdet.github.io/
"""All three services together. These tests check the conversations between them:
the stock count after an order, what happens when one service fails, and the request id."""

import time
import uuid

import requests
from trace_request import trace

SKU = "SNS-0042"


def available(system) -> int:
    return requests.get(f"{system['stock']}/stock/{SKU}", timeout=5).json()["available"]


def order(system, qty, request_id=None):
    headers = {"X-Request-ID": request_id} if request_id else {}
    body = {"sku": SKU, "qty": qty}
    return requests.post(f"{system['orders']}/orders", json=body, headers=headers, timeout=10)


def test_a_paid_order_takes_the_items_from_stock(system):
    before = available(system)
    response = order(system, 2)
    assert response.status_code == 201, response.text
    assert available(system) == before - 2


def test_a_declined_payment_puts_the_items_back(system):
    before = available(system)
    response = order(system, 25)  # 25 x £24.99 is over the £500 limit
    assert response.status_code == 402, response.text
    assert available(system) == before


def test_payments_down_puts_the_items_back(system, fault):
    before = available(system)
    fault("payments", down=True)
    response = order(system, 1)
    assert response.status_code == 503, response.text
    assert available(system) == before


def test_slow_stock_gives_a_503_within_the_timeout(system, fault):
    fault("stock", delay_ms=3000)
    started = time.monotonic()
    response = order(system, 1)
    assert response.status_code == 503, response.text
    assert time.monotonic() - started < 3


def test_one_request_id_reaches_every_service(system, log_lines):
    request_id = uuid.uuid4().hex[:12]
    response = order(system, 1, request_id)
    assert response.headers["X-Request-ID"] == request_id
    time.sleep(0.5)  # let the log lines reach the files
    services = {event["service"] for event in trace(request_id, log_lines())}
    assert services == {"orders", "stock", "payments"}
