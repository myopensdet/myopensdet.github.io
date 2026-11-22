# Template from myOpenSDET: https://myopensdet.github.io/
"""Reporting and logging: every run writes an HTML report, JUnit XML and a log file; a failed
page test puts a screenshot in the report; secrets never reach the log. Offline. Needs Chromium."""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
PROJECT = TOPIC / "templates" / "report_tests"
REPORTS = PROJECT / "reports"
CREDIT = "Template from myOpenSDET: https://myopensdet.github.io/"

SKIP_FOLDERS = {"__pycache__", ".pytest_cache", "reports"}
SUFFIXES = {".py", ".ini", ".txt", ".md"}
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file()
    and not SKIP_FOLDERS & set(p.parts)
    and (p.suffix in SUFFIXES or p.name == ".gitignore")
)


def chromium_installed() -> bool:
    from playwright.sync_api import sync_playwright  # noqa: PLC0415

    with sync_playwright() as playwright:
        return Path(playwright.chromium.executable_path).exists()


pytestmark = pytest.mark.skipif(
    not chromium_installed(), reason="Run: python -m playwright install chromium"
)


def run(*args):
    shutil.rmtree(REPORTS, ignore_errors=True)
    env = {k: v for k, v in os.environ.items() if k != "SHOP_URL"}
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", *args],
        cwd=PROJECT,
        env=env,
        capture_output=True,
        text=True,
        timeout=600,
    )


@pytest.fixture(scope="module")
def normal_run():
    result = run()
    files = {p.name: p.read_text(encoding="utf-8") for p in REPORTS.iterdir()}
    shutil.rmtree(REPORTS, ignore_errors=True)
    return result, files


@pytest.fixture(scope="module")
def failing_run():
    result = run("--runxfail")
    files = {p.name: p.read_text(encoding="utf-8") for p in REPORTS.iterdir()}
    shutil.rmtree(REPORTS, ignore_errors=True)
    return result, files


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:2])


def test_a_run_writes_three_reports(normal_run):
    result, files = normal_run
    assert result.returncode == 0, result.stdout[-3000:]
    assert "8 passed, 1 xfailed" in result.stdout
    assert set(files) == {"report.html", "junit.xml", "tests.log"}
    assert "Practice shop: test report" in files["report.html"]
    assert 'tests="9"' in files["junit.xml"]


def test_the_log_file_has_every_call_and_no_secret(normal_run):
    _, files = normal_run
    log = files["tests.log"]
    assert "---- tests/test_api.py::test_log_in" in log
    assert re.search(r"INFO +shop\.api: POST /api/orders -> 201 in \d+ ms", log)
    assert '"password": "***"' in log and '"card": "***"' in log
    assert "local_only_password" not in log and "4242" not in log
    assert "faker" not in log and "urllib3" not in log  # other libraries kept quiet


def test_a_failed_page_test_puts_a_screenshot_in_the_report(failing_run):
    result, files = failing_run
    assert result.returncode == 1
    assert "1 failed, 8 passed" in result.stdout
    assert "Screenshot" in files["report.html"] and "image/png;base64" in files["report.html"]
    assert 'failures="1"' in files["junit.xml"]
