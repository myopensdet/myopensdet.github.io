# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Debugging toolkit: the practice project fails exactly as the page shows, alone and
together, and the fixes the page describes make every test pass."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
KIT = TOPIC / "templates" / "debug_practice"
CREDIT = "Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/"
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file()
    and "__pycache__" not in p.parts
    and (p.suffix in {".py", ".md", ".txt", ".ini"} or p.name == ".gitignore")
)


def pytest_in(folder, *args):
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-p", "no:randomly", *args],
        cwd=folder, capture_output=True, text=True, timeout=120,
    ).stdout  # fmt: skip


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:3])


def test_together_three_fail():
    out = pytest_in(KIT)
    assert "3 failed, 2 passed" in out
    assert "assert 24.8 == 0.3" in out and "assert 67.32 == 45.0" in out
    assert "KeyError: 'SPRING'" in out


def test_alone_they_behave_differently():
    assert "assert 0.30000000000000004 == 0.3" in pytest_in(KIT, "-k", "two_cheap")
    assert "1 passed" in pytest_in(KIT, "-k", "small_letters")


def test_the_fixes_on_the_page_make_everything_pass(tmp_path):
    work = tmp_path / "debug_practice"
    shutil.copytree(KIT, work, ignore=shutil.ignore_patterns("__pycache__"))
    cart = work / "shop" / "cart.py"
    text = cart.read_text(encoding="utf-8")
    text = text.replace("def __init__(self, items=[]):", "def __init__(self, items=None):")
    text = text.replace("self.items = items", "self.items = list(items or [])")
    text = text.replace("return subtotal * (100 - off) / 100",
                        "return round(subtotal * (100 - off) / 100, 2)")  # fmt: skip
    cart.write_text(text, encoding="utf-8")
    discounts = work / "shop" / "discounts.py"
    text = discounts.read_text(encoding="utf-8")
    text = text.replace("return CODES[code.upper()]", "return CODES.get(code.upper(), 0)")
    discounts.write_text(text, encoding="utf-8")
    assert "5 passed" in pytest_in(work)
