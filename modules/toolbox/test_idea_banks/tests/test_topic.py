# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Test idea banks: every bank has the same five areas, and idea_checklist.py lists,
combines, filters and exports them as the page shows."""

import csv
import io
import re
import subprocess
import sys
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
KIT = TOPIC / "templates"
BANKS = sorted((KIT / "ideas").glob("*.md"))
CREDIT = "Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/"
AREAS = [
    "Works as it should",
    "Refuses bad input",
    "Edges and limits",
    "Security",
    "People, devices and failures",
]
FILES = sorted(
    p for p in TOPIC.rglob("*") if p.is_file() and "__pycache__" not in p.parts
    and p.suffix in {".py", ".md"}
)  # fmt: skip


def run(*args):
    return subprocess.run(
        [sys.executable, "idea_checklist.py", *args],
        cwd=KIT, capture_output=True, text=True, timeout=60,
    )  # fmt: skip


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:3])


@pytest.mark.parametrize("bank", BANKS, ids=lambda p: p.stem)
def test_every_bank_has_the_five_areas_and_no_duplicates(bank):
    text = bank.read_text(encoding="utf-8")
    assert re.findall(r"^## (.+)$", text, re.M) == AREAS
    ideas = re.findall(r"^- (.+)$", text, re.M)
    assert len(ideas) == len(set(ideas)) >= 15
    for email in re.findall(r"[\w.]+@[\w.]+", text):
        assert email.lower().endswith("example.com"), email


def test_list_shows_nine_banks():
    lines = run("--list").stdout.splitlines()
    assert len(lines) == 9
    assert lines[3] == "login                   26 ideas  Login"


def test_only_security_for_cart_and_payments():
    out = run("cart", "payments", "--only", "security").stdout
    assert out.startswith("# Test ideas: Cart and checkout, Payments\n\n7 ideas.")
    assert out.count("- [ ] ") == 7


def test_csv_has_every_idea():
    rows = list(csv.reader(io.StringIO(run("cart", "payments", "--csv").stdout)))
    assert rows[0] == ["Feature", "Area", "Idea"]
    assert len(rows) == 1 + 24 + 20


def test_mistakes_are_explained():
    assert run("logn").stderr.strip().startswith("No single idea bank called 'logn'. Choose from:")
    assert run("login", "--only", "speed").returncode == 1
    nothing = run()
    assert nothing.returncode == 2
    assert "Choose one or more, like:" in nothing.stdout


def test_a_bank_with_no_readable_ideas_says_why(tmp_path):
    kit = tmp_path / "kit"
    (kit / "ideas").mkdir(parents=True)
    (kit / "idea_checklist.py").write_text((KIT / "idea_checklist.py").read_text())
    (kit / "ideas" / "booking.md").write_text("# Booking\n\n## Works as it should\n\n* Book\n")
    result = subprocess.run(
        [sys.executable, "idea_checklist.py", "booking"],
        cwd=kit, capture_output=True, text=True, timeout=60,
    )  # fmt: skip
    assert result.stdout.startswith("No ideas found. Each idea is a line starting with '- '")
