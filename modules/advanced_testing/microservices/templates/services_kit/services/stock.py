# Template from myOpenSDET: https://myopensdet.github.io/
"""The stock service: what is in the warehouse, and reservations for orders.

GET    /stock/SNS-0042        {"sku": "SNS-0042", "available": 40, "price_cents": 2499}
POST   /reservations          {"sku": "SNS-0042", "qty": 2}  -> 201 {"reservation_id": "r1"}
DELETE /reservations/r1       -> 204, and the items go back on the shelf
"""

import threading

from common import serve

STOCK = {
    "SNS-0042": {"available": 40, "price_cents": 2499},
    "GW-0001": {"available": 0, "price_cents": 8900},
}
RESERVATIONS: dict[str, dict] = {}
lock = threading.Lock()


def routes(method, path, body, request_id):
    parts = path.strip("/").split("/")
    if method == "GET" and path == "/health":
        return 200, {"service": "stock", "ok": True}
    if method == "GET" and parts[0] == "stock" and len(parts) == 2:
        item = STOCK.get(parts[1])
        if item is None:
            return 404, {"error": f"unknown sku {parts[1]}"}
        return 200, {"sku": parts[1]} | item
    if method == "POST" and path == "/reservations":
        sku, qty = body.get("sku"), body.get("qty")
        with lock:
            item = STOCK.get(sku)
            if item is None:
                return 404, {"error": f"unknown sku {sku}"}
            if not isinstance(qty, int) or qty < 1 or qty > item["available"]:
                return 409, {"error": f"only {item['available']} of {sku} available"}
            item["available"] -= qty
            reservation_id = f"r{len(RESERVATIONS) + 1}"
            RESERVATIONS[reservation_id] = {"sku": sku, "qty": qty}
        return 201, {"reservation_id": reservation_id}
    if method == "DELETE" and parts[0] == "reservations" and len(parts) == 2:
        with lock:
            reservation = RESERVATIONS.pop(parts[1], None)
            if reservation is None:
                return 404, {"error": f"unknown reservation {parts[1]}"}
            STOCK[reservation["sku"]]["available"] += reservation["qty"]
        return 204, None
    return 404, {"error": f"no route {method} {path}"}


if __name__ == "__main__":
    serve("stock", routes, 8812)
