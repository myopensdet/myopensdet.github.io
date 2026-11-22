# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""BDD testing: behave and pytest-bdd run the same feature files, on the API and the web page.
All offline: the template starts its own shop. The web page runs need Playwright's Chromium."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
PROJECT = TOPIC / "templates" / "bdd_tests"
CREDIT = "Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/"
BEHAVE = [sys.executable, "-m", "behave", "--format=progress"]
PYTEST = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"]

SKIP_FOLDERS = {"__pycache__", ".pytest_cache", "reports"}
SUFFIXES = {".py", ".ini", ".txt", ".md", ".feature"}
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


needs_chromium = pytest.mark.skipif(
    not chromium_installed(), reason="Run: python -m playwright install chromium"
)


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:2])


def run(command, tmp_path):
    env = {k: v for k, v in os.environ.items() if k != "SHOP_URL"}
    result = subprocess.run(
        command, cwd=PROJECT, env=env, capture_output=True, text=True, timeout=300
    )
    shutil.rmtree(PROJECT / "reports", ignore_errors=True)  # screenshots from known bugs
    return result


@pytest.mark.parametrize("target", ["api", pytest.param("ui", marks=needs_chromium)])
def test_behave_passes(target, tmp_path):
    result = run([*BEHAVE, "-D", f"target={target}"], tmp_path)
    assert result.returncode == 0, result.stdout[-3000:] + result.stderr[-2000:]
    assert "8 scenarios passed, 0 failed, 1 skipped" in result.stdout


@pytest.mark.parametrize("target", ["api", pytest.param("ui", marks=needs_chromium)])
def test_behave_known_bug_still_fails(target, tmp_path):
    result = run(
        [*BEHAVE, "--format=pretty", "-D", f"target={target}", "--tags=@known_bug"], tmp_path
    )
    assert result.returncode == 1
    assert 'got "Coupon SAVE10 applied"' in result.stdout


@pytest.mark.parametrize("target", ["api", pytest.param("ui", marks=needs_chromium)])
def test_pytest_bdd_passes_with_the_known_bug_as_xfail(target, tmp_path):
    result = run([*PYTEST, f"--target={target}"], tmp_path)
    assert result.returncode == 0, result.stdout[-3000:] + result.stderr[-2000:]
    assert "8 passed, 1 xfailed" in result.stdout


def test_both_tools_read_the_same_features():
    steps = (PROJECT / "features" / "steps" / "shop_steps.py").read_text(encoding="utf-8")
    tests = (PROJECT / "tests" / "test_shop.py").read_text(encoding="utf-8")
    for pattern in ["an empty cart", 'I apply the coupon "{code}"', "the cart total is {amount}"]:
        assert pattern in steps and pattern in tests, pattern


def test_a_failed_setup_shows_only_the_real_error(tmp_path):
    """after_all must close only what before_all started, or its error hides the real one."""
    result = run([*BEHAVE, "-D", "target=web"], tmp_path)
    assert "not 'web'" in result.stdout
    assert "HOOK-ERROR in after_all" not in result.stdout
