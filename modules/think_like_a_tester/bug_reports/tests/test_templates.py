# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""The templates of "Bug reports" work, and the lessons' outputs stay true."""

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

TOPIC = Path(__file__).resolve().parents[1]
TEMPLATES = TOPIC / "templates"
EXAMPLES = TOPIC / "examples"
CREDIT = "Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/"


def check(path):
    return subprocess.run(
        [sys.executable, str(TEMPLATES / "bug_report_check.py"), str(path)],
        capture_output=True,
        text=True,
        check=False,
    )


def load_checker():
    sys.path.insert(0, str(TEMPLATES))
    try:
        import bug_report_check
    finally:
        sys.path.pop(0)
    return bug_report_check


@pytest.mark.parametrize(
    "path",
    sorted(
        p for p in [*TEMPLATES.iterdir(), *EXAMPLES.iterdir()] if p.suffix in {".py", ".md", ".yml"}
    ),
    ids=lambda p: p.name,
)
def test_every_file_starts_with_the_credit_line(path):
    assert CREDIT in path.read_text(encoding="utf-8").splitlines()[0]


def test_the_vague_report_gets_six_problems():
    result = check(EXAMPLES / "bug_before.md")
    assert result.returncode == 1
    assert result.stdout.splitlines()[:6] == [
        '- Title: "Signup broken" is too vague. Say what is wrong, where, and when.',
        "- Environment: missing or empty.",
        "- Severity and priority: missing or empty.",
        "- Steps to reproduce: write at least two numbered steps.",
        "- Expected result: too vague. Write exactly what you saw or expected.",
        "- Actual result: too vague. Write exactly what you saw or expected.",
    ]


def test_the_rewritten_report_passes():
    result = check(EXAMPLES / "bug_after.md")
    assert result.returncode == 0
    assert result.stdout.startswith("Looks ready to send.")


def test_the_empty_template_is_not_ready():
    result = check(TEMPLATES / "bug_report.md")
    assert result.returncode == 1
    assert "6 things to fix" in result.stdout


def test_same_expected_and_actual_is_questioned():
    checker = load_checker()
    text = (EXAMPLES / "bug_after.md").read_text()
    sections = checker.sections(text)
    same = text.replace(sections["Actual result"], sections["Expected result"])
    assert "Expected and actual results are the same. Is it really a bug?" in checker.check(same)


def test_the_checker_shows_usage_without_a_file():
    result = subprocess.run(
        [sys.executable, str(TEMPLATES / "bug_report_check.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2


def test_the_issue_form_is_valid_and_asks_for_the_key_fields():
    form = yaml.safe_load((TEMPLATES / "bug_report_issue_form.yml").read_text())
    assert form["name"] == "Bug report"
    fields = {item["id"]: item for item in form["body"] if "id" in item}
    for field in ["steps", "expected", "actual", "version", "environment", "severity"]:
        assert fields[field]["validations"]["required"] is True
    assert len(fields["severity"]["attributes"]["options"]) == 4


def test_the_guide_defines_every_state():
    text = (TEMPLATES / "severity_priority_guide.md").read_text()
    for state in [
        "New",
        "Triaged",
        "In progress",
        "Fixed",
        "Verified",
        "Reopened",
        "Closed",
        "Duplicate",
        "Not a bug",
        "Won't fix",
    ]:
        assert f"| {state} |" in text
