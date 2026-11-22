# Template from myOpenSDET: https://myopensdet.github.io/
"""SDET in Agile: story_check.py finds the vague words and missing areas in the
sample story, and passes the refined one, exactly as the page shows."""

import subprocess
import sys
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
KIT = TOPIC / "templates" / "agile_kit"
CREDIT = "Template from myOpenSDET: https://myopensdet.github.io/"
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file() and "__pycache__" not in p.parts and p.suffix in {".py", ".md"}
)


def check(*args, cwd=KIT):
    return subprocess.run(
        [sys.executable, str(KIT / "story_check.py"), *args],
        capture_output=True, text=True, timeout=60, cwd=cwd,
    )  # fmt: skip


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:3])


@pytest.mark.parametrize(
    "line",
    [
        "== 5 acceptance criteria",
        '      "properly" -> What exactly should happen? Which message, which status?',
        '      "handled" -> Handled how? Show an error, ignore it, or log it?',
        '      "quickly" -> How fast, in seconds? For how many users at once?',
        '      "etc" -> What else, exactly? List every item.',
        "   who can do it            Who may do this? Guests too?",
        "   repeats                  What if the user does it twice?",
        "15 questions for refinement.",
    ],
)
def test_vague_story_gets_questions(line):
    result = check("stories/SHOP-420.md")
    assert line in result.stdout.splitlines()
    assert result.returncode == 1


def test_refined_story_is_ready():
    result = check("stories/SHOP-420-after-refinement.md")
    assert "== 6 acceptance criteria" in result.stdout
    assert "->" not in result.stdout
    assert result.stdout.rstrip().endswith("Ready for the sprint.")
    assert result.returncode == 0


def test_template_lists_its_criteria():
    result = check("acceptance_criteria_template.md")
    assert "== 6 acceptance criteria" in result.stdout


def test_story_without_criteria(tmp_path):
    (tmp_path / "s.md").write_text("# SHOP-1: Login\n\nLog in fast.\n", encoding="utf-8")
    result = check("s.md", cwd=tmp_path)
    assert "No 'As a ..., I want ..., so that ...' sentence" in result.stdout
    assert (
        "No acceptance criteria found. Add a '## Acceptance criteria' list first." in result.stdout
    )
    assert result.returncode == 1


def test_no_file_shows_usage():
    result = check("nothere.md")
    assert result.stdout.strip() == "Usage: python story_check.py <story file>"
    assert result.returncode == 2
