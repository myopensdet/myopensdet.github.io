# Template from myOpenSDET: https://myopensdet.github.io/
"""UI automation: the Page Object Model template passes on each installed browser, the planted
bug still fails for the right reason, and a failure leaves a screenshot and a trace.
All offline: the template starts its own shop. Needs Playwright's browsers."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
PROJECT = TOPIC / "templates" / "ui_tests"
CREDIT = "Template from myOpenSDET: https://myopensdet.github.io/"
PYTEST = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"]

SKIP_FOLDERS = {"__pycache__", ".pytest_cache", "reports"}
SUFFIXES = {".py", ".ini", ".txt", ".md"}
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file()
    and not SKIP_FOLDERS & set(p.parts)
    and (p.suffix in SUFFIXES or p.name == ".gitignore")
)


def browser_starts(name: str) -> bool:
    """Installed, and able to start on this computer."""
    from playwright.sync_api import sync_playwright  # noqa: PLC0415

    with sync_playwright() as playwright:
        engine = getattr(playwright, name)
        if not Path(engine.executable_path).exists():
            return False
        try:
            engine.launch().close()
        except Exception:  # noqa: BLE001  (some engines don't start on every OS version)
            return False
        return True


def needs(name: str):
    return pytest.mark.skipif(
        not browser_starts(name), reason=f"{name} is not installed or doesn't start here"
    )


def run(*args):
    env = {k: v for k, v in os.environ.items() if k != "SHOP_URL"}
    return subprocess.run(
        [*PYTEST, *args], cwd=PROJECT, env=env, capture_output=True, text=True, timeout=600
    )


@pytest.fixture
def clean_reports():
    shutil.rmtree(PROJECT / "reports", ignore_errors=True)
    yield PROJECT / "reports"
    shutil.rmtree(PROJECT / "reports", ignore_errors=True)


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:2])


@pytest.mark.parametrize(
    "browser",
    [
        pytest.param("chromium", marks=needs("chromium")),
        pytest.param("firefox", marks=needs("firefox")),
        pytest.param("webkit", marks=needs("webkit")),
    ],
)
def test_the_suite_passes_with_the_known_bug_as_xfail(browser, clean_reports):
    result = run(f"--browser={browser}")
    assert result.returncode == 0, result.stdout[-3000:] + result.stderr[-2000:]
    assert "15 passed, 1 xfailed" in result.stdout
    assert not clean_reports.exists(), "passing tests must not leave screenshots"


@needs("chromium")
def test_a_failure_leaves_a_screenshot_and_a_trace(clean_reports):
    result = run("--runxfail", "tests/test_cart.py::test_remove_a_book_updates_the_cart_count")
    assert result.returncode == 1
    assert "Locator expected to have text '1'" in result.stdout
    assert "Actual value: 3" in result.stdout
    name = "test_remove_a_book_updates_the_cart_count"
    assert (clean_reports / "screenshots" / f"{name}_0.png").stat().st_size > 1000
    assert (clean_reports / "traces" / f"{name}.zip").stat().st_size > 1000


@needs("chromium")
def test_the_first_script_runs():
    result = subprocess.run(
        [sys.executable, "first_look.py"], cwd=PROJECT, capture_output=True, text=True, timeout=120
    )
    assert result.returncode == 0, result.stderr[-2000:]
    assert "Books: ['Python for Testers', 'SQL in a Week'" in result.stdout


def test_page_objects_do_not_assert():
    """Pages find and do; tests check. A page object that asserts hides what a test checks."""
    for path in (PROJECT / "pages").glob("*.py"):
        assert "assert " not in path.read_text(encoding="utf-8"), path.name


def test_no_test_sleeps():
    for path in (PROJECT / "tests").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "time.sleep" not in text and "wait_for_timeout" not in text, path.name
