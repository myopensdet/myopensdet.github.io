# Template from myOpenSDET: https://myopensdet.github.io/
"""The orders service: the one customers call. It talks to stock and payments.

    POST /orders  {"sku": "SNS-0042", "qty": 2}
      1. GET  stock/SNS-0042        the price
      2. POST stock/reservations    keep the items
      3. POST payments/charges      take the money
      If the payment fails, it gives the items back: DELETE stock/reservations/<id>.

Settings: STOCK_URL, PAYMENTS_URL, and ORDERS_BUG=no_release to plant a bug
(the items are not given back when a payment fails).
"""

import os

from common import ServiceDown, call, serve

STOCK_URL = os.environ.get("STOCK_URL", "http://127.0.0.1:8812")
PAYMENTS_URL = os.environ.get("PAYMENTS_URL", "http://127.0.0.1:8813")
TIMEOUT = float(os.environ.get("CALL_TIMEOUT", "2"))
ORDERS: dict[str, dict] = {}


def place_order(body, request_id):
    sku, qty = body.get("sku"), body.get("qty")
    status, item = call("orders", request_id, "GET", f"{STOCK_URL}/stock/{sku}", timeout=TIMEOUT)
    if status != 200:
        return 404, {"error": f"unknown sku {sku}"}
    status, reservation = call(
        "orders", request_id, "POST", f"{STOCK_URL}/reservations", {"sku": sku, "qty": qty}, TIMEOUT
    )
    if status != 201:
        return 409, reservation
    order_id = f"o{len(ORDERS) + 1}"
    amount = item["price_cents"] * qty
    try:
        status, charge = call(
            "orders", request_id, "POST", f"{PAYMENTS_URL}/charges",
            {"order_id": order_id, "amount_cents": amount}, TIMEOUT,
        )  # fmt: skip
    except ServiceDown:
        status = 503
    if status != 201:
        if os.environ.get("ORDERS_BUG") != "no_release":
            rid = reservation["reservation_id"]
            call("orders", request_id, "DELETE", f"{STOCK_URL}/reservations/{rid}", timeout=TIMEOUT)
        ORDERS[order_id] = {"status": "payment_failed", "sku": sku, "qty": qty}
        return (402 if status == 402 else 503), {"order_id": order_id, "status": "payment_failed"}
    ORDERS[order_id] = {"status": "paid", "sku": sku, "qty": qty, "amount_cents": amount}
    return 201, {"order_id": order_id, "status": "paid", "amount_cents": amount}


def routes(method, path, body, request_id):
    if method == "GET" and path == "/health":
        return 200, {"service": "orders", "ok": True}
    if method == "POST" and path == "/orders":
        try:
            return place_order(body, request_id)
        except ServiceDown as error:
            return 503, {"error": f"a service is unavailable: {error}"}
    if method == "GET" and path.startswith("/orders/"):
        order = ORDERS.get(path.rsplit("/", 1)[1])
        return (200, order) if order else (404, {"error": "unknown order"})
    return 404, {"error": f"no route {method} {path}"}


if __name__ == "__main__":
    serve("orders", routes, 8811)
