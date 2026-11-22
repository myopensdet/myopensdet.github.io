# Template from myOpenSDET: https://myopensdet.github.io/
"""The Markdown templates of "The SDET role" are complete, and the example tests pass."""

import re
import subprocess
import sys
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
TEMPLATES = TOPIC / "templates"
CREDIT = "<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->"

EXPECTED_HEADINGS = {
    "new_team_onboarding_checklist.md": [
        "Access (week 1)",
        "People (week 1)",
        "The product (weeks 1 and 2)",
        "The existing tests (week 2)",
        "My first useful change (weeks 2 and 3)",
        "Open questions",
    ],
    "first_90_days_plan.md": [
        "Days 1 to 30: learn",
        "Days 31 to 60: contribute",
        "Days 61 to 90: own",
        "What I need from the team",
        "Risks to this plan",
        "Check-ins",
    ],
    "automation_readiness_checklist.md": [
        "Is it worth automating?",
        "Can we automate it reliably?",
        "Rough payback",
        "Decision",
    ],
}


@pytest.mark.parametrize("name", sorted(EXPECTED_HEADINGS))
def test_template_starts_with_the_credit_line(name):
    assert (TEMPLATES / name).read_text(encoding="utf-8").splitlines()[0] == CREDIT


@pytest.mark.parametrize(("name", "expected"), sorted(EXPECTED_HEADINGS.items()))
def test_template_has_every_section(name, expected):
    text = (TEMPLATES / name).read_text(encoding="utf-8")
    assert re.findall(r"^## (.+)$", text, flags=re.MULTILINE) == expected


def test_shipping_example_passes():
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_shipping.py"],
        cwd=TOPIC / "examples",
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout
    assert "5 passed" in result.stdout
