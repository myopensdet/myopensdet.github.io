# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Database guide: offline checks of the kit's safety rules always run. With ZTS_DOCKER=1 and
Docker running, the practice database is started under its own name and port, the checks find
exactly the six planted problems, every query in sql/data_checks.sql runs, and the tests can't
write."""

import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

TOPIC = Path(__file__).resolve().parents[1]
KIT = TOPIC / "templates" / "db_checks"
CREDIT = "Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/"
COMPOSE = yaml.safe_load((KIT / "docker-compose.yml").read_text(encoding="utf-8"))
PASSWORD = "local_only_password"  # noqa: S105 (throwaway local practice database)

SKIP_FOLDERS = {"__pycache__", ".pytest_cache"}
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file()
    and not SKIP_FOLDERS & set(p.parts)
    and (
        p.suffix in {".py", ".ini", ".txt", ".md", ".sql", ".yml"}
        or p.name in {".gitignore", ".env.example"}
    )
    and p.name != "__init__.py"
)


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:3])


def test_the_database_is_pinned_local_and_needs_a_password():
    db = COMPOSE["services"]["db"]
    assert "@sha256:" in db["image"]
    assert all(port.startswith("127.0.0.1:") for port in db["ports"])
    assert db["environment"]["POSTGRES_PASSWORD"].startswith("${POSTGRES_PASSWORD:?")


def test_the_practice_data_uses_only_made_up_emails():
    sql = (KIT / "sql" / "practice_shop.sql").read_text(encoding="utf-8")
    emails = [word.strip("',();") for word in sql.split() if "@" in word]
    assert emails and all(email.lower().endswith("@example.com") for email in emails)


def test_the_tests_connect_read_only():
    assert "conn.read_only = True" in (KIT / "tests" / "conftest.py").read_text(encoding="utf-8")


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def database():
    if os.environ.get("ZTS_DOCKER") != "1":
        pytest.skip("set ZTS_DOCKER=1 to use Docker")
    port = free_port()
    env = {**os.environ, "POSTGRES_PASSWORD": PASSWORD, "DB_PORT": str(port)}
    compose = ["docker", "compose", "-p", "zts-db-checks-topic"]

    def run(*args, **kwargs):
        return subprocess.run(
            [*compose, *args], cwd=KIT, env=env, capture_output=True, text=True,
            timeout=300, **kwargs,
        )  # fmt: skip

    started = run("up", "-d", "--wait")
    assert started.returncode == 0, started.stderr
    try:
        yield run, f"postgresql://shop_tester:{PASSWORD}@127.0.0.1:{port}/shop"
    finally:
        run("down", "-v")


def test_the_checks_find_exactly_the_planted_problems(database):
    _, url = database
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider"],
        cwd=KIT,
        env={**os.environ, "DATABASE_URL": url},
        capture_output=True,
        text=True,
        timeout=120,
    )
    failed = sorted(
        line.split("::")[1].split(" ")[0] for line in result.stdout.splitlines()
        if line.startswith("FAILED")
    )  # fmt: skip
    assert failed == [
        "test_every_order_item_belongs_to_an_order",
        "test_no_duplicate_emails",
        "test_order_statuses_are_known",
        "test_order_totals_match_their_items",
        "test_orders_are_linked_to_customers_by_a_foreign_key",
        "test_stock_is_never_negative",
    ], result.stdout[-3000:]
    assert "6 failed, 8 passed" in result.stdout
    assert PASSWORD not in result.stdout


def test_every_query_in_the_sql_file_runs(database):
    run, _ = database
    sql = (KIT / "sql" / "data_checks.sql").read_text(encoding="utf-8")
    result = run(
        "exec", "-T", "db", "psql", "-v", "ON_ERROR_STOP=1", "-U", "shop_tester", "-d", "shop",
        input=sql,
    )  # fmt: skip
    assert result.returncode == 0, result.stderr
    assert "mia.khan@example.com |        2" in result.stdout
    assert "BK-1003      | 50.00 |           45.00" in result.stdout


def test_the_connection_cannot_change_data(database):
    import psycopg  # noqa: PLC0415  (installed with the kit, needed only here)

    _, url = database
    with psycopg.connect(url) as conn:
        conn.read_only = True
        with pytest.raises(psycopg.errors.ReadOnlySqlTransaction):
            conn.execute("DELETE FROM orders")
