# Template from myOpenSDET: https://myopensdet.github.io/
"""The templates of "Test levels and the pyramid" work on the example shop, as the lessons show."""

import re
import subprocess
import sys
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
TEMPLATES = TOPIC / "templates"
EXAMPLES = TOPIC / "examples"
CREDIT = "# Template from myOpenSDET: https://myopensdet.github.io/"


def run(*args, cwd=EXAMPLES):
    return subprocess.run(
        [sys.executable, *args], cwd=cwd, capture_output=True, text=True, check=False
    )


def pytest_in_examples(*args):
    return run("-m", "pytest", "-q", "-p", "no:cacheprovider", *args)


@pytest.mark.parametrize("name", ["pytest.ini", "conftest.py", "pyramid_report.py"])
def test_template_starts_with_the_credit_line(name):
    assert (TEMPLATES / name).read_text(encoding="utf-8").splitlines()[0] == CREDIT


@pytest.mark.parametrize(
    ("template", "copy"), [("pytest.ini", "pytest.ini"), ("conftest.py", "tests/conftest.py")]
)
def test_the_example_uses_the_templates_unchanged(template, copy):
    assert (EXAMPLES / copy).read_text(encoding="utf-8") == (TEMPLATES / template).read_text(
        encoding="utf-8"
    )


def test_the_example_suite_passes_and_skips_the_browser_test():
    result = pytest_in_examples()
    assert result.returncode == 0, result.stdout
    assert re.search(r"12 passed, 1 skipped", result.stdout)


@pytest.mark.parametrize(
    ("marker", "summary"),
    [
        ("unit", "7 passed, 6 deselected"),
        ("integration", "2 passed, 11 deselected"),
        ("api", "3 passed, 10 deselected"),
    ],
)
def test_folders_become_markers(marker, summary):
    result = pytest_in_examples("-m", marker)
    assert summary in result.stdout


def test_a_misspelled_level_is_an_error():
    result = pytest_in_examples("-m", "unti")
    assert result.returncode == 4
    assert "Unknown marker(s) in '-m' expression: unti" in result.stdout + result.stderr


def test_pyramid_report_counts_each_level():
    result = run(str(TEMPLATES / "pyramid_report.py"))
    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    assert lines[0] == "Tests per level (a healthy suite is widest at the bottom)"
    counts = {line.split()[0]: int(line.split()[-2]) for line in lines[2:7]}
    assert counts == {"e2e": 0, "ui": 1, "api": 3, "integration": 2, "unit": 7}
    assert "Total: 13 tests" in result.stdout
    assert "Warning" not in result.stdout


def test_pyramid_report_warns_about_an_ice_cream_cone(tmp_path):
    (tmp_path / "pytest.ini").write_text((TEMPLATES / "pytest.ini").read_text(encoding="utf-8"))
    tests = tmp_path / "tests"
    (tests / "ui").mkdir(parents=True)
    (tests / "unit").mkdir()
    (tests / "conftest.py").write_text((TEMPLATES / "conftest.py").read_text(encoding="utf-8"))
    (tests / "ui" / "test_pages.py").write_text(
        "def test_a():\n    pass\n\ndef test_b():\n    pass\n"
    )
    (tests / "unit" / "test_rule.py").write_text("def test_c():\n    pass\n")
    result = run(str(TEMPLATES / "pyramid_report.py"), cwd=tmp_path)
    assert "Warning: more UI and end-to-end tests than unit tests." in result.stdout


def test_decision_chart_has_every_section():
    text = (TEMPLATES / "test_level_decision_chart.md").read_text(encoding="utf-8")
    assert text.splitlines()[0].startswith("<!-- Template from myOpenSDET:")
    assert re.findall(r"^## (.+)$", text, flags=re.MULTILINE) == [
        "The questions",
        "Also ask",
        "My test ideas",
        "Check the shape",
    ]


def test_speed_check_runs_and_reports_percentiles():
    result = run("speed_check.py")
    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("200 requests\nmedian: ")
    assert "95th percentile:" in result.stdout
