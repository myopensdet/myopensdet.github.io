# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Database testing: offline checks always run. With ZTS_DATABASE_URL set to a
throwaway PostgreSQL database, the template project and the examples run against it."""

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
EXAMPLES = TOPIC / "examples"
PROJECT = TOPIC / "templates" / "shop_db_tests"
CREDIT = "Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/"

sys.path.insert(0, str(PROJECT))
from db.client import database_url  # noqa: E402

SKIP_FOLDERS = {"__pycache__", ".pytest_cache"}
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file()
    and not SKIP_FOLDERS & set(p.parts)
    and (p.suffix in {".py", ".ini", ".txt", ".md", ".sql"} or p.name == ".gitignore")
)

DB_URL = os.environ.get("ZTS_DATABASE_URL")
needs_db = pytest.mark.skipif(not DB_URL, reason="Set ZTS_DATABASE_URL to a throwaway PostgreSQL")


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:2])


def test_database_url_comes_only_from_the_environment(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(LookupError, match="Set the environment variable DATABASE_URL first"):
        database_url()


def test_seed_data_is_fake():
    seed = (PROJECT / "sql" / "seed.sql").read_text(encoding="utf-8")
    emails = re.findall(r"'([^']+@[^']+)'", seed)
    assert emails, "the seed should have customers"
    assert all(e.endswith("@example.com") for e in emails)


def test_no_password_is_written_in_code():
    for path in FILES:
        if path.suffix in {".py", ".sql", ".ini"} and path != Path(__file__).resolve():
            assert "local_only_password" not in path.read_text(encoding="utf-8"), path


@needs_db
def test_template_project_passes_and_leaves_nothing_behind():
    env = {**os.environ, "DATABASE_URL": DB_URL}
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
        cwd=PROJECT,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout[-3000:] + result.stderr[-2000:]
    import psycopg

    with psycopg.connect(DB_URL) as conn:
        left = conn.execute(
            "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'shop_test'"
        ).fetchall()
    assert left == []
