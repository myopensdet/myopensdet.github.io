# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""UI tests guide: the template is complete, pinned like the repo, holds no password,
and collects 18 tests offline. With ZTS_ONLINE=1 it runs against the public Sauce Demo
shop: all pass for standard_user, and problem_user fails exactly as the page shows."""

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
KIT = TOPIC / "templates" / "ui_tests"
ROOT = TOPIC.parents[2]
CREDIT = "Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/"
DEMO_PASSWORD = "secret_" + "sauce"  # noqa: S105  (the shop's public demo password)

SKIP_FOLDERS = {"__pycache__", ".pytest_cache", "test-results"}
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file()
    and not SKIP_FOLDERS & set(p.parts)
    and (p.suffix in {".py", ".ini", ".txt", ".md"} or p.name == ".gitignore")
)

PROBLEM_USER_FAILS = [  # the start of each failed test id
    "test_checkout.py::test_each_required_field_shows_an_error[chromium-First Name-",
    "test_checkout.py::test_each_required_field_shows_an_error[chromium-Zip/Postal Code-",
    "test_checkout.py::test_form_keeps_what_was_typed[",
    "test_checkout.py::test_totals_add_up[",
    "test_checkout.py::test_order_is_placed_and_the_cart_is_emptied[",
    "test_products.py::test_every_product_has_a_name_a_price_and_its_own_picture[",
    "test_products.py::test_sort_by_price_low_to_high[",
    "test_products.py::test_sort_by_name_z_to_a[",
]


def run_kit(*args, user=None):
    env = {
        k: v for k, v in os.environ.items() if k not in {"APP_USERNAME", "APP_PASSWORD", "BASE_URL"}
    }
    if user:
        env |= {"APP_USERNAME": user, "APP_PASSWORD": DEMO_PASSWORD}
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", *args],
        cwd=KIT, env=env, capture_output=True, text=True, timeout=600,
    )  # fmt: skip


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:3])


def test_pins_match_the_repo_lock_file():
    lock = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    for line in (KIT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        if "==" in line:
            assert re.search(rf"^{re.escape(line)} \\", lock, re.MULTILINE), line


def test_no_password_is_written_in_the_template():
    for path in KIT.rglob("*.py"):
        assert DEMO_PASSWORD not in path.read_text(encoding="utf-8"), path


def test_the_template_collects_18_tests():
    result = run_kit("--collect-only", "-q")
    assert "18 tests collected" in result.stdout, result.stdout[-1500:]


online = pytest.mark.skipif(
    os.environ.get("ZTS_ONLINE") != "1", reason="set ZTS_ONLINE=1 to use Sauce Demo"
)


@online
def test_all_pass_for_the_standard_user():
    result = run_kit(user="standard_user")
    assert "18 passed" in result.stdout, result.stdout[-3000:]
    assert DEMO_PASSWORD not in result.stdout


@online
def test_problem_user_fails_as_the_page_shows():
    result = run_kit(user="problem_user")
    failed = [
        line.removeprefix("FAILED tests/").split(" - ")[0]
        for line in result.stdout.splitlines()
        if line.startswith("FAILED")
    ]
    assert len(failed) == len(PROBLEM_USER_FAILS), result.stdout[-3000:]
    for start in PROBLEM_USER_FAILS:
        assert any(name.startswith(start) for name in failed), start
    assert "8 failed, 10 passed" in result.stdout
