# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""API automation guide: the GET, POST, PUT and DELETE templates all pass against a local
booking API that behaves well, never print the token, and skip clearly without a login.
With ZTS_ONLINE=1, Restful-booker still fails the five checks the page shows."""

import json
import os
import re
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
KIT = TOPIC / "templates" / "api_tests"
CREDIT = "Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/"
TOKEN = "local-test-token-42"  # noqa: S105 (fake token of the local test server)
FIELDS = {"firstname": str, "lastname": str, "totalprice": int, "depositpaid": bool}

SKIP_FOLDERS = {"__pycache__", ".pytest_cache"}
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file()
    and not SKIP_FOLDERS & set(p.parts)
    and (p.suffix in {".py", ".ini", ".txt", ".md"} or p.name == ".gitignore")
    and p.name != "__init__.py"
)


def valid(body) -> bool:
    if not isinstance(body, dict):
        return False
    for name, kind in FIELDS.items():
        if not isinstance(body.get(name), kind):
            return False
    dates = body.get("bookingdates") or {}
    return bool(dates.get("checkin")) and dates.get("checkout", "") > dates["checkin"]


class Bookings(BaseHTTPRequestHandler):
    """A booking API that does what the guide's tests expect."""

    store: dict = {}
    next_id = [1]

    def log_message(self, *args):  # keep test output quiet
        pass

    def reply(self, status, data=None):
        raw = json.dumps(data).encode() if data is not None else b""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def body(self):
        raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        try:
            return json.loads(raw)
        except ValueError:
            return None

    def logged_in(self):
        return self.headers.get("Cookie") == f"token={TOKEN}"

    def booking_id(self):
        match = re.fullmatch(r"/booking/(\d+)", self.path)
        return int(match.group(1)) if match else None

    def do_POST(self):  # noqa: N802  (names required by http.server)
        if self.path == "/auth":
            creds = self.body() or {}
            if creds == {"username": "tester", "password": "local_only_password"}:
                return self.reply(200, {"token": TOKEN})
            return self.reply(401, {"reason": "Bad credentials"})
        body = self.body()
        if self.path != "/booking" or not valid(body):
            return self.reply(400, {"reason": "Invalid booking"})
        new_id = self.next_id[0]
        self.next_id[0] += 1
        self.store[new_id] = body
        self.reply(200, {"bookingid": new_id, "booking": body})

    def do_GET(self):  # noqa: N802
        if self.path == "/booking":
            return self.reply(200, [{"bookingid": i} for i in self.store])
        found = self.store.get(self.booking_id())
        return self.reply(200, found) if found else self.reply(404, {"reason": "Not found"})

    def do_PUT(self):  # noqa: N802
        if not self.logged_in():
            return self.reply(403, {"reason": "Forbidden"})
        booking_id, body = self.booking_id(), self.body()
        if booking_id not in self.store:
            return self.reply(404, {"reason": "Not found"})
        if not valid(body):
            return self.reply(400, {"reason": "Invalid booking"})
        self.store[booking_id] = body
        self.reply(200, body)

    def do_DELETE(self):  # noqa: N802
        if not self.logged_in():
            return self.reply(403, {"reason": "Forbidden"})
        if self.store.pop(self.booking_id(), None) is None:
            return self.reply(404, {"reason": "Not found"})
        self.reply(201)


@pytest.fixture
def server():
    Bookings.store = {}
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Bookings)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()


def run_tests(base_url: str, login: bool = True, **extra):
    env = {k: v for k, v in os.environ.items() if k not in {"API_USERNAME", "API_PASSWORD"}}
    env |= {"BASE_URL": base_url, **extra}
    if login and "API_USERNAME" not in extra:
        env |= {"API_USERNAME": "tester", "API_PASSWORD": "local_only_password"}
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider"],
        cwd=KIT,
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
    )


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:3])


def test_all_fifteen_checks_pass_on_a_well_behaved_api(server):
    result = run_tests(server)
    assert result.returncode == 0, result.stdout[-3000:]
    assert "15 passed" in result.stdout
    assert Bookings.store == {}, "every test cleans up what it created"


def test_without_a_login_the_tests_skip_and_say_why(server):
    result = run_tests(server, login=False)
    assert "2 passed, 13 skipped" in result.stdout
    assert "Set API_USERNAME and API_PASSWORD" in result.stdout


def test_a_wrong_password_fails_with_a_clear_message(server):
    result = run_tests(server, API_USERNAME="tester", API_PASSWORD="wrong")  # noqa: S106
    assert "Login failed: 401" in result.stdout


def test_the_token_never_appears_in_the_output(server, monkeypatch):
    # Break one rule so tests fail and pytest prints their inputs.
    monkeypatch.setattr(Bookings, "do_DELETE", lambda self: self.reply(500, {}))
    result = run_tests(server)
    assert result.returncode == 1
    assert "auth_headers = {'Cookie': '***'}" in result.stdout
    assert TOKEN not in result.stdout + result.stderr


@pytest.mark.skipif(os.environ.get("ZTS_ONLINE") != "1", reason="set ZTS_ONLINE=1 to call it")
def test_restful_booker_still_fails_the_five_checks_the_page_shows():
    demo_login = {"API_USERNAME": "admin", "API_PASSWORD": "password123"}  # public demo login
    result = run_tests("https://restful-booker.herokuapp.com", **demo_login)
    failed = sorted(
        line.split("::", 1)[1].split(" ")[0]
        for line in result.stdout.splitlines()
        if line.startswith("FAILED")
    )
    assert failed == [
        "test_delete_twice_returns_404",
        "test_post_bad_booking_is_refused_with_400[checkout",
        "test_post_bad_booking_is_refused_with_400[missing",
        "test_post_bad_booking_is_refused_with_400[price",
        "test_put_missing_booking_returns_404",
    ], result.stdout[-2000:]
