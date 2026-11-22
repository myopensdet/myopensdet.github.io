# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""A tiny web app to see how the web works: a server, an HTML page, JavaScript that calls
a REST API in the background (AJAX), and JSON answers. Standard library only.

    python web_demo.py                  # everything works
    python web_demo.py --bug frontend   # the page shows a wrong price, the API is right
    python web_demo.py --bug backend    # the API sends a wrong price

Then open http://127.0.0.1:8797 in a browser. Ctrl+C stops it.

The REST API:
    GET  /api/products        every product
    GET  /api/products/<id>   one product
    POST /api/cart            {"product_id": 1, "quantity": 2} adds to a new cart
"""

import argparse
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PAGE = Path(__file__).with_name("page")
PRODUCTS = [
    {"id": 1, "title": "Practice book", "price": 24.50, "stock": 3},
    {"id": 2, "title": "Test mug", "price": 9.99, "stock": 12},
    {"id": 3, "title": "Bug sticker", "price": 1.50, "stock": 0},
]
BUG = None  # set by --bug


def products():
    if BUG == "backend":
        return [p | {"price": 99.90} if p["id"] == 2 else p for p in PRODUCTS]
    return PRODUCTS


class Shop(BaseHTTPRequestHandler):
    server_version = "PracticeShop/1.0"

    def send(self, status, body, content_type="application/json"):
        data = body.encode() if isinstance(body, str) else json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/":
            self.send(200, (PAGE / "index.html").read_text(encoding="utf-8"), "text/html")
        elif self.path == "/app.js":
            script = (PAGE / "app.js").read_text(encoding="utf-8")
            if BUG == "frontend":
                script = script.replace("price.toFixed(2)", "Math.round(price)")
            self.send(200, script, "text/javascript")
        elif self.path == "/api/products":
            self.send(200, products())
        elif match := re.fullmatch(r"/api/products/(\d+)", self.path):
            found = [p for p in products() if p["id"] == int(match[1])]
            if found:
                self.send(200, found[0])
            else:
                self.send(404, {"error": f"product {match[1]} not found"})
        else:
            self.send(404, {"error": f"nothing at {self.path}"})

    def do_POST(self):
        if self.path != "/api/cart":
            self.refuse()
            return
        if "application/json" not in self.headers.get("Content-Type", ""):
            self.send(415, {"error": "send JSON, with Content-Type: application/json"})
            return
        raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        try:
            order = json.loads(raw)
            product_id, quantity = int(order["product_id"]), int(order["quantity"])
        except (ValueError, KeyError, TypeError):
            self.send(400, {"error": 'send JSON like {"product_id": 1, "quantity": 2}'})
            return
        product = next((p for p in products() if p["id"] == product_id), None)
        if product is None:
            self.send(404, {"error": f"product {product_id} not found"})
        elif product["stock"] == 0:
            self.send(422, {"error": f"{product['title']} is sold out"})
        elif not 1 <= quantity <= product["stock"]:
            self.send(422, {"error": f"quantity must be 1 to {product['stock']}"})
        else:
            total = round(product["price"] * quantity, 2)
            self.send(201, {"items": [{"product_id": product_id, "quantity": quantity}],
                            "total": total})  # fmt: skip

    def refuse(self):
        self.send(405, {"error": f"{self.command} is not allowed on {self.path}"})

    do_PUT = do_PATCH = do_DELETE = refuse  # noqa: N815 (names http.server looks for)

    def log_message(self, fmt, *args):
        print(f"server got: {self.command} {self.path} -> {args[1]}", flush=True)


def main():
    global BUG  # noqa: PLW0603 (one setting for the whole small server)
    parser = argparse.ArgumentParser(description="A tiny practice web app.")
    parser.add_argument("--bug", choices=["frontend", "backend"], help="plant a price bug")
    parser.add_argument("--port", type=int, default=8797)
    args = parser.parse_args()
    BUG = args.bug
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Shop)
    note = f" with a {BUG} bug" if BUG else ""
    print(f"Practice shop{note} on http://127.0.0.1:{args.port}  (Ctrl+C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopped.")


if __name__ == "__main__":
    main()
