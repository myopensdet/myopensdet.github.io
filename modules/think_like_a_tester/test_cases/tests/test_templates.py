# Template from myOpenSDET: https://myopensdet.github.io/
"""The templates of "Test cases" work, and the lessons' outputs stay true."""

import csv
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
TEMPLATES = TOPIC / "templates"
EXAMPLES = TOPIC / "examples"
CREDIT = "Template from myOpenSDET: https://myopensdet.github.io/"
ALL_REF = "REF-1,REF-2,REF-3,REF-4,REF-5,REF-6,REF-7"


def run(*args, cwd=EXAMPLES):
    return subprocess.run(
        [sys.executable, *args], cwd=cwd, capture_output=True, text=True, check=False
    )


def pytest_in(folder, *args):
    return run("-m", "pytest", "-q", "-p", "no:cacheprovider", *args, cwd=folder)


@pytest.mark.parametrize(
    "path",
    sorted(
        p
        for p in [*TEMPLATES.iterdir(), *EXAMPLES.rglob("*")]
        if p.suffix in {".py", ".md", ".csv", ".txt", ".ini"}
    ),
    ids=lambda p: p.name,
)
def test_every_file_starts_with_the_credit_line(path):
    assert CREDIT in path.read_text(encoding="utf-8").splitlines()[0]


def test_the_example_uses_the_plugin_unchanged():
    assert (EXAMPLES / "tests" / "conftest.py").read_text() == (
        TEMPLATES / "covers_plugin.py"
    ).read_text()


def test_the_requirements_report_shows_the_gap():
    result = pytest_in(EXAMPLES, "--requirements", ALL_REF)
    assert "11 passed" in result.stdout
    lines = [line.split() for line in result.stdout.splitlines() if line.startswith("REF-")]
    assert lines == [
        ["REF-1", "3", "tests"],
        ["REF-2", "1", "test"],
        ["REF-3", "NO", "TESTS"],
        ["REF-4", "2", "tests"],
        ["REF-5", "3", "tests"],
        ["REF-6", "1", "test"],
        ["REF-7", "1", "test"],
    ]


def test_the_requirements_report_points_at_a_typo(tmp_path):
    copy = tmp_path / "examples"
    shutil.copytree(EXAMPLES, copy, ignore=shutil.ignore_patterns("__pycache__"))
    tests = copy / "tests" / "test_refunds.py"
    tests.write_text(tests.read_text().replace('covers("REF-2")', 'covers("REF2")'))
    result = pytest_in(copy, "--requirements", ALL_REF)
    assert "REF-2      NO TESTS" in result.stdout
    assert "REF2       not in --requirements (typo?)" in result.stdout


def test_without_the_option_nothing_extra_is_printed_for_plain_runs(tmp_path):
    (tmp_path / "conftest.py").write_text((TEMPLATES / "covers_plugin.py").read_text())
    (tmp_path / "test_plain.py").write_text("def test_one():\n    assert True\n")
    result = pytest_in(tmp_path)
    assert "1 passed" in result.stdout
    assert "requirements" not in result.stdout


def test_traceability_finds_the_missing_and_the_unknown():
    result = run(
        str(TEMPLATES / "traceability.py"), "refund_requirements.txt", "refund_test_cases.csv"
    )
    assert result.returncode == 1
    assert "| REF-1 | TC-01, TC-02, TC-06 | 3 |" in result.stdout
    assert "| REF-5 | NONE | 0 |" in result.stdout
    assert "No test case: REF-5" in result.stdout
    assert "TC-16 covers REF-8, which is not in the requirements" in result.stdout


def test_traceability_passes_when_everything_is_covered(tmp_path):
    (tmp_path / "req.txt").write_text("A-1: one\nA-2: two\n")
    (tmp_path / "cases.csv").write_text("ID,Covers\nTC-1,A-1;A-2\n")
    result = run(str(TEMPLATES / "traceability.py"), "req.txt", "cases.csv", cwd=tmp_path)
    assert result.returncode == 0
    assert "Every requirement has at least one test case." in result.stdout


def test_traceability_without_files_shows_usage():
    assert run(str(TEMPLATES / "traceability.py")).returncode == 2


def test_the_csv_template_and_example_have_the_same_columns():
    def header(path):
        lines = [line for line in path.read_text().splitlines() if not line.startswith("#")]
        return next(csv.reader(lines))

    assert header(TEMPLATES / "test_cases.csv") == header(EXAMPLES / "refund_test_cases.csv")


def test_automated_test_names_in_the_csv_exist():
    tests = (EXAMPLES / "tests" / "test_refunds.py").read_text()
    lines = [
        line
        for line in (EXAMPLES / "refund_test_cases.csv").read_text().splitlines()
        if not line.startswith("#")
    ]
    for case in csv.DictReader(lines):
        if case["Automated"] != "no":
            assert f"def {case['Automated']}(" in tests, case["ID"]


def test_the_markdown_template_has_every_part():
    text = (TEMPLATES / "test_case.md").read_text()
    for part in ["**Covers:**", "## Before you start", "## Test data", "## Steps", "## Expected"]:
        assert part in text
