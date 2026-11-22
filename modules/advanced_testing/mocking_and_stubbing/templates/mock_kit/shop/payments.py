# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""The code under test: checkout asks a payment provider to charge a card.

The provider is the part we can't control in tests: a sandbox that is slow, sometimes
down, and can't be told to fail on demand. The tests replace it three ways:
unittest.mock (in code), a stub server (over HTTP) and page.route (in the browser).
"""

import os

import requests

PAYMENT_URL = os.environ.get("PAYMENT_URL", "http://127.0.0.1:8798")


class PaymentDeclinedError(Exception):
    """The provider answered: no. The reason is safe to show the customer."""


class PaymentUnavailableError(Exception):
    """No clear answer: a timeout, a lost connection or a provider error. Try again later."""


class PaymentClient:
    def __init__(self, base_url: str = PAYMENT_URL, timeout: float = 2.0):
        self.base_url = base_url
        self.timeout = timeout

    def charge(self, card: str, amount_cents: int, order_id: int) -> dict:
        try:
            response = requests.post(
                f"{self.base_url}/v1/charges",
                json={"card": card, "amount": amount_cents, "currency": "gbp"},
                headers={"Idempotency-Key": f"order-{order_id}"},  # a retry never charges twice
                timeout=self.timeout,
            )
        except (requests.Timeout, requests.ConnectionError) as err:
            raise PaymentUnavailableError(type(err).__name__) from err
        if response.status_code == 402:
            raise PaymentDeclinedError(response.json()["error"]["decline_code"])
        if response.status_code >= 500:
            raise PaymentUnavailableError(f"provider error {response.status_code}")
        response.raise_for_status()
        return response.json()


def checkout(order_id: int, card: str, amount_cents: int, client: PaymentClient) -> dict:
    """Charge the card and say what the customer sees. The order is kept in every case."""
    try:
        charge = client.charge(card=card, amount_cents=amount_cents, order_id=order_id)
    except PaymentDeclinedError as err:
        return {"status": "declined", "message": f"Your card was declined ({err})."}
    except PaymentUnavailableError:
        return {
            "status": "pending",
            "message": "We couldn't reach the payment service. Your order is saved: try again.",
        }
    return {"status": "paid", "message": f"Paid. Receipt {charge['id']}."}
