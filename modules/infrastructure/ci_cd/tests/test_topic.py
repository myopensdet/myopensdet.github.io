# Template from myOpenSDET: https://myopensdet.github.io/
"""CI/CD: the workflow template is safe and complete, the kit's tests run like the
pipeline runs them, and ci_summary.py reports passes and failures. With ZTS_DOCKER=1,
actionlint checks the workflow too."""

import os
import re
import shutil
import subprocess
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
import yaml

TOPIC = Path(__file__).resolve().parents[1]
KIT = TOPIC / "templates" / "ci_kit"
WORKFLOW = KIT / "github_workflows" / "tests.yml"
REPORT = "reports/junit.xml"
DOCKER = shutil.which("docker") or "docker"
CREDIT = "Template from myOpenSDET: https://myopensdet.github.io/"
SUFFIXES = {".py", ".md", ".txt", ".yml", ".ini"}
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file() and "__pycache__" not in p.parts and p.suffix in SUFFIXES
)


@pytest.fixture(scope="module")
def workflow():
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


@pytest.fixture
def site(tmp_path):
    (tmp_path / "index.html").write_text("<h1>Shop</h1>", encoding="utf-8")
    (tmp_path / "health").write_text("ok", encoding="utf-8")

    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Quiet, directory=str(tmp_path)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield tmp_path, f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    server.server_close()


def run_kit(tmp_path, env):
    work = tmp_path / "kit"
    shutil.copytree(KIT, work)
    tests = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-q", f"--junitxml={REPORT}"],
        capture_output=True, text=True, timeout=60, cwd=work, env={**os.environ, **env},
    )  # fmt: skip
    summary = subprocess.run(
        [sys.executable, "ci_summary.py", REPORT],
        capture_output=True, text=True, timeout=30, cwd=work,
    )  # fmt: skip
    return tests, summary


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:3])


def test_workflow_runs_on_the_right_events(workflow):
    events = workflow[True]  # YAML reads the key "on" as True
    assert {"pull_request", "push", "schedule", "workflow_dispatch"} <= set(events)


def test_workflow_asks_for_read_only_rights(workflow):
    assert workflow["permissions"] == {"contents": "read"}


def test_every_action_is_pinned_to_a_full_sha():
    for line in WORKFLOW.read_text(encoding="utf-8").splitlines():
        if "uses:" in line:
            assert re.search(r"@[0-9a-f]{40} # v\d", line), line


def test_job_has_a_time_limit_and_keeps_the_report(workflow):
    job = workflow["jobs"]["tests"]
    assert job["timeout-minutes"] <= 30
    keep = [s for s in job["steps"] if "upload-artifact" in s.get("uses", "")]
    assert keep and keep[0]["if"] == "always()"


def test_secrets_come_from_settings_not_the_file(workflow):
    env = workflow["jobs"]["tests"]["env"]
    assert env["API_AUTH"] == "${{ secrets.API_AUTH }}"
    assert env["BASE_URL"] == "${{ vars.BASE_URL }}"


def test_kit_passes_and_summary_says_so(tmp_path, site):
    _, base = site
    tests, summary = run_kit(tmp_path, {"BASE_URL": base})
    assert "3 passed" in tests.stdout, tests.stdout
    assert "**3 passed, 0 failed, 0 skipped**" in summary.stdout


def test_missing_page_fails_and_summary_names_it(tmp_path, site):
    folder, base = site
    (folder / "health").unlink()
    tests, summary = run_kit(tmp_path, {"BASE_URL": base})
    assert tests.returncode == 1
    assert "**2 passed, 1 failed, 0 skipped**" in summary.stdout
    assert (
        "| `test_page_answers[/health]` | failure | AssertionError: /health gave 404 |"
        in summary.stdout
    )


def test_missing_base_url_is_a_clear_error(tmp_path):
    tests, _ = run_kit(tmp_path, {"BASE_URL": ""})
    assert "BASE_URL is not set" in tests.stdout
    assert "3 error" in tests.stdout


def test_summary_without_a_report_says_why(tmp_path):
    result = subprocess.run(
        [sys.executable, str(KIT / "ci_summary.py"), "nothere/junit.xml"],
        capture_output=True, text=True, timeout=30, cwd=tmp_path,
    )  # fmt: skip
    assert result.returncode == 1
    assert "did the tests run at all?" in result.stderr


@pytest.mark.skipif(os.environ.get("ZTS_DOCKER") != "1", reason="set ZTS_DOCKER=1")
def test_actionlint_finds_no_problems(tmp_path):
    folder = tmp_path / ".github" / "workflows"
    folder.mkdir(parents=True)
    shutil.copy(WORKFLOW, folder / "tests.yml")
    result = subprocess.run(
        [DOCKER, "run", "--rm", "-v", f"{tmp_path}:/repo", "-w", "/repo",
         "rhysd/actionlint:1.7.12", "-no-color", ".github/workflows/tests.yml"],
        capture_output=True, text=True, timeout=300,
    )  # fmt: skip
    assert result.returncode == 0, result.stdout
