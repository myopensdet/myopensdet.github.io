# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""The templates of "Test design techniques" work, and the lessons' claims stay true."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
TEMPLATES = TOPIC / "templates"
EXAMPLES = TOPIC / "examples"
CREDIT = "Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/"


def run(*args, cwd=EXAMPLES):
    return subprocess.run(
        [sys.executable, *args], cwd=cwd, capture_output=True, text=True, check=False
    )


def pytest_in(folder, *args):
    return run("-m", "pytest", "-q", "-p", "no:cacheprovider", *args, cwd=folder)


@pytest.mark.parametrize(
    "path",
    sorted(p for p in [*TEMPLATES.iterdir(), *EXAMPLES.rglob("*")] if p.suffix in {".py", ".md"}),
    ids=lambda p: p.name,
)
def test_every_file_starts_with_the_credit_line(path):
    assert CREDIT in path.read_text(encoding="utf-8").splitlines()[0]


def test_the_example_uses_the_boundaries_template_unchanged():
    assert (EXAMPLES / "boundaries.py").read_text() == (TEMPLATES / "boundaries.py").read_text()


def test_the_example_suite_passes():
    result = pytest_in(EXAMPLES)
    assert result.returncode == 0, result.stdout
    assert "56 passed" in result.stdout


def test_boundaries_lists_both_sides_of_each_edge():
    result = run(str(TEMPLATES / "boundaries.py"), "18", "120")
    assert result.returncode == 0
    lines = [line.split() for line in result.stdout.splitlines()[1:]]
    assert lines == [["17", "outside"], ["18", "inside"], ["120", "inside"], ["121", "outside"]]


def test_boundaries_three_adds_the_values_just_inside():
    sys.path.insert(0, str(TEMPLATES))
    try:
        from boundaries import boundary_values
    finally:
        sys.path.pop(0)
    assert [v for v, _ in boundary_values(3, 20, three=True)] == [2, 3, 4, 19, 20, 21]
    assert [v for v, _ in boundary_values(5, 6, three=True)] == [4, 5, 6, 7]
    with pytest.raises(ValueError, match="must not be bigger"):
        boundary_values(10, 1)


def test_boundaries_without_numbers_shows_usage():
    result = run(str(TEMPLATES / "boundaries.py"))
    assert result.returncode == 2
    assert "Usage" in result.stdout


def test_decision_table_prints_every_combination():
    result = run(str(TEMPLATES / "decision_table.py"), "Member", "Order $50 or more", "Express")
    assert result.returncode == 0
    lines = result.stdout.splitlines()
    assert lines[0] == "| # | Member | Order $50 or more | Express | Result |"
    assert len(lines) == 2 + 8
    assert lines[2] == "| 1 | Yes | Yes | Yes |  |"
    assert lines[-1] == "| 8 | No | No | No |  |"


def test_decision_table_warns_when_it_gets_too_big():
    result = run(str(TEMPLATES / "decision_table.py"), *[f"C{n}" for n in range(7)])
    assert "Warning: 128 rows" in result.stdout


@pytest.mark.parametrize(
    ("file", "old", "new", "caught_by", "missed_by"),
    [
        # Boundary values catch an off-by-one that equivalence partitioning misses.
        (
            "shop/signup.py",
            "if not MIN_AGE <= age <= MAX_AGE:",
            "if not MIN_AGE < age <= MAX_AGE:",
            "tests/test_signup_edges.py",
            "tests/test_signup_groups.py",
        ),
        # The decision table catches a forgotten condition.
        (
            "shop/delivery.py",
            "if member or subtotal_cents >= FREE_FROM:",
            "if subtotal_cents >= FREE_FROM:",
            "tests/test_delivery_table.py",
            None,
        ),
        # The state tests catch a move the rules don't allow.
        (
            "shop/order_status.py",
            '    ("shipped", "deliver"): "delivered",\n',
            '    ("shipped", "deliver"): "delivered",\n    ("shipped", "cancel"): "refunded",\n',
            "tests/test_order_states.py",
            None,
        ),
    ],
    ids=["off-by-one age", "forgotten member rule", "cancel after shipping"],
)
def test_the_tests_catch_the_bugs_shown_in_the_lessons(
    tmp_path, file, old, new, caught_by, missed_by
):
    copy = tmp_path / "examples"
    shutil.copytree(EXAMPLES, copy, ignore=shutil.ignore_patterns("__pycache__"))
    code = (copy / file).read_text()
    assert old in code
    (copy / file).write_text(code.replace(old, new))
    caught = pytest_in(copy, caught_by)
    assert caught.returncode == 1, caught.stdout
    assert "1 failed" in caught.stdout
    if missed_by:
        assert pytest_in(copy, missed_by).returncode == 0


