# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""A tiny API with a bug that "works on my machine": every third request for order 7
fails with a 500. Run it, then point evidence.py at it.

    python practice_server.py            (http://127.0.0.1:8795, Ctrl+C to stop)
    python practice_server.py --fixed    (the bug is fixed)
"""

import contextlib
import itertools
import json
import sys
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 8795
VERSION = "2.14.0"


class Handler(BaseHTTPRequestHandler):
    fixed = False
    counter = itertools.count(1)
    lock = threading.Lock()

    def do_GET(self):  # noqa: N802
        if self.path != "/api/orders/7":
            self.answer(404, {"error": "not found"})
            return
        with self.lock:
            number = next(self.counter)
        if number % 3 == 0 and not self.fixed:
            self.answer(500, {"error": "internal error"})
        else:
            self.answer(200, {"id": 7, "status": "paid", "total": 36.0})

    def answer(self, status, data):
        raw = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("X-Request-Id", "req-" + uuid.uuid4().hex[:8])
        self.send_header("X-App-Version", VERSION)
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, *args):
        pass


def serve(port=PORT, fixed=False):
    Handler.fixed = fixed
    Handler.counter = itertools.count(1)
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


if __name__ == "__main__":
    server = serve(fixed="--fixed" in sys.argv)
    mode = " (fixed)" if Handler.fixed else ""
    print(f"Practice API on http://127.0.0.1:{PORT}{mode}  (Ctrl+C to stop)")
    with contextlib.suppress(KeyboardInterrupt):
        server.serve_forever()
