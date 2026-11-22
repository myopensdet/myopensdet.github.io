# Template from myOpenSDET: https://myopensdet.github.io/
"""Level 2, over HTTP: the real PaymentClient talks to a stub server instead of the provider.

Tests the real requests, JSON, headers and timeouts, which a mock in code skips. Each
test card number makes the stub answer differently (see stubs/mappings).
"""

import json

from conftest import sent_to
from shop.payments import PaymentClient, checkout

OK, DECLINED, PROVIDER_ERROR, TOO_SLOW = (
    "4242424242424242",
    "4000000000000002",
    "4000000000000119",
    "4000000000009999",
)


def pay(stub, card):
    return checkout(order_id=101, card=card, amount_cents=2449, client=PaymentClient(stub))


def test_paid(stub):
    assert pay(stub, OK) == {"status": "paid", "message": "Paid. Receipt ch_test_1001."}


def test_declined(stub):
    assert pay(stub, DECLINED)["message"] == "Your card was declined (insufficient_funds)."


def test_provider_error_keeps_the_order(stub):
    assert pay(stub, PROVIDER_ERROR)["status"] == "pending"


def test_too_slow_keeps_the_order(stub):
    # the stub waits 3 seconds; the client gives up after 2
    assert pay(stub, TOO_SLOW)["status"] == "pending"


def test_what_was_sent(stub):
    pay(stub, OK)
    [request] = sent_to(stub)
    assert request["method"] == "POST"
    assert json.loads(request["body"]) == {"card": OK, "amount": 2449, "currency": "gbp"}
    assert request["headers"]["Idempotency-Key"] == "order-101"
