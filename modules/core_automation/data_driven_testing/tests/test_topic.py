# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Data-driven testing: all offline, including the whole template and Robot Framework."""

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from openpyxl import load_workbook

TOPIC = Path(__file__).resolve().parents[1]
PROJECT = TOPIC / "templates" / "data_driven_tests"
CREDIT = "Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/"

sys.path.insert(0, str(PROJECT))
from helpers import factories  # noqa: E402
from helpers.data_loaders import cases, to_bool, to_decimal  # noqa: E402

SKIP_FOLDERS = {"__pycache__", ".pytest_cache", "results"}
SUFFIXES = {".py", ".ini", ".txt", ".md", ".yaml", ".csv", ".robot"}
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file()
    and not SKIP_FOLDERS & set(p.parts)
    and (p.suffix in SUFFIXES or p.name == ".gitignore")
)


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:2])


def test_json_data_has_the_credit_line():
    assert CREDIT in (PROJECT / "test_data" / "order_totals.json").read_text(encoding="utf-8")


def test_yaml_quotes_every_country_and_number():
    """Unquoted, YAML reads NO (Norway) as false and 1.10 as 1.1."""
    data = yaml.safe_load((PROJECT / "test_data" / "shipping_cases.yaml").read_text())
    for case in data["cases"]:
        for key in ("country", "weight_kg", "expected"):
            if key in case:
                assert isinstance(case[key], str), f"{case['case']}: quote {key}"


def test_excel_sheet_matches_the_script_that_makes_it(tmp_path):
    from tools import make_discount_sheet  # noqa: PLC0415

    sheet = load_workbook(PROJECT / "test_data" / "discount_rules.xlsx")["Discounts"]
    assert [tuple(row) for row in sheet.iter_rows(values_only=True)] == make_discount_sheet.ROWS


def test_known_bug_rows_expect_an_assertion():
    params = cases("signup_cases.csv")
    marked = [p for p in params if p.marks]
    assert [p.id for p in marked] == ["exactly 18"]
    assert marked[0].marks[0].kwargs["raises"] is AssertionError


def test_converters():
    assert to_decimal(19.99) == to_decimal("19.99")
    assert to_bool("TRUE") is True and to_bool(False) is False and to_bool("") is False
    with pytest.raises(ValueError, match="Not true or false"):
        to_bool("maybe")
    with pytest.raises(ValueError, match="Not a number: None"):
        to_decimal(None)


def test_fake_emails_never_reach_a_real_inbox():
    domains = {factories.make_signup().email.split("@")[1] for _ in range(300)}
    assert domains <= {"example.com", "example.net", "example.org"}


def test_the_same_seed_gives_the_same_data():
    factories.fake.seed_instance(42)
    first = factories.make_order()
    factories.fake.seed_instance(42)
    assert factories.make_order() == first


def run(*command):
    env = {k: v for k, v in os.environ.items() if k != "TEST_SEED"}
    return subprocess.run(
        command, cwd=PROJECT, env=env, capture_output=True, text=True, timeout=300
    )


def test_template_passes_and_finds_the_planted_bug():
    result = run(sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider")
    assert result.returncode == 0, result.stdout[-3000:] + result.stderr[-2000:]
    assert "38 passed, 1 xfailed" in result.stdout


def test_robot_suites_pass_with_the_known_bug_skipped(tmp_path):
    result = run(
        sys.executable,
        "-m",
        "robot",
        "--pythonpath",
        ".",
        "--outputdir",
        str(tmp_path),
        "--skiponfailure",
        "known-bug",
        "robot",
    )
    assert result.returncode == 0, result.stdout[-3000:]
    assert re.search(r"10 tests, 9 passed, 0 failed, 1 skipped", result.stdout)
