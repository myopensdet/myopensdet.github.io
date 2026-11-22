# Template from myOpenSDET: https://myopensdet.github.io/
"""Upload and import guide: the template finds exactly the three planted bugs in the
practice API, passes on the fixed API, and writes no files. All offline, on a free port."""

import importlib.util
import os
import re
import subprocess
import sys
import threading
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
KIT = TOPIC / "templates" / "upload_tests"
ROOT = TOPIC.parents[2]
CREDIT = "Template from myOpenSDET: https://myopensdet.github.io/"
EXPECTED_FAILS = {
    "tests/test_import.py::test_bad_row_rejects_the_whole_file_and_names_the_row",
    "tests/test_upload.py::test_file_one_byte_over_the_limit_is_refused",
    "tests/test_upload.py::test_file_with_a_false_name_is_refused",
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
    server.server_close()


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
    before = {p for p in KIT.rglob("*") if "__pycache__" not in p.parts}
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider"],
        cwd=KIT, env={**os.environ, "BASE_URL": base_url},
        capture_output=True, text=True, timeout=120,
    )  # fmt: skip
    failed = {
        line.removeprefix("FAILED ").split(" - ")[0]
        for line in result.stdout.splitlines()
        if line.startswith("FAILED")
    }
    if fixed:
        assert "16 passed" in result.stdout, result.stdout[-3000:]
    else:
        assert failed == EXPECTED_FAILS, result.stdout[-3000:]
        assert "3 failed, 13 passed" in result.stdout
    after = {p for p in KIT.rglob("*") if "__pycache__" not in p.parts}
    assert after == before, "the tests or the API wrote files"


def test_practice_api_listens_on_this_computer_only():
    server = practice_api.serve(port=0)
    try:
        assert server.server_address[0] == "127.0.0.1"
    finally:
        server.server_close()
