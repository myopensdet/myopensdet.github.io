# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""A day in the life: morning_triage.py sorts last night's failures into known and new,
groups the same error, and its exit code says if anything needs a look."""

import subprocess
import sys
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
KIT = TOPIC / "templates" / "day_kit"
CREDIT = "Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/"
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file() and "__pycache__" not in p.parts and p.suffix in {".py", ".md", ".txt"}
)


def python(*args, cwd):
    return subprocess.run(
        [sys.executable, *args], capture_output=True, text=True, timeout=60, cwd=cwd
    )


@pytest.fixture(scope="module")
def report(tmp_path_factory):
    folder = tmp_path_factory.mktemp("night")
    python("-m", "pytest", "-p", "no:cacheprovider", "-q", str(KIT / "nightly_example"),
           f"--junitxml={folder / 'junit.xml'}", cwd=folder)  # fmt: skip
    return folder / "junit.xml"


def triage(*args, cwd=KIT):
    return python(str(KIT / "morning_triage.py"), *args, cwd=cwd)


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:3])


def test_without_known_issues_everything_is_new(report):
    result = triage(str(report))
    assert result.stdout.startswith("Last night: 9 tests, 4 failed\n\nNEW: look at these today")
    assert "   2 x AssertionError: payment provider did not answer" in result.stdout
    assert result.returncode == 1


def test_known_issue_is_matched_to_its_ticket(report):
    result = triage(str(report), "--known", str(KIT / "known_issues.txt"))
    assert "KNOWN (SHOP-412)\n   2 x AssertionError: payment provider" in result.stdout
    new_part = result.stdout.split("NEW: look at these today")[1]
    assert "payment provider" not in new_part
    assert "- test_discount_code_is_applied" in new_part
    assert "- test_order_history_is_sorted" in new_part


def test_a_clean_night_exits_zero(tmp_path):
    (tmp_path / "test_ok.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    python("-m", "pytest", "-p", "no:cacheprovider", "-q", "--junitxml=ok.xml", cwd=tmp_path)
    result = triage(str(tmp_path / "ok.xml"))
    assert result.stdout == "Last night: 1 test, 0 failed\n\nNo new failures.\n"
    assert result.returncode == 0


def test_missing_report_says_what_to_do(tmp_path):
    result = triage("nightly.xml", cwd=tmp_path)
    assert (
        result.stdout.strip()
        == "No report at nightly.xml. Download it from last night's run first."
    )
    assert result.returncode == 2
