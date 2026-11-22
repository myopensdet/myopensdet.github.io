# Template from myOpenSDET: https://myopensdet.github.io/
"""A small practice API for speed checks. Only for practice.

    python practice_api.py            # http://127.0.0.1:8770, with planted speed problems
    python practice_api.py --fixed    # the same API with the problems fixed

Two planted problems, the kind real apps ship: search handles one request at a time,
and the report page fails when more than 4 people use it at once.
Python only, no packages. It listens on your computer only (127.0.0.1)."""

import argparse
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

PRODUCTS = [{"id": n, "name": f"Book {n}", "price": "9.99"} for n in range(1, 21)]


def make_handler(fixed: bool):
    search_lock = threading.Lock()
    report_slots = threading.BoundedSemaphore(4)

    class API(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"  # keep connections open, like real servers

        def log_message(self, *args):  # keep the terminal quiet
            pass

        def answer(self, status, data):
            raw = json.dumps(data).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):  # noqa: N802  (name required by http.server)
            url = urlparse(self.path)
            if url.path == "/api/products":
                time.sleep(0.01)
                return self.answer(200, PRODUCTS)
            if url.path == "/api/search":
                word = parse_qs(url.query).get("q", [""])[0].lower()
                if fixed:
                    time.sleep(0.05)
                else:  # PROBLEM 1: one search at a time, so everyone waits in a queue
                    with search_lock:
                        time.sleep(0.05)
                return self.answer(200, [p for p in PRODUCTS if word in p["name"].lower()])
            if url.path == "/api/report":
                if fixed:
                    time.sleep(0.2)
                    return self.answer(200, {"orders": 128, "revenue": "1279.72"})
                # PROBLEM 2: only 4 reports at a time; the 5th person gets an error
                if not report_slots.acquire(blocking=False):
                    return self.answer(503, {"error": "Too busy"})
                try:
                    time.sleep(0.2)
                    return self.answer(200, {"orders": 128, "revenue": "1279.72"})
                finally:
                    report_slots.release()
            return self.answer(404, {"error": "No such page"})

    return API


class Server(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 128  # room for many users connecting at once


def serve(port: int = 8770, fixed: bool = False) -> ThreadingHTTPServer:
    return Server(("127.0.0.1", port), make_handler(fixed))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=8770)
    parser.add_argument("--fixed", action="store_true", help="run with the problems fixed")
    args = parser.parse_args()
    server = serve(args.port, args.fixed)
    kind = "problems fixed" if args.fixed else "with planted speed problems"
    print(f"Practice API ({kind}) on http://127.0.0.1:{args.port}  (Ctrl+C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopped")
