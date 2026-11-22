# Template from myOpenSDET: https://myopensdet.github.io/
"""Reach the shop through its API."""

from decimal import Decimal

import requests


class ApiDriver:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.http = requests.Session()
        self.cart_id = None
        self.last_message = ""

    def _send(self, method: str, path: str, **kwargs) -> dict:
        response = self.http.request(method, f"{self.base_url}{path}", timeout=10, **kwargs)
        body = response.json()
        if response.status_code == 400:  # the shop refused: keep its reason, like the page shows it
            self.last_message = body["detail"]
            return body
        response.raise_for_status()
        self.last_message = body.get("message", "")
        return body

    def start_empty_cart(self) -> None:
        self.cart_id = self._send("POST", "/api/carts")["id"]

    def add_book(self, book: str, copies: int) -> None:
        self._send(
            "POST", f"/api/carts/{self.cart_id}/items", json={"book": book, "copies": copies}
        )

    def apply_coupon(self, code: str) -> None:
        self._send("POST", f"/api/carts/{self.cart_id}/coupon", json={"code": code})

    def total(self) -> Decimal:
        return Decimal(self._send("GET", f"/api/carts/{self.cart_id}")["total"])

    def message(self) -> str:
        return self.last_message

    def close(self) -> None:
        self.http.close()
