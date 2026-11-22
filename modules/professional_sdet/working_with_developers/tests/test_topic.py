# Template from myOpenSDET: https://myopensdet.github.io/
"""Working with developers: evidence.py shows an intermittent 500 on the practice server
(2 of 6 fail), a clean run in --fixed mode, hides the token, and explains bad input."""

import importlib.util
import os
import socket
import subprocess
import sys
import threading
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
KIT = TOPIC / "templates" / "dev_kit"
CREDIT = "Template from myOpenSDET: https://myopensdet.github.io/"
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file() and "__pycache__" not in p.parts and p.suffix in {".py", ".md"}
)

spec = importlib.util.spec_from_file_location("dev_practice_server", KIT / "practice_server.py")
practice_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(practice_server)


def start(fixed):
    server = practice_server.serve(port=0, fixed=fixed)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}/api/orders/7"


def evidence(*args, env=None):
    return subprocess.run(
        [sys.executable, str(KIT / "evidence.py"), *args],
        capture_output=True, text=True, timeout=60, env={**os.environ, **(env or {})},
    )  # fmt: skip


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:3])


def test_intermittent_bug_is_shown():
    server, url = start(fixed=False)
    try:
        result = evidence(url, "--times", "6", "--wait", "0")
    finally:
        server.shutdown()
        server.server_close()
    assert "Sent 6 times: 4 OK, 2 failed." in result.stdout
    assert "that's why it 'works on my machine'" in result.stdout
    assert result.stdout.count("| 500 |") == 2
    assert "| 2.14.0 |" in result.stdout and "req-" in result.stdout
    assert 'First failed answer: `{"error": "internal error"}`' in result.stdout
    assert f"curl -i -X GET {url}" in result.stdout
    assert result.returncode == 1


def test_fixed_server_is_clean():
    server, url = start(fixed=True)
    try:
        result = evidence(url, "--times", "6", "--wait", "0")
    finally:
        server.shutdown()
        server.server_close()
    assert "Sent 6 times: 6 OK, 0 failed." in result.stdout
    assert result.returncode == 0


def test_token_is_never_printed():
    server, url = start(fixed=True)
    try:
        result = evidence(url, "--times", "1", env={"API_AUTH": "Bearer secret-value-123"})
    finally:
        server.shutdown()
        server.server_close()
    assert "secret-value-123" not in result.stdout
    assert '-H "Authorization: $API_AUTH"' in result.stdout


def test_closed_port_and_bad_address():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    closed = evidence(f"http://127.0.0.1:{port}/api/orders/7", "--times", "1")
    assert "Sent 1 time: 0 OK, 1 failed." in closed.stdout
    assert "no answer (" in closed.stdout and "First failed answer" not in closed.stdout
    bad = evidence("127.0.0.1:8795/api/orders/7")
    assert bad.stdout.strip().startswith("Not a full address: '127.0.0.1:8795/api/orders/7'")
    assert bad.returncode == 2
