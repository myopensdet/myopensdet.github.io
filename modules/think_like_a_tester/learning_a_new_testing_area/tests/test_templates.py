# Template from myOpenSDET: https://myopensdet.github.io/
"""The templates of "Learning a new testing area" are complete and usable."""

import re
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
TEMPLATES = TOPIC / "templates"
EXAMPLES = TOPIC / "examples"
CREDIT = "<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->"

EXPECTED_HEADINGS = {
    "day_one_questions.md": ["The ask", "The system", "Environments and access", "Risk", "Answers"],
    "one_page_test_plan.md": [
        "1. What and why",
        "2. In scope and out of scope",
        "3. Risks (highest first)",
        "4. Approach",
        "5. Environments and access",
        "6. Done when",
        "7. Open questions",
    ],
    "learning_log.md": ["<YYYY-MM-DD>"],
}


def headings(text: str) -> list[str]:
    return re.findall(r"^## (.+)$", text, flags=re.MULTILINE)


@pytest.mark.parametrize("name", sorted(EXPECTED_HEADINGS))
def test_template_starts_with_the_credit_line(name):
    first_line = (TEMPLATES / name).read_text(encoding="utf-8").splitlines()[0]
    assert first_line == CREDIT


@pytest.mark.parametrize(("name", "expected"), sorted(EXPECTED_HEADINGS.items()))
def test_template_has_every_section(name, expected):
    assert headings((TEMPLATES / name).read_text(encoding="utf-8")) == expected


def test_day_one_questions_are_checkboxes():
    text = (TEMPLATES / "day_one_questions.md").read_text(encoding="utf-8")
    assert text.count("- [ ] ") >= 15


def test_learning_log_has_every_field():
    text = (TEMPLATES / "learning_log.md").read_text(encoding="utf-8")
    for field in ["Goal today", "What I read or watched", "What I tried", "What I learned",
                  "Still confused about", "Next step"]:  # fmt: skip
        assert f"**{field}:**" in text


def test_the_example_plan_fills_every_section_of_the_template():
    template = headings((TEMPLATES / "one_page_test_plan.md").read_text(encoding="utf-8"))
    example = (EXAMPLES / "password_reset_test_plan.md").read_text(encoding="utf-8")
    assert headings(example) == template
    assert "<" not in example.replace("<!--", ""), "a placeholder like <name> was left in"
    assert "@" not in example or "@example.com" in example
