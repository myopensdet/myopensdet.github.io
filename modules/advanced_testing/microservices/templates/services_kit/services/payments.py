# Template from myOpenSDET: https://myopensdet.github.io/
"""The payments service: charges an order. Practice rule: over £500.00 is declined.

POST /charges  {"order_id": "o1", "amount_cents": 4998}  -> 201 {"charge_id": "c1"}
                                                        -> 402 {"error": "declined"}
"""

from common import serve

LIMIT_CENTS = 50000
CHARGES: list[dict] = []


def routes(method, path, body, request_id):
    if method == "GET" and path == "/health":
        return 200, {"service": "payments", "ok": True}
    if method == "POST" and path == "/charges":
        amount = body.get("amount_cents")
        if not isinstance(amount, int) or amount < 1:
            return 400, {"error": "amount_cents must be a whole number above 0"}
        if amount > LIMIT_CENTS:
            return 402, {"error": "declined: over the limit"}
        CHARGES.append(body)
        return 201, {"charge_id": f"c{len(CHARGES)}"}
    return 404, {"error": f"no route {method} {path}"}


if __name__ == "__main__":
    serve("payments", routes, 8813)
