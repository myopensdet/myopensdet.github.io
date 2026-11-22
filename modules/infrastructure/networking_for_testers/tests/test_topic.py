# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Networking: net_check.py names the failing step for each kind of problem the page shows.
Offline against the practice server; with ZTS_ONLINE=1 also example.com and badssl.com."""

import importlib.util
import os
import socket
import subprocess
import sys
import threading
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
KIT = TOPIC / "templates" / "net_kit"
CREDIT = "Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/"
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file() and "__pycache__" not in p.parts and p.suffix in {".py", ".md", ".txt"}
)

spec = importlib.util.spec_from_file_location("practice_server", KIT / "practice_server.py")
practice_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(practice_server)


@pytest.fixture(scope="module")
def base():
    server = practice_server.serve(port=0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    server.server_close()


def net_check(*args):
    return subprocess.run(
        [sys.executable, str(KIT / "net_check.py"), *args],
        capture_output=True, text=True, timeout=60,
    )  # fmt: skip


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:3])


def test_closed_port_is_refused():
    result = net_check(f"http://127.0.0.1:{free_port()}/")
    assert "2. Connect   FAILED: port" in result.stdout and "refused" in result.stdout
    assert result.returncode == 1


def test_unknown_name_fails_at_step_1():
    result = net_check("https://exmaple-shop.invalid")
    assert "1. Name      FAILED: exmaple-shop.invalid not found" in result.stdout


def test_missing_scheme_is_explained():
    result = net_check("example.com")
    assert "Start with http:// or https://" in result.stdout
    assert result.returncode == 2


def test_cookie_flags_redirect_and_cors(base):
    assert "Cookie session: missing Secure, HttpOnly, SameSite" in net_check(f"{base}/login").stdout
    assert "Sends you on to: /login" in net_check(f"{base}/old").stdout
    cors = net_check(f"{base}/api/me", "--origin", "http://evil.example").stdout
    assert "Allow-Origin=http://evil.example, Allow-Credentials=true" in cors


def test_slow_answer_is_an_app_problem(base):
    result = net_check(f"{base}/slow", "--timeout", "1")
    assert "3. Answer    FAILED: connected, but no answer in 1 s" in result.stdout


def test_practice_server_listens_on_this_computer_only():
    server = practice_server.serve(port=0)
    try:
        assert server.server_address[0] == "127.0.0.1"
    finally:
        server.server_close()


online = pytest.mark.skipif(os.environ.get("ZTS_ONLINE") != "1", reason="set ZTS_ONLINE=1")


@online
def test_a_good_https_site_passes_every_step():
    result = net_check("https://example.com")
    assert "3. HTTPS     certificate valid for" in result.stdout
    assert "4. Answer    200 OK" in result.stdout


@online
def test_an_expired_certificate_fails_at_step_3():
    result = net_check("https://expired.badssl.com/", "--timeout", "15")
    assert "3. HTTPS     FAILED:" in result.stdout  # "has expired", or a reset on a bad day