@pytest.mark.parametrize(
    ("name", "sections"),
    [
        ("partitions_and_boundaries_worksheet.md", ["## Groups", "## Edges", "## Questions"]),
        ("decision_table_worksheet.md", ["## The table", "## Check the table"]),
        ("state_transition_worksheet.md", ["## The state table", "## Tests to write"]),
        ("error_guessing_checklist.md", ["## Text", "## Actions", "## Our team's past bugs"]),
        ("exploratory_charter.md", ["## Charter", "## Notes", "## Found", "## Wrap-up"]),
        ("web_form_checklist.md", ["## Fields", "## Errors", "## Sending", "## Safety"]),
        ("api_endpoint_checklist.md", ["## Bad input", "## Who can do it"]),
    ],
)
def test_worksheets_have_their_sections(name, sections):
    text = (TEMPLATES / name).read_text(encoding="utf-8")
    for section in sections:
        assert section in text


def load_pairwise():
    sys.path.insert(0, str(TEMPLATES))
    try:
        import pairwise
    finally:
        sys.path.pop(0)
    return pairwise


@pytest.mark.parametrize(
    "settings",
    [
        {"Browser": ["Chrome", "Firefox", "Safari"], "Device": ["Desktop", "Phone"]},
        {
            "Browser": ["Chrome", "Firefox", "Safari"],
            "Device": ["Desktop", "Phone"],
            "Payment": ["Card", "PayPal", "Gift card"],
            "Language": ["English", "Bengali"],
        },
        {f"S{n}": ["a", "b", "c"] for n in range(6)},
    ],
    ids=["two settings", "checkout", "six settings"],
)
def test_pairwise_covers_every_pair_with_fewer_rows(settings):
    pairwise = load_pairwise()
    rows = pairwise.pairwise(settings)
    covered = set().union(*(pairwise.pairs_in(row) for row in rows))
    assert covered == pairwise.all_pairs(settings)
    every = 1
    for values in settings.values():
        every *= len(values)
    assert len(rows) <= every


def test_pairwise_prints_the_checkout_table():
    result = run(
        str(TEMPLATES / "pairwise.py"),
        "Browser=Chrome,Firefox,Safari",
        "Device=Desktop,Phone",
        "Payment=Card,PayPal,Gift card",
        "Language=English,Bengali",
    )
    assert result.returncode == 0
    assert result.stdout.splitlines()[0] == "| # | Browser | Device | Payment | Language |"
    assert "9 tests cover every pair. Every combination would be 36 tests." in result.stdout


def test_pairwise_explains_a_bad_setting():
    pairwise = load_pairwise()
    with pytest.raises(ValueError, match="Expected NAME=value,value"):
        pairwise.parse(["Browser"])
    assert run(str(TEMPLATES / "pairwise.py")).returncode == 2


def test_the_guesses_probe_shows_the_two_open_questions():
    result = run("try_guesses.py")
    assert result.returncode == 0
    lines = {line[:32].strip(): line[32:].strip() for line in result.stdout.splitlines()}
    assert lines["an accent"] == "accepted"
    assert lines["a Bengali name"] == "Username can only use letters and numbers"
    assert lines["wide letters (look like admin)"] == "accepted"
    assert lines["emoji"] == "Username can only use letters and numbers"


DEMO = EXAMPLES / "coverage_demo"
NOT_A_MEMBER_TEST = """


def test_a_customer_who_is_not_a_member():
    assert points_for(3000, member=False, first_order=False) == 30
"""


def coverage_report(folder, *run_options, report_options=()):
    run(
        "-m",
        "coverage",
        "run",
        *run_options,
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        cwd=folder,
    )
    return run("-m", "coverage", "report", "-m", "--include=points.py", *report_options, cwd=folder)


def copy_demo(tmp_path):
    demo = tmp_path / "demo"
    shutil.copytree(DEMO, demo, ignore=shutil.ignore_patterns("__pycache__", ".coverage"))
    return demo


def test_the_coverage_template_turns_on_branches():
    text = (TEMPLATES / ".coveragerc").read_text()
    assert text.splitlines()[0] == f"# {CREDIT}"
    assert "branch = True" in text
    assert "show_missing = True" in text


def test_coverage_lesson_lines_say_100_but_branches_find_the_gap(tmp_path):
    demo = copy_demo(tmp_path)
    assert "points.py       6      0   100%" in coverage_report(demo).stdout

    branches = coverage_report(demo, "--branch")
    assert branches.returncode == 0, branches.stdout
    assert "points.py       6      0      4      2    80%   10->12, 12->14" in branches.stdout

    strict = coverage_report(demo, "--branch", report_options=["--fail-under=90"])
    assert strict.returncode == 2
    assert "Coverage failure: total of 80 is less than fail-under=90" in strict.stdout


def test_coverage_lesson_the_missing_branch_hides_a_crash_and_the_fix_works(tmp_path):
    demo = copy_demo(tmp_path)
    tests = demo / "test_points.py"
    tests.write_text(tests.read_text() + NOT_A_MEMBER_TEST)

    crash = pytest_in(demo)
    assert "UnboundLocalError" in crash.stdout
    assert "1 failed, 1 passed" in crash.stdout

    code = demo / "points.py"
    old = "    if member:\n        points = order_cents // 100 * 2\n"
    new = "    points = order_cents // 100\n    if member:\n        points *= 2\n"
    assert old in code.read_text()
    code.write_text(code.read_text().replace(old, new))
    fixed = coverage_report(demo, "--branch")
    assert "points.py       7      0      4      0   100%" in fixed.stdout
