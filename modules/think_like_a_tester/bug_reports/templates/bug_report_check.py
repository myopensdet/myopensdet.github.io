# Template from myOpenSDET: https://myopensdet.github.io/
"""Check a bug report (Markdown, using the bug report template) before you send it.

    python bug_report_check.py my_bug.md

It looks for the parts developers ask about most: a clear title, numbered steps,
expected and actual results that differ, the environment, and severity.
Ends with exit code 1 if something needs fixing.
"""

import re
import sys

REQUIRED = [
    "Steps to reproduce",
    "Expected result",
    "Actual result",
    "Environment",
    "Severity and priority",
]
VAGUE_TITLES = [
    "doesn't work",
    "does not work",
    "not working",
    "broken",
    "bug",
    "error",
    "issue",
    "problem",
]
VAGUE_RESULTS = [
    "it works",
    "works correctly",
    "as expected",
    "should work",
    "it fails",
    "doesn't work",
]


def sections(text: str) -> dict[str, str]:
    """Return {heading: body} for every '## ' heading."""
    parts = re.split(r"^## +(.+?)\s*$", text, flags=re.MULTILINE)
    return {parts[i].strip(): parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}


def is_empty(body: str) -> bool:
    """True if no line has real text: every line is blank or still has a <placeholder>."""
    return not any(line.strip() and not re.search(r"<[^>]+>", line) for line in body.splitlines())


def check(text: str) -> list[str]:
    problems = []
    title = next((line[2:].strip() for line in text.splitlines() if line.startswith("# ")), "")
    if not title or "<" in title:
        problems.append("Title: missing. Say what is wrong, where, and when.")
    elif len(title.split()) < 5 or any(word in title.lower() for word in VAGUE_TITLES):
        problems.append(f'Title: "{title}" is too vague. Say what is wrong, where, and when.')

    found = sections(text)
    for name in REQUIRED:
        if name not in found or is_empty(found[name]):
            problems.append(f"{name}: missing or empty.")

    steps = found.get("Steps to reproduce", "")
    if steps and not is_empty(steps) and len(re.findall(r"^\s*\d+\.", steps, re.MULTILINE)) < 2:
        problems.append("Steps to reproduce: write at least two numbered steps.")

    expected = found.get("Expected result", "").lower()
    actual = found.get("Actual result", "").lower()
    for name, body in [("Expected result", expected), ("Actual result", actual)]:
        if not body or is_empty(body):
            continue
        if any(phrase in body for phrase in VAGUE_RESULTS) or len(body.split()) < 3:
            problems.append(f"{name}: too vague. Write exactly what you saw or expected.")
    if expected and expected == actual:
        problems.append("Expected and actual results are the same. Is it really a bug?")
    return problems


def main(args: list[str]) -> int:
    if len(args) != 1:
        print("Usage: python bug_report_check.py my_bug.md")
        return 2
    with open(args[0], encoding="utf-8") as file:
        problems = check(file.read())
    for problem in problems:
        print(f"- {problem}")
    if problems:
        print(f"\n{len(problems)} things to fix before you send it.")
        return 1
    print("Looks ready to send. Read it once more as if you were the developer.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
