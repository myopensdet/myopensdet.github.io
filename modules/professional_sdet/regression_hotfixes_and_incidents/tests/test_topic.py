# Template from myOpenSDET: https://myopensdet.github.io/
"""Regression, hotfixes and incidents: pick_tests.py maps changed files to the right
pytest command, and that command really selects the expected tests in the sample suite."""

import subprocess
import sys
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
KIT = TOPIC / "templates" / "hotfix_kit"
CREDIT = "Template from myOpenSDET: https://myopensdet.github.io/"
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file() and "__pycache__" not in p.parts and p.suffix in {".py", ".md", ".ini"}
)


def pick(*files, stdin=""):
    return subprocess.run(
        [sys.executable, str(KIT / "pick_tests.py"), *files],
        input=stdin, capture_output=True, text=True, timeout=60,
    )  # fmt: skip


def suite(*args):
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-q", *args],
        capture_output=True, text=True, timeout=60, cwd=KIT / "sample_suite",
    )  # fmt: skip


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:3])


def test_hotfix_picks_checkout_and_smoke():
    result = pick("src/payments/refund.py", "tests/test_checkout.py", "docs/refunds.md")
    assert "  docs/refunds.md                    -> no tests needed" in result.stdout
    assert result.stdout.rstrip().endswith('python -m pytest -m "checkout or smoke"')
    assert result.returncode == 0


@pytest.mark.parametrize(
    ("expression", "summary"),
    [("smoke", "3 passed, 8 deselected"), ("checkout or smoke", "6 passed, 5 deselected"),
     ("regression", "11 passed")],
)  # fmt: skip
def test_markers_select_the_page_counts(expression, summary):
    assert summary in suite("-m", expression).stdout


def test_shared_code_means_full_regression():
    result = pick("src/db/connection.py")
    assert "Run the full regression (shared code changed):" in result.stdout
    assert result.returncode == 1


def test_unknown_code_means_full_regression():
    result = pick(stdin="src/payments/refund.py\nsrc/emails/receipt.py\n")
    assert "  src/emails/receipt.py              -> NOT IN THE MAP" in result.stdout
    assert "Then add the unknown files to test_map.ini" in result.stdout
    assert result.returncode == 1


def test_no_files_and_typo_marker():
    assert pick().returncode == 2
    typo = suite("-m", "smokee")
    assert "Unknown marker(s) in '-m' expression: smokee" in typo.stdout + typo.stderr
    assert typo.returncode == 4
