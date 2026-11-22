# Template from myOpenSDET: https://myopensdet.github.io/
"""Cheat sheets: every SQL query runs on the practice shop, every HTTP status name is
the official one, every Gherkin example parses, every locator is in the Playwright test
(and it passes). With ZTS_DOCKER=1, every Docker command and flag exists (--help only)."""

import http
import os
import re
import shlex
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
KIT = TOPIC / "templates"
CREDIT = "Template from myOpenSDET: https://myopensdet.github.io/"
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file() and "__pycache__" not in p.parts
    and p.suffix in {".py", ".md", ".sql", ".html"}
)  # fmt: skip


def sheet(name):
    return (KIT / name).read_text(encoding="utf-8")


def blocks(text, lang):
    return re.findall(rf"```{lang}\n(.*?)```", text, re.S)


def try_sql(*args):
    return subprocess.run(
        [sys.executable, "try_sql.py", *args], cwd=KIT, capture_output=True, text=True, timeout=60
    )


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:3])


@pytest.mark.parametrize("query", blocks(sheet("sql_cheat_sheet.md"), "sql"))
def test_every_sql_query_runs(query):
    db = sqlite3.connect(":memory:")
    db.executescript(sheet("practice_shop.sql"))
    db.executescript(query)


def test_the_weekly_checks_find_the_planted_problems():
    checks = [b for b in blocks(sheet("sql_cheat_sheet.md"), "sql") if b.startswith("--")]
    db = sqlite3.connect(":memory:")
    db.executescript(sheet("practice_shop.sql"))
    found = [db.execute(q).fetchall() for q in checks]
    duplicates, orphans, no_email, bad_totals = found[:4]
    assert duplicates == [("sam@example.com", 2)]
    assert orphans == [(105, 99)]
    assert no_email == [(5, "No Email")]
    assert bad_totals == [(104, 40, 24.5)]


def test_try_sql_prints_a_table_and_errors():
    result = try_sql("SELECT status, COUNT(*) AS how_many FROM orders GROUP BY status")
    assert result.stdout.splitlines() == [
        "status     how_many",
        "---------  --------",
        "cancelled  1",
        "paid       4",
        "(2 rows)",
    ]
    assert try_sql("SELECT name FROM customer").stdout.strip() == (
        "SQL error: no such table: customer"
    )
    assert try_sql("UPDATE orders SET status = 'cancelled' WHERE id = 102").stdout.strip() == (
        "OK: 1 row(s) changed."
    )
    assert try_sql().returncode == 2


def test_status_names_are_the_official_ones():
    rows = re.findall(r"^\| (\d{3}) \| ([^|]+?) \|", sheet("http_cheat_sheet.md"), re.M)
    assert len(rows) == 19
    for code, name in rows:
        assert http.HTTPStatus(int(code)).phrase == name


def test_every_gherkin_example_parses():
    from gherkin.parser import Parser

    examples = blocks(sheet("gherkin_cheat_sheet.md"), "gherkin")
    assert len(examples) == 4
    for text in examples:
        assert Parser().parse(text)["feature"]["children"]


def test_every_locator_on_the_sheet_is_in_the_test():
    code = "".join(sheet("test_locators.py").split())
    for frag in re.findall(r"`((?:page|expect)\.?[^`]*)`", sheet("locators_cheat_sheet.md")):
        if frag != "page.pause()":
            assert "".join(frag.split()) in code, frag


def browser_installed():
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            return Path(p.chromium.executable_path).exists()
    except Exception:  # noqa: BLE001 (any problem means: skip)
        return False


@pytest.mark.skipif(not browser_installed(), reason="playwright install chromium")
def test_the_locator_test_passes():
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-q", "test_locators.py"],
        cwd=KIT, capture_output=True, text=True, timeout=300,
    )  # fmt: skip
    assert "3 passed" in result.stdout, result.stdout[-2000:]


def docker_flags(words):
    """The flags that belong to docker itself, up to the image or container name."""
    flags = []
    for before, word in zip(["docker", *words], words, strict=False):
        if word.startswith("-"):
            name = word.split("=")[0]
            flags += [f"-{c}" for c in name[1:]] if re.fullmatch(r"-[a-z]{2,}", name) else [name]
        elif not before.startswith("-") and flags:
            break
    return flags


@pytest.mark.skipif(os.environ.get("ZTS_DOCKER") != "1", reason="set ZTS_DOCKER=1")
def test_every_docker_command_and_flag_exists():
    docker = shutil.which("docker")
    groups = {"compose", "system", "container", "image"}
    for command in re.findall(r"`(docker [^`]+)`", sheet("docker_cheat_sheet.md")):
        words = shlex.split(command)[1:]
        sub = words[:2] if words[0] in groups else words[:1]
        helptext = subprocess.run(
            [docker, *sub, "--help"], capture_output=True, text=True, timeout=60
        ).stdout
        for flag in docker_flags(words[len(sub) :]):
            assert re.search(rf"(^|[\s,]){re.escape(flag)}([\s,=]|$)", helptext, re.M), command
