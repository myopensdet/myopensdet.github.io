# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""The templates of "Test strategy and planning" work, and the lessons' outputs stay true."""

import subprocess
import sys
from pathlib import Path

import pytest

TOPIC = Path(__file__).resolve().parents[1]
TEMPLATES = TOPIC / "templates"
EXAMPLES = TOPIC / "examples"
CREDIT = "Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/"


def run(script, *args, cwd=EXAMPLES):
    return subprocess.run(
        [sys.executable, str(TEMPLATES / script), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    "path",
    sorted(
        p
        for p in [*TEMPLATES.iterdir(), *EXAMPLES.iterdir()]
        if p.suffix in {".py", ".md", ".csv", ".toml"}
    ),
    ids=lambda p: p.name,
)
def test_every_file_starts_with_the_credit_line(path):
    assert CREDIT in path.read_text(encoding="utf-8").splitlines()[0]


# risk_score.py


def test_refund_risks_are_sorted_highest_first():
    result = run("risk_score.py", "refund_risks.csv")
    assert result.returncode == 0
    lines = result.stdout.splitlines()
    assert lines[2] == "| 6 | deep | Money | The same item is refunded twice (REF-2) |"
    assert lines[-3].startswith("| 1 | light | Page | The Cancel order link")
    assert lines[-1] == "3 deep, 3 normal, 2 light. Test the deep ones first."


def test_the_example_plan_shows_the_real_risk_table():
    table = run("risk_score.py", "refund_risks.csv").stdout.split("\n\n")[0]
    plan = (EXAMPLES / "refund_test_plan.md").read_text(encoding="utf-8")
    assert table in plan


@pytest.mark.parametrize(
    ("score", "depth"),
    [(9, "deep"), (6, "deep"), (4, "normal"), (3, "normal"), (2, "light"), (1, "light")],
)
def test_depth_limits(score, depth):
    sys.path.insert(0, str(TEMPLATES))
    import risk_score

    assert risk_score.depth(score) == depth


def test_a_word_instead_of_a_number_is_explained(tmp_path):
    risks = tmp_path / "risks.csv"
    risks.write_text("Area,Risk,Likelihood,Impact\nMoney,Paid twice,high,3\n", encoding="utf-8")
    result = run("risk_score.py", str(risks))
    assert result.returncode == 2
    assert result.stdout.strip() == "Row 1: Likelihood must be 1, 2 or 3, got 'high'"


def test_the_empty_template_is_refused():
    result = run("risk_score.py", str(TEMPLATES / "risks.csv"))
    assert result.returncode == 2
    assert "Likelihood must be 1, 2 or 3" in result.stdout


# exit_check.py


def test_refund_results_miss_one_criterion():
    result = run("exit_check.py", "refund_exit_criteria.toml", "refund_results.toml")
    assert result.returncode == 1
    assert "NOT MET  open_major_bugs: 1 (at most 0)" in result.stdout
    assert result.stdout.count("met      ") == 4
    assert "1 exit criterion not met." in result.stdout


def test_all_met_passes(tmp_path):
    results = tmp_path / "results.toml"
    text = (EXAMPLES / "refund_results.toml").read_text(encoding="utf-8")
    results.write_text(text.replace("open_major_bugs = 1", "open_major_bugs = 0"), encoding="utf-8")
    result = run("exit_check.py", "refund_exit_criteria.toml", str(results))
    assert result.returncode == 0
    assert result.stdout.strip().endswith(
        "All exit criteria met. Write the test summary and share it."
    )


def test_a_missing_result_is_not_met(tmp_path):
    results = tmp_path / "results.toml"
    results.write_text("failed_tests = 0\n", encoding="utf-8")
    result = run("exit_check.py", "refund_exit_criteria.toml", str(results))
    assert result.returncode == 1
    assert "MISSING  open_critical_bugs: no result (at most 0)" in result.stdout
    assert "4 exit criteria not met." in result.stdout


def test_the_example_criteria_are_the_template():
    assert (EXAMPLES / "refund_exit_criteria.toml").read_text() == (
        TEMPLATES / "exit_criteria.toml"
    ).read_text()


# automation_roi.py


def roi(*numbers):
    names = ["--manual-minutes", "--runs-per-month", "--build-hours", "--upkeep-hours"]
    args = [part for pair in zip(names, map(str, numbers), strict=True) for part in pair]
    return run("automation_roi.py", *args).stdout


def test_regression_check_pays_back_in_two_months():
    out = roi(30, 20, 16, 2)
    assert "Net saving per month:          8.0 hours" in out
    assert "Pays back after:               2.0 months" in out
    assert out.strip().endswith("Pays back fast. Worth automating, if the checklist agrees.")


def test_rare_check_never_pays_back():
    out = roi(5, 2, 6, 1)
    assert "Pays back after" not in out
    assert "Never pays back on time alone" in out


def test_slow_payback_says_keep_it_manual():
    out = roi(20, 2, 24, 0.5)
    assert "Pays back after:             144.0 months" in out
    assert "Probably keep it manual, or test it at a lower level." in out
