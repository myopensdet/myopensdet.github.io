# Template from myOpenSDET: https://myopensdet.github.io/
"""New API endpoint playbook: the probe script and the test template work against a small
local API that follows the rules (offline), and catch a bug put in on purpose.
With ZTS_ONLINE=1, the template finds the four known issues in DummyJSON's /carts/add."""

import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
KIT = TOPIC / "templates" / "endpoint_kit"
CREDIT = "Template from myOpenSDET: https://myopensdet.github.io/"
PRICES = {144: 44.99}

SKIP_FOLDERS = {"__pycache__", ".pytest_cache"}
SUFFIXES = {".py", ".ini", ".txt", ".md", ".json"}
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file()
    and not SKIP_FOLDERS & set(p.parts)
    and (p.suffix in SUFFIXES or p.name == ".gitignore")
    and p.name != "__init__.py"
)


def make_handler(allow_negative: bool):
    class Carts(BaseHTTPRequestHandler):
        def log_message(self, *args):  # keep test output quiet
            pass

        def answer(self, status, data):
            raw = json.dumps(data).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_POST(self):  # noqa: N802  (name required by http.server)
            raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            try:
                body = json.loads(raw)
            except ValueError:
                return self.answer(400, {"message": "Body must be JSON"})
            user = body.get("userId") if isinstance(body, dict) else None
            if not isinstance(user, int):
                return self.answer(400, {"message": "userId must be a number"})
            products = body.get("products") or []
            if not products:
                return self.answer(400, {"message": "products can not be empty"})
            lines = []
            for item in products:
                quantity = item.get("quantity")
                lowest = -(10**9) if allow_negative else 1
                if not isinstance(quantity, int) or quantity < lowest or quantity == 0:
                    return self.answer(400, {"message": "quantity must be 1 or more"})
                if item.get("id") not in PRICES:
                    return self.answer(400, {"message": f"Unknown product {item.get('id')}"})
                price = PRICES[item["id"]]
                lines.append({"id": item["id"], "price": price, "quantity": quantity})
            total = round(sum(line["price"] * line["quantity"] for line in lines), 2)
            self.answer(201, {"id": 1, "userId": user, "products": lines, "total": total})

    return Carts


@pytest.fixture
def server(request):
    allow_negative = getattr(request, "param", False)
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(allow_negative))
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()


def run_template(base_url: str):
    env = {**os.environ, "BASE_URL": base_url}
    env.pop("API_TOKEN", None)
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
        cwd=KIT,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )


def probe(*args):
    return subprocess.run(
        [sys.executable, str(KIT / "api_probe.py"), *args],
        cwd=KIT,
        capture_output=True,
        text=True,
        timeout=120,
    )


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:3])


def test_the_template_passes_on_an_api_that_follows_the_rules(server):
    result = run_template(server)
    assert result.returncode == 0, result.stdout[-3000:]
    assert "8 passed" in result.stdout


@pytest.mark.parametrize("server", [True], indirect=True)
def test_the_template_catches_a_negative_quantity_bug(server):
    result = run_template(server)
    assert result.returncode == 1
    assert "FAILED tests/test_endpoint.py::test_bad_input_is_refused[quantity negative]" in (
        result.stdout
    )
    assert "1 failed, 7 passed" in result.stdout


def test_the_probe_shows_every_case_and_the_chosen_fields(server, tmp_path):
    saved = tmp_path / "probe-results.json"
    result = probe(
        "POST", f"{server}/carts/add", "--cases", "cases.json",
        "--field", "products.0.quantity", "--field", "total", "--save", str(saved),
    )  # fmt: skip
    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    assert any(line.startswith("valid: one product") and "total=179.96" in line for line in lines)
    assert any(line.startswith("quantity negative") and " 400 " in line for line in lines)
    assert len(json.loads(saved.read_text())) == 12


def test_the_probe_never_prints_a_token(server):
    result = probe("GET", f"{server}/carts/add", "-H", "Authorization: Bearer secret-token-123")
    assert "secret-token-123" not in result.stdout + result.stderr
    assert "'Authorization': '***'" in result.stdout


def test_the_probe_explains_a_header_without_a_colon(server):
    result = probe("GET", server, "-H", "Accept application/json")
    assert result.returncode != 0
    assert "A header needs a colon" in result.stderr


@pytest.mark.skipif(
    os.environ.get("ZTS_ONLINE") != "1", reason="set ZTS_ONLINE=1 to call DummyJSON"
)
def test_dummyjson_still_has_the_four_issues_the_page_shows():
    result = run_template("https://dummyjson.com")
    failed = sorted(
        line.split("[")[1].split("]")[0]
        for line in result.stdout.splitlines()
        if line.startswith("FAILED")
    )
    assert failed == ["quantity 0", "quantity is text", "quantity negative", "unknown product"]
