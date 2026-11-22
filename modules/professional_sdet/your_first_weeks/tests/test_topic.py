# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Your first weeks: map_test_suite.py maps the sample framework exactly as the page
shows: tests, fixtures, markers, skips without reasons, settings, fixed waits, hosts."""

import subprocess
import sys
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
KIT = TOPIC / "templates" / "first_weeks_kit"
CREDIT = "Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/"
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file() and "__pycache__" not in p.parts and p.suffix in {".py", ".md", ".txt", ".ini"}
)


def mapper(*args, cwd=KIT):
    return subprocess.run(
        [sys.executable, str(KIT / "map_test_suite.py"), *args],
        capture_output=True, text=True, timeout=60, cwd=cwd,
    )  # fmt: skip


@pytest.fixture(scope="module")
def output():
    result = mapper("sample_framework")
    assert result.returncode == 0, result.stderr
    return result.stdout


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:3])


@pytest.mark.parametrize(
    "line",
    [
        "== sample_framework: 7 Python files, 9 test functions",
        "  pytest.ini, conftest.py, requirements.txt",
        "    5  tests/api/test_orders.py",
        "  api                    session   conftest.py",
        "  admin_api              function  conftest.py",
        "  smoke x2, skip x2, xfail x1, parametrize x1, slow x1",
        "  skip    test_cancel_order (tests/api/test_orders.py): SHOP-301 flaky on staging",
        "  skip    test_delete_user (tests/api/test_users.py): NO REASON GIVEN",
        "  API_TOKEN              in conftest.py",
        "  helpers/api.py:15  time.sleep(5)",
        "  tests/ui/test_checkout.py:11  page.wait_for_timeout(4000)",
        "  pay.partner.example.net x1",
    ],
)
def test_map_shows(output, line):
    assert line in output.splitlines()


def test_no_folder_shows_usage():
    result = mapper()
    assert result.stdout.strip() == "Usage: python map_test_suite.py <folder with the tests>"
    assert result.returncode == 2


def test_broken_file_is_reported_not_fatal(tmp_path):
    (tmp_path / "test_bad.py").write_text("def test_x(:\n", encoding="utf-8")
    (tmp_path / "test_good.py").write_text("def test_y():\n    pass\n", encoding="utf-8")
    result = mapper(str(tmp_path))
    assert "2 Python files, 1 test function" in result.stdout
    assert "Could not read test_bad.py: line 1 (not valid Python)" in result.stdout
