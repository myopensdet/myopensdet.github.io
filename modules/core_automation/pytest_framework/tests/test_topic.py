# Template from myOpenSDET: https://myopensdet.github.io/
"""pytest framework: the example project, the demos and the skeleton work as the pages say."""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
ROOT = TOPIC.parents[2]
DOCS = ROOT / "docs" / "automation-testing" / "pytest"
EXAMPLES = TOPIC / "examples"
PROJECT = EXAMPLES / "shop_project"
SKELETON = TOPIC / "templates" / "pytest_skeleton"
CREDIT = "Template from myOpenSDET: https://myopensdet.github.io/"


def pytest_run(*args, cwd=PROJECT, extra_env=None):
    """Run pytest the way a reader would: only pytest, no other plugins."""
    env = {**os.environ, "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    env.pop("TEST_ENV", None)
    env.update(extra_env or {})
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def normal(text: str) -> str:
    """Strip indentation, and the run time, which changes every run."""
    text = re.sub(r"in \d+\.\d+s", "in N.NNs", text)
    return "\n".join(line.strip() for line in text.splitlines()).strip()


def assert_on_page(page: str, output: str):
    assert normal(output) in normal((DOCS / page).read_text(encoding="utf-8"))


SKIP_FOLDERS = {"__pycache__", ".pytest_cache"}
FILES = sorted(
    p
    for p in TOPIC.rglob("*")
    if p.is_file()
    and not SKIP_FOLDERS & set(p.parts)
    and (p.suffix in {".py", ".ini", ".toml", ".txt", ".md"} or p.name == ".gitignore")
)


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(TOPIC)))
def test_every_file_has_the_credit_line(path):
    assert CREDIT in path.read_text(encoding="utf-8").splitlines()[0]


def test_default_run_leaves_out_api_tests():
    result = pytest_run()
    assert result.returncode == 0
    assert "63 passed, 1 deselected" in result.stdout


def test_verbose_cart_run_is_on_the_page():
    result = pytest_run("-v", "tests/test_cart.py")
    shown = result.stdout[result.stdout.index("tests/test_cart.py::") :]
    assert_on_page("tests-and-asserts.md", shown)


def test_setup_show_is_on_the_page():
    result = pytest_run(
        "-q", "--setup-show", "tests/test_cart.py::test_saved_order_is_in_the_store"
    )
    assert_on_page("fixtures-and-conftest.md", result.stdout)


def test_parametrize_ids_are_on_the_page():
    result = pytest_run("-v", "tests/test_coupons.py", "-m", "not nightly")
    assert "8 passed, 50 deselected" in result.stdout
    shown = result.stdout[result.stdout.index("tests/test_coupons.py::") :]
    assert_on_page("parametrize.md", shown)


def test_smoke_run_is_on_the_page():
    result = pytest_run("-m", "smoke", "-v")
    assert "2 passed, 62 deselected" in result.stdout
    shown = result.stdout[result.stdout.index("tests/test_cart.py::") :]
    assert_on_page("markers.md", shown)


def test_collect_only_count_is_on_the_page():
    result = pytest_run("--co", "-q")
    assert "63/64 tests collected (1 deselected)" in result.stdout
    assert_on_page("pytest-ini.md", result.stdout.strip().splitlines()[-1])


def test_environment_header():
    result = pytest_run("--env", "staging", "-m", "smoke")
    assert "environment: staging (https://staging.example.com)" in result.stdout


def test_unknown_environment_is_a_usage_error():
    result = pytest_run("--env", "prod")
    assert result.returncode == 4
    assert "ERROR: Unknown environment 'prod'. Choose one of: local, staging" in result.stderr


def test_env_variable_chooses_the_environment():
    result = pytest_run("-m", "smoke", extra_env={"TEST_ENV": "staging"})
    assert "environment: staging" in result.stdout


def test_api_test_skips_when_there_is_no_server(tmp_path):
    project = tmp_path / "shop_project"
    shutil.copytree(PROJECT, project, ignore=shutil.ignore_patterns("__pycache__"))
    config = project / "config" / "environments.toml"
    # Port 9 on this computer: nothing listens there, so the connection is refused.
    config.write_text(
        config.read_text().replace("http://127.0.0.1:8080", "http://127.0.0.1:9"), encoding="utf-8"
    )
    result = pytest_run("-m", "api", cwd=project)
    assert result.returncode == 0
    assert "1 skipped, 63 deselected" in result.stdout
    assert "no server at http://127.0.0.1:9" in result.stdout


def test_failures_on_purpose():
    result = pytest_run(cwd=EXAMPLES / "assert_demo")
    assert result.returncode == 1
    assert "E       assert 1000 == 1100" in result.stdout
    assert "E         {'price': 450} != {'price': 425}" in result.stdout
    shown = result.stdout[
        result.stdout.index("    def test_total_is_wrong") : result.stdout.index(
            "test_failures_on_purpose.py:7"
        )
    ]
    assert_on_page("tests-and-asserts.md", shown)


def test_marker_typo_is_an_error():
    result = pytest_run(cwd=EXAMPLES / "typo_demo")
    assert result.returncode == 2
    assert "'smok' not found in `markers` configuration option" in result.stdout


def test_skeleton_runs_as_copied(tmp_path):
    copy = tmp_path / "my_tests"
    shutil.copytree(SKELETON, copy)
    result = pytest_run(cwd=copy)
    assert result.returncode == 0
    assert "3 passed, 1 deselected" in result.stdout


def test_skeleton_api_test_skips_without_a_token(tmp_path):
    copy = tmp_path / "my_tests"
    shutil.copytree(SKELETON, copy)
    result = pytest_run("-m", "", cwd=copy)
    assert "SKIPPED [1] tests/test_example.py:17: set APP_LOCAL_TOKEN to run tests" in result.stdout
    with_token = pytest_run(
        "-m", "api", "--env", "staging", cwd=copy, extra_env={"APP_STAGING_TOKEN": "fake-token"}
    )
    assert "1 passed, 3 deselected" in with_token.stdout


def test_skeleton_conftest_matches_the_example():
    """The skeleton's conftest is the example's, without the shop fixtures."""
    example = (PROJECT / "tests" / "conftest.py").read_text()
    skeleton = (SKELETON / "tests" / "conftest.py").read_text()
    assert example.startswith(
        skeleton.replace("import pytest\n", "import pytest\nfrom shop.cart import Cart\n")
    )
