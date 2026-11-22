# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Docker for testers: offline checks of the Dockerfiles and the compose file always run.
With ZTS_DOCKER=1 and Docker running, the whole environment is built and the tests run in it."""

import os
import re
import subprocess
from pathlib import Path

import pytest
import yaml

TOPIC = Path(__file__).resolve().parents[1]
PROJECT = TOPIC / "templates" / "docker_tests"
CREDIT = "Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/"
DOCKERFILES = [PROJECT / "Dockerfile", PROJECT / "app" / "Dockerfile"]
COMPOSE = yaml.safe_load((PROJECT / "docker-compose.yml").read_text(encoding="utf-8"))

SKIP_FOLDERS = {"__pycache__", ".pytest_cache", "reports"}
NAMES = {"Dockerfile", ".dockerignore", ".gitignore", ".env.example"}
SUFFIXES = {".py", ".ini", ".txt", ".yml"}
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file()
    and not SKIP_FOLDERS & set(p.parts)
    and (p.suffix in SUFFIXES or p.name in NAMES)
    and p.name != "__init__.py"
)


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:2])


@pytest.mark.parametrize("path", DOCKERFILES, ids=lambda p: str(p.relative_to(PROJECT)))
def test_each_image_starts_from_a_pinned_base_and_runs_as_a_normal_user(path):
    text = path.read_text(encoding="utf-8")
    assert re.search(r"^FROM \S+:\d+\.\d+\.\d+\S*@sha256:[0-9a-f]{64}$", text, re.M)
    users = re.findall(r"^USER (\S+)$", text, re.M)
    assert users and users[-1] not in {"root", "0"}


def test_every_image_in_compose_is_pinned_or_built_here():
    for name, service in COMPOSE["services"].items():
        assert "build" in service or "@sha256:" in service["image"], name


def test_ports_are_only_open_on_this_computer():
    for name, service in COMPOSE["services"].items():
        for port in service.get("ports", []):
            assert port.startswith("127.0.0.1:"), f"{name}: {port}"


def test_the_password_comes_from_env_and_is_required():
    db_env = COMPOSE["services"]["db"]["environment"]
    assert db_env["POSTGRES_PASSWORD"].startswith("${POSTGRES_PASSWORD:?")
    compose_text = (PROJECT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "local_only_password" not in compose_text


def test_secrets_and_reports_stay_out_of_the_image_and_git():
    dockerignore = (PROJECT / ".dockerignore").read_text(encoding="utf-8").splitlines()
    gitignore = (PROJECT / ".gitignore").read_text(encoding="utf-8").splitlines()
    for ignore in (dockerignore, gitignore):
        assert ".env" in ignore
        assert "reports/" in ignore


def test_the_test_service_runs_only_when_asked():
    tests = COMPOSE["services"]["tests"]
    assert tests["profiles"] == ["tests"]
    assert tests["environment"]["API_URL"] == "http://api:8000"
    assert tests["depends_on"]["api"]["condition"] == "service_healthy"


@pytest.mark.skipif(os.environ.get("ZTS_DOCKER") != "1", reason="set ZTS_DOCKER=1 to use Docker")
def test_the_tests_pass_inside_the_compose_environment():
    env = {
        **os.environ,
        "POSTGRES_PASSWORD": "local_only_password",
        "API_PORT": "58181",
        "DB_PORT": "58134",
    }
    compose = ["docker", "compose", "-p", "zts-docker-topic-check"]

    def run(*args):
        return subprocess.run(
            [*compose, *args], cwd=PROJECT, env=env, capture_output=True, text=True, timeout=600
        )

    try:
        result = run("run", "--rm", "--build", "-v", "/tests/reports", "tests")
        assert result.returncode == 0, result.stdout[-3000:] + result.stderr[-2000:]
        assert "5 passed" in result.stdout
    finally:
        run("down", "-v")
