# Template from myOpenSDET: https://myopensdet.github.io/
"""The consumer: the code in the orders service that calls the stock service.

The contract test checks THIS code against a Pact mock of stock, and writes down
exactly what it needs from stock: the contract.
"""

from dataclasses import dataclass

import requests


@dataclass
class Item:
    sku: str
    available: int
    price_cents: int


class NotFound(Exception):  # noqa: N818 (reads better: except NotFound)
    pass


class StockClient:
    def __init__(self, base_url: str, timeout: float = 5):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get_item(self, sku: str) -> Item:
        response = requests.get(f"{self.base_url}/stock/{sku}", timeout=self.timeout)
        if response.status_code == 404:
            raise NotFound(sku)
        response.raise_for_status()
        body = response.json()
        # Only these three fields are used, so only these go in the contract.
        return Item(sku=body["sku"], available=body["available"], price_cents=body["price_cents"])

    def reserve(self, sku: str, qty: int) -> str:
        response = requests.post(
            f"{self.base_url}/reservations", json={"sku": sku, "qty": qty}, timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()["reservation_id"]
