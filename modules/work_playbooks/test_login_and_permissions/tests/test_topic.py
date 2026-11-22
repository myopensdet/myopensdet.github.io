# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Login and permissions guide: the template finds exactly the three planted bugs in the
practice API, passes on the fixed API, skips without users, and never prints a token or
a password. All offline: the practice API runs on a free local port."""

import importlib.util
import os
import re
import subprocess
import sys
import threading
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
KIT = TOPIC / "templates" / "auth_tests"
ROOT = TOPIC.parents[2]
CREDIT = "Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/"
PASSWORD = "local_only_password"  # noqa: S105  (the practice API's fake password)
USERS = {
    "USER_A": f"arshad.test@example.com:{PASSWORD}",
    "USER_B": f"mia.khan@example.com:{PASSWORD}",
    "ADMIN": f"admin@example.com:{PASSWORD}",
}
EXPECTED_FAILS = {
    "tests/test_login.py::test_unknown_user_gets_the_same_answer_as_a_wrong_password",
    "tests/test_permissions.py::test_user_cannot_read_another_users_record",
    "tests/test_permissions.py::test_other_user_cannot_read_user_as_record",
    "tests/test_tokens.py::test_token_stops_working_after_logout",
}

SKIP_FOLDERS = {"__pycache__", ".pytest_cache"}
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file()
    and not SKIP_FOLDERS & set(p.parts)
    and (p.suffix in {".py", ".ini", ".txt", ".md"} or p.name == ".gitignore")
)

spec = importlib.util.spec_from_file_location("practice_api", KIT / "practice_api.py")
practice_api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(practice_api)


@pytest.fixture(params=[False, True], ids=["with bugs", "fixed"])
def api(request):
    server = practice_api.serve(port=0, fixed=request.param)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield request.param, f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


def run_kit(base_url, users=True):
    names = {"BASE_URL", *USERS}
    env = {k: v for k, v in os.environ.items() if k not in names} | {"BASE_URL": base_url}
    if users:
        env |= USERS
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider"],
        cwd=KIT, env=env, capture_output=True, text=True, timeout=120,
    )  # fmt: skip


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:3])


def test_pins_match_the_repo_lock_file():
    lock = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    for line in (KIT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        if "==" in line:
            assert re.search(rf"^{re.escape(line)} \\", lock, re.MULTILINE), line


def test_the_tests_find_the_bugs_and_pass_when_fixed(api):
    fixed, base_url = api
    result = run_kit(base_url)
    failed = {
        line.removeprefix("FAILED ").split(" - ")[0]
        for line in result.stdout.splitlines()
        if line.startswith("FAILED")
    }
    if fixed:
        assert "16 passed" in result.stdout, result.stdout[-3000:]
    else:
        assert failed == EXPECTED_FAILS, result.stdout[-3000:]
        assert "4 failed, 12 passed" in result.stdout
    assert PASSWORD not in result.stdout
    assert "Bearer" not in result.stdout  # tokens print as ***


def test_without_users_the_login_tests_skip(api):
    _, base_url = api
    result = run_kit(base_url, users=False)
    assert 'Set USER_A="email:password" to run this test' in result.stdout
    assert "5 passed, 11 skipped" in result.stdout, result.stdout[-2000:]


def test_practice_api_listens_on_this_computer_only():
    server = practice_api.serve(port=0)
    try:
        assert server.server_address[0] == "127.0.0.1"
    finally:
        server.server_close()
