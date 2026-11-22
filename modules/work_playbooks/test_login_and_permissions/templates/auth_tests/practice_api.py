# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""A small practice API with login, tokens, orders and an admin page. Only for practice.

    python practice_api.py            # http://127.0.0.1:8765, with planted bugs
    python practice_api.py --fixed    # the same API with the bugs fixed

It has three planted access bugs, the kind real apps ship. Your tests should find them.
Python only, no packages. It listens on your computer only (127.0.0.1)."""

import argparse
import json
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PASSWORD = "local_only_password"  # noqa: S105  (fake practice password)
USERS = {
    "arshad.test@example.com": {"id": 1, "role": "customer"},
    "mia.khan@example.com": {"id": 2, "role": "customer"},
    "admin@example.com": {"id": 3, "role": "admin"},
}
ORDERS = {
    101: {"id": 101, "user_id": 1, "total": "64.48"},
    102: {"id": 102, "user_id": 2, "total": "15.99"},
}


def make_handler(fixed: bool):
    tokens: dict[str, str] = {}  # token -> email

    class API(BaseHTTPRequestHandler):
        def log_message(self, *args):  # keep the terminal quiet
            pass

        def answer(self, status, data=None):
            raw = b"" if data is None else json.dumps(data).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def current_user(self):
            header = self.headers.get("Authorization", "")
            email = tokens.get(header.removeprefix("Bearer "))
            return None if email is None else {"email": email, **USERS[email]}

        def do_POST(self):  # noqa: N802  (name required by http.server)
            if self.path == "/api/login":
                return self.log_in()
            if self.path == "/api/logout":
                user = self.current_user()
                if user is None:
                    return self.answer(401, {"error": "Log in first"})
                if fixed:  # BUG 3 when not fixed: logout leaves the token working
                    tokens.pop(self.headers["Authorization"].removeprefix("Bearer "))
                return self.answer(204)
            return self.answer(404, {"error": "No such page"})

        def log_in(self):
            length = int(self.headers.get("Content-Length") or 0)
            try:
                body = json.loads(self.rfile.read(length) or b"{}")
                email, password = body["email"], body["password"]
            except (ValueError, KeyError, TypeError):
                return self.answer(400, {"error": "Send email and password"})
            if email not in USERS:  # BUG 1 when not fixed: tells who has an account
                return self.answer(
                    401, {"error": "Wrong email or password" if fixed else "No such user"}
                )
            if password != PASSWORD:
                return self.answer(401, {"error": "Wrong email or password"})
            token = secrets.token_urlsafe(24)
            tokens[token] = email
            return self.answer(200, {"token": token, "user": {"email": email, **USERS[email]}})

        def do_GET(self):  # noqa: N802
            user = self.current_user()
            if user is None:
                return self.answer(401, {"error": "Log in first"})
            if self.path == "/api/me":
                return self.answer(200, user)
            if self.path.startswith("/api/orders/"):
                order_id = self.path.removeprefix("/api/orders/")
                order = ORDERS.get(int(order_id)) if order_id.isdigit() else None
                # BUG 2 when not fixed: any logged-in user can read anyone's order
                if order is None or (fixed and order["user_id"] != user["id"]):
                    return self.answer(404, {"error": "No such order"})
                return self.answer(200, order)
            if self.path == "/api/admin/users":
                if user["role"] != "admin":
                    return self.answer(403, {"error": "Admins only"})
                return self.answer(200, [{"email": e, **u} for e, u in USERS.items()])
            return self.answer(404, {"error": "No such page"})

    return API


def serve(port: int = 8765, fixed: bool = False) -> ThreadingHTTPServer:
    return ThreadingHTTPServer(("127.0.0.1", port), make_handler(fixed))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--fixed", action="store_true", help="run with the bugs fixed")
    args = parser.parse_args()
    server = serve(args.port, args.fixed)
    kind = "bugs fixed" if args.fixed else "with planted bugs"
    print(f"Practice API ({kind}) on http://127.0.0.1:{args.port}  (Ctrl+C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopped")
