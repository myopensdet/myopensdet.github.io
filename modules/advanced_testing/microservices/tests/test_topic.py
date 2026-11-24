# Template from myOpenSDET: https://myopensdet.github.io/
"""Testing microservices: the kit passes, the planted bug is caught at both levels,
the trace tool follows one request, a busy port is refused, and with ZTS_DOCKER=1
the same cross-service tests pass against Docker Compose."""

import json
import os
import re
import shutil
import socket
import subprocess
import sys
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
ROOT = TOPIC.parents[1].parent
KIT = TOPIC / "templates" / "services_kit"
CREDIT = "Template from myOpenSDET: https://myopensdet.github.io/"
FILES = sorted(
    p for p in TOPIC.rglob("*")
    if p.is_file() and not {"__pycache__", "logs"} & set(p.parts)
    and (p.suffix in {".py", ".ini", ".txt", ".yml"} or p.name == ".gitignore")
)  # fmt: skip

sys.path.insert(0, str(KIT))
import run_all  # noqa: E402
from trace_request import describe, trace  # noqa: E402


def run_kit(*args, env=None):
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", *args],
        cwd=KIT, capture_output=True, text=True, timeout=300, env=env,
    )  # fmt: skip


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:3])


def test_pins_match_the_repo_lock_file():
    lock = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    for line in (KIT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        if "==" in line:
            assert re.search(rf"^{re.escape(line)} \\", lock, re.MULTILINE), line


def test_the_kit_passes():
    result = run_kit("-q")
    assert "8 passed" in result.stdout, result.stdout[-3000:]
    assert "failed" not in result.stdout


def test_the_planted_bug_is_caught_alone_and_together():
    result = run_kit("-q", env=os.environ | {"ORDERS_BUG": "no_release"})
    assert "3 failed, 5 passed" in result.stdout, result.stdout[-3000:]
    for name in (
        "test_across_services.py::test_a_declined_payment_puts_the_items_back",
        "test_across_services.py::test_payments_down_puts_the_items_back",
        "test_orders_alone.py::test_a_declined_payment_gives_the_items_back",
    ):
        assert f"FAILED tests/{name}" in result.stdout


def test_trace_keeps_one_request_in_time_order():
    lines = [
        json.dumps(
            {"time": 2.0, "service": "stock", "request_id": "a", "event": "answered", "status": 200}
        ),
        "not json",
        json.dumps({"time": 1.0, "service": "orders", "request_id": "a", "event": "received"}),
        json.dumps({"time": 1.5, "service": "orders", "request_id": "b", "event": "received"}),
        "[1, 2]",
    ]
    events = trace("a", lines)
    assert [e["service"] for e in events] == ["orders", "stock"]
    assert describe(events[1]) == "stock     answered     status=200"


def test_trace_says_when_nothing_matches(tmp_path):
    result = subprocess.run(
        [sys.executable, "trace_request.py", "nope", str(tmp_path)],
        cwd=KIT, capture_output=True, text=True, timeout=30,
    )  # fmt: skip
    assert result.stdout.strip() == "No log lines with request id nope"
    assert result.returncode == 1


def test_a_busy_port_is_refused():
    with socket.socket() as busy:
        busy.bind(("127.0.0.1", 0))
        busy.listen()
        port = busy.getsockname()[1]
        with pytest.raises(RuntimeError, match=rf"^Port {port} for stock is already in use"):
            run_all.check_port_free(port, "stock")


@pytest.mark.skipif(os.environ.get("ZTS_DOCKER") != "1", reason="set ZTS_DOCKER=1")
def test_same_tests_pass_against_docker_compose():
    compose = [shutil.which("docker"), "compose"]
    subprocess.run(
        [*compose, "up", "-d", "--wait"], cwd=KIT, check=True, capture_output=True, timeout=600
    )
    try:
        result = run_kit(
            "-q",
            "tests/test_across_services.py",
            env=os.environ | {"ORDERS_URL": "http://127.0.0.1:8811"},
        )
        assert "5 passed" in result.stdout, result.stdout[-3000:]
    finally:
        subprocess.run([*compose, "down"], cwd=KIT, capture_output=True, timeout=300)
