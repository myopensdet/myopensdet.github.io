# Template from myOpenSDET: https://myopensdet.github.io/
"""The provider: a small stock service. Standard library only.

    python stock_service.py                       # port 8812
    STOCK_CHANGE=rename_price python stock_service.py

STOCK_CHANGE plants a change another team might make:
  rename_price   "price_cents" becomes "price" (a breaking change)
  price_as_text  "price_cents": 2499 becomes "24.99" (a breaking change)
  add_field      adds "warehouse" (a safe change: consumers ignore extra fields)
"""

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ITEMS: dict[str, dict] = {}
RESERVATIONS: dict[str, dict] = {}


def item_view(sku: str, item: dict) -> dict:
    view = {"sku": sku, "available": item["available"], "price_cents": item["price_cents"]}
    change = os.environ.get("STOCK_CHANGE", "")
    if change == "rename_price":
        view["price"] = view.pop("price_cents")
    if change == "price_as_text":
        view["price_cents"] = f"{view['price_cents'] / 100:.2f}"
    if change == "add_field":
        view["warehouse"] = "Dhaka-1"
    return view


class Handler(BaseHTTPRequestHandler):
    def answer(self, status: int, body: dict) -> None:
        raw = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        parts = self.path.strip("/").split("/")
        if len(parts) == 2 and parts[0] == "stock":
            item = ITEMS.get(parts[1])
            if item is None:
                return self.answer(404, {"error": f"unknown sku {parts[1]}"})
            return self.answer(200, item_view(parts[1], item))
        self.answer(404, {"error": f"no route GET {self.path}"})

    def do_POST(self):
        if self.path != "/reservations":
            return self.answer(404, {"error": f"no route POST {self.path}"})
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
        item = ITEMS.get(body.get("sku"))
        if item is None:
            return self.answer(404, {"error": f"unknown sku {body.get('sku')}"})
        qty = body.get("qty")
        if not isinstance(qty, int) or not 1 <= qty <= item["available"]:
            return self.answer(409, {"error": f"only {item['available']} available"})
        item["available"] -= qty
        reservation_id = f"r{len(RESERVATIONS) + 1}"
        RESERVATIONS[reservation_id] = body
        self.answer(201, {"reservation_id": reservation_id})

    def log_message(self, *_):
        pass


def start(port: int = 0) -> ThreadingHTTPServer:
    """Start in a background thread (for tests). Port 0 means any free port."""
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


if __name__ == "__main__":
    ITEMS.update({"SNS-0042": {"available": 40, "price_cents": 2499}})
    server = start(int(os.environ.get("PORT", "8812")))
    print(f"stock on http://127.0.0.1:{server.server_port}  (Ctrl+C to stop)")
    threading.Event().wait()
