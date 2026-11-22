# Template from myOpenSDET: https://myopensdet.github.io/
"""A small practice web server for networking checks. Only for practice.

    python practice_server.py      # http://127.0.0.1:8790

  /login   sets a session cookie (planted problem: no HttpOnly, no SameSite)
  /api/me  answers any website's scripts with your cookie (planted problem: CORS too open)
  /slow    takes 30 seconds to answer
  /old     sends you on to /login
Python only, no packages. It listens on your computer only (127.0.0.1)."""

import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # keep the terminal quiet
        pass

    def answer(self, status, data, headers=()):
        raw = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        for name, value in headers:
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):  # noqa: N802  (name required by http.server)
        if self.path == "/login":
            return self.answer(200, {"logged_in": True},
                               [("Set-Cookie", "session=practice-only; Path=/")])  # fmt: skip
        if self.path == "/api/me":
            origin = self.headers.get("Origin", "")
            cors = [("Access-Control-Allow-Origin", origin),
                    ("Access-Control-Allow-Credentials", "true")] if origin else []  # fmt: skip
            return self.answer(200, {"email": "arshad.test@example.com"}, cors)
        if self.path == "/slow":
            time.sleep(30)
            return self.answer(200, {"done": True})
        if self.path == "/old":
            return self.answer(301, {}, [("Location", "/login")])
        return self.answer(404, {"error": "No such page"})


class Server(ThreadingHTTPServer):
    daemon_threads = True


def serve(port: int = 8790) -> ThreadingHTTPServer:
    return Server(("127.0.0.1", port), Handler)


if __name__ == "__main__":
    print("Practice server on http://127.0.0.1:8790  (Ctrl+C to stop)", flush=True)
    try:
        serve().serve_forever()
    except KeyboardInterrupt:
        print("Stopped")
