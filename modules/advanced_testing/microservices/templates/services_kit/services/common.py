# Template from myOpenSDET: https://myopensdet.github.io/
"""What every practice service shares: a JSON web server, JSON log lines with the
request id, calls to other services that pass the request id on, and test-only faults.

Standard library only, so the services run anywhere Python 3.13 runs.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

REQUEST_ID = "X-Request-ID"


def log(service: str, request_id: str, event: str, **fields) -> None:
    """One JSON line per event. The request id ties lines from different services together."""
    line = {"time": round(time.time(), 6), "service": service, "request_id": request_id}
    print(json.dumps(line | {"event": event} | fields), flush=True)


class ServiceDown(Exception):  # noqa: N818 (reads better in the tests)
    """Another service could not be reached, or did not answer in time."""


def call(service, request_id, method, url, body=None, timeout=2.0):
    """Call another service. Returns (status, json). Passes the request id on."""
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(url, data=data, method=method)  # noqa: S310
    request.add_header(REQUEST_ID, request_id)
    if data is not None:
        request.add_header("Content-Type", "application/json")
    started = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            status, raw = response.status, response.read()
    except urllib.error.HTTPError as error:
        status, raw = error.code, error.read()
    except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
        reason = getattr(error, "reason", error)
        log(service, request_id, "call_failed", method=method, url=url, error=str(reason))
        raise ServiceDown(f"{method} {url}: {reason}") from None
    ms = round((time.monotonic() - started) * 1000)
    log(service, request_id, "called", method=method, url=url, status=status, ms=ms)
    return status, json.loads(raw) if raw else None


class Faults:
    """Test-only switches, set with POST /__faults: {"down": true} or {"delay_ms": 3000}.
    Never ship these to production: they exist so tests can break a service on purpose."""

    down = False
    delay_ms = 0


def make_handler(service: str, routes):
    """routes(method, path, body, request_id) -> (status, json body or None)."""

    class Handler(BaseHTTPRequestHandler):
        def handle_any(self, method):
            request_id = self.headers.get(REQUEST_ID) or uuid.uuid4().hex[:12]
            length = int(self.headers.get("Content-Length") or 0)
            try:
                body = json.loads(self.rfile.read(length)) if length else None
            except ValueError:
                return self.reply(400, {"error": "send JSON"}, request_id)
            if self.path == "/__faults" and method == "POST":
                body = body or {}
                Faults.down = bool(body.get("down", False))
                Faults.delay_ms = int(body.get("delay_ms", 0))
                return self.reply(
                    200, {"down": Faults.down, "delay_ms": Faults.delay_ms}, request_id
                )
            if Faults.down and self.path != "/health":
                return self.reply(
                    503, {"error": f"{service} is down (fault switched on)"}, request_id
                )
            if Faults.delay_ms:
                time.sleep(Faults.delay_ms / 1000)
            log(service, request_id, "received", method=method, path=self.path)
            status, answer = routes(method, self.path, body or {}, request_id)
            self.reply(status, answer, request_id)

        def reply(self, status, answer, request_id):
            raw = json.dumps(answer).encode() if answer is not None else b""
            self.send_response(status)
            self.send_header(REQUEST_ID, request_id)
            if raw:
                self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            log(service, request_id, "answered", path=self.path, status=status)

        def do_GET(self):
            self.handle_any("GET")

        def do_POST(self):
            self.handle_any("POST")

        def do_DELETE(self):
            self.handle_any("DELETE")

        def log_message(self, *_):
            pass

    return Handler


def serve(service: str, routes, default_port: int) -> None:
    port = int(os.environ.get("PORT", default_port))
    # 0.0.0.0 so other containers can reach it. Ports are published on 127.0.0.1 only.
    server = ThreadingHTTPServer(("0.0.0.0", port), make_handler(service, routes))  # noqa: S104
    print(f"{service} on port {port}", file=sys.stderr, flush=True)
    server.serve_forever()
