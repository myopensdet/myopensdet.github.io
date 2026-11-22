# Template from myOpenSDET: https://myopensdet.github.io/
"""Level 1, in code: replace the payment client with a mock (unittest.mock, part of Python).

Fast and exact: no network at all. Use it for the rules in your own code: what does
checkout do for each answer the provider can give?
"""

from unittest.mock import create_autospec, patch

import pytest
import requests
from shop.payments import (
    PaymentClient,
    PaymentDeclinedError,
    PaymentUnavailableError,
    checkout,
)


@pytest.fixture
def client():
    # autospec: the mock has the real class's methods and arguments, so a typo fails
    return create_autospec(PaymentClient, instance=True)


def test_paid(client):
    client.charge.return_value = {"id": "ch_1", "status": "succeeded"}

    result = checkout(order_id=101, card="4242424242424242", amount_cents=2449, client=client)

    assert result == {"status": "paid", "message": "Paid. Receipt ch_1."}
    client.charge.assert_called_once_with(card="4242424242424242", amount_cents=2449, order_id=101)


def test_declined(client):
    client.charge.side_effect = PaymentDeclinedError("insufficient_funds")

    result = checkout(order_id=101, card="4242424242424242", amount_cents=2449, client=client)

    assert result["status"] == "declined"
    assert result["message"] == "Your card was declined (insufficient_funds)."


def test_provider_down_keeps_the_order(client):
    client.charge.side_effect = PaymentUnavailableError("Timeout")

    result = checkout(order_id=101, card="4242424242424242", amount_cents=2449, client=client)

    assert result["status"] == "pending"


def test_a_timeout_becomes_payment_unavailable():
    # patch where it's USED: shop.payments.requests, not the requests package everywhere
    with (
        patch("shop.payments.requests.post", side_effect=requests.Timeout),
        pytest.raises(PaymentUnavailableError, match="Timeout"),
    ):
        PaymentClient(base_url="http://payments.invalid").charge("4242424242424242", 2449, 101)
