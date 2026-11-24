# Template from myOpenSDET: https://myopensdet.github.io/
import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
import requests
import run_all

KIT = Path(__file__).resolve().parents[1]


# ---------- All three services together ----------


@pytest.fixture(scope="session")
def system(tmp_path_factory):
    """The running system. With ORDERS_URL set (Docker Compose, or a test environment),
    use it. Otherwise start the three services here, with fresh logs."""
    if os.environ.get("ORDERS_URL"):
        yield {
            "orders": os.environ["ORDERS_URL"],
            "stock": os.environ.get("STOCK_URL", "http://127.0.0.1:8812"),
            "payments": os.environ.get("PAYMENTS_URL", "http://127.0.0.1:8813"),
            "logs": None,
        }
        return
    logs = tmp_path_factory.mktemp("logs")
    processes = run_all.start(logs)
    urls = {name: f"http://127.0.0.1:{port}" for name, port in run_all.PORTS.items()}
    yield urls | {"logs": logs}
    run_all.stop(processes)


@pytest.fixture
def fault(system):
    """fault("payments", down=True) breaks one service.
    Every fault is switched off again after the test."""
    touched = []

    def switch(service, down=False, delay_ms=0):
        touched.append(service)
        body = {"down": down, "delay_ms": delay_ms}
        requests.post(f"{system[service]}/__faults", json=body, timeout=5).raise_for_status()

    yield switch
    for service in touched:
        requests.post(f"{system[service]}/__faults", json={}, timeout=5)


@pytest.fixture
def log_lines(system):
    """Every service's log lines so far."""

    def read():
        if system["logs"] is None:
            out = subprocess.run(
                ["docker", "compose", "logs", "--no-log-prefix"],  # noqa: S607
                cwd=KIT, capture_output=True, text=True, check=True,
            )  # fmt: skip
            return out.stdout.splitlines()
        return [line for p in system["logs"].glob("*.jsonl") for line in p.read_text().splitlines()]

    return read


# ---------- One service alone, with fakes for the others ----------


class Fake:
    """A fake service. answers[(method, path)] = (status, body). It keeps every call."""

    def __init__(self):
        self.answers: dict = {}
        self.calls: list = []
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def any(self):
                length = int(self.headers.get("Content-Length") or 0)
                body = json.loads(self.rfile.read(length)) if length else None
                fake.calls.append((self.command, self.path, body))
                status, answer = fake.answers.get((self.command, self.path), (404, {}))
                if callable(answer):
                    answer = answer()
                raw = json.dumps(answer).encode() if answer is not None else b""
                self.send_response(status)
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            do_GET = do_POST = do_DELETE = any  # noqa: N815 (names http.server needs)

            def log_message(self, *_):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_port}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()


@pytest.fixture
def orders_alone(tmp_path):
    """The orders service on its own port, talking to a fake stock and a fake payments."""
    stock, payments = Fake(), Fake()
    port = 8821
    run_all.check_port_free(port, "orders (alone)")
    env = os.environ | {
        "PORT": str(port),
        "STOCK_URL": stock.url,
        "PAYMENTS_URL": payments.url,
        "CALL_TIMEOUT": "0.5",
    }
    process = subprocess.Popen(
        [sys.executable, str(KIT / "services" / "orders.py")],
        env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )  # fmt: skip
    run_all.wait_until_up(f"http://127.0.0.1:{port}/health", "orders")
    yield {"url": f"http://127.0.0.1:{port}", "stock": stock, "payments": payments}
    process.terminate()
    process.wait(timeout=5)
    stock.server.shutdown()
    payments.server.shutdown()
