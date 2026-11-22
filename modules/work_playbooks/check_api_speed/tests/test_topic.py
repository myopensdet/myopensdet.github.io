# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Speed check guide: the script and the pytest template find both planted problems in
the practice API and pass on the fixed API. Short runs, all offline on a free local port."""

import importlib.util
import os
import re
import subprocess
import sys
import threading
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
KIT = TOPIC / "templates" / "speed_check"
ROOT = TOPIC.parents[2]
CREDIT = "Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/"

SKIP_FOLDERS = {"__pycache__", ".pytest_cache"}
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file()
    and not SKIP_FOLDERS & set(p.parts)
    and (p.suffix in {".py", ".ini", ".txt", ".md"} or p.name == ".gitignore")
)


def load(name):
    spec = importlib.util.spec_from_file_location(name, KIT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


practice_api = load("practice_api")
speed_check = load("speed_check")


@pytest.fixture(params=[False, True], ids=["with problems", "fixed"])
def api(request):
    server = practice_api.serve(port=0, fixed=request.param)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield request.param, f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    server.server_close()


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:3])


def test_pins_match_the_repo_lock_file():
    lock = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    for line in (KIT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        if "==" in line:
            assert re.search(rf"^{re.escape(line)} \\", lock, re.MULTILINE), line


def test_search_is_slow_only_with_the_problem(api):
    fixed, base = api
    result = speed_check.run(f"{base}/api/search?q=book", users=10, seconds=1.5)
    assert result.errors == 0
    assert (result.percentile(95) < 300) is fixed


def test_report_fails_under_load_only_with_the_problem(api):
    fixed, base = api
    result = speed_check.run(f"{base}/api/report", users=10, seconds=1)
    assert (result.statuses.get(503, 0) > 0) is not fixed
    assert repr(result).startswith("Result(")  # short, never the raw timings


def test_one_user_sees_no_problem(api):
    _, base = api
    result = speed_check.run(f"{base}/api/report", users=1, seconds=0.5)
    assert result.errors == 0


def test_the_script_exit_code_follows_the_targets(api):
    fixed, base = api
    url = f"{base}/api/search?q=book"
    command = [sys.executable, str(KIT / "speed_check.py"), url, "--users", "10",
               "--seconds", "1.5", "--max-p95", "300", "--max-errors", "1"]  # fmt: skip
    result = subprocess.run(command, capture_output=True, text=True, timeout=60)
    assert "(10 users, " in result.stdout
    assert result.returncode == (0 if fixed else 1), result.stdout
    assert ("TOO SLOW OR FAILING: p95" in result.stdout) is not fixed


def test_the_pytest_template_fails_on_both_problems(api):
    fixed, base = api
    env = {**os.environ, "BASE_URL": base, "SPEED_SECONDS": "1"}
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider"],
        cwd=KIT, env=env, capture_output=True, text=True, timeout=120,
    )  # fmt: skip
    expected = "3 passed" if fixed else "2 failed, 1 passed"
    assert expected in result.stdout, result.stdout[-2000:]


def test_practice_api_listens_on_this_computer_only():
    server = practice_api.serve(port=0)
    try:
        assert server.server_address[0] == "127.0.0.1"
    finally:
        server.server_close()
