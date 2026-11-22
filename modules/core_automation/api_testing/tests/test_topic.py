# Template from myOpenSDET: https://myopensdet.github.io/
"""API testing: the helpers work offline against a local server, and, with ZTS_ONLINE=1,
the examples and the template project work against the real public APIs."""

import json
import os
import re
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
ROOT = TOPIC.parents[2]
DOCS = ROOT / "docs" / "api-testing"
EXAMPLES = TOPIC / "examples"
PROJECT = TOPIC / "templates" / "booker_api_tests"
CREDIT = "Template from myOpenSDET: https://myopensdet.github.io/"

sys.path.insert(0, str(PROJECT))
from api.auth import (  # noqa: E402
    BearerAuth,
    api_key_header,
    basic_auth,
    booker_token,
    oauth2_client_credentials,
)
from api.client import ApiClient, check_status, safe_headers  # noqa: E402
from api.schema import load_schema, schema_errors  # noqa: E402

SKIP_FOLDERS = {"__pycache__", ".pytest_cache"}
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file()
    and not SKIP_FOLDERS & set(p.parts)
    and (p.suffix in {".py", ".ini", ".txt", ".md", ".csv", ".json"} or p.name == ".gitignore")
)


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:2])


# A tiny local API, so the client can be tested without the internet.


class EchoHandler(BaseHTTPRequestHandler):
    def _answer(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length).decode() if length else ""
        if self.path == "/token":
            reply, status = {"access_token": "local-token", "seen": body}, 200
            reply["auth"] = self.headers.get("Authorization")
        elif self.path.startswith("/missing"):
            reply, status = {"error": "not found"}, 404
        else:
            reply, status = {"method": self.command, "path": self.path, "body": body}, 200
            reply["headers"] = dict(self.headers)
        data = json.dumps(reply).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = _answer  # noqa: N815

    def log_message(self, *args):
        pass


