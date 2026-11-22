# Template from myOpenSDET: https://myopensdet.github.io/
"""Mocking and stubbing: the kit's tests pass at all three levels (mock, stub, route),
the stub explains its mistakes, and with ZTS_DOCKER=1 the same tests pass against WireMock
reading the same mapping files."""

import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests

TOPIC = Path(__file__).resolve().parents[1]
ROOT = TOPIC.parents[1].parent
KIT = TOPIC / "templates" / "mock_kit"
CREDIT = "Template from myOpenSDET: https://myopensdet.github.io/"
FILES = sorted(
    p for p in TOPIC.rglob("*")
    if p.is_file() and not {"__pycache__", "test-results"} & set(p.parts)
    and (p.suffix in {".py", ".ini", ".txt", ".html", ".yml"} or p.name == ".gitignore")
)  # fmt: skip


def run_kit(*args, env=None):
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", *args],
        cwd=KIT, capture_output=True, text=True, timeout=600, env=env,
    )  # fmt: skip


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:3])


def test_pins_match_the_repo_lock_file():
    lock = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    for line in (KIT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        if "==" in line:
            assert re.search(rf"^{re.escape(line)} \\", lock, re.MULTILINE), line


@pytest.mark.parametrize("path", sorted((KIT / "stubs" / "mappings").glob("*.json")))
def test_mappings_use_the_wiremock_shape(path):
    mapping = json.loads(path.read_text(encoding="utf-8"))
    assert set(mapping) <= {"priority", "request", "response"}
    assert set(mapping["request"]) <= {"method", "urlPath", "bodyPatterns"}
    assert set(mapping["response"]) <= {"status", "headers", "jsonBody", "fixedDelayMilliseconds"}


def test_the_kit_passes_at_every_level():
    result = run_kit("-q")
    assert re.search(r"\b(14|9) passed", result.stdout), result.stdout[-3000:]
    assert "failed" not in result.stdout


def test_stub_explains_bad_mappings(tmp_path):
    (tmp_path / "x.json").write_text('{\n  "request": {}\n  "response": {}\n}\n', encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "stub_server.py", "--mappings", str(tmp_path)],
        cwd=KIT, capture_output=True, text=True, timeout=30,
    )  # fmt: skip
    assert result.stderr.strip() == (
        "x.json is not valid JSON: Expecting ',' delimiter: line 3 column 3 (char 20)"
    )


@pytest.mark.skipif(os.environ.get("ZTS_DOCKER") != "1", reason="set ZTS_DOCKER=1")
def test_same_tests_pass_against_wiremock():
    docker = shutil.which("docker")
    compose = [docker, "compose", "-p", "zts-wiremock"]
    subprocess.run([*compose, "up", "-d"], cwd=KIT, check=True, capture_output=True, timeout=600)
    try:
        for _ in range(60):
            try:
                if requests.get("http://127.0.0.1:8799/__admin/mappings", timeout=2).ok:
                    break
            except requests.ConnectionError:
                time.sleep(1)
        result = run_kit(
            "-q",
            "tests/test_stub_over_http.py",
            env=os.environ | {"STUB_URL": "http://127.0.0.1:8799"},
        )
        assert "5 passed" in result.stdout, result.stdout[-3000:]
    finally:
        subprocess.run([*compose, "down"], cwd=KIT, capture_output=True, timeout=300)
