# Template from myOpenSDET: https://myopensdet.github.io/
"""Python for testers: examples print what the pages say, exercises and starters work."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
ROOT = TOPIC.parents[2]
DOCS = ROOT / "docs" / "programming-for-testers"
TEMPLATES = TOPIC / "templates"
EXAMPLES = TOPIC / "examples"
CREDIT = "Template from myOpenSDET: https://myopensdet.github.io/"

# Each example script, and the page that shows its output.
PAGES = {
    "types_demo.py": "variables-and-data-types.md",
    "collections_demo.py": "lists-tuples-sets-and-dictionaries.md",
    "loops_demo.py": "conditions-and-loops.md",
    "functions_demo.py": "functions.md",
    "modules_demo.py": "modules-and-imports.md",
    "classes_demo.py": "object-oriented-programming.md",
    "errors_demo.py": "exception-handling.md",
    "files_demo.py": "file-handling.md",
    "json_demo.py": "json.md",
    "mystery.py": "reading-other-peoples-code.md",
}


def python(*args, cwd):
    return subprocess.run(
        [sys.executable, *args], cwd=cwd, capture_output=True, text=True, check=False
    )


def stripped(text: str) -> str:
    return "\n".join(line.strip() for line in text.splitlines())


@pytest.fixture
def examples(tmp_path):
    """A copy of the examples, so scripts that write files don't touch the repo."""
    folder = tmp_path / "examples"
    shutil.copytree(EXAMPLES, folder, ignore=shutil.ignore_patterns("__pycache__", "out"))
    return folder


FILES = sorted(
    p
    for folder in ("templates", "examples", "exercises", "solutions")
    for p in (TOPIC / folder).rglob("*")
    if p.suffix in {".py", ".csv", ".json", ".ini"}
    and "__pycache__" not in p.parts
    and "out" not in p.parts  # files the examples write when run by hand
)


@pytest.mark.parametrize("path", FILES, ids=lambda p: f"{p.parent.name}/{p.name}")
def test_every_file_has_the_credit_line(path):
    assert CREDIT in "\n".join(path.read_text(encoding="utf-8").splitlines()[:2])


@pytest.mark.parametrize(("script", "page"), PAGES.items())
def test_the_page_shows_the_real_output(examples, script, page):
    result = python(script, cwd=examples)
    assert result.returncode == 0, result.stderr
    assert stripped(result.stdout).strip() in stripped((DOCS / page).read_text(encoding="utf-8"))


def copy_exercise_tests(tmp_path, source):
    shutil.copytree(TOPIC / "exercises" / "tests", tmp_path / "tests")
    for path in (TOPIC / source).glob("ex*.py"):
        shutil.copy(path, tmp_path)
    shutil.copy(TOPIC / "exercises" / "pytest.ini", tmp_path)


def test_every_solution_passes_the_exercise_tests(tmp_path):
    copy_exercise_tests(tmp_path, "solutions")
    result = python("-m", "pytest", "-q", "-p", "no:cacheprovider", cwd=tmp_path)
    assert result.returncode == 0, result.stdout
    summary = result.stdout.strip().splitlines()[-1]
    assert " passed" in summary and "failed" not in summary


def test_the_solutions_folder_runs_on_its_own():
    result = python("-m", "pytest", "-q", "-p", "no:cacheprovider", cwd=TOPIC / "solutions")
    assert result.returncode == 0, result.stdout


def test_the_exercises_start_empty(tmp_path):
    copy_exercise_tests(tmp_path, "exercises")
    result = python("-m", "pytest", "-q", "-p", "no:cacheprovider", cwd=tmp_path)
    summary = result.stdout.strip().splitlines()[-1]
    assert " failed" in summary and "passed" not in summary
    assert "NotImplementedError: Write your code here" in result.stdout


# Starter scripts


def test_run_summary(examples):
    result = python(str(TEMPLATES / "run_summary.py"), "nightly_results.json", cwd=examples)
    assert result.returncode == 1
    assert "12 tests: 2 failed, 9 passed, 1 skipped (75.0% passed)" in result.stdout
    assert stripped(result.stdout).strip() in stripped((DOCS / "index.md").read_text())


def test_run_summary_explains_a_wrong_file(examples):
    (examples / "wrong.json").write_text('{"results": []}', encoding="utf-8")
    result = python(str(TEMPLATES / "run_summary.py"), "wrong.json", cwd=examples)
    assert result.returncode == 2
    assert result.stdout.strip() == 'Can\'t read the results: wrong.json has no "tests" list'


def test_compare_json(examples):
    result = python(
        str(TEMPLATES / "compare_json.py"),
        "expected_product.json",
        "actual_product.json",
        cwd=examples,
    )
    assert result.returncode == 1
    assert result.stdout.splitlines() == [
        '$.price: expected 4.25, got "4.25"',
        "$.tags: expected 2 items, got 1",
        '$.created_at: not expected, got "2026-11-16T09:30:00Z"',
        "3 difference(s).",
    ]


def test_compare_json_ignores_keys(examples):
    result = python(
        str(TEMPLATES / "compare_json.py"),
        "expected_product.json",
        "actual_product.json",
        "--ignore",
        "created_at,tags",
        cwd=examples,
    )
    assert result.stdout.splitlines() == ['$.price: expected 4.25, got "4.25"', "1 difference(s)."]


def test_compare_json_same_file_matches(examples):
    result = python(
        str(TEMPLATES / "compare_json.py"),
        "expected_product.json",
        "expected_product.json",
        cwd=examples,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "They match."


def test_script_starter(examples):
    result = python(str(TEMPLATES / "script_starter.py"), "users.csv", "--verbose", cwd=examples)
    assert result.returncode == 0
    assert result.stdout.splitlines() == ["Read 5 lines from users.csv", "5 lines"]
    missing = python(str(TEMPLATES / "script_starter.py"), "nope.txt", cwd=examples)
    assert missing.returncode == 2