@pytest.fixture(scope="module")
def local_api():
    server = HTTPServer(("127.0.0.1", 0), EchoHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


@pytest.mark.parametrize("method", ["get", "post", "put", "patch", "delete"])
def test_client_sends_each_method_to_the_right_path(local_api, method):
    with ApiClient(local_api + "/") as api:
        answer = getattr(api, method)("/booking/7").json()
    assert answer["method"] == method.upper()
    assert answer["path"] == "/booking/7"
    assert answer["headers"]["Accept"] == "application/json"


def test_client_logs_method_url_and_status(local_api, caplog):
    caplog.set_level("INFO", logger="api")
    with ApiClient(local_api) as api:
        api.get("/booking", params={"firstname": "Test"})
    assert re.search(
        r"GET http://127\.0\.0\.1:\d+/booking\?firstname=Test -> 200 in \d+ ms", caplog.text
    )


def test_check_status_explains_and_hides_secrets(local_api):
    with ApiClient(local_api, headers={"Authorization": "Bearer secret-value"}) as api:
        response = api.get("/missing", headers={"Cookie": "token=secret-cookie"})
    with pytest.raises(AssertionError) as failure:
        check_status(response, 200)
    message = str(failure.value)
    assert message.startswith(f"GET {local_api}/missing returned 404, expected 200")
    assert "secret-value" not in message
    assert "secret-cookie" not in message
    assert "'Authorization': '***'" in message


def test_safe_headers_hides_only_secrets():
    shown = safe_headers({"X-API-Key": "k", "Accept": "application/json"})
    assert shown == {"X-API-Key": "***", "Accept": "application/json"}


def test_auth_helpers(local_api):
    assert api_key_header("abc") == {"X-API-Key": "abc"}
    assert repr(BearerAuth("very-secret")) == "BearerAuth(token=***)"
    with ApiClient(local_api, auth=BearerAuth("t1")) as api:
        assert api.get("/x").json()["headers"]["Authorization"] == "Bearer t1"
    with ApiClient(local_api, auth=basic_auth("tester", "s3cret")) as api:
        # "tester:s3cret" in base64
        assert api.get("/x").json()["headers"]["Authorization"] == "Basic dGVzdGVyOnMzY3JldA=="


def test_oauth2_client_credentials(local_api):
    token = oauth2_client_credentials(f"{local_api}/token", "my-client", "my-secret", scope="read")
    assert token == "local-token"  # noqa: S105 (a fake token from the local test server)


def test_booker_token_explains_a_refused_login():
    class FakeResponse:
        def json(self):
            return {"reason": "Bad credentials"}

    class FakeClient:
        def post(self, path, json):
            return FakeResponse()

    with pytest.raises(PermissionError, match="Login refused: Bad credentials"):
        booker_token(FakeClient(), "admin", "wrong")


def test_schema_accepts_a_good_booking_and_lists_every_problem():
    good = {
        "bookingid": 5,
        "booking": {
            "firstname": "Test",
            "lastname": "Booker",
            "totalprice": 120,
            "depositpaid": True,
            "bookingdates": {"checkin": "2026-12-01", "checkout": "2026-12-03"},
        },
    }
    assert schema_errors(good, load_schema("created_booking.json")) == []
    bad = {**good, "bookingid": "5", "booking": {**good["booking"], "totalprice": -1}}
    assert schema_errors(bad, load_schema("created_booking.json")) == [
        "$.booking.totalprice: -1 is less than the minimum of 0",
        "$.bookingid: '5' is not of type 'integer'",
    ]


# Online: only with ZTS_ONLINE=1, because these call real public APIs.

online = pytest.mark.skipif(
    os.environ.get("ZTS_ONLINE") != "1", reason="set ZTS_ONLINE=1 to call the real public APIs"
)

PAGES = {
    "http_basics.py": "how-http-works.md",
    "methods_tour.py": "http-methods.md",
    "status_codes.py": "status-codes.md",
    "headers_and_json.py": "headers-and-json.md",
    "params.py": "query-and-path-params.md",
    "auth_demo.py": "authentication.md",
    "schema_demo.py": "schema-validation.md",
    "upload_demo.py": "file-upload.md",
    "client_demo.py": "api-client-class.md",
}
DEMO_LOGIN = {"BOOKER_USERNAME": "admin", "BOOKER_PASSWORD": "password123"}


def normal(text: str) -> str:
    """Ignore what changes between runs: booking ids, timings, indentation."""
    text = re.sub(r"\d+ ms", "N ms", text)
    text = re.sub(r"in \d+\.\d+s", "in N.NNs", text)
    text = re.sub(r"\b\d{2,5}\b(?= |$)", "ID", text, flags=re.MULTILINE)
    return "\n".join(line.strip() for line in text.splitlines()).strip()


@online
@pytest.mark.parametrize(("script", "page"), PAGES.items())
def test_example_output_is_on_the_page(script, page):
    result = subprocess.run(
        [sys.executable, script],
        cwd=EXAMPLES,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        env={**os.environ, **DEMO_LOGIN},
    )
    assert result.returncode == 0, result.stderr
    assert normal(result.stdout) in normal((DOCS / page).read_text(encoding="utf-8"))


@online
def test_template_project_passes_against_restful_booker():
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-q"],
        cwd=PROJECT,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
        env={**os.environ, **DEMO_LOGIN, "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"},
    )
    assert "11 passed, 1 xfailed" in result.stdout, result.stdout


# The login fixture: skip on a laptop, fail in CI. Offline: no request is sent.


def run_login_test(ci: bool):
    env = {k: v for k, v in os.environ.items() if k not in ("CI", *DEMO_LOGIN)}
    env.update({"BOOKER_URL": "http://127.0.0.1:9", "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"})
    if ci:
        env["CI"] = "true"
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-p",
            "no:cacheprovider",
            "-q",
            "-rs",
            "tests/test_auth.py::test_login_gives_a_token",
        ],
        cwd=PROJECT,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
        env=env,
    )


def test_missing_login_is_skipped_on_a_laptop():
    result = run_login_test(ci=False)
    assert "1 skipped" in result.stdout, result.stdout
    assert "in CI this fails" in result.stdout


def test_missing_login_fails_in_ci():
    result = run_login_test(ci=True)
    assert result.returncode != 0
    assert "1 error" in result.stdout, result.stdout
    assert "In CI the login tests must run, not be skipped." in result.stdout
