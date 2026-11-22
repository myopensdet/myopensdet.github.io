# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Git in a team: git_practice.sh builds the practice server and copies, and the page's
flow (branch, push, colleague's change, rebase conflict, resolve, force-with-lease)
behaves exactly as shown."""

import shutil
import subprocess
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
KIT = TOPIC / "templates" / "git_kit"
CREDIT = "Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/"
BASH = shutil.which("bash") or "bash"
GIT = shutil.which("git") or "git"
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file() and "__pycache__" not in p.parts and p.suffix in {".py", ".md", ".txt", ".sh"}
)

pytestmark = pytest.mark.skipif(not shutil.which("git"), reason="needs git")


def practice(*args, cwd):
    return subprocess.run(
        [BASH, str(KIT / "git_practice.sh"), *args],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=cwd,
    )


def git(*args, cwd):
    return subprocess.run(
        [GIT, *args], capture_output=True, text=True, timeout=60, cwd=cwd,
        env={"GIT_EDITOR": "true", "PATH": "/usr/bin:/bin", "HOME": str(cwd)},
    )  # fmt: skip


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:3])


def test_usage_and_double_setup(tmp_path):
    assert practice(cwd=tmp_path).returncode == 2
    assert practice("setup", cwd=tmp_path).stdout.startswith("Ready: git-practice/me")
    again = practice("setup", cwd=tmp_path)
    assert again.returncode == 1
    assert "git-practice already exists" in again.stderr


def test_the_page_flow(tmp_path):
    practice("setup", cwd=tmp_path)
    me = tmp_path / "git-practice" / "me"
    assert git("config", "user.email", cwd=me).stdout.strip() == "arshad@example.com"
    assert git("remote", "get-url", "origin", cwd=me).stdout.strip() == "../server.git"

    git("switch", "-c", "test/login-lockout", cwd=me)
    conftest = me / "conftest.py"
    conftest.write_text(conftest.read_text().replace("TIMEOUT = 10", "TIMEOUT = 15"))
    tests = me / "tests" / "test_login.py"
    tests.write_text(tests.read_text() + "\n\ndef test_account_locks():\n    assert True\n")
    git("commit", "-q", "-am", "Add the account lockout test", cwd=me)
    assert git("push", "-u", "origin", "test/login-lockout", cwd=me).returncode == 0

    assert "pushed a change to conftest.py" in practice("colleague", cwd=tmp_path).stdout
    git("fetch", "origin", cwd=me)
    rebase = git("rebase", "origin/main", cwd=me)
    assert rebase.returncode == 1
    assert "CONFLICT (content): Merge conflict in conftest.py" in rebase.stdout
    text = conftest.read_text()
    assert (
        "<<<<<<< HEAD\nTIMEOUT = 30  # the staging server is slow\n=======\nTIMEOUT = 15\n" in text
    )

    conftest.write_text(text.split("<<<<<<<")[0] + "TIMEOUT = 30  # the staging server is slow\n")
    git("add", "conftest.py", cwd=me)
    assert git("rebase", "--continue", cwd=me).returncode == 0
    plain = git("push", cwd=me)
    assert plain.returncode == 1 and "(non-fast-forward)" in plain.stderr
    forced = git("push", "--force-with-lease", cwd=me)
    assert "(forced update)" in forced.stderr
    log = git("log", "--oneline", "--format=%s", cwd=me).stdout.splitlines()
    assert log == [
        "Add the account lockout test",
        "Raise the timeout for staging",
        "Start the test project",
    ]


def test_reset_deletes_only_the_practice_folder(tmp_path):
    (tmp_path / "keep.txt").write_text("mine")
    practice("setup", cwd=tmp_path)
    assert practice("reset", cwd=tmp_path).stdout.strip() == "Deleted git-practice/"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["keep.txt"]
