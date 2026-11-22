# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Linux and shell: the practice logs are the same on every computer, and the summary
script prints what the page shows. Needs bash (macOS, Linux, WSL or Git Bash)."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
KIT = TOPIC / "templates" / "shell_kit"
CREDIT = "Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/"
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file()
    and "__pycache__" not in p.parts
    and "logs" not in p.parts
    and (p.suffix in {".py", ".sh", ".md"} or p.name == ".gitignore")
)
BASH = shutil.which("bash") or "bash"
needs_bash = pytest.mark.skipif(shutil.which("bash") is None, reason="needs bash")


@pytest.fixture
def logs(tmp_path):
    subprocess.run([sys.executable, str(KIT / "make_practice_logs.py")], cwd=tmp_path, check=True)
    return tmp_path / "logs"


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:3])


def test_practice_logs_are_the_same_every_time(logs):
    app = (logs / "app.log").read_text(encoding="utf-8").splitlines()
    assert len(app) == 400
    assert sum(" ERROR " in line for line in app) == 19
    assert app[333].endswith("error=KeyError:'discount_code'")
    assert len((logs / "worker.log").read_text(encoding="utf-8").splitlines()) == 18
    assert all(line[19] == "Z" for line in app), "times must be UTC, never local time"


@needs_bash
def test_summary_shows_levels_errors_and_slowest(logs):
    out = subprocess.run(
        [BASH, str(KIT / "log_summary.sh"), str(logs / "app.log")],
        capture_output=True, text=True, check=True,
    ).stdout  # fmt: skip
    squeezed = [" ".join(line.split()) for line in out.splitlines()]
    for expected in ["331 INFO", "50 WARN", "19 ERROR", "21 error=WrongPassword",
                     "18 error=PaymentTimeout", "4169 req-01247 /api/search"]:  # fmt: skip
        assert expected in squeezed, expected


@needs_bash
def test_summary_explains_how_to_use_it():
    result = subprocess.run([BASH, str(KIT / "log_summary.sh")], capture_output=True, text=True)
    assert result.returncode != 0
    assert "Usage: ./log_summary.sh <log file>" in result.stderr


@needs_bash
def test_script_has_no_syntax_errors():
    subprocess.run([BASH, "-n", str(KIT / "log_summary.sh")], check=True)
