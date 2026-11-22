# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Communicating your work: status_update.py gives RED with a failing test, AMBER with a
known risk, GREEN without, and estimate.py gives the range shown on the page."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
KIT = TOPIC / "templates" / "comms_kit"
CREDIT = "Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/"
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file() and "__pycache__" not in p.parts
    and p.suffix in {".py", ".md", ".ini", ".csv"}
)  # fmt: skip


def run(*args, cwd=KIT):
    return subprocess.run(
        [sys.executable, *args], capture_output=True, text=True, timeout=60, cwd=cwd
    )


def report(tmp_path, *extra):
    xml = tmp_path / "junit.xml"
    run("-m", "pytest", "-p", "no:cacheprovider", "-q", str(KIT / "example_run"),
        f"--junitxml={xml}", *extra, cwd=tmp_path)  # fmt: skip
    return str(xml)


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:3])


def test_failing_test_is_red(tmp_path):
    result = run("status_update.py", report(tmp_path), "status_notes.ini")
    assert (
        "RED: Release 2.15 testing: 4/5 tests pass. 1 test failing: "
        "test_order_history_is_sorted." in result.stdout
    )
    assert "Must fix first:\n- FAILED test_order_history_is_sorted" in result.stdout
    assert result.returncode == 1


def test_known_risk_is_amber(tmp_path):
    result = run(
        "status_update.py", report(tmp_path, "-k", "not order_history"), "status_notes.ini"
    )
    assert (
        "AMBER: Release 2.15 testing: 4/4 tests pass. Tests pass, 1 known risk to accept."
        in result.stdout
    )
    assert "Can release if you accept the risks below. Your decision." in result.stdout
    assert result.returncode == 0


def test_no_risks_is_green(tmp_path):
    notes = tmp_path / "notes.ini"
    text = (KIT / "status_notes.ini").read_text(encoding="utf-8")
    notes.write_text(text.split("[risks]")[0], encoding="utf-8")
    result = run("status_update.py", report(tmp_path, "-k", "not order_history"), str(notes))
    assert (
        "GREEN: Release 2.15 testing: 4/4 tests pass. Tests pass, no known risks." in result.stdout
    )


def test_estimate_range():
    result = run("estimate.py", "estimate.csv")
    assert "Expected: 24 hours. Likely between 21 and 26 hours." in result.stdout
    assert "If every task hits its worst case: 47 hours." in result.stdout


def test_estimate_and_status_bad_input(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("task,best,likely,worst\nAPI tests,8,4,12\n", encoding="utf-8")
    result = run("estimate.py", str(bad))
    assert result.stdout.strip() == "'API tests': needs best <= likely <= worst, got 8, 4, 12"
    assert run("status_update.py", "nothere.xml").returncode == 2


def test_example_run_has_no_leftover_reports():
    assert not (KIT / "reports").exists()
    assert shutil.which(sys.executable)
