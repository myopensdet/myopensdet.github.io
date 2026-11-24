# Template from myOpenSDET: https://myopensdet.github.io/
"""Contract testing: the consumer tests write a pact, the stock service keeps it,
each planted breaking change fails with a clear report, and a safe change passes."""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
ROOT = TOPIC.parents[1].parent
KIT = TOPIC / "templates" / "contract_kit"
CREDIT = "Template from myOpenSDET: https://myopensdet.github.io/"
FILES = sorted(
    p for p in TOPIC.rglob("*")
    if p.is_file() and not {"__pycache__", "pacts"} & set(p.parts)
    and (p.suffix in {".py", ".ini", ".txt"} or p.name == ".gitignore")
)  # fmt: skip


def run_kit(tmp_path, *args, change=""):
    """Run the kit in a copy, so pact files never land in the repo."""
    copy = tmp_path / "contract_kit"
    if not copy.exists():
        shutil.copytree(KIT, copy, ignore=shutil.ignore_patterns("pacts", "__pycache__"))
    env = os.environ | {"STOCK_CHANGE": change, "PACT_DO_NOT_TRACK": "true"}
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-q", *args],
        cwd=copy, capture_output=True, text=True, timeout=300, env=env,
    )  # fmt: skip


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:3])


def test_pins_match_the_repo_lock_file():
    lock = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    for line in (KIT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        if "==" in line:
            assert re.search(rf"^{re.escape(line)} \\", lock, re.MULTILINE), line


def test_tracking_is_off_by_default():
    conftest = (KIT / "tests" / "conftest.py").read_text(encoding="utf-8")
    assert conftest.index('setdefault("PACT_DO_NOT_TRACK", "true")') < conftest.index("from pact")


def test_the_kit_passes_and_writes_one_pact(tmp_path):
    result = run_kit(tmp_path)
    assert "4 passed" in result.stdout, result.stdout[-3000:]
    assert [p.name for p in (tmp_path / "contract_kit" / "pacts").iterdir()] == [
        "orders-stock.json"
    ]


def test_a_new_field_is_a_safe_change(tmp_path):
    assert "4 passed" in run_kit(tmp_path, change="add_field").stdout


@pytest.mark.parametrize(
    "change, says",
    [
        ("rename_price", "$ -> Actual map is missing the following keys: price_cents"),
        ("price_as_text", "$.price_cents -> Expected '24.99' (String) to be an integer"),
    ],
)
def test_a_breaking_change_fails_with_a_clear_report(tmp_path, change, says):
    run_kit(tmp_path, "tests/test_consumer.py")
    result = run_kit(tmp_path, "tests/test_provider.py", change=change)
    assert "1 failed" in result.stdout, result.stdout[-3000:]
    assert says in result.stdout
    assert "There were 1 pact failures" in result.stdout


def test_the_provider_asks_for_the_pact_first(tmp_path):
    result = run_kit(tmp_path, "tests/test_provider.py")
    assert "No pact files in pacts/. Run the consumer tests first" in result.stdout
