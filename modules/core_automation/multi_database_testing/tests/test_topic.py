# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Multi-database testing: offline checks always run, including the whole template
on SQLite. With ZTS_MULTI_DB=1 and the template's Docker databases up, it runs on all four."""

import os
import re
import subprocess
import sys
from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pytest
import yaml

TOPIC = Path(__file__).resolve().parents[1]
PROJECT = TOPIC / "templates" / "multi_db_tests"
CREDIT = "Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/"

sys.path.insert(0, str(PROJECT))
from db_clients import make_client  # noqa: E402
from db_clients.base_client import as_utc, normalize  # noqa: E402

SKIP_FOLDERS = {"__pycache__", ".pytest_cache"}
SUFFIXES = {".py", ".ini", ".txt", ".md", ".sql", ".json", ".yaml", ".yml", ".csv", ".example"}
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


def test_normalize_makes_each_database_look_the_same():
    assert normalize(Decimal("49.50")) == normalize(49.5) == "49.5"
    assert normalize(Decimal("15.00")) == normalize(15) == "15"
    aware = datetime(2026, 10, 3, 12, 0, tzinfo=UTC)
    dhaka = datetime(2026, 10, 3, 18, 0, tzinfo=timezone(timedelta(hours=6)))
    naive = datetime(2026, 10, 3, 12, 0)
    assert normalize(aware) == normalize(dhaka) == normalize(naive) == "2026-10-03 12:00:00"


def test_a_time_with_no_zone_is_utc_on_every_computer():
    assert as_utc(datetime(2026, 1, 1, 0, 30)).hour == 0


def test_password_comes_only_from_the_environment(monkeypatch):
    monkeypatch.delenv("MYSQL_PASSWORD", raising=False)
    settings = {"driver": "mysql", "password_env": "MYSQL_PASSWORD"}
    with pytest.raises(LookupError, match="Set MYSQL_PASSWORD"):
        make_client("mysql", settings)


def test_compose_is_safe():
    compose = yaml.safe_load((PROJECT / "docker-compose.yml").read_text(encoding="utf-8"))
    for name, service in compose["services"].items():
        assert "@sha256:" in service["image"], f"{name}: pin the image digest"
        for port in service["ports"]:
            assert port.startswith("127.0.0.1:"), f"{name}: open to the network: {port}"
        for key, value in service["environment"].items():
            if "PASSWORD" in key and key != "MYSQL_RANDOM_ROOT_PASSWORD":
                assert str(value).startswith("${"), f"{name}: {key} must come from .env"


def test_test_data_is_fake():
    emails = re.findall(r"[\w.]+@[\w.]+", (PROJECT / "test_data" / "customers.csv").read_text())
    assert emails and all(e.endswith("@example.com") for e in emails)


def run_template(env_extra):
    env = {k: v for k, v in os.environ.items() if not k.endswith("_PASSWORD")}
    env.update(env_extra)
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
        cwd=PROJECT,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )


def test_template_passes_on_sqlite(tmp_path):
    result = run_template({"TEST_DATABASES": "sqlite"})
    assert result.returncode == 0, result.stdout[-3000:] + result.stderr[-2000:]
    assert "8 passed, 4 skipped" in result.stdout


@pytest.mark.skipif(
    not os.environ.get("ZTS_MULTI_DB"), reason="Set ZTS_MULTI_DB=1 with the databases up"
)
def test_template_passes_on_all_four():
    result = run_template({})
    assert result.returncode == 0, result.stdout[-3000:] + result.stderr[-2000:]
    assert "44 passed" in result.stdout
