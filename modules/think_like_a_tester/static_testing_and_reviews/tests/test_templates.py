# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""The templates of "Static testing and reviews" work, and the lessons' outputs stay true."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

TOPIC = Path(__file__).resolve().parents[1]
TEMPLATES = TOPIC / "templates"
EXAMPLES = TOPIC / "examples"
STATIC = EXAMPLES / "static_analysis"
CREDIT = "Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/"
RUFF = Path(sys.executable).with_name("ruff")


def run(*args, cwd=EXAMPLES, stdin=None):
    return subprocess.run(
        [*args], cwd=cwd, input=stdin, capture_output=True, text=True, check=False
    )


def scan(*args, stdin=None):
    return run(sys.executable, str(TEMPLATES / "ambiguity_scan.py"), *args, stdin=stdin)


@pytest.mark.parametrize(
    "path",
    sorted(
        p
        for p in [*TEMPLATES.iterdir(), *EXAMPLES.rglob("*")]
        if p.suffix in {".py", ".md", ".toml", ".yaml"}
    ),
    ids=lambda p: p.name,
)
def test_every_file_starts_with_the_credit_line(path):
    assert CREDIT in path.read_text(encoding="utf-8").splitlines()[0]


def test_the_scan_finds_the_seven_vague_words_in_the_story():
    result = scan("story_refund_request.md")
    assert result.returncode == 1
    words = [line.split('"')[1] for line in result.stdout.splitlines() if line.startswith("line")]
    assert words == ["quickly", "recent", "should", "fast", "may", "etc", "properly"]
    assert "7 vague words found" in result.stdout


def test_the_reviewed_story_has_only_one_flag_and_it_is_fine():
    result = scan("story_refund_request_reviewed.md")
    assert result.stdout.splitlines()[0] == ('line 4: "support"  Support how? Which cases exactly?')
    assert "1 vague words found" in result.stdout


def test_the_scan_reads_stdin_and_passes_clear_text():
    result = scan(stdin="The total must be shown within 2 seconds.\n")
    assert result.returncode == 0
    assert result.stdout.startswith("No vague words found.")


def test_the_scan_matches_whole_words_only():
    sys.path.insert(0, str(TEMPLATES))
    try:
        from ambiguity_scan import scan as scan_text
    finally:
        sys.path.pop(0)
    assert scan_text("breakfast is a steady fastener") == []
    assert [w for _, w, _ in scan_text("Should be FAST, etc.")] == ["Should", "FAST", "etc"]


def test_pytest_alone_misses_the_mistakes(tmp_path):
    # A fresh copy: pytest shows the "always true" warning only the first time it reads a file.
    shutil.copy(STATIC / "test_cart_mistakes.py", tmp_path)
    result = run(
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        "test_cart_mistakes.py",
        cwd=tmp_path,
    )
    assert "1 failed, 3 passed, 1 warning" in result.stdout
    assert "assertion is always true, perhaps remove parentheses?" in result.stdout
    assert "assert ['book', 'pen'] == ['pen']" in result.stdout


def test_ruff_with_the_template_settings_finds_all_five(tmp_path):
    shutil.copy(TEMPLATES / "ruff_settings.toml", tmp_path / "ruff.toml")
    shutil.copy(STATIC / "test_cart_mistakes.py", tmp_path)
    shutil.copy(STATIC / "test_cart_fixed.py", tmp_path)
    mistakes = run(
        str(RUFF), "check", "--output-format", "concise", "test_cart_mistakes.py", cwd=tmp_path
    )
    assert mistakes.returncode == 1
    codes = [line.split()[1] for line in mistakes.stdout.splitlines() if ".py:" in line]
    assert codes == ["F401", "B006", "F631", "E722", "E711"]
    fixed = run(str(RUFF), "check", "test_cart_fixed.py", cwd=tmp_path)
    assert fixed.returncode == 0, fixed.stdout


def test_the_fixed_tests_pass():
    result = run(
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        "test_cart_fixed.py",
        cwd=STATIC,
    )
    assert "4 passed" in result.stdout


def test_the_pre_commit_template_is_valid_yaml_with_the_main_hooks():
    config = yaml.safe_load((TEMPLATES / "pre-commit-config.yaml").read_text())
    hooks = {hook["id"] for repo in config["repos"] for hook in repo["hooks"]}
    assert {"gitleaks", "ruff-check", "ruff-format"} <= hooks


@pytest.mark.parametrize(
    ("name", "sections"),
    [
        ("user_story_review_worksheet.md", ["## 2. Acceptance criteria", "## 3. Missing cases"]),
        ("requirements_review_checklist.md", ["## Clear", "## Complete", "## Testable"]),
        ("review_comments_guide.md", ["**must:**", "**question:**", "## When you receive"]),
    ],
)
def test_review_templates_have_their_sections(name, sections):
    text = (TEMPLATES / name).read_text(encoding="utf-8")
    for section in sections:
        assert section in text
