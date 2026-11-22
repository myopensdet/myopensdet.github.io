# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""API + database: offline checks always run. With ZTS_API_DB=1, the practice API on
127.0.0.1:8090 and its database up, the whole template runs against them."""

import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

TOPIC = Path(__file__).resolve().parents[1]
PROJECT = TOPIC / "templates" / "api_db_tests"
APP = TOPIC / "examples" / "bookshop_api"
CREDIT = "Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/"

sys.path.insert(0, str(PROJECT))
from helpers.clients import Cleanup, setting, wait_for  # noqa: E402

SKIP_FOLDERS = {"__pycache__", ".pytest_cache"}
SUFFIXES = {".py", ".ini", ".txt", ".md", ".sql", ".yaml", ".yml", ".example"}
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file()
    and not SKIP_FOLDERS & set(p.parts)
    and p.name != ".env"
    and (p.suffix in SUFFIXES or p.name == ".gitignore")
)


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:2])


def test_wait_for_returns_as_soon_as_the_value_is_there():
    answers = iter([None, None, {"event": "order_created"}])
    assert wait_for(lambda: next(answers), every=0) == {"event": "order_created"}


def test_wait_for_fails_with_a_clear_message():
    with pytest.raises(AssertionError, match="Waited 0.1 s for the event, it never happened"):
        wait_for(lambda: None, timeout=0.1, every=0.01, what="the event")


class FakeDb:
    def __init__(self):
        self.deleted = []

    def run(self, sql, params):
        self.deleted.append((sql.split()[2], params[0]))


def test_cleanup_deletes_newest_first():
    db = FakeDb()
    cleanup = Cleanup(db)
    cleanup.add("customers", 1)
    cleanup.add("books", 2)
    cleanup.add("orders", 3)
    cleanup.run()
    assert db.deleted == [("orders", 3), ("books", 2), ("customers", 1)]


def test_settings_come_only_from_the_environment(monkeypatch):
    monkeypatch.delenv("API_URL", raising=False)
    with pytest.raises(LookupError, match="Set the environment variable API_URL first"):
        setting("API_URL")


def test_every_xfail_names_the_error_it_expects():
    """A strict xfail without raises= also passes when the test itself is broken."""
    for path in (PROJECT / "tests").glob("test_*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "xfail":
                names = {k.arg for k in node.keywords}
                assert {"raises", "strict"} <= names, (
                    f"{path.name}: xfail needs raises= and strict="
                )


def test_compose_is_safe():
    compose = yaml.safe_load((APP / "docker-compose.yml").read_text(encoding="utf-8"))
    for name, service in compose["services"].items():
        assert "@sha256:" in service["image"], f"{name}: pin the image digest"
        for port in service["ports"]:
            assert port.startswith("127.0.0.1:"), f"{name}: open to the network: {port}"
        for key, value in service["environment"].items():
            if "PASSWORD" in key:
                assert str(value).startswith("${"), f"{name}: {key} must come from .env"


def test_test_emails_are_fake():
    for path in (PROJECT / "tests").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "@" not in text.replace("@example.com", "").replace("@pytest", "")


def run_template(env_extra):
    env = {k: v for k, v in os.environ.items() if k not in ("API_URL", "DATABASE_URL")}
    env.update(env_extra)
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
        cwd=PROJECT,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )


def test_template_skips_cleanly_without_settings():
    result = run_template({})
    assert result.returncode == 0, result.stdout[-3000:] + result.stderr[-2000:]
    assert "11 skipped" in result.stdout


@pytest.mark.skipif(not os.environ.get("ZTS_API_DB"), reason="Set ZTS_API_DB=1 with the API up")
def test_template_finds_the_two_planted_bugs():
    result = run_template(
        {
            "API_URL": "http://127.0.0.1:8090",
            "DATABASE_URL": os.environ.get(
                "ZTS_API_DB_URL",
                "postgresql://shop_tester:local_only_password@127.0.0.1:5432/bookshop",
            ),
        }
    )
    assert result.returncode == 0, result.stdout[-3000:] + result.stderr[-2000:]
    assert "9 passed, 2 xfailed" in result.stdout
