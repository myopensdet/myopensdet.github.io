# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Everyday tools: curl_to_pytest.py turns copied requests into tests that run, keeps
secrets out of them, and the VS Code files are valid JSON. Offline against a tiny local
server; with ZTS_ONLINE=1 the page's dummyjson example runs for real too."""

import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
KIT = TOPIC / "templates" / "everyday_kit"
TOOL = KIT / "curl_to_pytest.py"
CREDIT = "Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/"
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file() and "__pycache__" not in p.parts and p.suffix in {".py", ".txt"}
    and p.name != "copied_request.txt"
)  # fmt: skip


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802
        size = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(size) or b"{}")
        self.answer(201, {"id": 195, **body, "auth": self.headers.get("authorization")})

    def do_GET(self):  # noqa: N802
        self.answer(200, {"cookie": self.headers.get("Cookie"), "path": self.path})

    def answer(self, status, data):
        raw = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, *args):
        pass


@pytest.fixture(scope="module")
def base():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    server.server_close()


def convert(command: str):
    return subprocess.run(
        [sys.executable, str(TOOL)], input=command, capture_output=True, text=True, timeout=30
    )


def run_test(tmp_path, code, env):
    test = tmp_path / "test_from_curl.py"
    test.write_text(code, encoding="utf-8")
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-q", str(test)],
        capture_output=True, text=True, timeout=60, cwd=tmp_path, env={**os.environ, **env},
    )  # fmt: skip


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:3])


@pytest.mark.parametrize("name", ["settings.json", "launch.json", "extensions.json"])
def test_vscode_files_are_valid_json(name):
    data = json.loads((KIT / "vscode" / name).read_text(encoding="utf-8"))
    assert data


def test_copied_request_becomes_a_passing_test_without_the_secret(tmp_path, base):
    result = convert((KIT / "copied_request.txt").read_text(encoding="utf-8"))
    assert result.returncode == 0
    assert "token copied from the browser" not in result.stdout
    assert "user-agent" not in result.stdout.lower()
    assert "Moved out of the test: authorization" in result.stderr
    assert "def test_post_products_add():" in result.stdout
    run = run_test(tmp_path, result.stdout, {"BASE_URL": base, "API_AUTH": "Bearer from-env"})
    assert "1 passed" in run.stdout, run.stdout


def test_get_with_cookie_reads_it_from_the_environment(tmp_path, base):
    result = convert(f"curl '{base}/api/orders?page=2' -b 'session=abc123'")
    assert "abc123" not in result.stdout
    assert "def test_get_api_orders():" in result.stdout
    assert "'GET'" in result.stdout
    run = run_test(tmp_path, result.stdout, {"API_COOKIE": "session=from-env"})
    assert "1 passed" in run.stdout, run.stdout


def test_form_body_is_sent_as_data():
    result = convert("curl https://shop.example.com/login --data 'email=a@example.com&x=1'")
    assert "data='email=a@example.com&x=1'" in result.stdout
    assert "'POST'" in result.stdout


@pytest.mark.parametrize(
    ("command", "message"),
    [("wget https://example.com", "Paste a command that starts with curl"),
     ("curl -H 'accept: text/html'", "No address found in the curl command")],
)  # fmt: skip
def test_bad_input_says_what_is_wrong(command, message):
    result = convert(command)
    assert result.returncode == 1
    assert message in result.stderr


@pytest.mark.skipif(os.environ.get("ZTS_ONLINE") != "1", reason="set ZTS_ONLINE=1")
def test_page_example_against_dummyjson(tmp_path):
    result = convert((KIT / "copied_request.txt").read_text(encoding="utf-8"))
    run = run_test(tmp_path, result.stdout, {})
    assert "1 passed" in run.stdout, run.stdout
