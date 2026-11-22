# Template from myOpenSDET: https://myopensdet.github.io/
"""The smoke test template passes on a healthy app and fails clearly on a broken one."""

import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

TEMPLATE = Path(__file__).resolve().parents[1] / "templates" / "test_smoke.py"


class FakeApp(BaseHTTPRequestHandler):
    health_status = 200

    def do_GET(self):  # noqa: N802  (the name http.server expects)
        if self.path == "/health":
            self.answer(self.health_status, json.dumps({"status": "ok"}), "application/json")
        elif self.path in ("/", "/login"):
            self.answer(200, "<h1>Shop</h1>", "text/html")
        else:
            self.answer(404, "Not found", "text/plain")

    def answer(self, status, body, content_type):
        data = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):  # keep the test output quiet
        pass


@pytest.fixture
def fake_app():
    FakeApp.health_status = 200
    server = ThreadingHTTPServer(("127.0.0.1", 0), FakeApp)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


def run_smoke(env_changes):
    env = {k: v for k, v in os.environ.items() if k not in ("BASE_URL", "SMOKE_PAGES")}
    env.update(env_changes)
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(TEMPLATE)],
        cwd=TEMPLATE.parent,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_a_healthy_app_passes(fake_app):
    result = run_smoke({"BASE_URL": fake_app, "SMOKE_PAGES": "/,/login"})
    assert result.returncode == 0, result.stdout
    assert "4 passed" in result.stdout


def test_a_broken_health_check_fails_with_its_status(fake_app):
    FakeApp.health_status = 503
    result = run_smoke({"BASE_URL": fake_app})
    assert result.returncode == 1
    assert "/health answered 503" in result.stdout


def test_a_missing_page_fails_with_its_name(fake_app):
    result = run_smoke({"BASE_URL": fake_app, "SMOKE_PAGES": "/checkout"})
    assert result.returncode == 1
    assert "/checkout answered 404" in result.stdout


def test_without_base_url_every_test_is_skipped():
    result = run_smoke({})
    assert result.returncode == 0
    assert "3 skipped" in result.stdout
